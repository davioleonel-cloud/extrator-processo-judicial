"""Perfil do perito para o cabeçalho do pré-laudo; substituível por JSON local."""

import json
from pathlib import Path

from .pdf import ErroExtrator

PERFIL_PADRAO = {
    "nome": "Dr. Davi de Oliveira Leonel",
    "crm": "CRM-SP 259.031",
    "cabecalho": [
        "Dr. Davi de Oliveira Leonel — CRM-SP 259.031",
        "Graduado pela Universidade Federal do Triângulo Mineiro (UFTM)",
        "Jurisperito | Pós-graduado em Perícias Médicas Judiciais (TPMED)",
    ],
    "cidade": "",
    "logo": "",
}


def carregar_perfil(caminho=None):
    """Perfil padrão, ou JSON com as mesmas chaves (as ausentes usam o padrão)."""
    perfil = dict(PERFIL_PADRAO)
    if caminho is None:
        return perfil
    try:
        with Path(caminho).open(encoding="utf-8") as arquivo:
            lido = json.load(arquivo)
    except (OSError, ValueError):
        raise ErroExtrator("Não foi possível abrir o perfil JSON UTF-8 do perito.") from None
    if not isinstance(lido, dict):
        raise ErroExtrator("Perfil do perito inválido: esperado objeto JSON.")
    for chave, valor in lido.items():
        if chave not in PERFIL_PADRAO:
            raise ErroExtrator(f"Perfil do perito: chave desconhecida {chave!r}.")
        if chave == "cabecalho":
            if not isinstance(valor, list) or not all(isinstance(v, str) for v in valor):
                raise ErroExtrator("Perfil do perito: cabecalho deve ser lista de textos.")
        elif not isinstance(valor, str):
            raise ErroExtrator(f"Perfil do perito: {chave} deve ser texto.")
        perfil[chave] = valor
    if perfil["logo"]:
        logo = Path(perfil["logo"])
        if not logo.is_absolute():
            logo = Path(caminho).resolve().parent / logo
        perfil["logo"] = str(logo)
    return perfil
