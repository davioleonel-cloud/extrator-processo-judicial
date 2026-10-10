"""Modelo JSON versionado e estados explicitamente documentais."""

CAMPOS = (
    "numero_processo", "autores", "reus", "vara_judicial", "juiz", "tipo_acao",
    "pedido",
)
ESTADOS = ("a_revisar", "confirmado", "corrigido", "rejeitado")
NATUREZAS = ("alegacao", "informacao_documental", "anotacao_humana")
TITULO = "RASCUNHO — REVISÃO NECESSÁRIA"


def atualizar_resumo(dados):
    ficha = {}
    pendencias = []
    for campo in CAMPOS:
        candidatos = [c for c in dados["candidatos"] if c["campo"] == campo]
        ativos = [c for c in candidatos if c["estado"] != "rejeitado"]
        divergente = len({c["valor"] for c in ativos}) > 1
        if not ativos:
            estado = "nao_localizado"
        elif divergente:
            estado = "conflitante"
        elif any(c["estado"] == "a_revisar" for c in ativos):
            estado = "a_revisar"
        else:
            estado = "revisado"
        ficha[campo] = {"estado": estado, "candidatos": [c["id"] for c in candidatos]}
        if estado != "revisado":
            pendencias.append(f"{campo}: {estado}")
    for candidato in dados["candidatos"]:
        if candidato["estado"] == "a_revisar":
            pendencias.append(f'{candidato["id"]}: candidato a revisar')
    if dados["pericia"]["tipo"] == "a_confirmar":
        pendencias.append("Tipo de perícia e objeto específico a confirmar por humano.")
    if not dados["pericia"]["objeto"]:
        pendencias.append("Objeto específico a preencher pelo perito.")
    avisos = [
        f'Página {p["numero"]}: necessita OCR; ausência de texto não significa ausência de informação.'
        for p in dados["paginas"] if p["necessita_ocr"]
    ]
    avisos.extend([
        "Informação documental não significa verdade comprovada.",
        "Localização por indicadores: candidatos, não segmentação completa. "
        "Blocos limitados à página; conferir continuação no PDF.",
        "OCR, inventário médico/CTPS e checklist especializado não implementados.",
    ])
    dados["ficha"] = ficha
    dados["pendencias"] = pendencias
    dados["avisos"] = avisos
    dados["status"] = TITULO


def novo_modelo(documento, paginas):
    return {
        "versao_esquema": 1,
        "documento": documento,
        "paginas": paginas,
        "candidatos": [],
        "pericia": {"tipo": "a_confirmar", "objeto": "", "historico": []},
    }
