"""Layout no estilo PJe, com dados exclusivamente fictícios."""

import errno
import os

import pytest

from extrator_judicial.extracao import extrair
from extrator_judicial.pdf import ErroExtrator, ler_pdf
from extrator_judicial.persistencia import salvar_arquivos
from extrator_judicial.relatorios import markdown

CABECALHO = (
    "PODER JUDICIÁRIO\n"
    "PROCESSO: ATOrd 0000000-00.2099.5.99.0000\n"
    "AUTOR: PESSOA FICTÍCIA ALFA\n"
    "RÉU: EMPRESA FICTÍCIA BETA LTDA.\n"
    "Órgão Julgador de Origem: 1ª VARA FICTÍCIA DO TRABALHO\n"
)


@pytest.fixture
def pdf_pje(criar_pdf):
    return criar_pdf([
        CABECALHO
        + "DESPACHO\n"
        "Tendo em vista a manifestação da perita nomeada nos autos,\n"
        "destituo a mesma do encargo e nomeio em substituição o Dr. PERITO FICTÍCIO\n"
        "GAMA.\n"
        "Para as partes apresentarem\n"
        "quesitos e indicarem assistentes técnicos, sob pena de preclusão.\n",
        CABECALHO
        + "II - DOS QUESITOS PARA PERÍCIA MÉDICA.\n"
        "1. Pergunta fictícia?\n"
        "Os quesitos do juízo serão respondidos no laudo.\n"
        "Nomeio o Dr. Advogado Fictício como curador especial.\n",
    ], nome="pje.pdf")


def test_rotulos_pje_nomeacao_e_quesitos(pdf_pje):
    dados = extrair(*ler_pdf(pdf_pje))
    por_campo = {}
    for candidato in dados["candidatos"]:
        por_campo.setdefault(candidato["campo"], []).append(candidato)
    assert {c["valor"] for c in por_campo["vara_judicial"]} == {"1ª VARA FICTÍCIA DO TRABALHO"}
    nomeacoes = por_campo["nomeacao_perito"]
    assert len(nomeacoes) == 1 and nomeacoes[0]["fonte"]["pagina"] == 1
    assert "nomeio em substituição o Dr." in nomeacoes[0]["fonte"]["trecho"]
    quesitos = por_campo["quesitos"]
    assert len(quesitos) == 1
    assert quesitos[0]["fonte"]["pagina"] == 2 and quesitos[0]["origem"] == "indefinida"
    assert quesitos[0]["valor"].startswith("II - DOS QUESITOS")
    # Origem e tipo continuam dependentes de revisão humana.
    assert dados["pericia"]["tipo"] == "a_confirmar"
    assert "juiz" not in por_campo


def test_markdown_agrupa_cabecalhos_repetidos(pdf_pje):
    texto = markdown(extrair(*ler_pdf(pdf_pje)))
    ficha = texto.split("## Tipo de perícia")[0]
    assert "2 ocorrência(s), páginas 1, 2" in ficha
    assert ficha.count("EMPRESA FICTÍCIA BETA LTDA.") == 1


def test_gravacao_sem_suporte_a_hard_link(tmp_path, monkeypatch):
    def sem_link(*_):
        raise OSError(errno.EPERM, "hard link não suportado")

    monkeypatch.setattr(os, "link", sem_link)
    saida = tmp_path / "revisao.json"
    salvar_arquivos([(saida, "{}\n")])
    assert saida.read_text(encoding="utf-8") == "{}\n"
    with pytest.raises(ErroExtrator, match="já existe"):
        salvar_arquivos([(saida, "novo")])
    assert saida.read_text(encoding="utf-8") == "{}\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["revisao.json"]
