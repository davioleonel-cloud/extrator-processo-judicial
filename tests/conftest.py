"""Todos os PDFs gerados são sintéticos e fictícios; nada é persistido no repo."""

import pytest
from pypdf import PdfWriter
from pypdf.generic import (
    DecodedStreamObject, DictionaryObject, NameObject,
)


@pytest.fixture
def criar_pdf(tmp_path):
    def criar(textos, nome="ficticio.pdf", senha=None):
        writer = PdfWriter()
        for texto in textos:
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
            stream = DecodedStreamObject()
            comandos = [b"BT /F1 12 Tf 20 760 Td 14 TL"]
            for linha in texto.splitlines():
                conteudo = linha.encode("cp1252").hex().encode("ascii")
                comandos.append(b"<" + conteudo + b"> Tj T*")
            comandos.append(b"ET")
            stream.set_data(b"\n".join(comandos))
            pagina[NameObject("/Contents")] = writer._add_object(stream)
        if senha is not None:
            writer.encrypt(senha)
        caminho = tmp_path / nome
        with caminho.open("wb") as arquivo:
            writer.write(arquivo)
        return caminho
    return criar


@pytest.fixture
def pdf_ficticio(criar_pdf):
    return criar_pdf([
        "DOCUMENTO SINTÉTICO — DADOS FICTÍCIOS\n"
        "Número do processo: 0000000-00.2099.0.00.0000\n"
        "Autor: Pessoa Fictícia Alfa\n"
        "Réu: Entidade Fictícia Beta\n"
        "Vara judicial: Vara Fictícia\n"
        "Juíza: Magistrada Fictícia\n"
        "Classe processual: Ação Fictícia\n"
        "Pedido: Solicitação fictícia\n"
        "Nomeio a perita Pessoa Fictícia Gama.\n"
        "Quesitos do juiz:\n"
        "1. Pergunta fictícia do juízo?\n"
        "Quesitos do autor:\n"
        "1) Pergunta fictícia da parte?\n",
        None,
        "Autor: Pessoa Fictícia Delta\n"
        "Quesitos:\n"
        "2. Pergunta fictícia sem origem indicada?\n"
        "Petição inicial\n"
        "A parte alega evento fictício; não é fato comprovado.\n",
    ])
