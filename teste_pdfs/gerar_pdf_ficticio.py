#!/usr/bin/env python3
"""Gera um PDF SINTÉTICO, com dados exclusivamente fictícios, para testar a CLI.

Usa apenas pypdf (dependência já instalada com o pacote); funciona offline.
O PDF gerado é ignorado pelo Git (*.pdf) e não deve ser versionado.

Uso:
    python teste_pdfs/gerar_pdf_ficticio.py [caminho_saida.pdf]
"""

import sys
from pathlib import Path

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

SAIDA_PADRAO = Path("teste_pdfs") / "processo_ficticio.pdf"

# Rótulos seguem o formato reconhecido pelo extrator ("Rótulo: valor").
# Pessoas, entidades e números são inventados.
PAGINAS = [
    "DOCUMENTO SINTÉTICO — DADOS FICTÍCIOS PARA TESTE\n"
    "Número do processo: 0000000-00.2099.0.00.0000\n"
    "Autor: Pessoa Fictícia Alfa\n"
    "Réu: Empresa Fictícia Beta Ltda\n"
    "Vara judicial: 1ª Vara Fictícia do Trabalho\n"
    "Juiz: Magistrado Fictício Gama\n"
    "Classe processual: Ação Trabalhista Fictícia\n"
    "Pedido: Indenização fictícia por alegada doença ocupacional\n"
    "\n"
    "Nomeio o perito Pessoa Fictícia Delta para realizar a perícia médica.\n"
    "\n"
    "Quesitos do juiz:\n"
    "1. O periciando apresenta doença? Qual?\n"
    "2. Há nexo causal ou concausal com o trabalho?\n"
    "3. Há incapacidade? Total ou parcial, temporária ou permanente?\n"
    "Quesitos do autor:\n"
    "1) Qual a data provável de início da doença?\n"
    "2) Quais atividades eram efetivamente realizadas?\n",
    # Página sem texto: deve aparecer como "necessita OCR".
    None,
    "Quesitos da ré:\n"
    "1. O cargo registrado exige esforço físico?\n"
    "Petição inicial\n"
    "A parte autora alega ter exercido o cargo de auxiliar fictício.\n"
    "Alega dor no ombro direito desde data fictícia.\n"
    "Trata-se de alegação; não é fato comprovado.\n",
]


def criar_pdf(caminho, paginas=PAGINAS):
    writer = PdfWriter()
    for texto in paginas:
        pagina = writer.add_blank_page(width=612, height=792)
        if texto is None:
            continue
        fonte = DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
            NameObject("/Encoding"): NameObject("/WinAnsiEncoding"),
        })
        pagina[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({
                NameObject("/F1"): writer._add_object(fonte),
            }),
        })
        comandos = [b"BT /F1 11 Tf 40 760 Td 14 TL"]
        for linha in texto.splitlines():
            comandos.append(b"<" + linha.encode("cp1252").hex().encode("ascii") + b"> Tj T*")
        comandos.append(b"ET")
        stream = DecodedStreamObject()
        stream.set_data(b"\n".join(comandos))
        pagina[NameObject("/Contents")] = writer._add_object(stream)
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("wb") as arquivo:
        writer.write(arquivo)
    return caminho


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    caminho = criar_pdf(argv[0] if argv else SAIDA_PADRAO)
    print(f"PDF fictício criado: {caminho}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
