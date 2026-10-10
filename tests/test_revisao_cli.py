from copy import deepcopy
import json
import os

import pytest

from extrator_judicial.cli import main
from extrator_judicial.extracao import extrair
from extrator_judicial.pdf import ErroExtrator, ler_pdf
from extrator_judicial.persistencia import carregar, json_texto, salvar_arquivos
from extrator_judicial.relatorios import exportacao
from extrator_judicial.revisao import classificar, revisar, validar


def test_revisao_preserva_originais_e_historico(pdf_ficticio):
    base = extrair(*ler_pdf(pdf_ficticio))
    dados = deepcopy(base)
    candidato = dados["candidatos"][0]
    original = candidato["original"]
    fonte = deepcopy(candidato["fonte"])
    revisar(dados, candidato["id"], "confirmar")
    revisar(dados, candidato["id"], "corrigir", "Número fictício corrigido")
    revisar(dados, candidato["id"], "rejeitar")
    revisar(dados, candidato["id"], "confirmar")
    assert candidato["original"] == original
    assert candidato["fonte"] == fonte
    assert candidato["natureza"] == "anotacao_humana"
    assert candidato["natureza_original"] == "informacao_documental"
    assert candidato["historico"][1]["valor_anterior"] == original
    assert candidato["historico"][1]["novo_valor"] == "Número fictício corrigido"
    assert candidato["historico"][2]["novo_estado"] == "rejeitado"
    classificar(dados, "previdenciaria", "Objeto fictício informado pelo humano")
    assert validar(dados, base) == dados
    assert dados["pericia"]["historico"][0]["tipo_anterior"] == "a_confirmar"


@pytest.mark.parametrize("acao,valor", [
    ("corrigir", ""), ("corrigir", None), ("confirmar", "alteração"),
    ("rejeitar", "alteração"), ("invalida", None),
])
def test_revisao_invalida(pdf_ficticio, acao, valor):
    dados = extrair(*ler_pdf(pdf_ficticio))
    with pytest.raises(ErroExtrator):
        revisar(dados, dados["candidatos"][0]["id"], acao, valor)
    with pytest.raises(ErroExtrator):
        revisar(dados, "ausente", "confirmar")


@pytest.mark.parametrize("atributo", [
    "hash", "pagina", "trecho", "original", "estado", "historico",
    "versao", "paginas", "pericia",
])
def test_json_adulterado_rejeitado(pdf_ficticio, atributo):
    base = extrair(*ler_pdf(pdf_ficticio))
    dados = deepcopy(base)
    candidato = dados["candidatos"][0]
    if atributo == "hash":
        dados["documento"]["hash"] = "0" * 64
    elif atributo in ("pagina", "trecho"):
        candidato["fonte"][atributo] = 0 if atributo == "pagina" else "Trecho inventado"
    elif atributo in ("original", "estado"):
        candidato[atributo] = "Inventado"
    elif atributo == "historico":
        revisar(dados, candidato["id"], "confirmar")
        candidato["historico"][0]["valor_anterior"] = "Inventado"
    elif atributo == "versao":
        dados["versao_esquema"] = 2
    elif atributo == "paginas":
        dados["paginas"][0]["texto"] = "Alterado"
    else:
        dados["pericia"]["tipo"] = "trabalhista"
    with pytest.raises(ErroExtrator):
        validar(dados, base)


def test_conflito_nao_resolvido_por_confirmacao(pdf_ficticio):
    dados = extrair(*ler_pdf(pdf_ficticio))
    autores = [c for c in dados["candidatos"] if c["campo"] == "autores"]
    for candidato in autores:
        revisar(dados, candidato["id"], "confirmar")
    assert dados["ficha"]["autores"]["estado"] == "conflitante"
    revisar(dados, autores[1]["id"], "rejeitar")
    assert dados["ficha"]["autores"]["estado"] == "revisado"


def test_persistencia_exclusiva_utf8(tmp_path):
    caminho = tmp_path / "revisao.json"
    salvar_arquivos([(caminho, json_texto({"texto": "Revisão fictícia"}))])
    assert carregar(caminho) == {"texto": "Revisão fictícia"}
    assert "Revisão" in caminho.read_text(encoding="utf-8")
    assert caminho.stat().st_mode & 0o077 == 0
    with pytest.raises(ErroExtrator, match="já existe"):
        salvar_arquivos([(caminho, "alterado")])
    salvar_arquivos([(caminho, "{}")], sobrescrever=True)
    assert carregar(caminho) == {}


def test_protecao_entradas_links_e_saidas(tmp_path, pdf_ficticio):
    original = pdf_ficticio.read_bytes()
    hardlink = tmp_path / "link.pdf"
    os.link(pdf_ficticio, hardlink)
    for caminho in [pdf_ficticio, hardlink]:
        with pytest.raises(ErroExtrator, match="substituir"):
            salvar_arquivos([(caminho, "alterado")], [pdf_ficticio], True)
    assert pdf_ficticio.read_bytes() == original
    symlink = tmp_path / "link.json"
    symlink.symlink_to(tmp_path / "nao-existe.json")
    with pytest.raises(ErroExtrator, match="link"):
        salvar_arquivos([(symlink, "{}")], sobrescrever=True)
    saida = tmp_path / "igual.json"
    with pytest.raises(ErroExtrator, match="distintos"):
        salvar_arquivos([(saida, "{}"), (saida, "texto")])


def test_exportacao_pre_valida_todas_saidas(tmp_path):
    novo = tmp_path / "novo.json"
    existe = tmp_path / "existe.md"
    existe.write_text("anterior")
    with pytest.raises(ErroExtrator):
        salvar_arquivos([(novo, "{}"), (existe, "novo")])
    assert not novo.exists()
    assert existe.read_text() == "anterior"


def test_fluxo_cli_completo(pdf_ficticio, tmp_path, capsys, criar_pdf):
    inicial = tmp_path / "inicial.json"
    revisado = tmp_path / "revisado.json"
    classificado = tmp_path / "classificado.json"
    resultado = tmp_path / "resultado.json"
    markdown = tmp_path / "rascunho.md"
    assert main(["extrair", str(pdf_ficticio), "--saida", str(inicial)]) == 0
    dados = carregar(inicial)
    candidato = dados["candidatos"][0]["id"]
    assert main([
        "revisar", str(pdf_ficticio), "--revisao", str(inicial),
        "--candidato", candidato, "--acao", "corrigir", "--valor", "Correção fictícia",
        "--saida", str(revisado),
    ]) == 0
    assert main([
        "classificar", str(pdf_ficticio), "--revisao", str(revisado),
        "--tipo", "trabalhista", "--objeto", "Objeto fictício", "--saida", str(classificado),
    ]) == 0
    assert main([
        "exportar", str(pdf_ficticio), "--revisao", str(classificado),
        "--json", str(resultado), "--markdown", str(markdown),
    ]) == 0
    exportado = carregar(resultado)
    assert exportado["candidatos"][0]["original"] == dados["candidatos"][0]["original"]
    assert exportado["candidatos"][0]["valor"] == "Correção fictícia"
    assert exportado["pericia"]["tipo"] == "trabalhista"
    assert exportado["pendencias"]
    assert exportado["pre_laudo"]["conclusao"] == ""
    texto = markdown.read_text(encoding="utf-8")
    assert "RASCUNHO — REVISÃO NECESSÁRIA" in texto
    assert "Página 2" in texto and "necessita OCR" in texto
    assert "A preencher pelo perito" in texto
    assert str(tmp_path) not in texto and str(tmp_path) not in json.dumps(exportado)
    assert "confirmado" not in exportado["status"]
    assert main(["extrair", str(pdf_ficticio), "--saida", str(inicial)]) == 1
    outro = criar_pdf(["Outro conteúdo fictício"], nome="outro.pdf")
    assert main([
        "exportar", str(outro), "--revisao", str(classificado),
        "--json", str(tmp_path / "outro.json"), "--markdown", str(tmp_path / "outro.md"),
    ]) == 1
    captura = capsys.readouterr()
    assert str(tmp_path) not in captura.err
    assert "Pessoa Fictícia" not in captura.out


def test_rascunho_exportado_sem_revisar_e_markdown_seguro(criar_pdf):
    dados = extrair(*ler_pdf(criar_pdf(["Autor: <script>alert('fictício')</script>"])))
    texto_json, md = exportacao(dados)
    assert json.loads(texto_json)["pendencias"]
    assert "<script>" not in md
    assert "    &lt;script&gt;" in md


def test_exatamente_um_pdf_e_erros_argumentos(tmp_path, capsys):
    with pytest.raises(SystemExit) as erro:
        main(["extrair", "/segredo/a.pdf", "/segredo/b.pdf", "--saida", str(tmp_path / "r.json")])
    assert erro.value.code == 2
    assert "/segredo" not in capsys.readouterr().err


def test_listar_mostra_ids_sem_conteudo_documental(pdf_ficticio, tmp_path, capsys):
    inicial = tmp_path / "inicial.json"
    revisado = tmp_path / "revisado.json"
    assert main(["extrair", str(pdf_ficticio), "--saida", str(inicial)]) == 0
    dados = carregar(inicial)
    assert main([
        "revisar", str(pdf_ficticio), "--revisao", str(inicial),
        "--candidato", "c0002", "--acao", "rejeitar", "--saida", str(revisado),
    ]) == 0
    capsys.readouterr()
    antes = sorted(p.name for p in tmp_path.iterdir())
    assert main(["listar", str(pdf_ficticio), "--revisao", str(revisado)]) == 0
    saida = capsys.readouterr().out
    assert sorted(p.name for p in tmp_path.iterdir()) == antes
    for candidato in dados["candidatos"]:
        assert candidato["id"] in saida
    assert "c0002  autores          rejeitado" in saida
    assert "quesitos         a_revisar  juiz" in saida
    assert "Tipo de perícia: a_confirmar." in saida
    assert "Pessoa Fictícia" not in saida and "Pergunta" not in saida
    assert str(tmp_path) not in saida


def test_listar_recusa_revisao_de_outro_pdf(pdf_ficticio, tmp_path, criar_pdf, capsys):
    inicial = tmp_path / "inicial.json"
    assert main(["extrair", str(pdf_ficticio), "--saida", str(inicial)]) == 0
    outro = criar_pdf(["Outro conteúdo fictício"], nome="outro.pdf")
    assert main(["listar", str(outro), "--revisao", str(inicial)]) == 1
    assert "hash diferente" in capsys.readouterr().err
    with pytest.raises(SystemExit) as erro:
        main(["listar", str(pdf_ficticio), "--revisao", str(inicial), "--saida", "x.json"])
    assert erro.value.code == 2
