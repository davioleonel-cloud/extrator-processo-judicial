"""Formatação de textos exibidos na interface (sem dependência de tkinter)."""

# Rótulos dos valores de referência opcionais, na ordem de exibição.
REFERENCIAS_SENSIBILIDADE = (
    ('normal_polpa_digital', 'Normal (polpa digital)'),
    ('normal_dorso_mao', 'Normal (dorso da mão)'),
)


def formatar_testes_sensibilidade(testes: dict) -> str:
    """Monta o texto da aba "Sensibilidade" a partir da base de testes."""
    conteudo = "TESTES DE SENSIBILIDADE\n" + "=" * 70 + "\n\n"
    for nome_teste, teste in testes.items():
        conteudo += f"\n{'─' * 70}\n"
        conteudo += f"{nome_teste.upper()}\n"
        conteudo += f"{'─' * 70}\n"
        conteudo += f"Descrição: {teste['descricao']}\n"
        conteudo += f"Material: {teste['material']}\n"

        referencias = [(rotulo, teste[chave])
                       for chave, rotulo in REFERENCIAS_SENSIBILIDADE if chave in teste]
        if referencias:
            conteudo += "\nVALORES DE REFERÊNCIA:\n"
            for rotulo, valor in referencias:
                conteudo += f"{rotulo}: {valor}\n"

        conteudo += "\nPASSOS:\n"
        for passo in teste['passos']:
            conteudo += f"{passo}\n"

        if teste.get('interpretacao'):
            conteudo += f"\nINTERPRETAÇÃO:\n{teste['interpretacao']}\n"
        conteudo += "\n"
    return conteudo
