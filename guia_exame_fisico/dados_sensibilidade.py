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
        'interpretacao': 'Perda de sensibilidade indica neuropatia'
    },

    'Teste de Discriminação de Dois Pontos': {
        'descricao': 'Capacidade de diferenciar dois estímulos próximos',
        'material': 'Compass de dois pontos ou calibrador',
        'normal_fingertip': '2-3 mm',
        'normal_dorso': '30-40 mm',
        'passos': [
            '1. Paciente com olhos fechados',
            '2. Aplicar dois pontos simultaneamente',
            '3. Começar com distância maior',
            '4. Diminuir até encontrar limite',
            '5. Paciente identifica "um" ou "dois" pontos',
            '6. Registrar a menor distância discriminada'
        ]
    }
}
