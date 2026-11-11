"""Testes especiais ortopédicos: execução, sensibilidade e especificidade."""

TESTES_ESPECIAIS = {
    'Teste de Tinnel (Síndrome do Túnel do Carpo)': {
        'descricao': 'Percussão do nervo mediano no punho',
        'positivo': 'Sensação de formigamento nos dedos polegar, indicador, médio e metade radial do anular',
        'passos': [
            '1. Paciente com punho em extensão',
            '2. Localize o nervo mediano entre os tendões palmares',
            '3. Use o dedo (percutor) ou martelo neurológico',
            '4. Percuta levemente sobre o local',
            '5. Observe se há irradiação para os dedos'
        ],
        'sensibilidade': '72-95%',
        'especificidade': '95%',
        'interpretacao': 'Positivo sugere compressão do nervo mediano'
    },

    'Teste de Phalen (Síndrome do Túnel do Carpo)': {
        'descricao': 'Flexão palmar máxima do punho por 60 segundos',
        'positivo': 'Aparecimento de parestesias nos dedos inervados por nervo mediano',
        'passos': [
            '1. Paciente com cotovelos flexionados a 90°',
            '2. Junte as mãos com punhos flexionados (dorso das mãos tocando)',
            '3. Mantenha a posição por 60 segundos',
            '4. Observe se há formigamento nos dedos',
            '5. Registre o tempo para início dos sintomas'
        ],
        'sensibilidade': '51-93%',
        'especificidade': '95-98%',
        'interpretacao': 'Quanto mais rápido os sintomas, mais grave a compressão'
    },

    'Teste do Sinal de Lachman (Instabilidade do Joelho)': {
        'descricao': 'Teste de translação anterior da tíbia',
        'positivo': 'Movimento anterior anormal da tíbia em relação ao fêmur',
        'passos': [
            '1. Paciente deitado',
            '2. Joelho flexionado a 20-30°',
            '3. Fixe o fêmur com uma mão',
            '4. Com a outra, puxe a tíbia anteriormente',
            '5. Avalie o grau de movimento anormal',
            '6. Compare com o lado normal'
        ],
        'sensibilidade': '72-98%',
        'especificidade': '96-99%',
        'interpretacao': 'Melhor teste para lesão aguda do LCA'
    },

    'Teste de Gaveta Anterior (Joelho)': {
        'descricao': 'Teste de translação anterior em flexão maior',
        'positivo': 'Movimento anterior da tíbia',
        'passos': [
            '1. Paciente deitado, joelho flexionado 90°',
            '2. Mantenha o pé do paciente fixo no leito',
            '3. Puxe a tíbia anteriormente com ambas as mãos',
            '4. Observe o movimento',
            '5. Compare com o lado contralateral'
        ],
        'sensibilidade': '60-90%',
        'especificidade': '97%',
        'interpretacao': 'Pode ser negativo em lesões agudas pelo espasmo muscular'
    },

    'Teste de Lassitude (Frouxidão) do Ombro': {
        'descricao': 'Teste de mobilidade excessiva glenoumeral',
        'positivo': 'Movimento excessivo da cabeça do úmero',
        'passos': [
            '1. Paciente em decúbito lateral',
            '2. Ombro abduzido 90° e rotação externa máxima',
            '3. Observe quanto de translação anterior há',
            '4. Paciente em prona para teste posterior',
            '5. Ombro abduzido, cotovelo flexionado, teste rotação interna'
        ],
        'sensibilidade': 'Varia',
        'especificidade': 'Varia',
        'interpretacao': 'Indicador de instabilidade glenoumeral'
    },

    'Teste de Apprehension (Apreensão do Ombro)': {
        'descricao': 'Teste de deslocação anterior do ombro',
        'positivo': 'Sensação de apreensão ou medo de deslocação',
        'passos': [
            '1. Paciente em decúbito dorsal',
            '2. Ombro abduzido 90°',
            '3. Cotovelo flexionado 90°',
            '4. Realize rotação externa lentamente',
            '5. Paciente relata sensação de medo da cabeça deslocar',
            '6. Registre o ponto em que ocorre'
        ],
        'sensibilidade': '50-72%',
        'especificidade': '96-98%',
        'interpretacao': 'Altamente específico para instabilidade anterior'
    },

    'Teste de Rotação Interna Máxima (ROM)': {
        'descricao': 'Amplitude de movimento de rotação interna',
        'normal': '0-70°',
        'passos': [
            '1. Paciente em pé ou sentado',
            '2. Ombro abduzido 90°',
            '3. Cotovelo flexionado 90°',
            '4. Peça para rodar o braço internamente',
            '5. Meça o ângulo alcançado'
        ],
        'comparacao': 'Comparar com lado contralateral',
        'interpretacao': 'Restrição pode indicar lesão do manguito rotador'
    }
}
