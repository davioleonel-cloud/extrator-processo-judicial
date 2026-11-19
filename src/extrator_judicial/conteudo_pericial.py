"""Conteúdo técnico fixo dos modelos de pré-laudo.

Roteiros de exame, fundamentação normativa e referências bibliográficas.
Nada aqui é conclusão sobre o caso: são estruturas a preencher e textos de
apoio que o perito confere, adapta ou remove. Redação sem hífens/travessões
na prosa, conforme preferência do perito; nomes próprios de normas mantidos.
"""

import re

# Marcador de campo a preencher no ato pericial (destacado em amarelo no Word).
CAMPO = "[preencher]"

# ---------------------------------------------------------------------------
# Índice documental: páginas com possíveis documentos relevantes.
# Busca simples por palavras (texto normalizado, sem acentos); conferir no PDF.
# ---------------------------------------------------------------------------
INDICE_COMUM = (
    ("Petição inicial", r"\bpeticao inicial\b|\bexcelentissimo\b"),
    ("Decisão / despacho / nomeação", r"\bdecisao\b|\bdespacho\b|\bnomeio\b"),
    ("Contestação", r"\bcontestacao\b"),
    ("Quesitos", r"\bquesitos?\b"),
    ("Atestado médico", r"\batestado\b"),
    ("Relatório médico", r"\brelatorio medico\b|\brelatorio clinico\b"),
    ("Receituário / prescrição", r"\breceituario\b|\bprescricao\b|\buso continuo\b"),
    ("Exame de imagem", r"\bressonancia\b|\btomografia\b|\bradiografia\b|\bultrassonografia\b|\bultrassom\b|\braio x\b"),
    ("Eletroneuromiografia", r"\beletroneuromiografia\b|\benmg\b"),
    ("Exames laboratoriais", r"\bhemograma\b|\blaboratorial\b|\bvalores de referencia\b"),
    ("Internação / alta / cirurgia", r"\binternacao\b|\bsumario de alta\b|\bdescricao cirurgica\b|\bcirurgia\b"),
)
INDICE_PREVIDENCIARIO = (
    ("Comunicação de decisão / indeferimento INSS", r"\bcomunicacao de decisao\b|\bindeferi|\bcessacao\b"),
    ("Laudo da perícia administrativa (SABI)", r"\bsabi\b|\bpericia medica federal\b|\blaudo medico pericial\b"),
    ("CNIS / extrato previdenciário", r"\bcnis\b|\bextrato previdenciario\b|\bcadastro nacional de informacoes sociais\b"),
    ("Benefício acidentário (espécie 91/94)", r"\bb ?91\b|\bb ?94\b|\bespecie 91\b|\bespecie 94\b|\bacidentario\b"),
    ("Benefício previdenciário comum (espécie 31/32/36)", r"\bb ?31\b|\bb ?32\b|\bb ?36\b|\bespecie 31\b"),
    ("CAT (Comunicação de Acidente de Trabalho)", r"\bcat\b|\bcomunicacao de acidente\b"),
    ("CTPS / vínculo de emprego", r"\bctps\b|\bcarteira de trabalho\b|\badmissao\b"),
    ("PPP / descrição de atividades", r"\bppp\b|\bperfil profissiografico\b|\bdescricao das atividades\b"),
    ("Boletim de ocorrência / acidente", r"\bboletim de ocorrencia\b|\bacidente de transito\b|\bacidente de trabalho\b"),
)
INDICE_CURATELA = (
    ("Pedido de interdição / curatela", r"\binterdicao\b|\bcuratela\b|\binterditand"),
    ("Curador provisório", r"\bcurador provisorio\b|\bcuratela provisoria\b"),
    ("Neurologia / psiquiatria", r"\bneurolog|\bpsiquiatr|\bgeriatr"),
    ("Doença neurocognitiva / demência", r"\bdemencia\b|\balzheimer\b|\bcomprometimento cognitivo\b|\bneurocognitiv"),
    ("Testes cognitivos (MEEM, MoCA, CDR)", r"\bmeem\b|\bmini ?exame\b|\bmoca\b|\bcdr\b|\bminimental\b"),
    ("Imagem do encéfalo", r"\bcranio\b|\bencefalo\b"),
    ("Estudo social / psicológico", r"\bestudo social\b|\bassistente social\b|\bavaliacao psicologica\b"),
    ("Documentos civis / certidões", r"\bcertidao\b|\bregistro geral\b|\bcpf\b"),
    ("Benefícios / patrimônio", r"\bbeneficio\b|\baposentadoria\b|\bimovel\b|\bconta bancaria\b"),
)
INDICE_TRABALHISTA = (
    ("CTPS / contrato de trabalho", r"\bctps\b|\bcarteira de trabalho\b|\bcontrato de trabalho\b"),
    ("PPP / PGR / PCMSO / LTCAT", r"\bppp\b|\bpgr\b|\bppra\b|\bpcmso\b|\bltcat\b"),
    ("ASO (atestado de saúde ocupacional)", r"\baso\b|\batestado de saude ocupacional\b|\badmissional\b|\bdemissional\b"),
    ("CAT (Comunicação de Acidente de Trabalho)", r"\bcat\b|\bcomunicacao de acidente\b"),
    ("Benefício acidentário (espécie 91/94)", r"\bb ?91\b|\bespecie 91\b|\bacidentario\b"),
    ("Descrição de função / atividades", r"\bdescricao (?:da funcao|das atividades|do cargo)\b"),
)

CID_TEXTO = re.compile(r"\bCID(?:[\s-]?10|[\s-]?11)?\s*[:–-]?\s*([A-TV-Z]\d{2}(?:\.\d{1,2})?)", re.IGNORECASE)
# Em texto de OCR a letra inicial do CID costuma virar dígito (S52.5 lido como 552.5).
CID_OCR = re.compile(r"\bCID(?:[\s-]?10)?\s*[:–-]?\s*([0-9])(\d{2}\.\d{1,2})\b", re.IGNORECASE)
TROCAS_OCR = {"5": "S", "1": "I", "0": "O", "8": "B", "2": "Z", "6": "G"}
CID_CODIGO = re.compile(r"\b([A-TV-Z]\d{2}(?:\.\d{1,2})?)\b")


# ---------------------------------------------------------------------------
# Exame físico: blocos por segmento, escolhidos pelos CIDs citados nos autos.
# Amplitudes normais de referência: AAOS (as mesmas do guia ortopédico legado).
# ---------------------------------------------------------------------------
def _faixa(inicio, fim):
    """Lista de categorias CID entre duas (inclusive), por exemplo M40 a M54."""
    letra = inicio[0]
    return {f"{letra}{n:02d}" for n in range(int(inicio[1:]), int(fim[1:]) + 1)}


BLOCOS_EXAME = {
    "coluna": {
        "titulo": "Coluna vertebral (cervical, torácica e lombar)",
        "cids": _faixa("M40", "M54") | {"G54", "G55", "S12", "S13", "S14", "S22", "S23", "S32", "S33", "S34"},
        "inspecao": [
            "Postura, curvaturas fisiológicas, escoliose, assimetria de ombros e pelve",
            "Contratura muscular paravertebral, pontos dolorosos à palpação",
            "Marcha na ponta dos pés (S1) e nos calcanhares (L5)",
        ],
        "adm": [
            ("Cervical: flexão", "45°"), ("Cervical: extensão", "45°"),
            ("Cervical: inclinação lateral D / E", "45°"), ("Cervical: rotação D / E", "60° a 80°"),
            ("Lombar: flexão (distância dedos chão em cm)", "0 a 10 cm"),
            ("Lombar: extensão", "25° a 30°"), ("Lombar: inclinação lateral D / E", "25° a 35°"),
            ("Teste de Schober (cm)", "aumento de 5 cm ou mais"),
        ],
        "testes": [
            ("Lasègue (elevação da perna estendida)",
             "Dor irradiada abaixo do joelho entre 30° e 70° sugere radiculopatia lombar"),
            ("Lasègue contralateral (cruzado)", "Alta especificidade para hérnia discal"),
            ("Bragard", "Reforça o Lasègue com dorsiflexão do tornozelo"),
            ("Spurling", "Reproduz dor radicular cervical"),
            ("Reflexos patelar (L4) e aquileu (S1)", "Assimetria sugere comprometimento radicular"),
            ("Força: dorsiflexão do hálux (L5), flexão plantar (S1), extensão do joelho (L4)", "Graduar de 0 a 5 (MRC)"),
            ("Sensibilidade por dermátomos", "Hipoestesia em território radicular específico"),
            ("Sinais de Waddell", "Três ou mais positivos indicam componente não orgânico a valorizar com cautela"),
        ],
    },
    "ombro": {
        "titulo": "Ombros",
        "cids": {"M75", "S42", "S43", "S44", "S46", "S48"},
        "inspecao": ["Atrofia de supraespinal, infraespinal e deltoide; assimetrias; cicatrizes"],
        "adm": [
            ("Flexão", "180°"), ("Extensão", "60°"), ("Abdução", "180°"),
            ("Rotação interna", "70°"), ("Rotação externa", "90°"),
        ],
        "testes": [
            ("Neer", "Dor na elevação passiva indica impacto subacromial"),
            ("Hawkins-Kennedy", "Dor na rotação interna com ombro a 90° indica impacto"),
            ("Jobe", "Dor ou fraqueza indica lesão do supraespinal"),
            ("Patte", "Fraqueza na rotação externa indica lesão do infraespinal"),
            ("Gerber (lift off)", "Incapacidade de afastar a mão do dorso indica lesão do subescapular"),
            ("Speed e Yergason", "Dor no sulco bicipital indica tendinopatia da cabeça longa do bíceps"),
            ("Queda do braço (drop arm)", "Sugere rotura extensa do manguito"),
        ],
    },
    "cotovelo": {
        "titulo": "Cotovelos e antebraços",
        "cids": {"M77", "S52", "S53", "S56", "S58"},
        "inspecao": ["Edema, deformidades, ângulo de carregamento, cicatrizes"],
        "adm": [("Flexão", "150°"), ("Extensão", "0°"), ("Pronação", "80°"), ("Supinação", "80°")],
        "testes": [
            ("Cozen", "Dor no epicôndilo lateral à extensão resistida do punho (epicondilite lateral)"),
            ("Mill", "Dor no epicôndilo lateral ao alongamento passivo dos extensores"),
            ("Epicondilite medial (flexão resistida do punho)", "Dor no epicôndilo medial"),
            ("Tinel no túnel cubital", "Parestesia no território do nervo ulnar"),
        ],
    },
    "punho_mao": {
        "titulo": "Punhos e mãos",
        "cids": {"G56", "M65", "M67", "M70", "M72", "S52"} | _faixa("S60", "S69"),
        "inspecao": [
            "Trofismo tenar e hipotenar, deformidades, amputações (nível e dedos), cicatrizes",
            "Calosidades palmares (indicam uso das mãos), unhas, coloração",
        ],
        "adm": [
            ("Punho: flexão", "80°"), ("Punho: extensão", "70°"),
            ("Punho: desvio radial", "20°"), ("Punho: desvio ulnar", "30° a 35°"),
            ("Dedos: flexão MCF / IFP / IFD", "90° / 100° / 90°"),
            ("Preensão palmar dinamômetro Jamar D / E (kgf)", "comparar lados"),
            ("Pinça polpa a polpa D / E (kgf)", "comparar lados"),
        ],
        "testes": [
            ("Phalen", "Parestesia em até 60 segundos sugere síndrome do túnel do carpo"),
            ("Tinel no punho", "Choque no território do nervo mediano"),
            ("Durkan (compressão do carpo)", "Maior sensibilidade para túnel do carpo"),
            ("Finkelstein", "Dor no processo estiloide radial indica tenossinovite de De Quervain"),
            ("Dedo em gatilho", "Bloqueio ou ressalto à flexão e extensão"),
            ("Sensibilidade (monofilamentos / discriminação de dois pontos)", "Território mediano, ulnar e radial"),
        ],
    },
    "quadril": {
        "titulo": "Quadris",
        "cids": {"M16", "M87"} | _faixa("S70", "S79"),
        "inspecao": ["Marcha (claudicação, Trendelenburg), dismetria de membros inferiores"],
        "adm": [
            ("Flexão", "120°"), ("Extensão", "30°"), ("Abdução", "45°"),
            ("Adução", "30°"), ("Rotação interna", "45°"), ("Rotação externa", "45°"),
        ],
        "testes": [
            ("Patrick (FABERE)", "Dor inguinal sugere doença coxofemoral; dor posterior, sacroilíaca"),
            ("Trendelenburg", "Queda da pelve indica insuficiência do glúteo médio"),
            ("Thomas", "Contratura em flexão do quadril"),
        ],
    },
    "joelho": {
        "titulo": "Joelhos",
        "cids": {"M17", "M22", "M23"} | _faixa("S80", "S89"),
        "inspecao": [
            "Derrame articular, alinhamento (varo / valgo), cicatrizes",
            "Perimetria da coxa a 10 cm do polo superior da patela D / E (cm)",
        ],
        "adm": [("Flexão", "135°"), ("Extensão", "0°")],
        "testes": [
            ("Lachman", "Translação anterior aumentada indica lesão do ligamento cruzado anterior"),
            ("Gaveta anterior e posterior", "Instabilidade dos ligamentos cruzados"),
            ("Estresse em varo e valgo", "Instabilidade dos ligamentos colaterais"),
            ("McMurray", "Estalido doloroso sugere lesão meniscal"),
            ("Apley", "Dor à compressão rotacional sugere lesão meniscal"),
            ("Compressão patelar (Zohlen)", "Dor femoropatelar"),
        ],
    },
    "tornozelo_pe": {
        "titulo": "Tornozelos e pés",
        "cids": {"M20", "M21", "M76", "M77", "S82"} | _faixa("S90", "S99"),
        "inspecao": ["Edema, deformidades, apoio plantar, calosidades, uso de órtese"],
        "adm": [
            ("Dorsiflexão", "20°"), ("Flexão plantar", "50°"),
            ("Inversão", "35°"), ("Eversão", "15°"),
        ],
        "testes": [
            ("Gaveta anterior do tornozelo", "Instabilidade do ligamento talofibular anterior"),
            ("Thompson", "Ausência de flexão plantar indica rotura do tendão calcâneo"),
            ("Marcha na ponta dos pés e nos calcanhares", "Capacidade funcional global do segmento"),
        ],
    },
    "neurologico": {
        "titulo": "Exame neurológico",
        "cids": (_faixa("G00", "G99") - {"G54", "G55", "G56"}) | _faixa("I60", "I69") | {"S06", "T90"},
        "inspecao": ["Nível de consciência, fala e linguagem, nervos cranianos"],
        "adm": [],
        "testes": [
            ("Força muscular por segmento (MRC 0 a 5)", "Registrar por grupo muscular e lado"),
            ("Tônus e reflexos profundos; sinal de Babinski", "Liberação piramidal ou hiporreflexia"),
            ("Coordenação: índex nariz, calcanhar joelho, diadococinesia", "Ataxia, dismetria"),
            ("Romberg e marcha", "Equilíbrio e padrão de marcha"),
            ("Sensibilidade tátil, dolorosa, vibratória e propriocepção", "Padrão de distribuição"),
            ("Escala de Rankin modificada", "Grau de dependência funcional de 0 a 6"),
        ],
    },
    "mental": {
        "titulo": "Exame do estado mental",
        "cids": _faixa("F00", "F99") | {"G30", "G31"},
        "inspecao": [
            "Apresentação: vestes, higiene, postura, contato visual, atitude diante do perito",
            "Consciência e orientação (tempo, espaço, pessoa)",
            "Atenção e concentração; memória imediata, recente e remota",
            "Pensamento: curso, forma e conteúdo (ideação delirante, ideação suicida)",
            "Sensopercepção (alucinações); linguagem",
            "Humor e afeto (modulação, ressonância); psicomotricidade",
            "Volição, pragmatismo, juízo crítico e insight sobre o adoecimento",
            "Coerência entre queixa, comportamento observado e tratamento em uso",
        ],
        "adm": [],
        "testes": [],
    },
    "cardiorrespiratorio": {
        "titulo": "Sistema cardiovascular e respiratório",
        "cids": (_faixa("I00", "I99") - _faixa("I60", "I69")) | _faixa("J00", "J99"),
        "inspecao": ["Dispneia ao repouso ou ao esforço, cianose, edema de membros inferiores, turgência jugular"],
        "adm": [],
        "testes": [
            ("Ausculta cardíaca e pulmonar", "Sopros, arritmias, estertores, sibilos"),
            ("Saturação periférica de oxigênio em repouso", "Valor em %"),
            ("Classe funcional NYHA (I a IV)", "Limitação para atividades habituais"),
        ],
    },
}
BLOCOS_ORTOPEDICOS = ("coluna", "ombro", "cotovelo", "punho_mao", "quadril", "joelho", "tornozelo_pe")


def blocos_para_cids(codigos, modelo):
    """Blocos de exame direcionados; sem CID reconhecido, roteiro ortopédico geral."""
    categorias = {c[:3].upper() for c in codigos}
    escolhidos = [nome for nome, bloco in BLOCOS_EXAME.items() if bloco["cids"] & categorias]
    if modelo == "curatela":
        for obrigatorio in ("neurologico", "mental"):
            if obrigatorio not in escolhidos:
                escolhidos.append(obrigatorio)
    elif not escolhidos:
        escolhidos = list(BLOCOS_ORTOPEDICOS) + ["mental"]
    return escolhidos


EXAME_GERAL = [
    ("Estado geral / fácies", CAMPO), ("Peso (kg) / altura (m) / IMC", CAMPO),
    ("Pressão arterial / frequência cardíaca", CAMPO), ("Dominância (destro / canhoto)", CAMPO),
    ("Marcha e deambulação; uso de órtese, bengala ou cadeira de rodas", CAMPO),
    ("Despiu e vestiu sem auxílio? Subiu e desceu da maca sem auxílio?", CAMPO),
    ("Comportamento e colaboração durante o exame", CAMPO),
]

ESCALAS_CURATELA = [
    ("Miniexame do Estado Mental (MEEM)", "0 a 30. Pontos de corte por escolaridade (Brucki et al., 2003): "
     "analfabetos 20; 1 a 4 anos 25; 5 a 8 anos 26,5; 9 a 11 anos 28; mais de 11 anos 29"),
    ("Montreal Cognitive Assessment (MoCA)",
     "0 a 30; abaixo de 26 sugere comprometimento (somar 1 ponto se escolaridade até 12 anos)"),
    ("Teste do desenho do relógio", "Função executiva e visuoespacial"),
    ("Fluência verbal (animais em 1 minuto)", "Abaixo de 9 (até 8 anos de estudo) ou 13 (8 anos ou mais) sugere déficit"),
    ("Clinical Dementia Rating (CDR)", "0 normal; 0,5 questionável; 1 leve; 2 moderada; 3 grave"),
    ("Questionário de Atividades Funcionais de Pfeffer",
     "0 a 30; quanto maior, maior a dependência para atividades instrumentais"),
    ("Índice de Katz (atividades básicas)", "Banho, vestir, higiene, transferência, continência, alimentação"),
    ("Escala de Lawton (atividades instrumentais)", "Telefone, compras, finanças, medicações, transporte, tarefas domésticas"),
]

CAPACIDADES_CURATELA = [
    "Compreender informações relevantes sobre a decisão",
    "Apreciar a situação e suas consequências",
    "Raciocinar e comparar alternativas",
    "Expressar uma escolha de forma estável",
    "Reconhecer o valor do dinheiro e realizar cálculos simples (troco)",
    "Administrar recursos do dia a dia (compras, contas)",
    "Movimentar conta bancária, cartões e senhas",
    "Contratar empréstimos, financiamentos ou dar bens em garantia",
    "Comprar, vender ou doar bens móveis e imóveis",
    "Firmar contratos e outorgar procurações",
    "Receber e administrar benefícios previdenciários ou assistenciais",
    "Manejar as próprias medicações e comparecer a consultas",
]


# ---------------------------------------------------------------------------
# Dados a coletar na perícia.
# ---------------------------------------------------------------------------
DADOS_PREVIDENCIARIOS = [
    ("Escolaridade", CAMPO),
    ("Atividade exercida na época do fato / início da doença", CAMPO),
    ("Empregador e tempo na função", CAMPO),
    ("Descrição das tarefas (posturas, cargas, repetitividade, jornada)", CAMPO),
    ("Data do acidente ou do início dos sintomas (alegada pelo periciando)", CAMPO),
    ("CAT emitida? (data e emitente)", "( ) Sim  ( ) Não  " + CAMPO),
    ("Natureza reconhecida pelo INSS", "( ) Acidentária (espécie 91 / 94)  ( ) Previdenciária comum (espécie 31 / 32 / 36)"),
    ("Tempo total de afastamento", CAMPO),
    ("Retornou ao trabalho? Em qual função? Houve readaptação?", CAMPO),
    ("Reabilitação profissional pelo INSS?", "( ) Sim  ( ) Não  " + CAMPO),
    ("Atividade atual / última atividade", CAMPO),
]
NOTA_ESPECIES = (
    "Para orientação do Juízo: a espécie 91 corresponde ao auxílio por incapacidade temporária "
    "acidentário e a espécie 31 ao previdenciário comum; a espécie 94 corresponde ao auxílio acidente "
    "acidentário e a 36 ao previdenciário; as espécies 92 e 32 correspondem à aposentadoria por "
    "incapacidade permanente acidentária e previdenciária. A concessão em espécie acidentária indica "
    "que o próprio INSS reconheceu o nexo com o trabalho, inclusive pelo Nexo Técnico Epidemiológico "
    "(Lei 8.213/1991, art. 21-A)."
)
TABELA_BENEFICIOS = ("NB", "Espécie", "DIB", "DCB", "CID", "Fls.")

DADOS_TRABALHISTAS = [
    ("Escolaridade", CAMPO),
    ("Função na admissão e funções posteriores (datas)", CAMPO),
    ("Descrição detalhada das tarefas, ritmo, metas, pausas e jornada", CAMPO),
    ("Posturas, cargas manuseadas, movimentos repetitivos, vibração, ruído, agentes químicos", CAMPO),
    ("Equipamentos de proteção fornecidos e utilizados", CAMPO),
    ("Data do acidente ou início dos sintomas; CAT emitida?", CAMPO),
    ("Afastamentos (períodos, espécie do benefício 31 ou 91)", CAMPO),
    ("Atividades anteriores e paralelas, esportes e atividades domésticas", CAMPO),
    ("Data da demissão / situação atual", CAMPO),
]

DADOS_CURATELA = [
    ("Escolaridade (anos de estudo) e ocupação anterior", CAMPO),
    ("Com quem reside; quem presta os cuidados diários", CAMPO),
    ("Informante e grau de parentesco com o periciando", CAMPO),
    ("Início dos sintomas segundo o informante (data e primeira manifestação)", CAMPO),
    ("Evolução (súbita, progressiva, estável, flutuante)", CAMPO),
    ("Tratamentos e medicações em uso", CAMPO),
    ("Internações, quedas, episódios de desorientação ou perda de objetos e dinheiro", CAMPO),
    ("Fonte de renda e quem a administra atualmente", CAMPO),
    ("Episódios de exploração financeira, golpes ou gastos incompatíveis", CAMPO),
]
TEMPORALIDADE = [
    ("Documento médico mais antigo que menciona a doença (data e fls.)", CAMPO),
    ("Data provável de início da doença", CAMPO),
    ("Data provável em que a doença passou a comprometer a capacidade", CAMPO),
    ("Natureza: ( ) transitória ( ) permanente; ( ) estável ( ) progressiva ( ) potencialmente reversível", CAMPO),
]


# ---------------------------------------------------------------------------
# Discussão técnica: fundamentação de apoio (texto fixo, conferir vigência).
# ---------------------------------------------------------------------------
DISCUSSAO = {
    "previdenciario": [
        ("Doença não é sinônimo de incapacidade",
         "A perícia previdenciária não se limita a confirmar o diagnóstico. O ponto central é saber se a "
         "doença ou a sequela produz limitação funcional que impeça ou reduza o desempenho da atividade "
         "habitual do periciando. Incapacidade laborativa é a impossibilidade de desempenhar as funções "
         "específicas de uma atividade em consequência de alterações provocadas por doença ou acidente, "
         "avaliada em relação à profissão efetivamente exercida (INSS, Manual Técnico de Perícia Médica "
         "Previdenciária, 2018). Por isso o confronto entre os achados do exame físico e as exigências da "
         "função descrita é o núcleo da conclusão."),
        ("Benefício por incapacidade temporária (Lei 8.213/1991, art. 59)",
         "É devido ao segurado que ficar incapacitado para o seu trabalho ou para a sua atividade habitual "
         "por mais de quinze dias consecutivos. Pressupõe incapacidade com perspectiva de recuperação, "
         "razão pela qual o laudo deve estimar prazo para reavaliação."),
        ("Aposentadoria por incapacidade permanente (Lei 8.213/1991, arts. 42 e 45)",
         "É devida ao segurado considerado incapaz e insuscetível de reabilitação para o exercício de "
         "atividade que lhe garanta a subsistência. O art. 45 prevê acréscimo de 25% quando houver "
         "necessidade de assistência permanente de outra pessoa. Segundo a Súmula 47 da TNU, reconhecida "
         "incapacidade parcial, cabe ao Juízo analisar as condições pessoais e sociais do segurado "
         "(idade, escolaridade, histórico profissional), razão pela qual esses dados devem constar do laudo."),
        ("Auxílio acidente (Lei 8.213/1991, art. 86; Decreto 3.048/1999, art. 104 e Anexo III)",
         "É indenização devida quando, após a consolidação das lesões decorrentes de acidente de qualquer "
         "natureza, resultarem sequelas que impliquem redução da capacidade para o trabalho que o segurado "
         "habitualmente exercia. Não exige incapacidade total: exige sequela consolidada e redução da "
         "capacidade para a atividade habitual. Para o STJ (Tema 416), o grau da lesão e do maior esforço "
         "não interfere na concessão, bastando que a redução exista. O Anexo III do Decreto 3.048/1999 "
         "relaciona situações que dão direito ao benefício e deve ser citado quando houver enquadramento."),
        ("Acidente do trabalho e doença ocupacional (Lei 8.213/1991, arts. 19 a 21-A)",
         "São equiparadas ao acidente do trabalho a doença profissional e a doença do trabalho (art. 20), além "
         "das hipóteses de concausa e acidente de trajeto (art. 21). O Nexo Técnico Epidemiológico (art. 21-A) "
         "permite ao INSS presumir o nexo pela correlação estatística entre a atividade da empresa e o CID. "
         "A espécie do benefício recebido (91 ou 31) informa se o INSS reconheceu o caráter acidentário."),
        ("Data de início da doença e da incapacidade",
         "A data de início da doença (DID) e a data de início da incapacidade (DII) são datas distintas e "
         "devem ser fixadas com base em documento ou achado objetivo (exame, internação, cirurgia, atestado "
         "com descrição clínica), indicando a folha dos autos. Quando não houver elemento seguro, o laudo "
         "deve declarar a impossibilidade de fixação em vez de estimar sem fundamento."),
    ],
    "trabalhista": [
        ("Nexo causal e concausal",
         "A caracterização do nexo exige a análise conjunta da história clínica e ocupacional, do estudo "
         "do posto e da organização do trabalho, dos dados epidemiológicos e da literatura, conforme os "
         "critérios do art. 2º da Resolução CFM nº 2.323/2022. A classificação de Schilling auxilia: no "
         "grupo I o trabalho é causa necessária; no grupo II é fator contributivo, mas não necessário; no "
         "grupo III é provocador de distúrbio latente ou agravador de doença já estabelecida (concausa)."),
        ("Doença ocupacional (Lei 8.213/1991, arts. 20 e 21)",
         "Doença profissional é a produzida pelo exercício do trabalho peculiar a determinada atividade; "
         "doença do trabalho é a adquirida em função de condições especiais em que o trabalho é realizado. "
         "Não são consideradas doenças do trabalho a doença degenerativa, a inerente a grupo etário e a que "
         "não produza incapacidade (art. 20, § 1º), ressalvada a hipótese de concausa (art. 21, I)."),
        ("Dano, incapacidade e quantificação",
         "É preciso distinguir a incapacidade temporária (período de tratamento), a incapacidade permanente "
         "(parcial ou total) e o dano estético. Quando solicitada quantificação percentual, deve ser "
         "indicada a tabela utilizada, como a tabela anexa à Lei 6.194/1974 (incluída pela Lei "
         "11.945/2009), com a ressalva de que se trata de referência analógica."),
    ],
    "curatela": [
        ("Capacidade civil após o Estatuto da Pessoa com Deficiência",
         "Com a Lei 13.146/2015, apenas os menores de dezesseis anos são absolutamente incapazes "
         "(Código Civil, art. 3º). Aqueles que, por causa transitória ou permanente, não puderem exprimir "
         "sua vontade são relativamente incapazes (art. 4º, III) e sujeitos a curatela (art. 1.767, I). "
         "A deficiência, por si só, não afeta a plena capacidade civil (Lei 13.146/2015, art. 6º)."),
        ("Curatela como medida extraordinária e proporcional",
         "A curatela é medida protetiva extraordinária, proporcional às necessidades de cada caso, e deve "
         "durar o menor tempo possível (Lei 13.146/2015, art. 84, § 3º). Afeta apenas atos de natureza "
         "patrimonial e negocial, não alcançando o direito ao próprio corpo, à sexualidade, ao matrimônio, "
         "à privacidade, à educação, à saúde, ao trabalho e ao voto (art. 85). Como alternativa menos "
         "restritiva existe a tomada de decisão apoiada (Código Civil, art. 1.783-A)."),
        ("O que o laudo deve indicar (CPC, arts. 753 e 755)",
         "O Código de Processo Civil determina que o laudo indique especificadamente, se for o caso, os atos "
         "para os quais haverá necessidade de curatela (art. 753, § 2º), cabendo ao juiz fixar os limites da "
         "curatela segundo o estado e o desenvolvimento mental do interditando (art. 755, I). Por isso a "
         "conclusão deve descrever a capacidade para cada grupo de atos, e não apenas o diagnóstico."),
        ("Capacidade de decisão: critérios clínicos",
         "A avaliação clínica da capacidade de decisão considera quatro habilidades: compreender a "
         "informação, apreciar a própria situação, raciocinar sobre as alternativas e expressar uma escolha "
         "(Appelbaum, 2007). Testes cognitivos como MEEM e MoCA rastreiam déficits, mas não definem "
         "isoladamente a capacidade; o desempenho funcional nas atividades instrumentais (Pfeffer, Lawton) "
         "e o estadiamento (CDR) aproximam o achado clínico dos atos da vida civil."),
        ("Temporalidade da doença",
         "Doenças neurocognitivas degenerativas têm início insidioso e curso progressivo, de modo que o "
         "comprometimento costuma preceder o diagnóstico formal. Quando relevante para o Juízo (por exemplo, "
         "validade de atos anteriores), o laudo deve indicar o documento mais antigo que registra a doença e "
         "a data a partir da qual há elementos objetivos de comprometimento, sem retroagir além do que os "
         "documentos sustentam."),
    ],
}

REFERENCIAS = {
    "comum": [
        "BRASIL. Lei nº 12.842, de 10 de julho de 2013 (Lei do Ato Médico), art. 5º, II.",
        "BRASIL. Lei nº 13.105, de 16 de março de 2015. Código de Processo Civil, arts. 156 a 158 e 464 a 480.",
        "CONSELHO FEDERAL DE MEDICINA. Resolução CFM nº 2.217/2018. Código de Ética Médica, Capítulo XI.",
        "FRANÇA, G. V. Medicina Legal. Rio de Janeiro: Guanabara Koogan.",
        "CROCE, D.; CROCE JÚNIOR, D. Manual de Medicina Legal. São Paulo: Saraiva.",
    ],
    "previdenciario": [
        "BRASIL. Lei nº 8.213, de 24 de julho de 1991, arts. 19 a 21-A, 42, 45, 59 e 86.",
        "BRASIL. Decreto nº 3.048, de 6 de maio de 1999, art. 104 e Anexo III.",
        "INSTITUTO NACIONAL DO SEGURO SOCIAL. Manual Técnico de Perícia Médica Previdenciária. Brasília: INSS, 2018.",
        "SUPERIOR TRIBUNAL DE JUSTIÇA. Tema Repetitivo 416 (REsp 1.109.591/SC).",
        "TURMA NACIONAL DE UNIFORMIZAÇÃO. Súmula 47.",
        "CONSELHO NACIONAL DE JUSTIÇA. Recomendação Conjunta nº 1/2015 (quesitos padronizados em perícias previdenciárias).",
        "AMERICAN ACADEMY OF ORTHOPAEDIC SURGEONS. Joint Motion: Method of Measuring and Recording.",
    ],
    "trabalhista": [
        "BRASIL. Lei nº 8.213, de 24 de julho de 1991, arts. 19 a 21-A.",
        "CONSELHO FEDERAL DE MEDICINA. Resolução CFM nº 2.323/2022 (atendimento ao trabalhador e nexo causal).",
        "SCHILLING, R. S. F. More effective prevention in occupational health practice? J Soc Occup Med, 1984.",
        "BRASIL. Lei nº 6.194/1974, anexo incluído pela Lei nº 11.945/2009.",
        "AMERICAN ACADEMY OF ORTHOPAEDIC SURGEONS. Joint Motion: Method of Measuring and Recording.",
    ],
    "curatela": [
        "BRASIL. Código Civil (Lei nº 10.406/2002), arts. 3º, 4º, 1.767, 1.772, 1.781 e 1.783-A.",
        "BRASIL. Lei nº 13.146/2015 (Estatuto da Pessoa com Deficiência), arts. 2º, 6º, 84 e 85.",
        "BRASIL. Código de Processo Civil, arts. 747 a 758.",
        "APPELBAUM, P. S. Assessment of patients' competence to consent to treatment. N Engl J Med, 2007;357:1834-40.",
        "FOLSTEIN, M. F.; FOLSTEIN, S. E.; McHUGH, P. R. Mini-mental state. J Psychiatr Res, 1975;12:189-98.",
        "BRUCKI, S. M. D. et al. Sugestões para o uso do mini-exame do estado mental no Brasil. "
        "Arq Neuropsiquiatr, 2003;61(3B):777-81.",
        "NASREDDINE, Z. S. et al. The Montreal Cognitive Assessment, MoCA. J Am Geriatr Soc, 2005;53:695-9.",
        "MORRIS, J. C. The Clinical Dementia Rating (CDR). Neurology, 1993;43:2412-4.",
        "PFEFFER, R. I. et al. Measurement of functional activities in older adults in the community. "
        "J Gerontol, 1982;37:323-9.",
        "KATZ, S. et al. Studies of illness in the aged. The index of ADL. JAMA, 1963;185:914-9.",
        "LAWTON, M. P.; BRODY, E. M. Assessment of older people. Gerontologist, 1969;9:179-86.",
        "AMERICAN PSYCHIATRIC ASSOCIATION. DSM-5-TR. Washington: APA, 2022.",
    ],
}

# ---------------------------------------------------------------------------
# Conclusão: roteiro de marcação, sem nenhuma resposta pré-definida.
# ---------------------------------------------------------------------------
CONCLUSAO = {
    "previdenciario": [
        "Diagnóstico (CID 10): " + CAMPO,
        "Data de início da doença (DID): " + CAMPO + "  Fundamento (fls.): " + CAMPO,
        "Incapacidade atual: ( ) ausente  ( ) presente",
        "Se presente: ( ) temporária, reavaliação sugerida em " + CAMPO + "  ( ) permanente",
        "Extensão: ( ) parcial  ( ) total;  ( ) para a atividade habitual  ( ) para toda e qualquer atividade",
        "Data de início da incapacidade (DII): " + CAMPO + "  Fundamento (fls.): " + CAMPO,
        "Passível de reabilitação profissional: ( ) sim  ( ) não  ( ) prejudicado",
        "Sequela consolidada com redução da capacidade para a atividade habitual (auxílio acidente): "
        "( ) sim  ( ) não;  enquadramento no Anexo III do Decreto 3.048/1999, quadro " + CAMPO,
        "Nexo com o trabalho (se alegado): ( ) presente  ( ) ausente  ( ) concausa  ( ) prejudicado",
        "Necessidade de assistência permanente de terceiros (art. 45): ( ) sim  ( ) não",
    ],
    "trabalhista": [
        "Diagnóstico (CID 10): " + CAMPO,
        "Nexo com o trabalho: ( ) causal  ( ) concausal (Schilling " + CAMPO + ")  ( ) ausente",
        "Incapacidade: ( ) ausente  ( ) temporária no período " + CAMPO + "  ( ) permanente",
        "Extensão: ( ) parcial  ( ) total;  percentual, se solicitado: " + CAMPO + " (tabela utilizada: " + CAMPO + ")",
        "Dano estético: ( ) ausente  ( ) presente, grau " + CAMPO,
        "Necessidade de tratamento futuro: " + CAMPO,
    ],
    "curatela": [
        "Diagnóstico (CID 10): " + CAMPO,
        "Início provável da doença: " + CAMPO + "  Comprometimento da capacidade desde: " + CAMPO,
        "Natureza: ( ) transitória  ( ) permanente;  ( ) estável  ( ) progressiva  ( ) potencialmente reversível",
        "Capacidade de exprimir a vontade: ( ) preservada  ( ) parcialmente comprometida  ( ) ausente",
        "Atos patrimoniais e negociais: ( ) capaz  ( ) necessita de apoio  ( ) incapaz",
        "Atos que necessitam de curatela (CPC, art. 753, § 2º): " + CAMPO,
        "Medida sugerida ao Juízo: ( ) nenhuma  ( ) tomada de decisão apoiada  ( ) curatela limitada aos atos "
        "indicados  ( ) curatela de todos os atos patrimoniais e negociais",
        "Prognóstico e reavaliação sugerida: " + CAMPO,
    ],
}

NOTA_QUESITOS_AUSENTES = {
    "previdenciario": (
        "Não foram localizados quesitos automaticamente. Conferir nos autos a decisão de nomeação, "
        "eventual portaria do Juízo e os quesitos padronizados da Recomendação Conjunta CNJ nº 1/2015."
    ),
    "trabalhista": "Não foram localizados quesitos automaticamente. Conferir nos autos e nas atas de audiência.",
    "curatela": (
        "Não foram localizados quesitos automaticamente. Conferir nos autos, inclusive manifestação do "
        "Ministério Público (CPC, art. 752, § 1º)."
    ),
}
