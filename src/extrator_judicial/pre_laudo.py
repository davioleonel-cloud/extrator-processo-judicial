"""Pré-laudo em Word (.docx) para preencher no ato pericial.

Usa apenas candidatos não rejeitados, sempre com a folha de origem. Campos que
o extrator não localizou, ou que divergem, ficam destacados em amarelo para o
perito preencher ou conferir. Nenhum diagnóstico, nexo, incapacidade ou
resposta a quesito é gerado: essas partes são roteiros de marcação.
"""

import io
import re
from collections import Counter
from pathlib import Path

from . import conteudo_pericial as cp
from .extracao import normalizar
from .inicial import FOLHA, RODAPE_PJE
from .pdf import ErroExtrator

MODELOS = ("previdenciario", "trabalhista", "curatela")
MODELO_POR_TIPO = {"previdenciaria": "previdenciario", "trabalhista": "trabalhista", "curatela": "curatela"}
TITULOS = {
    "previdenciario": "Perícia médica previdenciária",
    "trabalhista": "Perícia médica trabalhista",
    "curatela": "Perícia médica em ação de curatela / interdição",
}
ORIGENS_QUESITOS = (
    ("juiz", "Quesitos do Juízo"),
    ("autor", "Quesitos da parte autora"),
    ("reu", "Quesitos da parte ré"),
    ("ministerio_publico", "Quesitos do Ministério Público"),
    ("indefinida", "Quesitos de origem a confirmar nos autos"),
)
ITEM_QUESITO = re.compile(r"^\s*(\d{1,3}|[a-z])\s*[.)–:-]\s*\S")
LOGO_ALTURA_PX = 90

# ---------------------------------------------------------------------------
# Valores visuais do documento (únicos pontos a alterar para mudar o padrão).
# ---------------------------------------------------------------------------
FONTE = "Arial"
TAMANHOS = {  # pt
    "titulo": 15, "subtitulo": 11.5, "secao": 12.5, "subsecao": 11, "corpo": 11,
    "tabela": 9.5, "nota": 9.5, "aviso": 9, "cabecalho_nome": 10, "cabecalho": 9, "rodape": 8,
}
ESPACOS = {"paragrafo": 4, "fim_cabecalho": 12, "linhas_cabecalho": 0}  # pt
ENTRELINHAS = 1.15
PAGINA = {"altura": 29.7, "largura": 21, "superior": 2, "inferior": 2, "esquerda": 3, "direita": 2}  # cm
LARGURA_UTIL_CM = PAGINA["largura"] - PAGINA["esquerda"] - PAGINA["direita"]
# Marcadores no texto: [preencher] = dado ausente; ⟦…⟧ = dado extraído a conferir.
MARCADOR = re.compile(r"(\[preencher\]|⟦[^⟧]*⟧)")
DESTAQUES = {"preencher": "YELLOW", "conferir": "GRAY_25"}  # WD_COLOR_INDEX
LEGENDA = (
    "Rascunho de trabalho para o ato pericial. Fundo amarelo: dado a preencher na perícia. "
    "Fundo cinza: dado extraído dos autos que precisa ser conferido na folha indicada. "
    "Dados extraídos automaticamente não substituem a leitura dos autos."
)


def _docx():
    try:
        import docx
    except ImportError:
        raise ErroExtrator("Exportação Word requer o pacote python-docx. Reinstale com: pip install -e .") from None
    return docx


# ---------------------------------------------------------------------------
# Leitura dos candidatos revisados.
# ---------------------------------------------------------------------------
def _ativos(dados, campo):
    candidatos = [c for c in dados["candidatos"] if c["campo"] == campo and c["estado"] != "rejeitado"]
    revisados = [c for c in candidatos if c["estado"] in ("confirmado", "corrigido")]
    return revisados or candidatos


def valor_campo(dados, campo):
    """(texto, folhas, situação): situação é 'ok', 'conferir' (divergente/não revisado) ou 'ausente'."""
    candidatos = _ativos(dados, campo)
    if not candidatos:
        return None, [], "ausente"
    contagem = Counter(c["valor"].strip() for c in candidatos)
    valores = [v for v, _ in contagem.most_common()]
    folhas = sorted({c["fonte"]["pagina"] for c in candidatos})
    revisado = all(c["estado"] in ("confirmado", "corrigido") for c in candidatos)
    situacao = "ok" if len(valores) == 1 and revisado else "conferir"
    return " / ".join(valores[:3]), folhas, situacao


def _folhas(folhas, limite=8):
    if not folhas:
        return ""
    texto = ", ".join(map(str, folhas[:limite])) + (" …" if len(folhas) > limite else "")
    return f"fls. {texto}"


def _faixa(fonte):
    final = fonte.get("pagina_final", fonte["pagina"])
    return str(fonte["pagina"]) if final == fonte["pagina"] else f'{fonte["pagina"]} a {final}'


def separar_quesitos(texto):
    """Título e itens numerados; sem numeração, o bloco inteiro vira um item."""
    linhas = [
        linha.rstrip() for linha in texto.splitlines()
        if linha.strip() and not RODAPE_PJE.search(linha) and not FOLHA.match(linha)
    ]
    titulo, itens = [], []
    for linha in linhas:
        if ITEM_QUESITO.match(linha):
            itens.append([linha.strip()])
        elif itens:
            itens[-1].append(linha.strip())
        else:
            titulo.append(linha.strip())
    if not itens:
        return " ".join(titulo[:1]), [" ".join(titulo[1:]) or " ".join(titulo)]
    return " ".join(titulo), [" ".join(item) for item in itens]


def cids_dos_autos(dados):
    """Códigos CID citados com rótulo 'CID' em qualquer página, e os da inicial.

    Em páginas lidas por OCR, um dígito no lugar da letra inicial é corrigido
    pelas trocas mais comuns e o código recebe a marca '(OCR, conferir)'.
    """
    encontrados = {}
    for pagina in dados["paginas"]:
        for linha in pagina["texto"].splitlines():
            # Na linha rotulada com "CID", todos os códigos citados (ex.: "CID G30.1 e F00.1").
            if cp.CID_TEXTO.search(linha):
                for codigo in cp.CID_CODIGO.findall(linha.upper()):
                    encontrados.setdefault(codigo, set()).add(pagina["numero"])
        if "ocr" in pagina:
            for digito, resto in cp.CID_OCR.findall(pagina["texto"]):
                if digito in cp.TROCAS_OCR:
                    codigo = f"{cp.TROCAS_OCR[digito]}{resto} (OCR, conferir)"
                    encontrados.setdefault(codigo, set()).add(pagina["numero"])
    for candidato in _ativos(dados, "cid_mencionado"):
        for codigo in cp.CID_CODIGO.findall(candidato["valor"]):
            encontrados.setdefault(codigo.upper(), set()).add(candidato["fonte"]["pagina"])
    return {codigo: sorted(paginas) for codigo, paginas in sorted(encontrados.items())}


def indice_documental(dados, modelo):
    especifico = {
        "previdenciario": cp.INDICE_PREVIDENCIARIO,
        "trabalhista": cp.INDICE_TRABALHISTA,
        "curatela": cp.INDICE_CURATELA,
    }[modelo]
    resultado = []
    for categoria, padrao in cp.INDICE_COMUM + especifico:
        regex = re.compile(padrao)
        paginas = [p["numero"] for p in dados["paginas"] if regex.search(normalizar(p["texto"]))]
        if paginas:
            resultado.append((categoria, paginas))
    return resultado


# ---------------------------------------------------------------------------
# Formatação Word.
# ---------------------------------------------------------------------------
class _Documento:
    def __init__(self, perfil, logo):
        docx = _docx()
        from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
        from docx.shared import Cm, Pt
        self.Pt, self.Cm = Pt, Cm
        self.alinhamento = WD_ALIGN_PARAGRAPH
        self.destaques = {nome: getattr(WD_COLOR_INDEX, cor) for nome, cor in DESTAQUES.items()}
        self.doc = docx.Document()
        estilo = self.doc.styles["Normal"]
        estilo.font.name = FONTE
        estilo.font.size = Pt(TAMANHOS["corpo"])
        estilo.paragraph_format.space_after = Pt(ESPACOS["paragrafo"])
        estilo.paragraph_format.line_spacing = ENTRELINHAS
        from docx.oxml.ns import qn
        for nome, token in (("Heading 1", "secao"), ("Heading 2", "subsecao"), ("Title", "titulo")):
            titulo = self.doc.styles[nome]
            titulo.font.name = FONTE
            titulo.font.size = Pt(TAMANHOS[token])
            titulo.font.color.rgb = None
            fontes = titulo.element.rPr.rFonts
            for atributo in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                fontes.attrib.pop(qn(atributo), None)
        # Título sem a borda inferior colorida do modelo padrão do Word.
        titulo = self.doc.styles["Title"]
        borda = titulo.element.pPr.find(qn("w:pBdr")) if titulo.element.pPr is not None else None
        if borda is not None:
            titulo.element.pPr.remove(borda)
        titulo.font.bold = True
        titulo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        titulo.paragraph_format.space_after = Pt(ESPACOS["paragrafo"])
        secao = self.doc.sections[0]
        secao.page_height, secao.page_width = Cm(PAGINA["altura"]), Cm(PAGINA["largura"])
        secao.top_margin, secao.bottom_margin = Cm(PAGINA["superior"]), Cm(PAGINA["inferior"])
        secao.left_margin, secao.right_margin = Cm(PAGINA["esquerda"]), Cm(PAGINA["direita"])
        self._cabecalho(secao, perfil, logo)
        self._rodape(secao)

    def _cabecalho(self, secao, perfil, logo):
        cabecalho = secao.header
        primeiro = cabecalho.paragraphs[0]
        primeiro.alignment = self.alinhamento.CENTER
        if logo:
            caminho = Path(logo)
            if not caminho.is_file():
                raise ErroExtrator("Logotipo não encontrado; confira o caminho informado.")
            try:
                # 90 px a 96 dpi = 67,5 pt de altura; largura proporcional.
                imagem = primeiro.add_run().add_picture(str(caminho), height=self.Pt(LOGO_ALTURA_PX * 72 / 96))
                imagem._inline.docPr.set("descr", "Logotipo do perito")
            except Exception:
                raise ErroExtrator("Logotipo inválido; use imagem PNG ou JPEG.") from None
            primeiro = cabecalho.add_paragraph()
            primeiro.alignment = self.alinhamento.CENTER
        for indice, linha in enumerate(perfil["cabecalho"]):
            paragrafo = primeiro if indice == 0 else cabecalho.add_paragraph()
            paragrafo.alignment = self.alinhamento.CENTER
            paragrafo.paragraph_format.space_after = self.Pt(ESPACOS["linhas_cabecalho"])
            run = paragrafo.add_run(linha)
            run.bold = indice == 0
            run.font.size = self.Pt(TAMANHOS["cabecalho_nome" if indice == 0 else "cabecalho"])
        paragrafo.paragraph_format.space_after = self.Pt(ESPACOS["fim_cabecalho"])

    def _campo_word(self, paragrafo, codigo):
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        run = paragrafo.add_run()
        for tipo, texto in (("begin", None), (None, codigo), ("separate", None), (None, "1"), ("end", None)):
            if tipo:
                elemento = OxmlElement("w:fldChar")
                elemento.set(qn("w:fldCharType"), tipo)
            else:
                elemento = OxmlElement("w:instrText" if texto == codigo else "w:t")
                elemento.set(qn("xml:space"), "preserve")
                elemento.text = texto
            run._r.append(elemento)
        run.font.size = self.Pt(TAMANHOS["rodape"])

    def _rodape(self, secao):
        paragrafo = secao.footer.paragraphs[0]
        paragrafo.alignment = self.alinhamento.CENTER
        paragrafo.add_run("Pré laudo, rascunho de trabalho  |  Página ").font.size = self.Pt(TAMANHOS["rodape"])
        self._campo_word(paragrafo, "PAGE")
        paragrafo.add_run(" de ").font.size = self.Pt(TAMANHOS["rodape"])
        self._campo_word(paragrafo, "NUMPAGES")

    def _escrever(self, paragrafo, texto, negrito=False, italico=False, tamanho=None):
        """Escreve o texto destacando [preencher] (amarelo) e ⟦trechos a conferir⟧ (cinza)."""
        for pedaco in MARCADOR.split(str(texto)):
            if not pedaco:
                continue
            conferir = pedaco.startswith("⟦")
            run = paragrafo.add_run(pedaco.strip("⟦⟧") if conferir else pedaco)
            run.bold = negrito
            run.italic = italico
            if tamanho:
                run.font.size = self.Pt(TAMANHOS[tamanho])
            if conferir:
                run.font.highlight_color = self.destaques["conferir"]
            elif pedaco == cp.CAMPO:
                run.font.highlight_color = self.destaques["preencher"]

    def titulo_documento(self, texto):
        self.doc.add_paragraph(texto, style="Title")

    def titulo(self, texto, nivel=1):
        self.doc.add_heading(texto, level=nivel)

    def paragrafo(self, *partes, negrito=False, italico=False, tamanho=None, centro=False, justificar=True):
        """Partes str; tamanho é uma chave de TAMANHOS (por exemplo "nota")."""
        paragrafo = self.doc.add_paragraph()
        if centro:
            paragrafo.alignment = self.alinhamento.CENTER
        elif justificar:
            paragrafo.alignment = self.alinhamento.JUSTIFY
        for parte in partes:
            self._escrever(paragrafo, parte, negrito, italico, tamanho)
        return paragrafo

    def _propriedade_linha(self, linha, nome):
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        elemento = OxmlElement(nome)
        elemento.set(qn("w:val"), "true")
        linha._tr.get_or_add_trPr().append(elemento)

    def tabela(self, cabecalho, linhas, larguras):
        """Larguras em cm devem somar a largura útil da página (LARGURA_UTIL_CM)."""
        if len(larguras) != len(cabecalho) or abs(sum(larguras) - LARGURA_UTIL_CM) > 0.01:
            raise ValueError("Larguras da tabela incompatíveis com a largura útil da página.")
        tabela = self.doc.add_table(rows=1, cols=len(cabecalho))
        tabela.style = "Table Grid"
        for celula, texto in zip(tabela.rows[0].cells, cabecalho):
            self._escrever(celula.paragraphs[0], texto, negrito=True, tamanho="tabela")
        # Cabeçalho repetido em cada página; nenhuma linha partida entre páginas.
        self._propriedade_linha(tabela.rows[0], "w:tblHeader")
        for linha in linhas:
            nova = tabela.add_row()
            for celula, texto in zip(nova.cells, linha):
                self._escrever(celula.paragraphs[0], texto, tamanho="tabela")
        for linha in tabela.rows:
            self._propriedade_linha(linha, "w:cantSplit")
        tabela.autofit = False
        for coluna, largura in zip(tabela.columns, larguras):
            coluna.width = self.Cm(largura)
        for linha in tabela.rows:
            for celula, largura in zip(linha.cells, larguras):
                celula.width = self.Cm(largura)
        self.doc.add_paragraph()
        return tabela

    def bytes(self):
        saida = io.BytesIO()
        self.doc.save(saida)
        return saida.getvalue()


def _valor_ou_campo(dados, campo):
    valor, folhas, situacao = valor_campo(dados, campo)
    if situacao == "ausente":
        return cp.CAMPO
    texto = f"{valor} ({_folhas(folhas)})"
    return texto if situacao == "ok" else f"⟦{texto}⟧ (conferir)"


# ---------------------------------------------------------------------------
# Seções.
# ---------------------------------------------------------------------------
def _preambulo(d, dados, perfil, modelo):
    d.titulo("1. PREÂMBULO")
    processo = _valor_ou_campo(dados, "numero_processo")
    vara = _valor_ou_campo(dados, "vara_judicial")
    autor = _valor_ou_campo(dados, "autores")
    reu = _valor_ou_campo(dados, "reus")
    parte = "interditando(a)" if modelo == "curatela" else "periciando(a)"
    d.paragrafo(
        f'Eu, {perfil["nome"]}, médico inscrito no {perfil["crm"]}, nomeado perito judicial nos autos do '
        f"processo nº ", processo, ", em trâmite perante ", vara, ", em que figuram como requerente ", autor,
        " e como requerido(a) ", reu, ", apresento o presente laudo médico pericial, elaborado a partir da "
        "análise dos autos, da anamnese e do exame físico pericial realizados em ", cp.CAMPO, ", às ",
        cp.CAMPO, ", no endereço ", cp.CAMPO, ".",
    )
    d.tabela(("Item", "Dado (conferir na folha indicada)"), [
        ("Processo", processo), ("Vara / Juízo", vara), ("Juiz(a)", _valor_ou_campo(dados, "juiz")),
        ("Classe / tipo de ação", _valor_ou_campo(dados, "tipo_acao")),
        ("Requerente", autor), ("Requerido(a)", reu),
        (f"Documento de identificação do(a) {parte}", cp.CAMPO),
        ("Data de nascimento / idade", cp.CAMPO),
        ("Acompanhante(s) e grau de parentesco", cp.CAMPO),
        ("Assistentes técnicos presentes", cp.CAMPO),
    ], larguras=(5.5, 10.5))


def _objeto(d, dados, modelo):
    d.titulo("2. OBJETO DA PERÍCIA")
    objeto = dados["pericia"]["objeto"]
    if objeto:
        d.paragrafo(objeto)
    else:
        d.paragrafo(cp.CAMPO, " (objeto específico ainda não confirmado na revisão; conferir decisão de nomeação).")
    nomeacoes = _ativos(dados, "nomeacao_perito")
    if nomeacoes:
        folhas = sorted({c["fonte"]["pagina"] for c in nomeacoes})
        d.paragrafo(f"Decisão de nomeação localizada em {_folhas(folhas)} (conferir).", italico=True)
    pedido, folhas, situacao = valor_campo(dados, "pedido")
    if situacao != "ausente":
        d.paragrafo("Pedido indicado nos autos: ", f"⟦{pedido}⟧" if situacao != "ok" else pedido,
                    f" ({_folhas(folhas)}).")


def _sintese(d, dados, modelo):
    d.titulo("3. SÍNTESE DOS AUTOS E DOCUMENTOS IMPORTANTES")
    d.paragrafo(
        "Os itens abaixo foram localizados por leitura automatizada dos autos e são alegações ou "
        "informações documentais, não fatos comprovados. Cada item indica a folha para conferência.",
        italico=True, tamanho="nota",
    )
    pedidos = _ativos(dados, "pedido_item")
    if pedidos:
        d.titulo("3.1 Pedidos da petição inicial", 2)
        for c in pedidos:
            d.paragrafo(f'Fls. {_faixa(c["fonte"])}: ', " ".join(c["valor"].split()))
    secoes = _ativos(dados, "inicial_secao")
    if secoes:
        d.titulo("3.2 Estrutura da petição inicial", 2)
        d.tabela(("Seção", "Fls."), [(c["valor"].split("\n")[0], _faixa(c["fonte"])) for c in secoes],
                 larguras=(13, 3))
    d.titulo("3.3 Índice de documentos possivelmente relevantes", 2)
    indice = indice_documental(dados, modelo)
    if indice:
        d.tabela(("Categoria (busca por palavras, conferir)", "Folhas"),
                 [(categoria, _folhas(paginas, 15)) for categoria, paginas in indice], larguras=(9, 7))
    else:
        d.paragrafo(cp.CAMPO, " (nenhuma categoria localizada automaticamente; verificar páginas sem texto).")
    ocr = [p["numero"] for p in dados["paginas"] if p["necessita_ocr"] and not p["texto"].strip()]
    if ocr:
        d.paragrafo(f"Páginas sem texto legível, a ler diretamente no PDF: {_folhas(ocr, 30)}.", italico=True)
    lidas_ocr = [p["numero"] for p in dados["paginas"] if "ocr" in p and p["texto"].strip()]
    if lidas_ocr:
        d.paragrafo(f"Páginas lidas por OCR (podem conter erros de leitura): {_folhas(lidas_ocr, 30)}.",
                    italico=True)
    cids = cids_dos_autos(dados)
    d.titulo("3.4 CID citados nos autos", 2)
    if cids:
        d.tabela(("CID", "Folhas"), [(codigo, _folhas(pags)) for codigo, pags in cids.items()],
                 larguras=(4, 12))
    else:
        d.paragrafo(cp.CAMPO, " (nenhum CID localizado automaticamente).")
    datas = _ativos(dados, "data_mencionada")
    d.titulo("3.5 Datas citadas na inicial (classificar o tipo)", 2)
    if datas:
        d.tabela(("Fls.", "Trecho", "Tipo (DID, DII, acidente, DER, DCB, atestado)"),
                 [(_faixa(c["fonte"]), " ".join(c["valor"].split()), cp.CAMPO) for c in datas],
                 larguras=(1.5, 10, 4.5))
    else:
        d.paragrafo(cp.CAMPO)
    d.titulo("3.6 Documentos médicos analisados", 2)
    d.tabela(("Fls.", "Data", "Documento e emissor", "Conteúdo relevante"),
             [(cp.CAMPO, cp.CAMPO, cp.CAMPO, cp.CAMPO) for _ in range(4)], larguras=(1.5, 2.5, 4.5, 7.5))


def _dados_especificos(d, modelo):
    if modelo == "previdenciario":
        d.titulo("4. DADOS LABORAIS E PREVIDENCIÁRIOS")
        d.tabela(("Item", "Registro"), cp.DADOS_PREVIDENCIARIOS, larguras=(7, 9))
        d.paragrafo("Benefícios recebidos (conferir CNIS e comunicações de decisão):", negrito=True)
        d.tabela(cp.TABELA_BENEFICIOS, [(cp.CAMPO,) * len(cp.TABELA_BENEFICIOS) for _ in range(3)],
                 larguras=(3, 2, 2.5, 2.5, 3, 3))
        d.paragrafo(cp.NOTA_ESPECIES, italico=True, tamanho="nota")
    elif modelo == "trabalhista":
        d.titulo("4. HISTÓRIA OCUPACIONAL")
        d.tabela(("Item", "Registro"), cp.DADOS_TRABALHISTAS, larguras=(7, 9))
    else:
        d.titulo("4. DADOS SOCIAIS, FUNCIONAIS E TEMPORALIDADE")
        d.tabela(("Item", "Registro"), cp.DADOS_CURATELA, larguras=(7, 9))
        d.paragrafo("Temporalidade da doença:", negrito=True)
        d.tabela(("Item", "Registro"), cp.TEMPORALIDADE, larguras=(9, 7))


def _historia(d, modelo):
    d.titulo("5. HISTÓRIA CLÍNICA")
    itens = [
        "Queixa principal", "História da doença atual (início, evolução, tratamentos realizados e resposta)",
        "Cirurgias e internações", "Medicações em uso e adesão", "Comorbidades e antecedentes pessoais",
        "Antecedentes familiares", "Hábitos (tabagismo, etilismo, outras substâncias)",
        "Atividades da vida diária e lazer relatadas",
    ]
    if modelo == "curatela":
        itens.insert(1, "Relato do informante (comparar com o relato do interditando)")
    d.tabela(("Item", "Registro"), [(item, cp.CAMPO) for item in itens], larguras=(6, 10))


def _exame(d, dados, modelo):
    d.titulo("6. EXAME FÍSICO PERICIAL")
    d.titulo("6.1 Exame físico geral", 2)
    d.tabela(("Item", "Achado"), cp.EXAME_GERAL, larguras=(8, 8))
    cids = list(cids_dos_autos(dados))
    blocos = cp.blocos_para_cids(cids, modelo)
    if cids:
        d.paragrafo(
            "Segmentos selecionados a partir dos CID citados nos autos (" + ", ".join(cids[:12]) + "). "
            "Acrescentar outros segmentos se a queixa atual for diferente.", italico=True, tamanho="nota",
        )
    else:
        d.paragrafo("Nenhum CID localizado: roteiro ortopédico geral. Remover os segmentos não pertinentes.",
                    italico=True, tamanho="nota")
    for numero, nome in enumerate(blocos, 2):
        bloco = cp.BLOCOS_EXAME[nome]
        d.titulo(f'6.{numero} {bloco["titulo"]}', 2)
        if bloco["inspecao"]:
            d.tabela(("Inspeção / observação", "Achado"), [(i, cp.CAMPO) for i in bloco["inspecao"]],
                     larguras=(9, 7))
        if bloco["adm"]:
            d.tabela(("Amplitude de movimento", "Referência normal", "Direito", "Esquerdo"),
                     [(m, ref, cp.CAMPO, cp.CAMPO) for m, ref in bloco["adm"]], larguras=(6.5, 3.5, 3, 3))
        if bloco["testes"]:
            d.tabela(("Manobra / teste", "Significado do achado positivo", "Resultado"),
                     [(t, s, cp.CAMPO) for t, s in bloco["testes"]], larguras=(5, 7.5, 3.5))
    if modelo == "curatela":
        d.titulo(f"6.{len(blocos) + 2} Escalas cognitivas e funcionais", 2)
        d.tabela(("Instrumento", "Interpretação", "Resultado"),
                 [(nome, interp, cp.CAMPO) for nome, interp in cp.ESCALAS_CURATELA], larguras=(4.5, 8.5, 3))
        d.titulo(f"6.{len(blocos) + 3} Capacidades específicas avaliadas", 2)
        d.tabela(("Capacidade", "Preservada / com apoio / ausente"),
                 [(c, cp.CAMPO) for c in cp.CAPACIDADES_CURATELA], larguras=(10, 6))
    d.titulo("7. EXAMES COMPLEMENTARES APRESENTADOS NO ATO PERICIAL", 1)
    d.tabela(("Data", "Exame", "Resultado relevante"), [(cp.CAMPO,) * 3 for _ in range(3)],
             larguras=(2.5, 4.5, 9))


def _discussao(d, modelo):
    d.titulo("8. DISCUSSÃO TÉCNICA")
    d.titulo("8.1 Análise do caso", 2)
    d.paragrafo(
        cp.CAMPO, " (correlacionar história, documentos com folhas, achados do exame físico e exigências "
        "da atividade ou dos atos da vida civil; explicar em linguagem simples o significado de cada achado "
        "relevante para o Juízo).",
    )
    d.titulo("8.2 Fundamentação técnica e normativa de apoio", 2)
    d.paragrafo("Textos de apoio: manter apenas o que for pertinente ao caso.", italico=True, tamanho="nota")
    for titulo, texto in cp.DISCUSSAO[modelo]:
        d.paragrafo(titulo, negrito=True)
        d.paragrafo(texto)


def _conclusao(d, modelo):
    d.titulo("9. CONCLUSÃO")
    for linha in cp.CONCLUSAO[modelo]:
        d.paragrafo(linha)


def _quesitos(d, dados, modelo):
    d.titulo("10. RESPOSTA AOS QUESITOS")
    candidatos = _ativos(dados, "quesitos")
    if not candidatos:
        d.paragrafo(cp.NOTA_QUESITOS_AUSENTES[modelo])
        return
    d.paragrafo(
        "Quesitos transcritos dos autos na redação e numeração originais. Os blocos foram delimitados "
        "automaticamente e podem continuar na página seguinte: conferir no original.",
        italico=True, tamanho="nota",
    )
    vistos = set()
    for origem, rotulo in ORIGENS_QUESITOS:
        grupo = []
        for c in candidatos:
            chave = " ".join(c["valor"].split())
            if c["origem"] == origem and chave not in vistos:
                vistos.add(chave)
                grupo.append(c)
        if not grupo:
            continue
        d.titulo(rotulo, 2)
        for c in grupo:
            titulo, itens = separar_quesitos(c["valor"])
            d.paragrafo(f'Transcrição de fls. {_faixa(c["fonte"])}' + (f": {titulo}" if titulo else ""),
                        italico=True, tamanho="nota")
            for item in itens:
                d.paragrafo(item, italico=True)
                d.paragrafo("Resposta: ", cp.CAMPO)


def _encerramento(d, perfil):
    d.titulo("11. ENCERRAMENTO")
    d.paragrafo(
        "Nada mais havendo a relatar, encerro o presente laudo, que segue assinado digitalmente, "
        "e permaneço à disposição do Juízo para eventuais esclarecimentos.",
    )
    d.paragrafo(perfil["cidade"] or cp.CAMPO, ", ", cp.CAMPO, ".", centro=True)
    d.paragrafo("")
    d.paragrafo(perfil["nome"], negrito=True, centro=True)
    d.paragrafo(f'Médico Perito Judicial | {perfil["crm"]}', centro=True)


def _referencias(d, modelo):
    d.titulo("REFERÊNCIAS")
    for referencia in cp.REFERENCIAS["comum"] + cp.REFERENCIAS[modelo]:
        d.paragrafo(referencia, tamanho="nota", justificar=False)


def gerar_pre_laudo(dados, modelo, perfil, logo=None):
    """Bytes de um .docx; levanta ErroExtrator em modelo ou logotipo inválido."""
    if modelo not in MODELOS:
        raise ErroExtrator("Modelo de pré-laudo inválido.")
    d = _Documento(perfil, logo or perfil.get("logo") or None)
    d.titulo_documento("PRÉ LAUDO MÉDICO PERICIAL")
    d.paragrafo(TITULOS[modelo], tamanho="subtitulo", centro=True)
    d.paragrafo(LEGENDA, italico=True, tamanho="aviso", centro=True)
    _preambulo(d, dados, perfil, modelo)
    _objeto(d, dados, modelo)
    _sintese(d, dados, modelo)
    _dados_especificos(d, modelo)
    _historia(d, modelo)
    _exame(d, dados, modelo)
    _discussao(d, modelo)
    _conclusao(d, modelo)
    _quesitos(d, dados, modelo)
    _encerramento(d, perfil)
    _referencias(d, modelo)
    return d.bytes()
