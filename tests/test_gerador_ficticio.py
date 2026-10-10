"""O gerador de PDF fictício alimenta o roteiro ponta a ponta."""

import importlib.util
from pathlib import Path

from extrator_judicial.extracao import extrair
from extrator_judicial.pdf import ler_pdf

GERADOR = Path(__file__).resolve().parents[1] / "teste_pdfs" / "gerar_pdf_ficticio.py"


def _gerador():
    especificacao = importlib.util.spec_from_file_location("gerar_pdf_ficticio", GERADOR)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def test_gerador_cria_pdf_reconhecido_pelo_extrator(tmp_path):
    caminho = _gerador().criar_pdf(tmp_path / "sub" / "ficticio.pdf")
    dados = extrair(*ler_pdf(caminho))
    assert [p["necessita_ocr"] for p in dados["paginas"]] == [False, True, False]
    assert all(e["estado"] == "a_revisar" for e in dados["ficha"].values())
    quesitos = [c["origem"] for c in dados["candidatos"] if c["campo"] == "quesitos"]
    assert quesitos == ["juiz", "autor", "reu"]
    campos = {c["campo"] for c in dados["candidatos"]}
    assert {"nomeacao_perito", "peticao_inicial"} <= campos
    assert dados["pericia"]["tipo"] == "a_confirmar"
