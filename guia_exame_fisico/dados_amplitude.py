"""Testes de amplitude de movimento: valores normais e instruções."""

TESTES_AMPLITUDE = {
    'Flexão do Punho': {
        'descricao': 'Movimento de dobra do punho para frente',
        'normal': '0-80°',
        'posicao_paciente': 'Sentado, antebraço apoiado na maca, mão para fora da maca',
        'posicao_examinador': 'Fixar o antebraço com uma mão e mobilizar a mão com a outra',
        'passos': [
            '1. Posicione o paciente sentado',
            '2. Apoie o antebraço do paciente na maca',
            '3. Deixe a mão pendente para fora da maca',
            '4. Peça ao paciente para dobrar o punho para baixo',
            '5. Meça o ângulo com goniômetro'
        ],
        'referencia_anatomica': 'Centro do goniômetro no punho, braço fixo no antebraço, braço móvel na mão'
    },

    'Extensão do Punho': {
        'descricao': 'Movimento de extensão do punho para trás',
        'normal': '0-70°',
        'posicao_paciente': 'Sentado, antebraço apoiado',
        'posicao_examinador': 'Fixar antebraço e mobilizar mão',
        'passos': [
            '1. Mesma posição do teste de flexão',
            '2. Peça ao paciente para estender o punho (levantar a mão)',
            '3. Não force além da amplitude passiva',
            '4. Meça com goniômetro'
        ],
        'referencia_anatomica': 'Mesmo alinhamento, medindo extensão'
    },

    'Abducção do Punho': {
        'descricao': 'Movimento lateral do punho para o lado radial',
        'normal': '0-20°',
        'posicao_paciente': 'Antebraço pronado, apoiado',
        'posicao_examinador': 'Mão sobre o antebraço para estabilizar',
        'passos': [
            '1. Posicione antebraço em pronação completa',
            '2. Peça para mover punho para o lado do polegar',
            '3. Realize movimento lento e controlado',
            '4. Meça o ângulo resultante'
        ],
        'referencia_anatomica': 'Alinhamento: terceiro dedo do paciente'
    },

    'Adducção do Punho': {
        'descricao': 'Movimento lateral do punho para o lado ulnar',
        'normal': '0-35°',
        'posicao_paciente': 'Antebraço pronado',
        'posicao_examinador': 'Estabilizar antebraço',
        'passos': [
            '1. Mesma posição da abducção',
            '2. Peça para mover punho para o lado do dedo mínimo',
            '3. Mantenha o antebraço fixo',
            '4. Meça com goniômetro'
        ],
        'referencia_anatomica': 'Alinhamento: terceiro dedo'
    },

    'Pronação do Antebraço': {
        'descricao': 'Rotação do antebraço com palma para baixo',
        'normal': '0-80°',
        'posicao_paciente': 'Cotovelo flexionado 90°, cotovelo junto ao corpo',
        'posicao_examinador': 'Cotovelo estabilizado',
        'passos': [
            '1. Flexione cotovelo do paciente a 90°',
            '2. Mantenha cotovelo junto ao corpo',
            '3. Peça para virar a mão para baixo (palma down)',
            '4. Meça o ângulo de rotação'
        ],
        'referencia_anatomica': 'Goniômetro no punho, braço fixo no antebraço'
    },

    'Supinação do Antebraço': {
        'descricao': 'Rotação do antebraço com palma para cima',
        'normal': '0-80°',
        'posicao_paciente': 'Cotovelo flexionado 90°',
        'posicao_examinador': 'Cotovelo estabilizado',
        'passos': [
            '1. Mesma posição inicial da pronação',
            '2. Peça para virar a mão para cima (palma up)',
            '3. Não force além da amplitude natural',
            '4. Meça a rotação alcançada'
        ],
        'referencia_anatomica': 'Alinhamento: linha entre cotovelo e punho'
    },

    'Flexão do Cotovelo': {
        'descricao': 'Dobra do cotovelo aproximando mão ao ombro',
        'normal': '0-150°',
        'posicao_paciente': 'Sentado, braço ao lado do corpo',
        'posicao_examinador': 'Mão estabilizando ombro',
        'passos': [
            '1. Posicione braço relaxado ao lado',
            '2. Peça para dobrar cotovelo trazendo mão em direção ao ombro',
            '3. Verifique se encosta no ombro (movimento completo)',
            '4. Meça o ângulo se houver limitação'
        ],
        'referencia_anatomica': 'Goniômetro na articulação do cotovelo'
    },

    'Extensão do Cotovelo': {
        'descricao': 'Extensão completa do braço',
        'normal': '0° (posição neutra)',
        'posicao_paciente': 'Braço ao longo do corpo',
        'posicao_examinador': 'Estabilizar ombro',
        'passos': [
            '1. Solte o cotovelo',
            '2. O braço deve ficar completamente reto',
            '3. Verifique se há hiperextensão (deformidade)',
            '4. Registre qualquer limitação'
        ],
        'referencia_anatomica': 'Alinhamento: ombro-cotovelo-punho em linha reta'
    },

    'Abdução do Ombro': {
        'descricao': 'Elevação do braço para o lado, acima da cabeça',
        'normal': '0-180°',
        'posicao_paciente': 'Sentado ou em pé, braço ao lado',
        'posicao_examinador': 'Uma mão estabiliza a escápula',
        'passos': [
            '1. Paciente em pé ou sentado',
            '2. Braço inicial ao lado do corpo',
            '3. Peça para elevar o braço lateralmente',
            '4. Mantenha a escápula fixa (não deixar subir)',
            '5. Continue até 180° (braço acima da cabeça)',
            '6. Meça a amplitude alcançada'
        ],
        'referencia_anatomica': 'Goniômetro no ombro, braço fixo no tórax'
    },

    'Adducção do Ombro': {
        'descricao': 'Aproximar braço do corpo',
        'normal': '0-50°',
        'posicao_paciente': 'Braço elevado, então traz perto do corpo',
        'posicao_examinador': 'Estabilizar ombro',
        'passos': [
            '1. Eleve o braço primeiro',
            '2. Peça para trazer em direção ao corpo',
            '3. Pode cruzar na frente do tórax',
            '4. Meça o ângulo da aproximação'
        ],
        'referencia_anatomica': 'Alinhamento: corpo como referência'
    }
}
