"""Rascunho documental editável; texto de entrada nunca é HTML ativo."""

import html

from .modelos import TITULO
from .persistencia import json_texto


CHECKLIST = [
    "Conferir identificação, pedido e fontes no PDF original.",
    "Revisar candidatos, divergências e campos não localizados.",
    "Conferir nomeação, objeto e continuação dos trechos nas páginas seguintes.",
    "Conferir quesitos e sua origem; não responder automaticamente.",
    "Providenciar leitura das páginas que necessitam OCR.",
    "Confirmar manualmente tipo de perícia e objeto específico.",
    "Distinguir alegação, informação documental e anotação humana.",
]


def _texto(texto):
    # Linhas indentadas preservam perguntas e impedem injeção de Markdown/HTML.
    return "\n".join("    " + html.escape(linha) for linha in str(texto).splitlines()) + "\n"


def _valores_agrupados(dados, ids):
    """Cabeçalhos repetidos (ex.: PJe) viram uma linha por valor distinto."""
    grupos = {}
    for candidato in dados["candidatos"]:
        if candidato["id"] in ids and candidato["estado"] != "rejeitado":
            grupos.setdefault(candidato["valor"], []).append(candidato)
    linhas = []
    for valor, candidatos in grupos.items():
        paginas = sorted({c["fonte"]["pagina"] for c in candidatos})
        resumo = ", ".join(map(str, paginas[:10])) + (" …" if len(paginas) > 10 else "")
        linhas.append(f"  - {len(candidatos)} ocorrência(s), páginas {resumo}; primeiro: {candidatos[0]['id']}\n")
        linhas.append(_texto(valor))
    return linhas


def exportacao(dados):
    resultado = dict(dados)
    resultado["checklist_documental"] = CHECKLIST
    resultado["pre_laudo"] = {
        "status": TITULO, "exame": "", "discussao": "", "conclusao": "",
    }
    return json_texto(resultado), markdown(dados)


def markdown(dados):
    partes = [
        f"# {TITULO}\n",
        "Pré-laudo de estudo documental. Não é laudo validado nem conclusão pericial.\n",
        "## Documento\n",
        _texto(dados["documento"]["nome"]),
        f'SHA-256: {dados["documento"]["hash"]}\n',
        "## Ficha de identificação\n",
    ]
    for campo, ficha in dados["ficha"].items():
        partes.append(f'- {campo}: {ficha["estado"]}; candidatos: {", ".join(ficha["candidatos"]) or "nenhum"}\n')
        partes.extend(_valores_agrupados(dados, ficha["candidatos"]))
    partes.extend([
        "## Tipo de perícia e objeto específico (revisão humana)\n",
        _texto(dados["pericia"]["tipo"]), _texto(dados["pericia"]["objeto"] or "A preencher pelo perito."),
        "## Candidatos para revisão\n",
    ])
    for candidato in dados["candidatos"]:
        fonte = candidato["fonte"]
        partes.extend([
            f'### {candidato["id"]} — {candidato["campo"]}\n',
            f'Estado: {candidato["estado"]}; origem: {candidato["origem"]}; natureza: {candidato["natureza"]}.\n',
            f'Fonte: SHA-256 {fonte["documento"]}, página {fonte["pagina"]}.\n',
            "Valor atual:\n", _texto(candidato["valor"]),
            "Original preservado:\n", _texto(candidato["original"]),
            "Trecho de origem:\n", _texto(fonte["trecho"]),
            "Histórico de revisão:\n", _texto(json_texto(candidato["historico"])),
        ])
    partes.append("## Histórico de classificação humana\n")
    partes.append(_texto(json_texto(dados["pericia"]["historico"])))
    partes.append("## Avisos e pendências\n")
    for item in dados["avisos"] + dados["pendencias"]:
        partes.append(_texto(item))
    partes.append("## Checklist DOCUMENTAL genérico\n")
    partes.extend(f"- [ ] {item}\n" for item in CHECKLIST)
    partes.extend([
        "## Exame\n\nA preencher pelo perito.\n",
        "## Discussão\n\nA preencher pelo perito.\n",
        "## Conclusão\n\nA preencher pelo perito. Nenhuma conclusão automática.\n",
        "## Texto por página do PDF original\n",
    ])
    for pagina in dados["paginas"]:
        partes.extend([
            f'### Página {pagina["numero"]}\n',
            _texto(pagina["texto"] or "Sem texto extraível — necessita OCR."),
        ])
    return "\n".join(partes)
