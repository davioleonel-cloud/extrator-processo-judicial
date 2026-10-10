"""Petição inicial PJe fictícia: seções, pedidos, datas e CID como alegações."""

from copy import deepcopy

import pytest

from extrator_judicial.extracao import extrair
from extrator_judicial.pdf import ler_pdf
from extrator_judicial.relatorios import markdown
from extrator_judicial.revisao import revisar, validar


def rodape(id_doc, folha):
    return (
        f"Documento assinado eletronicamente por ADVOGADO FICTÍCIO, em 01/01/2099, às 10:00:00 - {id_doc}\n"
        f"Fls.: {folha}\n"
    )


@pytest.fixture
def pdf_inicial(criar_pdf):
    return criar_pdf([
        "AO JUÍZO FICTÍCIO\n"
        "1. DO CONTRATO DE TRABALHO\n"
        "A autora alega ter sido admitida para o cargo de auxiliar fictício.\n"
        "Alega afastamento desde 20.03.2099, com diagnóstico CID F32.1.\n"
        "2. DO RECONHECIMENTO DA DOENÇA\n"
        "OCUPACIONAL\n"
        "Texto fictício da causa de pedir.\n"
        + rodape("abc1234", 1),
        "3. DOS PEDIDOS\n"
        "Ante o exposto, requer:\n"
        "a. RECONHECIMENTO DA DOENÇA\n"
        "OCUPACIONAL, por equiparação;\n"
        "b. INDENIZAÇÃO FICTÍCIA: R$ 1.000,00\n"
        "b.1. Requer ainda item acessório fictício;\n"
        + rodape("abc1234", 2),
        "c. HONORÁRIOS FICTÍCIOS.\n"
        "4. REQUERIMENTOS FINAIS\n"
        "Cidade Fictícia, 16 de abril de 2099.\n"
        + rodape("abc1234", 3),
        "CONTESTAÇÃO FICTÍCIA\n"
        "1. DAS PRELIMINARES\n"
        "Data fictícia 01/02/2099 citada pela ré.\n"
        + rodape("def5678", 4),
    ], nome="inicial.pdf")


def _por_campo(dados, campo):
    return [c for c in dados["candidatos"] if c["campo"] == campo]


def test_secoes_pedidos_datas_e_cid_da_inicial(pdf_inicial):
    dados = extrair(*ler_pdf(pdf_inicial))
    secoes = _por_campo(dados, "inicial_secao")
    assert [s["valor"] for s in secoes] == [
        "1. DO CONTRATO DE TRABALHO",
        "2. DO RECONHECIMENTO DA DOENÇA\nOCUPACIONAL",
        "3. DOS PEDIDOS",
        "4. REQUERIMENTOS FINAIS",
    ]
    pedidos = _por_campo(dados, "pedido_item")
    assert [p["valor"].split("\n")[0] for p in pedidos] == [
        "a. RECONHECIMENTO DA DOENÇA", "b. INDENIZAÇÃO FICTÍCIA: R$ 1.000,00", "c. HONORÁRIOS FICTÍCIOS.",
    ]
    # Subitem permanece no pedido; rodapé PJe não entra no texto; páginas preservadas.
    assert "b.1. Requer ainda" in pedidos[1]["valor"]
    assert secoes[2]["fonte"]["pagina"] == 2 and secoes[2]["fonte"]["pagina_final"] == 3
    assert "c. HONORÁRIOS" in secoes[2]["fonte"]["trecho"]
    assert all("assinado eletronicamente" not in p["valor"] for p in pedidos)
    datas = _por_campo(dados, "data_mencionada")
    assert [d["fonte"]["pagina"] for d in datas] == [1, 3]
    assert "afastamento desde 20.03.2099" in datas[0]["valor"]
    assert "cargo de auxiliar" in datas[0]["fonte"]["trecho"]
    assert [c["fonte"]["pagina"] for c in _por_campo(dados, "cid_mencionado")] == [1]
    # Nada da contestação (outro ID PJe) é tratado como inicial.
    assert all(c["fonte"]["pagina"] <= 3 for c in secoes + pedidos + datas)
    assert all(c["natureza"] == "alegacao" and c["estado"] == "a_revisar" for c in secoes + pedidos + datas)
    assert any("ID PJe da página 1" in a for a in dados["avisos"])
    assert "pedido_item" not in dados["ficha"]


def test_markdown_e_revisao_da_inicial(pdf_inicial):
    base = extrair(*ler_pdf(pdf_inicial))
    dados = deepcopy(base)
    pedido = _por_campo(dados, "pedido_item")[2]
    revisar(dados, pedido["id"], "rejeitar")
    assert validar(dados, base) == dados
    texto = markdown(dados)
    resumo = texto.split("## Petição inicial — alegações a revisar")[1].split("## Tipo de perícia")[0]
    assert "### Pedidos" in resumo and "a. RECONHECIMENTO DA DOENÇA" in resumo
    assert "HONORÁRIOS FICTÍCIOS" not in resumo
    assert "páginas 2–3" in resumo
    assert "### Datas citadas (tipo a confirmar)" in resumo


def test_sem_rodape_pje_nao_delimita_inicial(pdf_ficticio):
    dados = extrair(*ler_pdf(pdf_ficticio))
    assert not [c for c in dados["candidatos"] if c["campo"] in ("inicial_secao", "pedido_item")]
    assert "Petição inicial — alegações" not in markdown(dados)
