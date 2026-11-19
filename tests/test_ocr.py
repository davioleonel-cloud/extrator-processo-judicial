"""OCR local: texto registrado na revisão e aceito só em páginas sem texto no PDF."""

import json
import shutil
from copy import deepcopy

import pytest

from extrator_judicial.cli import main
from extrator_judicial.extracao import extrair
from extrator_judicial.ocr import incorporar_ocr
from extrator_judicial.pdf import ErroExtrator, ler_pdf
from extrator_judicial.persistencia import carregar
from extrator_judicial.revisao import validar

OCR = {"motor": "tesseract ficticio", "idioma": "por", "dpi": 300}


def _com_ocr_simulado(pdf, pagina=2, texto="Quesitos do juiz:\n1. Pergunta fictícia lida por OCR?\n"):
    documento, paginas = ler_pdf(pdf)
    paginas[pagina - 1].update(texto=texto, ocr=dict(OCR))
    return json.loads(json.dumps(extrair(documento, paginas)))


def test_ocr_registrado_reabre_e_valida(pdf_ficticio):
    dados = _com_ocr_simulado(pdf_ficticio)
    documento, paginas = ler_pdf(pdf_ficticio)
    base = extrair(documento, incorporar_ocr(paginas, dados))
    assert validar(deepcopy(dados), base) == dados
    quesito = [c for c in dados["candidatos"] if "lida por OCR" in c["valor"]][0]
    assert quesito["fonte"]["texto_ocr"] is True
    assert any("texto obtido por OCR" in aviso for aviso in dados["avisos"])
    assert not any("Página 2: necessita OCR" in aviso for aviso in dados["avisos"])


def test_ocr_recusado_em_pagina_com_texto(pdf_ficticio):
    dados = _com_ocr_simulado(pdf_ficticio, pagina=1, texto="Texto inventado")
    _, paginas = ler_pdf(pdf_ficticio)
    with pytest.raises(ErroExtrator):
        incorporar_ocr(paginas, dados)


@pytest.mark.parametrize("ocr", [None, {"motor": "x"}, {"motor": "x", "idioma": "por", "dpi": 1, "extra": 1}])
def test_ocr_registrado_malformado(pdf_ficticio, ocr):
    dados = _com_ocr_simulado(pdf_ficticio)
    dados["paginas"][1]["ocr"] = ocr
    _, paginas = ler_pdf(pdf_ficticio)
    with pytest.raises(ErroExtrator):
        incorporar_ocr(paginas, dados)


def test_ocr_sem_tesseract(pdf_ficticio, tmp_path, monkeypatch, capsys):
    pytest.importorskip("pypdfium2")
    monkeypatch.setattr(shutil, "which", lambda _: None)
    assert main(["extrair", str(pdf_ficticio), "--ocr", "--saida", str(tmp_path / "r.json")]) == 1
    assert "Tesseract" in capsys.readouterr().err
    assert not (tmp_path / "r.json").exists()


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="Tesseract não instalado")
def test_ocr_real_em_pagina_digitalizada(criar_pdf_imagem, tmp_path):
    pdf = criar_pdf_imagem("ATESTADO FICTICIO\nCID M54.5\nAfastamento por 30 dias.")
    r1, r2 = tmp_path / "r1.json", tmp_path / "r2.json"
    assert main(["extrair", str(pdf), "--saida", str(tmp_path / "sem_ocr.json")]) == 0
    assert carregar(tmp_path / "sem_ocr.json")["paginas"][0]["texto"] == ""
    assert main(["extrair", str(pdf), "--ocr", "--saida", str(r1)]) == 0
    pagina = carregar(r1)["paginas"][0]
    assert pagina["necessita_ocr"] and pagina["ocr"]["idioma"] == "por"
    assert "ATESTADO" in pagina["texto"].upper()
    # Reabrir não refaz OCR: usa o texto registrado e valida o restante contra o PDF.
    assert main(["classificar", str(pdf), "--revisao", str(r1), "--tipo", "previdenciaria",
                 "--objeto", "Objeto fictício", "--saida", str(r2)]) == 0
