"""Petição inicial em processos PJe: seções, pedidos, datas e CID citados.

Tudo é alegação da parte autora, com fonte; nada é classificado ou inferido
(cargo não vira atividade real, data não vira data de início da doença).
"""

import re

from . import extracao

RODAPE_PJE = re.compile(
    r"Documento assinado eletronicamente por .+?, em \d{2}/\d{2}/\d{4}, às [\d:]+ - (\w+)\s*$"
)
FOLHA = re.compile(r"^\s*Fls\.:\s*\d+\s*$")
SECAO = re.compile(r"^\s*(\d{1,2})\s*[.)–-]\s+(\S.*)$")
ITEM = re.compile(r"^\s*([a-z])\s*[.)]\s+\S")
DATA = re.compile(
    r"\b\d{1,2}[/.]\d{1,2}[/.](?:\d{4}|\d{2})\b"
    r"|\b\d{1,2} de (?:janeiro|fevereiro|marco|abril|maio|junho|julho|agosto|setembro"
    r"|outubro|novembro|dezembro) de \d{4}\b"
)
CID = re.compile(r"\bCID(?:-?10|-?11)?\s*[:–-]?\s*[A-TV-Z]\d{2}(?:\.\d{1,2})?\b|\b[A-TV-Z]\d{2}\.\d{1,2}\b")


def _id_documento(texto):
    ids = [RODAPE_PJE.search(linha) for linha in texto.splitlines()]
    ids = [m.group(1) for m in ids if m]
    return ids[-1] if ids else None


def paginas_da_inicial(paginas):
    """Páginas iniciais com o mesmo ID PJe da página 1; vazio sem rodapé PJe."""
    primeiro = _id_documento(paginas[0]["texto"])
    if primeiro is None:
        return []
    resultado = []
    for pagina in paginas:
        if _id_documento(pagina["texto"]) != primeiro:
            break
        resultado.append(pagina)
    return resultado


def _linhas(paginas):
    """(página, linha original) sem rodapés de assinatura e número de folha."""
    for pagina in paginas:
        for linha in pagina["texto"].splitlines():
            if RODAPE_PJE.search(linha) or FOLHA.match(linha):
                continue
            yield pagina["numero"], linha


def _maiuscula(texto):
    letras = [c for c in texto if c.isalpha()]
    return len(letras) >= 3 and all(c.isupper() for c in letras)


def _blocos(linhas, inicio):
    """Agrupa linhas a partir de cada índice de início até o próximo."""
    for posicao, indice in enumerate(inicio):
        fim = inicio[posicao + 1] if posicao + 1 < len(inicio) else len(linhas)
        yield linhas[indice:fim]


def _texto(bloco):
    return "\n".join(linha.rstrip() for _, linha in bloco).strip()


def extrair_inicial(paginas, adicionar):
    """Chama adicionar(campo, valor, trecho, pagina, pagina_final) para cada candidato."""
    inicial = paginas_da_inicial(paginas)
    if not inicial:
        return
    linhas = list(_linhas(inicial))
    secoes = [
        i for i, (_, linha) in enumerate(linhas)
        if SECAO.match(linha) and _maiuscula(SECAO.match(linha).group(2))
    ]
    for bloco in _blocos(linhas, secoes):
        titulo = [bloco[0]]
        for seguinte in bloco[1:]:
            if not seguinte[1].strip() or not _maiuscula(seguinte[1]) or ITEM.match(seguinte[1]):
                break
            titulo.append(seguinte)
        adicionar("inicial_secao", _texto(titulo), _texto(bloco), bloco[0][0], bloco[-1][0])
        if "pedidos" not in extracao.normalizar(_texto(titulo)):
            continue
        itens = [i for i, (_, linha) in enumerate(bloco) if ITEM.match(linha)]
        for item in _blocos(bloco, itens):
            adicionar("pedido_item", _texto(item), _texto(item), item[0][0], item[-1][0])
    for indice, (numero, linha) in enumerate(linhas):
        # Linha vizinha dá contexto; o tipo da data (emissão, atendimento, início) é humano.
        contexto = _texto(linhas[max(0, indice - 1):indice + 2])
        if DATA.search(extracao.normalizar(linha)):
            adicionar("data_mencionada", linha.strip(), contexto, numero, numero)
        if CID.search(linha):
            adicionar("cid_mencionado", linha.strip(), contexto, numero, numero)
