import hashlib

import pytest

from extrator_judicial.cli import main
from extrator_judicial.extracao import extrair
from extrator_judicial.pdf import ErroExtrator, ler_pdf


def test_ordem_fontes_e_paginas_mistas(pdf_ficticio):
    antes = pdf_ficticio.read_bytes()
    documento, paginas = ler_pdf(pdf_ficticio)
    assert documento["nome"] == pdf_ficticio.name
    assert documento["hash"] == hashlib.sha256(antes).hexdigest()
    assert documento["total_paginas"] == 3
    assert [p["numero"] for p in paginas] == [1, 2, 3]
    assert [p["necessita_ocr"] for p in paginas] == [False, True, False]
    assert pdf_ficticio.read_bytes() == antes
    dados = extrair(documento, paginas)
    for candidato in dados["candidatos"]:
        fonte = candidato["fonte"]
        assert fonte["documento"] == documento["hash"]
        assert fonte["trecho"] in paginas[fonte["pagina"] - 1]["texto"]
        assert candidato["estado"] == "a_revisar"
    assert dados["ficha"]["autores"]["estado"] == "conflitante"
    assert dados["ficha"]["numero_processo"]["estado"] == "a_revisar"
    assert "0000000-00.2099.0.00.0000" in dados["candidatos"][0]["valor"]
    assert any("Página 2: necessita OCR" in a for a in dados["avisos"])
    assert dados["pericia"]["tipo"] == "a_confirmar"


def test_quesitos_separados_e_inicial(pdf_ficticio):
    dados = extrair(*ler_pdf(pdf_ficticio))
    quesitos = [c for c in dados["candidatos"] if c["campo"] == "quesitos"]
    assert [c["origem"] for c in quesitos] == ["juiz", "autor", "indefinida"]
    assert "1. Pergunta fictícia do juízo?" in quesitos[0]["original"]
    assert "1) Pergunta fictícia da parte?" not in quesitos[0]["original"]
    assert "2. Pergunta fictícia sem origem indicada?" in quesitos[2]["original"]
    inicial = next(c for c in dados["candidatos"] if c["campo"] == "peticao_inicial")
    assert inicial["natureza"] == "alegacao"
    assert inicial["fonte"]["pagina"] == 3


def test_ausentes_e_ocorrencia_generica_perito(criar_pdf):
    dados = extrair(*ler_pdf(criar_pdf(["Um perito mencionado. Pedido sem rótulo."])))
    assert not dados["candidatos"]
    assert all(f["estado"] == "nao_localizado" for f in dados["ficha"].values())
    assert dados["pericia"]["tipo"] == "a_confirmar"


@pytest.mark.parametrize("rotulo,campo", [
    ("Requerente", "autores"), ("Reclamantes", "autores"), ("Polo ativo", "autores"),
    ("Ré", "reus"), ("Requerida", "reus"), ("Reclamadas", "reus"),
    ("Juízo", "vara_judicial"), ("Magistrado", "juiz"),
    ("Tipo de ação", "tipo_acao"), ("Solicitação pleiteada", "pedido"),
    ("Processo nº", "numero_processo"),
])
def test_variacoes_rotulos(criar_pdf, rotulo, campo):
    dados = extrair(*ler_pdf(criar_pdf([f"{rotulo}: Valor fictício"])))
    assert dados["candidatos"][0]["campo"] == campo
    assert dados["candidatos"][0]["valor"] == "Valor fictício"


def test_origem_ambigua_e_reu(criar_pdf):
    dados = extrair(*ler_pdf(criar_pdf([
        "Quesitos do autor e réu:\n1. Pergunta fictícia?\n"
        "Quesitos da ré:\n2. Outra pergunta fictícia?"
    ])))
    assert [c["origem"] for c in dados["candidatos"]] == ["indefinida", "reu"]


def test_paginas_sem_texto_e_longo(criar_pdf):
    dados = extrair(*ler_pdf(criar_pdf([None] * 150)))
    assert len(dados["paginas"]) == 150
    assert all(p["necessita_ocr"] for p in dados["paginas"])
    assert len(dados["avisos"]) >= 150


@pytest.mark.parametrize("conteudo", [b"nao e PDF", b"%PDF-1.7\ncorrompido", b""])
def test_invalidos(tmp_path, conteudo, capsys):
    caminho = tmp_path / "invalido.pdf"
    caminho.write_bytes(conteudo)
    with pytest.raises(ErroExtrator, match="inválido|corrompido"):
        ler_pdf(caminho)
    assert main(["extrair", str(caminho), "--saida", str(tmp_path / "r.json")]) == 1
    captura = capsys.readouterr()
    assert str(tmp_path) not in captura.err
    assert "corrompido" not in captura.out


def test_ausente(tmp_path):
    with pytest.raises(ErroExtrator, match="não encontrado"):
        ler_pdf(tmp_path / "ausente.pdf")


@pytest.mark.parametrize("senha", ["senha-ficticia", ""])
def test_pdf_protegido(criar_pdf, senha):
    with pytest.raises(ErroExtrator, match="protegido por senha"):
        ler_pdf(criar_pdf(["Texto fictício"], senha=senha))


def test_pdf_sem_paginas(criar_pdf):
    with pytest.raises(ErroExtrator, match="não contém páginas"):
        ler_pdf(criar_pdf([]))
