"""OCR local opcional das páginas sem texto, via Tesseract instalado na máquina.

Somente páginas sem texto extraível passam por OCR; o PDF não é alterado.
O texto obtido fica registrado na revisão com motor, idioma e resolução, e é
sempre sinalizado como OCR, a conferir no original. Nenhum dado sai da máquina.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from .pdf import ErroExtrator

DPI_PADRAO = 300
IDIOMA_PADRAO = "por"


def _tesseract():
    executavel = shutil.which("tesseract")
    if executavel is None:
        raise ErroExtrator(
            "OCR solicitado, mas o Tesseract não está instalado. Instale o Tesseract "
            "com o idioma português (por) ou execute sem --ocr."
        )
    return executavel


def _versao(executavel):
    saida = subprocess.run(
        [executavel, "--version"], capture_output=True, text=True, timeout=30, check=False
    )
    primeira = (saida.stdout or saida.stderr).strip().splitlines()
    return primeira[0].strip() if primeira else "tesseract"


def _idiomas(executavel):
    saida = subprocess.run(
        [executavel, "--list-langs"], capture_output=True, text=True, timeout=30, check=False
    )
    return {linha.strip() for linha in (saida.stdout or "").splitlines()[1:]}


def _gravar_pgm(bitmap, destino):
    """Imagem em tons de cinza como PGM binário, sem depender de Pillow."""
    largura, altura, passo = bitmap.width, bitmap.height, bitmap.stride
    dados = bytes(bitmap.buffer)
    with open(destino, "wb") as arquivo:
        arquivo.write(f"P5\n{largura} {altura}\n255\n".encode("ascii"))
        for linha in range(altura):
            arquivo.write(dados[linha * passo:linha * passo + largura])


def aplicar_ocr(caminho, paginas, idioma=IDIOMA_PADRAO, dpi=DPI_PADRAO):
    """Preenche o texto das páginas que necessitam OCR; devolve quantas foram lidas."""
    try:
        import pypdfium2 as pdfium
    except ImportError:
        raise ErroExtrator(
            "OCR solicitado, mas falta o pacote pypdfium2. Instale com: pip install -e .[ocr]"
        ) from None
    executavel = _tesseract()
    if idioma not in _idiomas(executavel):
        raise ErroExtrator(f"Idioma de OCR indisponível no Tesseract: {idioma}.")
    motor = _versao(executavel)
    pendentes = [p for p in paginas if p["necessita_ocr"]]
    if not pendentes:
        return 0
    lidas = 0
    try:
        documento = pdfium.PdfDocument(str(caminho))
    except (OSError, pdfium.PdfiumError):
        raise ErroExtrator("Não foi possível abrir o PDF para OCR.") from None
    try:
        with tempfile.TemporaryDirectory() as pasta:
            imagem = Path(pasta) / "pagina.pgm"
            for pagina in pendentes:
                objeto = documento[pagina["numero"] - 1]
                try:
                    bitmap = objeto.render(scale=dpi / 72, grayscale=True)
                    _gravar_pgm(bitmap, imagem)
                finally:
                    objeto.close()
                resultado = subprocess.run(
                    [executavel, str(imagem), "stdout", "-l", idioma, "--dpi", str(dpi)],
                    capture_output=True, timeout=600, check=False,
                )
                if resultado.returncode != 0:
                    raise ErroExtrator(f'OCR falhou na página {pagina["numero"]}.')
                texto = resultado.stdout.decode("utf-8", errors="replace").replace("\f", "").strip()
                pagina["ocr"] = {"motor": motor, "idioma": idioma, "dpi": dpi}
                pagina["texto"] = texto + "\n" if texto else ""
                lidas += 1 if texto else 0
    except subprocess.TimeoutExpired:
        raise ErroExtrator("OCR excedeu o tempo limite.") from None
    finally:
        documento.close()
    return lidas


def incorporar_ocr(paginas, revisao):
    """Reaproveita o OCR registrado na revisão, só em páginas sem texto no PDF.

    O OCR não é refeito a cada comando; o texto registrado é aceito apenas
    onde o PDF realmente não tem texto, preservando a validação das demais páginas.
    """
    try:
        registradas = [p for p in revisao["paginas"] if isinstance(p, dict) and "ocr" in p]
        for registrada in registradas:
            numero = registrada["numero"]
            if type(numero) is not int or not 1 <= numero <= len(paginas):
                raise ValueError("Página")
            pagina = paginas[numero - 1]
            ocr = registrada["ocr"]
            if (
                not pagina["necessita_ocr"]
                or not isinstance(registrada["texto"], str)
                or not isinstance(ocr, dict)
                or set(ocr) != {"motor", "idioma", "dpi"}
            ):
                raise ValueError("OCR")
            pagina["texto"] = registrada["texto"]
            pagina["ocr"] = dict(ocr)
    except (KeyError, TypeError, ValueError):
        raise ErroExtrator("Revisão inválida: OCR registrado inconsistente com o PDF.") from None
    return paginas
