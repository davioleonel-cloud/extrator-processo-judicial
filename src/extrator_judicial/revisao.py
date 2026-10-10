"""Revisão auditável e validação contra o PDF original, não contra JSON confiado."""

from copy import deepcopy
from datetime import datetime, timezone

from .modelos import ESTADOS, atualizar_resumo
from .pdf import ErroExtrator


def _agora():
    return datetime.now(timezone.utc).isoformat()


def revisar(dados, identificador, acao, valor=None):
    if acao not in ("confirmar", "corrigir", "rejeitar"):
        raise ErroExtrator("Ação de revisão inválida.")
    candidato = next((c for c in dados["candidatos"] if c["id"] == identificador), None)
    if candidato is None:
        raise ErroExtrator("Candidato não encontrado.")
    if acao == "corrigir" and (not isinstance(valor, str) or not valor.strip()):
        raise ErroExtrator("Correção exige um novo valor não vazio.")
    if acao != "corrigir" and valor is not None:
        raise ErroExtrator("Novo valor é permitido somente ao corrigir.")
    estado = {"confirmar": "confirmado", "corrigir": "corrigido", "rejeitar": "rejeitado"}[acao]
    novo = valor if acao == "corrigir" else candidato["valor"]
    natureza = "anotacao_humana" if acao == "corrigir" else candidato["natureza"]
    candidato["historico"].append({
        "acao": acao, "data": _agora(),
        "valor_anterior": candidato["valor"], "novo_valor": novo,
        "estado_anterior": candidato["estado"], "novo_estado": estado,
        "natureza_anterior": candidato["natureza"], "nova_natureza": natureza,
    })
    candidato.update(valor=novo, estado=estado, natureza=natureza)
    atualizar_resumo(dados)


def classificar(dados, tipo, objeto):
    if tipo not in ("trabalhista", "previdenciaria") or not isinstance(objeto, str) or not objeto.strip():
        raise ErroExtrator("Confirmação humana exige tipo permitido e objeto específico.")
    pericia = dados["pericia"]
    pericia["historico"].append({
        "data": _agora(), "natureza": "anotacao_humana", "estado": "confirmado",
        "tipo_anterior": pericia["tipo"], "novo_tipo": tipo,
        "objeto_anterior": pericia["objeto"], "novo_objeto": objeto,
    })
    pericia.update(tipo=tipo, objeto=objeto)
    atualizar_resumo(dados)


def _validar_data(valor):
    if not isinstance(valor, str) or datetime.fromisoformat(valor).tzinfo is None:
        raise ValueError("Data inválida")


def validar(dados, base):
    """Reconstitui alterações permitidas e exige igualdade das fontes imutáveis."""
    try:
        if dados["versao_esquema"] != 1 or type(dados["versao_esquema"]) is not int:
            raise ValueError("Versão")
        if dados["documento"]["hash"] != base["documento"]["hash"]:
            raise ErroExtrator("Revisão vinculada a outro PDF (hash diferente).")
        esperado = deepcopy(base)
        # O mesmo PDF pode ser renomeado, mas nunca registrar caminho absoluto.
        nome = dados["documento"]["nome"]
        if not isinstance(nome, str) or not nome or "/" in nome or "\\" in nome:
            raise ValueError("Nome")
        esperado["documento"]["nome"] = nome
        if len(dados["candidatos"]) != len(esperado["candidatos"]):
            raise ValueError("Candidatos")
        for candidato, original in zip(dados["candidatos"], esperado["candidatos"]):
            for evento in candidato["historico"]:
                _validar_data(evento["data"])
                revisar(esperado, original["id"], evento["acao"],
                        evento["novo_valor"] if evento["acao"] == "corrigir" else None)
                gerado = original["historico"][-1]
                gerado["data"] = evento["data"]
                if gerado != evento:
                    raise ValueError("Histórico")
            if candidato["estado"] not in ESTADOS or candidato != original:
                raise ValueError("Referência, original ou estado")
        for evento in dados["pericia"]["historico"]:
            _validar_data(evento["data"])
            classificar(esperado, evento["novo_tipo"], evento["novo_objeto"])
            gerado = esperado["pericia"]["historico"][-1]
            gerado["data"] = evento["data"]
            if gerado != evento:
                raise ValueError("Classificação")
        atualizar_resumo(esperado)
        if dados != esperado:
            raise ValueError("Modelo")
    except ErroExtrator:
        raise
    except (ValueError, KeyError, TypeError, IndexError, AttributeError):
        raise ErroExtrator("Revisão inválida: esquema, histórico ou referências inconsistentes.") from None
    return dados
