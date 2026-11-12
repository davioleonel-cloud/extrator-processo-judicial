"""Formatação de textos exibidos na interface (sem dependência de tkinter)."""

# Rótulos dos valores normais (campos "normal_*") da aba Sensibilidade.
ROTULOS_VALORES_NORMAIS = {
    'normal_polpa_digital': 'Polpa digital',
    'normal_palma': 'Palma',
    'normal_dorso_mao': 'Dorso da mão',
    'normal_dorso_antebraco': 'Dorso do antebraço',
}


def formatar_testes_sensibilidade(testes: dict) -> str:
    """Monta o texto da aba "Sensibilidade" a partir da base de testes."""
    conteudo = "TESTES DE SENSIBILIDADE\n" + "=" * 70 + "\n\n"
    for nome_teste, teste in testes.items():
        conteudo += f"\n{'─' * 70}\n"
        conteudo += f"{nome_teste.upper()}\n"
        conteudo += f"{'─' * 70}\n"
        conteudo += f"Descrição: {teste['descricao']}\n"
        conteudo += f"Material: {teste['material']}\n"

        valores_normais = {c: v for c, v in teste.items() if c.startswith('normal_')}
        if valores_normais:
            conteudo += "\nVALORES NORMAIS:\n"
            for chave, valor in valores_normais.items():
                rotulo = ROTULOS_VALORES_NORMAIS.get(
                    chave, chave.replace('normal_', '').replace('_', ' ').capitalize())
                conteudo += f"{rotulo}: {valor}\n"

        conteudo += "\nPASSOS:\n"
        for passo in teste['passos']:
            conteudo += f"{passo}\n"

        if teste.get('classificacao'):
            conteudo += "\nCLASSIFICAÇÃO:\n"
            for filamento, resultado in teste['classificacao'].items():
                conteudo += f"{filamento}: {resultado}\n"

        if teste.get('interpretacao'):
            conteudo += f"\nINTERPRETAÇÃO:\n{teste['interpretacao']}\n"
        conteudo += "\n"
    return conteudo


def _caixa(titulo: str, recuo: int = 20) -> str:
    return (
        "\n╔════════════════════════════════════════════════════════════════════╗\n"
        f"║{' ' * recuo}{titulo}\n"
        "╚════════════════════════════════════════════════════════════════════╝\n"
    )


def formatar_teste_amplitude(nome: str, teste: dict) -> str:
    """Texto exibido na aba "Amplitude de Movimento"."""
    conteudo = _caixa(nome.upper()) + f"""
DESCRIÇÃO:
{teste['descricao']}

AMPLITUDE NORMAL:
{teste['normal']}

POSIÇÃO DO PACIENTE:
{teste['posicao_paciente']}

POSIÇÃO DO EXAMINADOR:
{teste['posicao_examinador']}

REFERÊNCIA ANATÔMICA:
{teste['referencia_anatomica']}

PASSOS PARA REALIZAÇÃO:
"""
    for passo in teste['passos']:
        conteudo += f"\n{passo}"
    conteudo += "\n\n" + "=" * 70
    conteudo += "\nDICAS IMPORTANTES:\n"
    conteudo += "• Sempre compare com o lado contralateral\n"
    conteudo += "• Comece com movimento ativo (paciente fazendo)\n"
    conteudo += "• Depois teste movimento passivo (examinador fazendo)\n"
    conteudo += "• Use goniômetro para maior precisão\n"
    conteudo += "• Registre qualquer dor durante o movimento\n"
    return conteudo


def formatar_teste_especial(nome: str, teste: dict) -> str:
    """Texto exibido na aba "Testes Especiais".

    Campos ausentes em alguns testes (ex.: 'positivo' no teste de rotação
    interna, que é uma medida de amplitude) são tratados como opcionais.
    """
    conteudo = _caixa(nome.upper(), 14) + f"""
DESCRIÇÃO:
{teste['descricao']}
"""
    if 'positivo' in teste:
        conteudo += f"\nRESULTADO POSITIVO:\n{teste['positivo']}\n"
    if 'normal' in teste:
        conteudo += f"\nVALOR NORMAL:\n{teste['normal']}\n"
    conteudo += f"""
SENSIBILIDADE: {teste.get('sensibilidade', 'N/A')}
ESPECIFICIDADE: {teste.get('especificidade', 'N/A')}

PASSOS PARA REALIZAÇÃO:
"""
    for passo in teste['passos']:
        conteudo += f"\n{passo}"
    if 'comparacao' in teste:
        conteudo += f"\n\nCOMPARAÇÃO:\n{teste['comparacao']}"
    conteudo += f"""

INTERPRETAÇÃO:
{teste.get('interpretacao', 'N/A')}

NOTA CLÍNICA:
Este é um teste importante para diagnóstico diferencial.
Combine com outros testes e achados clínicos para conclusão.
Nunca realize diagnóstico baseado em apenas um teste.
"""
    return conteudo


def formatar_teste_forca(nome: str, teste: dict) -> str:
    """Texto exibido na aba "Avaliação de Força"."""
    conteudo = _caixa(f"TESTE DE FORÇA: {nome.upper()}", 14) + f"""
DESCRIÇÃO:
{teste['descricao']}

MATERIAL UTILIZADO:
{teste.get('teste', 'Teste manual')}

VALORES NORMAIS:
"""
    if 'normal' in teste:
        conteudo += f"{teste['normal']}\n"
    if 'normal_masculino' in teste:
        conteudo += f"Masculino: {teste['normal_masculino']}\n"
        conteudo += f"Feminino: {teste['normal_feminino']}\n"
    if not any(k in teste for k in ('normal', 'normal_masculino')):
        conteudo += "Não se aplica (ver escala/avaliação abaixo)\n"
    conteudo += "\n\nPASSOS:\n"
    for passo in teste['passos']:
        conteudo += f"\n{passo}"
    if 'escala' in teste:
        conteudo += "\n\nESCALA DE FORÇA (Grau 0-5):\n"
        for grau, descricao in teste['escala'].items():
            conteudo += f"\nGrau {grau}: {descricao}"
    conteudo += f"""

INTERPRETAÇÃO:
{teste.get('avaliacao', teste.get('interpretacao', 'Veja valores normais acima'))}

DICAS:
• Sempre teste bilateralmente
• Compare com o lado não afetado
• Não realize teste se há dor intensa
• Paciente deve estar relaxado mas atento
"""
    return conteudo


def formatar_resumo(dados_exame: dict, agora) -> str:
    """Texto da aba "Resumo do Exame"."""
    conteudo = f"""
RESUMO DO EXAME FÍSICO ORTOPÉDICO
Data: {agora.strftime('%d/%m/%Y %H:%M')}

{'=' * 70}

DADOS COLETADOS:

"""
    for categoria, dados in dados_exame.items():
        conteudo += f"\n{categoria}:\n"
        if isinstance(dados, list):
            for item in dados:
                if isinstance(item, dict):
                    for chave, valor in item.items():
                        conteudo += f"  • {chave}: {valor}\n"
                else:
                    conteudo += f"  • {item}\n"
        conteudo += "\n"
    return conteudo
