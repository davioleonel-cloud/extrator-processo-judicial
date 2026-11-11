"""Testes de sensibilidade: material e passos."""

TESTES_SENSIBILIDADE = {
    'Monofilamento de Semmes-Weinstein': {
        'descricao': 'Teste de sensibilidade à pressão',
        'material': 'Filamentos de nylon de diferentes espessuras',
        'passos': [
            '1. Paciente com olhos fechados',
            '2. Examinador aplicar filamento perpendicularmente à pele',
            '3. Começar com filamento mais fino',
            '4. Aumentar espessura até paciente sentir',
            '5. Testar várias regiões da mão/pé',
            '6. Registrar limite de sensibilidade'
        ],
        'classificacao': {
            '2.83': 'Normal',
            '4.31': 'Diminuída',
            '6.65': 'Diminuída profundamente',
            'Não sente 6.65': 'Perda severa de sensibilidade'
        },
        'interpretacao': 'Perda de sensibilidade indica neuropatia'
    },

    'Teste de Discriminação de Dois Pontos': {
        'descricao': 'Capacidade de diferenciar dois estímulos próximos',
        'material': 'Compasso de dois pontos ou calibrador',
        'normal_polpa_digital': '2-3 mm',
        'normal_palma': '8-10 mm',
        'normal_dorso_mao': '20-30 mm',
        'normal_dorso_antebraco': '30-40 mm',
        'passos': [
            '1. Paciente com olhos fechados',
            '2. Aplicar dois pontos simultaneamente',
            '3. Começar com distância maior',
            '4. Diminuir até encontrar limite',
            '5. Paciente identifica "um" ou "dois" pontos',
            '6. Registrar a menor distância discriminada'
        ],
        'interpretacao': 'Aumento da distância mínima discriminada indica comprometimento da sensibilidade tátil fina, associado a neuropatia periférica ou compressão nervosa (ex.: síndrome do túnel do carpo)'
    }
}
