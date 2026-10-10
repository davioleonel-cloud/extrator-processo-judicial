"""Indicadores conservadores; cada ocorrência mantém sua própria fonte."""

import re
import unicodedata

from .modelos import atualizar_resumo, novo_modelo


ROTULOS = {
    "numero_processo": r"(?:numero (?:do )?processo|processo(?: n[.oº°]*)?|autos(?: n[.oº°]*)?)",
    "autores": r"(?:autor(?:a)?(?:es|\(es\))?|requerentes?|reclamantes?|polo ativo)",
    "reus": r"(?:reu(?:s|\(s\))?|re(?:s)?|requerid[oa]s?|reclamad[oa]s?|polo passivo)",
    "vara_judicial": r"(?:vara(?: judicial)?|juizo)",
    "juiz": r"(?:juiz(?:a)?(?: de direito)?|magistrad[oa])",
    "tipo_acao": r"(?:tipo (?:de |da )?acao|acao|classe(?: processual)?)",
    "pedido": r"(?:pedido(?: principal)?|solicitacao(?: pleiteada)?|objeto (?:da acao|do pedido))",
}
PADROES = {
    campo: re.compile(r"^\s*" + rotulo + r"\s*[:–-]\s*(\S.*?)\s*$")
    for campo, rotulo in ROTULOS.items()
}


def normalizar(texto):
    return "".join(
        c for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )


def _cabecalho(linha):
    texto = normalizar(linha).strip()
    if re.match(r"^(?:peticao inicial|da peticao inicial)\b", texto):
        return "peticao_inicial", "indefinida"
    if re.match(r"^(?:quesitos|dos quesitos)\b", texto):
        origens = []
        for origem, padrao in (
            ("juiz", r"\b(?:juiz|juizo|magistrado)\b"),
            ("autor", r"\b(?:autor|autora|autores|requerente|reclamante)\b"),
            ("reu", r"\b(?:reu|re|reus|requerido|requerida|reclamado|reclamada)\b"),
        ):
            if re.search(padrao, texto):
                origens.append(origem)
        return "quesitos", origens[0] if len(origens) == 1 else "indefinida"
    if (
        re.search(r"\b(?:nomeio|designo)\b.{0,100}\bperit[oa]\b", texto)
        or re.search(r"\b(?:nomeacao|designacao) (?:do|da|de) perit[oa]\b", texto)
    ):
        return "nomeacao_perito", "indefinida"
    return None


def extrair(documento, paginas):
    dados = novo_modelo(documento, paginas)

    def adicionar(campo, original, numero, trecho, origem="indefinida"):
        natureza = "alegacao" if campo in ("pedido", "peticao_inicial") else "informacao_documental"
        dados["candidatos"].append({
            "id": f'c{len(dados["candidatos"]) + 1:04d}',
            "campo": campo,
            "origem": origem,
            "original": original,
            "valor": original,
            "natureza_original": natureza,
            "natureza": natureza,
            "fonte": {"documento": documento["hash"], "pagina": numero, "trecho": trecho},
            "estado": "a_revisar",
            "historico": [],
        })

    for pagina in paginas:
        linhas = pagina["texto"].splitlines(keepends=True)
        for indice, linha in enumerate(linhas):
            limpa = linha.rstrip("\r\n")
            for campo, padrao in PADROES.items():
                match = padrao.match(normalizar(limpa))
                if match:
                    valor = re.split(r"[:–-]", limpa, maxsplit=1)[1].strip()
                    adicionar(campo, valor, pagina["numero"], limpa)
            cabecalho = _cabecalho(limpa)
            if not cabecalho:
                continue
            campo, origem = cabecalho
            fim = indice + 1
            if campo != "nomeacao_perito":
                while fim < len(linhas):
                    proxima = linhas[fim].rstrip("\r\n")
                    if _cabecalho(proxima) or any(
                        p.match(normalizar(proxima)) for p in PADROES.values()
                    ):
                        break
                    fim += 1
            trecho = "".join(linhas[indice:fim])
            adicionar(campo, trecho, pagina["numero"], trecho, origem)
    atualizar_resumo(dados)
    return dados
