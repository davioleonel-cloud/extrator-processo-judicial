"""Testes de força muscular: material, valores normais e escala."""

TESTES_FORCA = {
    'Mão - Preensão Palmar': {
        'descricao': 'Força de preensão geral da mão',
        'teste': 'Dinamômetro de mão',
        'normal_masculino': '35-60 kg',
        'normal_feminino': '20-40 kg',
        'passos': [
            '1. Paciente em pé, ombro aduzido',
            '2. Cotovelo flexionado 90°',
            '3. Punho em posição neutra',
            '4. Aperta o dinamômetro com força máxima',
            '5. Realizar 3 tentativas',
            '6. Registrar a melhor tentativa'
        ],
        'interpretacao': 'Redução > 10% comparado ao lado normal é significativa'
    },

    'Mão - Pinça Digital': {
        'descricao': 'Força de pinça entre polegar e indicador',
        'teste': 'Pinçômetro ou dinamômetro de pinça',
        'normal': '8-12 kg',
        'passos': [
            '1. Posição: polegar e indicador em oposição',
            '2. Aperte o pinçômetro',
            '3. Realizar 3 tentativas em cada mão',
            '4. Comparar entre os lados',
            '5. Registrar melhor medida'
        ],
        'interpretacao': 'Importante para atividades de precisão'
    },

    'Ombro - Abdutor': {
        'descricao': 'Força dos músculos abdutores (deltóide e supraespinhal)',
        'teste': 'Teste manual 0-5 ou com dinamômetro',
        'passos': [
            '1. Paciente deitado ou sentado',
            '2. Ombro abduzido 90°',
            '3. Examinador aplica resistência',
            '4. Paciente tenta manter posição',
            '5. Classificar de 0 (paralisia) a 5 (normal)'
        ],
        'escala': {
            '0': 'Sem contração muscular',
            '1': 'Contração palpável sem movimento',
            '2': 'Movimento ativo sem gravidade',
            '3': 'Movimento contra gravidade',
            '4': 'Movimento contra resistência moderada',
            '5': 'Força normal contra resistência máxima'
        }
    },

    'Cotovelo - Flexor': {
        'descricao': 'Força dos músculos flexores (bíceps, braquial)',
        'teste': 'Teste manual ou dinamômetro',
        'passos': [
            '1. Paciente sentado, ombro ao lado',
            '2. Cotovelo flexionado 90°',
            '3. Examinador oferece resistência',
            '4. Paciente tenta flexionar mais',
            '5. Resistência no punho em pronação e supinação'
        ],
        'avaliacao': 'Escala 0-5, comparar ambos os lados'
    }
}
