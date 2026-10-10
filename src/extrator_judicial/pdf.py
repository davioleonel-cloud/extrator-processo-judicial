"""Leitura local sem alterar ou dividir o PDF."""

import hashlib
import logging
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PyPdfError


class ErroExtrator(ValueError):
    """Erro apresentável sem conteúdo documental ou caminhos locais."""


def _hash(arquivo):
    arquivo.seek(0)
    digest = hashlib.sha256()
    for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
        digest.update(bloco)
    arquivo.seek(0)
    return digest.hexdigest()


def ler_pdf(caminho):
    """Mantém texto uma vez por página; hash calculado em blocos."""
    logger = logging.getLogger("pypdf")
    anterior = logger.disabled
    logger.disabled = True
    try:
        with Path(caminho).open("rb") as arquivo:
            identificador = _hash(arquivo)
            if arquivo.read(5) != b"%PDF-":
                raise ErroExtrator("Arquivo inválido: esperado um PDF.")
            arquivo.seek(0)
            leitor = PdfReader(arquivo, strict=True)
            if leitor.is_encrypted:
                raise ErroExtrator(
                    "PDF protegido por senha; forneça uma cópia autorizada sem proteção."
                )
            paginas = []
            for numero, pagina in enumerate(leitor.pages, 1):
                texto = pagina.extract_text() or ""
                paginas.append({
                    "numero": numero,
                    "texto": texto,
                    "necessita_ocr": not bool(texto.strip()),
                })
            if not paginas:
                raise ErroExtrator("PDF inválido: não contém páginas.")
            if _hash(arquivo) != identificador:
                raise ErroExtrator("PDF alterado durante a leitura; tente novamente.")
            return {
                "nome": Path(caminho).name,
                "hash": identificador,
                "total_paginas": len(paginas),
            }, paginas
    except FileNotFoundError:
        raise ErroExtrator("PDF não encontrado.") from None
    except OSError:
        raise ErroExtrator("Não foi possível ler o PDF local.") from None
    except (PyPdfError, TypeError, KeyError, IndexError, RecursionError, UnicodeError):
        raise ErroExtrator("PDF inválido ou corrompido; leitura interrompida.") from None
    finally:
        logger.disabled = anterior
