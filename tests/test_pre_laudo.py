"""Pré-laudo Word: cabeçalho, dados com folha, quesitos e roteiros sem conclusão automática."""

import io
import json

import pytest

docx = pytest.importorskip("docx")

from extrator_judicial.cli import main  # noqa: E402
from extrator_judicial.extracao import extrair  # noqa: E402
from extrator_judicial.pdf import ErroExtrator, ler_pdf  # noqa: E402
from extrator_judicial.perfil import PERFIL_PADRAO, carregar_perfil  # noqa: E402
from extrator_judicial.persistencia import salvar_arquivos  # noqa: E402
from extrator_judicial.pre_laudo import (  # noqa: E402
    cids_dos_autos, gerar_pre_laudo, separar_quesitos, valor_campo,
)
from extrator_judicial.revisao import revisar  # noqa: E402

RODAPE = "Documento assinado eletronicamente por JUIZ FICTÍCIO, em 01/01/2099, às 10:00:00 - abc1234"


def _texto(conteudo):
    documento = docx.Document(io.BytesIO(conteudo))
    partes = [p.text for p in documento.paragraphs]
    for tabela in documento.tables:
        for linha in tabela.rows:
            partes.extend(c.text for c in linha.cells)
    cabecalho = [p.text for p in documento.sections[0].header.paragraphs]
    return "\n".join(partes), "\n".join(cabecalho)


@pytest.fixture
def pdf_previdenciario(criar_pdf):
    return criar_pdf([
        "Processo: 5000000-00.2099.4.03.6100\n"
        "Autor: Pessoa Fictícia Alfa\n"
        "Réu: Instituto Nacional do Seguro Social\n"
        "Vara judicial: 1ª Vara Federal Fictícia\n"
        "Relatório médico fictício: lombalgia, CID M54.5 e M51.1.\n"
        "Quesitos do Juízo:\n"
        "1. O autor é portador de doença?\n"
        "2. Há incapacidade?\n"
        + RODAPE + "\n"
        "Quesitos do INSS:\n"
        "1. Há redução da capacidade?\n",
    ])


def test_separar_quesitos_remove_rodape_e_mantem_numeracao():
    titulo, itens = separar_quesitos(
        "Quesitos do Juízo:\n1. Primeira pergunta\ncontinua aqui?\n2) Segunda?\n" + RODAPE + "\nFls.: 3\n"
    )
    assert titulo == "Quesitos do Juízo:"
    assert itens == ["1. Primeira pergunta continua aqui?", "2) Segunda?"]
    assert separar_quesitos("Quesitos:\nTexto sem numeração") == ("Quesitos:", ["Texto sem numeração"])


def test_valor_campo_prefere_revisado_e_sinaliza_divergencia(pdf_ficticio):
    dados = extrair(*ler_pdf(pdf_ficticio))
    valor, folhas, situacao = valor_campo(dados, "autores")
    assert situacao == "conferir" and folhas == [1, 3] and "/" in valor
    autores = [c for c in dados["candidatos"] if c["campo"] == "autores"]
    revisar(dados, autores[0]["id"], "confirmar")
    assert valor_campo(dados, "autores") == ("Pessoa Fictícia Alfa", [1], "ok")
    revisar(dados, autores[0]["id"], "rejeitar")
    assert valor_campo(dados, "autores")[0] == "Pessoa Fictícia Delta"
    assert valor_campo(dados, "juiz")[2] != "ausente"
    assert valor_campo(dados, "inexistente") == (None, [], "ausente")


def test_previdenciario_completo(pdf_previdenciario):
    dados = extrair(*ler_pdf(pdf_previdenciario))
    assert {"M54.5", "M51.1"} <= set(cids_dos_autos(dados))
    origens = {c["origem"] for c in dados["candidatos"] if c["campo"] == "quesitos"}
    assert origens == {"juiz", "reu"}
    corpo, cabecalho = _texto(gerar_pre_laudo(dados, "previdenciario", carregar_perfil()))
    for linha in PERFIL_PADRAO["cabecalho"]:
        assert linha in cabecalho
    assert "5000000-00.2099.4.03.6100 (fls. 1)" in corpo
    assert "Coluna vertebral" in corpo and "Lasègue" in corpo
    assert "Ombros" not in corpo
    assert "1. O autor é portador de doença?" in corpo and "Quesitos da parte ré" in corpo
    assert "assinado eletronicamente" not in corpo
    assert "art. 86" in corpo and "Tema 416" in corpo
    assert "[preencher]" in corpo


def test_curatela_e_trabalhista(pdf_ficticio):
    dados = extrair(*ler_pdf(pdf_ficticio))
    curatela, _ = _texto(gerar_pre_laudo(dados, "curatela", carregar_perfil()))
    assert "Miniexame do Estado Mental" in curatela and "art. 753" in curatela
    assert "Exame do estado mental" in curatela and "Exame neurológico" in curatela
    assert "tomada de decisão apoiada" in curatela
    trabalhista, _ = _texto(gerar_pre_laudo(dados, "trabalhista", carregar_perfil()))
    assert "Schilling" in trabalhista and "HISTÓRIA OCUPACIONAL" in trabalhista
    with pytest.raises(ErroExtrator):
        gerar_pre_laudo(dados, "inexistente", carregar_perfil())


def test_sem_cid_usa_roteiro_ortopedico_geral(pdf_ficticio):
    corpo, _ = _texto(gerar_pre_laudo(extrair(*ler_pdf(pdf_ficticio)), "previdenciario", carregar_perfil()))
    for segmento in ("Coluna vertebral", "Ombros", "Joelhos", "Exame do estado mental"):
        assert segmento in corpo


def test_perfil_personalizado_e_invalido(tmp_path, pdf_ficticio):
    perfil = tmp_path / "perfil.json"
    perfil.write_text(json.dumps({"cabecalho": ["Perito Fictício"], "nome": "Perito Fictício"}), encoding="utf-8")
    _, cabecalho = _texto(gerar_pre_laudo(extrair(*ler_pdf(pdf_ficticio)), "curatela", carregar_perfil(perfil)))
    assert cabecalho.strip() == "Perito Fictício"
    perfil.write_text(json.dumps({"desconhecida": "x"}), encoding="utf-8")
    with pytest.raises(ErroExtrator):
        carregar_perfil(perfil)
    perfil.write_text(json.dumps({"cabecalho": "texto"}), encoding="utf-8")
    with pytest.raises(ErroExtrator):
        carregar_perfil(perfil)


def test_logo_ausente_ou_invalido(tmp_path, pdf_ficticio):
    dados = extrair(*ler_pdf(pdf_ficticio))
    with pytest.raises(ErroExtrator):
        gerar_pre_laudo(dados, "curatela", carregar_perfil(), tmp_path / "nao_existe.png")
    falso = tmp_path / "falso.png"
    falso.write_bytes(b"nao e imagem")
    with pytest.raises(ErroExtrator):
        gerar_pre_laudo(dados, "curatela", carregar_perfil(), falso)


def test_salvar_bytes(tmp_path):
    destino = tmp_path / "a.docx"
    salvar_arquivos([(destino, b"\x00\x01binario")])
    assert destino.read_bytes() == b"\x00\x01binario"


def test_cli_pre_laudo_e_exportar_docx(pdf_ficticio, tmp_path, capsys):
    revisao, laudo = tmp_path / "r.json", tmp_path / "pre.docx"
    assert main(["pre-laudo", str(pdf_ficticio), "--modelo", "curatela",
                 "--saida", str(revisao), "--docx", str(laudo)]) == 0
    assert docx.Document(str(laudo)).paragraphs
    # Saídas existentes continuam protegidas.
    assert main(["pre-laudo", str(pdf_ficticio), "--modelo", "curatela",
                 "--saida", str(tmp_path / "r2.json"), "--docx", str(laudo)]) == 1
    assert not (tmp_path / "r2.json").exists()
    # Sem modelo e sem tipo confirmado: erro explicativo.
    assert main(["exportar", str(pdf_ficticio), "--revisao", str(revisao),
                 "--docx", str(tmp_path / "x.docx")]) == 1
    assert "--modelo" in capsys.readouterr().err
    assert main(["exportar", str(pdf_ficticio), "--revisao", str(revisao)]) == 1
    classificado = tmp_path / "c.json"
    assert main(["classificar", str(pdf_ficticio), "--revisao", str(revisao), "--tipo", "curatela",
                 "--objeto", "Capacidade civil fictícia", "--saida", str(classificado)]) == 0
    so_word = tmp_path / "so_word.docx"
    assert main(["exportar", str(pdf_ficticio), "--revisao", str(classificado), "--docx", str(so_word)]) == 0
    corpo, _ = _texto(so_word.read_bytes())
    assert "Capacidade civil fictícia" in corpo and "Escalas cognitivas" in corpo


def _documento(pdf, modelo="previdenciario", logo=None):
    dados = extrair(*ler_pdf(pdf))
    return docx.Document(io.BytesIO(gerar_pre_laudo(dados, modelo, carregar_perfil(), logo)))


def _destaques(documento):
    """Texto destacado agrupado por cor, no corpo e nas tabelas."""
    from docx.enum.text import WD_COLOR_INDEX
    paragrafos = list(documento.paragraphs)
    for tabela in documento.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                paragrafos.extend(celula.paragraphs)
    cores = {}
    for paragrafo in paragrafos:
        for run in paragrafo.runs:
            if run.font.highlight_color is not None:
                cores.setdefault(run.font.highlight_color, []).append(run.text)
    return cores, WD_COLOR_INDEX


def test_cores_distintas_para_preencher_e_conferir(pdf_previdenciario):
    cores, indice = _destaques(_documento(pdf_previdenciario))
    assert set(cores) == {indice.YELLOW, indice.GRAY_25}
    assert set(cores[indice.YELLOW]) == {"[preencher]"}
    assert any("5000000-00.2099.4.03.6100" in texto for texto in cores[indice.GRAY_25])
    assert "[preencher]" not in cores[indice.GRAY_25]


def test_tabelas_repetem_cabecalho_e_nao_partem_linhas(pdf_previdenciario):
    from docx.oxml.ns import qn
    documento = _documento(pdf_previdenciario)
    assert documento.tables
    for tabela in documento.tables:
        assert tabela.rows[0]._tr.trPr.find(qn("w:tblHeader")) is not None
        for linha in tabela.rows:
            assert linha._tr.trPr.find(qn("w:cantSplit")) is not None
        larguras = [coluna.width.cm for coluna in tabela.columns]
        assert abs(sum(larguras) - 16) < 0.05


def test_titulo_com_estilo_e_logotipo_com_texto_alternativo(pdf_previdenciario, tmp_path):
    import base64
    logo = tmp_path / "logo.png"
    logo.write_bytes(base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    ))
    documento = _documento(pdf_previdenciario, logo=logo)
    titulo = [p for p in documento.paragraphs if p.style.name == "Title"]
    assert [p.text for p in titulo] == ["PRÉ LAUDO MÉDICO PERICIAL"]
    cabecalho = documento.sections[0].header._element.xml
    assert 'descr="Logotipo do perito"' in cabecalho
    assert "Fundo amarelo" in "\n".join(p.text for p in documento.paragraphs)


def test_tabela_com_larguras_incoerentes_recusada():
    from extrator_judicial.pre_laudo import _Documento
    documento = _Documento(carregar_perfil(), None)
    with pytest.raises(ValueError):
        documento.tabela(("A", "B"), [("1", "2")], larguras=(5, 5))
