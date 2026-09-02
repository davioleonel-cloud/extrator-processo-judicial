"""
GUIA INTERATIVO DE EXAME FÍSICO ORTOPÉDICO
Interface para realizar e documentar exame físico ortopédico completo
com orientações passo a passo e checklist de testes
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestesOrtopedicos:
    """Base de dados de testes ortopédicos com instruções"""
    
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

class InterfaceExameFisico:
    """Interface gráfica para realização do exame físico"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Guia Completo - Exame Físico Ortopédico")
        self.root.geometry("1200x800")
        
        self.estilo = ttk.Style()
        self.estilo.theme_use('clam')
        
        # Frame principal com abas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Abas
        self.criar_aba_amplitude()
        self.criar_aba_testes_especiais()
        self.criar_aba_forca()
        self.criar_aba_sensibilidade()
        self.criar_aba_resumo()
        self.criar_aba_tabelas_referencia()
        
        # Dados do exame
        self.dados_exame = {}
    
    def criar_aba_amplitude(self):
        """Aba de testes de amplitude de movimento"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Amplitude de Movimento")
        
        # Seleção do teste
        frame_selecao = ttk.LabelFrame(frame, text="Selecione o Teste", padding=10)
        frame_selecao.pack(fill=tk.X, padx=10, pady=5)
        
        self.teste_selecionado = tk.StringVar()
        teste_combo = ttk.Combobox(frame_selecao, textvariable=self.teste_selecionado, 
                                   values=list(TestesOrtopedicos.TESTES_AMPLITUDE.keys()),
                                   state='readonly', width=40)
        teste_combo.pack(side=tk.LEFT, padx=5)
        teste_combo.bind('<<ComboboxSelected>>', self.carregar_teste_amplitude)
        
        tk.Button(frame_selecao, text="Carregar Teste", 
                 command=self.carregar_teste_amplitude).pack(side=tk.LEFT, padx=5)
        
        # Área de conteúdo
        frame_conteudo = ttk.Frame(frame)
        frame_conteudo.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.texto_amplitude = scrolledtext.ScrolledText(frame_conteudo, height=30, wrap=tk.WORD)
        self.texto_amplitude.pack(fill=tk.BOTH, expand=True)
        
        # Frame de entrada
        frame_entrada = ttk.LabelFrame(frame, text="Registrar Medição", padding=10)
        frame_entrada.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_entrada, text="Amplitude encontrada (graus):").pack(side=tk.LEFT, padx=5)
        self.entrada_amplitude = tk.Entry(frame_entrada, width=10)
        self.entrada_amplitude.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_entrada, text="Salvar Medição",
                 command=self.salvar_amplitude).pack(side=tk.LEFT, padx=5)
    
    def carregar_teste_amplitude(self, event=None):
        """Carrega informações do teste de amplitude"""
        teste_nome = self.teste_selecionado.get()
        if not teste_nome:
            return
        
        teste = TestesOrtopedicos.TESTES_AMPLITUDE[teste_nome]
        
        conteudo = f"""
╔════════════════════════════════════════════════════════════════════╗
║                    {teste_nome.upper()}
╚════════════════════════════════════════════════════════════════════╝

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
        
        conteudo += "\n\n" + "="*70
        conteudo += "\nDICAS IMPORTANTES:\n"
        conteudo += "• Sempre compare com o lado contralateral\n"
        conteudo += "• Comece com movimento ativo (paciente fazendo)\n"
        conteudo += "• Depois teste movimento passivo (examinador fazendo)\n"
        conteudo += "• Use goniômetro para maior precisão\n"
        conteudo += "• Registre qualquer dor durante o movimento\n"
        conteudo += "• Verifique presença de crepitação ou estalidos\n"
        
        self.texto_amplitude.delete(1.0, tk.END)
        self.texto_amplitude.insert(1.0, conteudo)
    
    def salvar_amplitude(self):
        """Salva medição de amplitude"""
        teste = self.teste_selecionado.get()
        valor = self.entrada_amplitude.get()
        
        if not teste or not valor:
            messagebox.showwarning("Aviso", "Selecione um teste e digite a amplitude!")
            return
        
        if teste not in self.dados_exame:
            self.dados_exame[teste] = []
        
        self.dados_exame[teste].append({
            'valor': valor,
            'data': datetime.now().isoformat()
        })
        
        messagebox.showinfo("Sucesso", f"Medição salva: {teste} = {valor}°")
        self.entrada_amplitude.delete(0, tk.END)
    
    def criar_aba_testes_especiais(self):
        """Aba de testes especiais"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Testes Especiais")
        
        frame_selecao = ttk.LabelFrame(frame, text="Selecione o Teste", padding=10)
        frame_selecao.pack(fill=tk.X, padx=10, pady=5)
        
        self.teste_especial = tk.StringVar()
        teste_combo = ttk.Combobox(frame_selecao, textvariable=self.teste_especial,
                                   values=list(TestesOrtopedicos.TESTES_ESPECIAIS.keys()),
                                   state='readonly', width=50)
        teste_combo.pack(side=tk.LEFT, padx=5)
        teste_combo.bind('<<ComboboxSelected>>', self.carregar_teste_especial)
        
        tk.Button(frame_selecao, text="Carregar Teste",
                 command=self.carregar_teste_especial).pack(side=tk.LEFT, padx=5)
        
        frame_conteudo = ttk.Frame(frame)
        frame_conteudo.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.texto_especial = scrolledtext.ScrolledText(frame_conteudo, height=30, wrap=tk.WORD)
        self.texto_especial.pack(fill=tk.BOTH, expand=True)
        
        frame_resultado = ttk.LabelFrame(frame, text="Resultado do Teste", padding=10)
        frame_resultado.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_resultado, text="Resultado:").pack(side=tk.LEFT, padx=5)
        self.combo_resultado = ttk.Combobox(frame_resultado, 
                                           values=["Positivo", "Negativo", "Indefinido"],
                                           state='readonly', width=15)
        self.combo_resultado.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_resultado, text="Salvar Resultado",
                 command=self.salvar_teste_especial).pack(side=tk.LEFT, padx=5)
    
    def carregar_teste_especial(self, event=None):
        """Carrega teste especial"""
        teste_nome = self.teste_especial.get()
        if not teste_nome:
            return
        
        teste = TestesOrtopedicos.TESTES_ESPECIAIS[teste_nome]
        
        conteudo = f"""
╔════════════════════════════════════════════════════════════════════╗
║              {teste_nome.upper()}
╚════════════════════════════════════════════════════════════════════╝

DESCRIÇÃO:
{teste['descricao']}

RESULTADO POSITIVO:
{teste['positivo']}

SENSIBILIDADE: {teste.get('sensibilidade', 'N/A')}
ESPECIFICIDADE: {teste.get('especificidade', 'N/A')}

PASSOS PARA REALIZAÇÃO:
"""
        for passo in teste['passos']:
            conteudo += f"\n{passo}"
        
        conteudo += f"""

INTERPRETAÇÃO:
{teste['interpretacao']}

NOTA CLÍNICA:
Este é um teste importante para diagnóstico diferencial.
Combine com outros testes e achados clínicos para conclusão.
Nunca realize diagnóstico baseado em apenas um teste.
"""
        
        self.texto_especial.delete(1.0, tk.END)
        self.texto_especial.insert(1.0, conteudo)
    
    def salvar_teste_especial(self):
        """Salva resultado do teste especial"""
        teste = self.teste_especial.get()
        resultado = self.combo_resultado.get()
        
        if not teste or not resultado:
            messagebox.showwarning("Aviso", "Complete todos os campos!")
            return
        
        if 'Testes Especiais' not in self.dados_exame:
            self.dados_exame['Testes Especiais'] = []
        
        self.dados_exame['Testes Especiais'].append({
            'teste': teste,
            'resultado': resultado
        })
        
        messagebox.showinfo("Sucesso", f"Teste salvo: {teste} = {resultado}")
    
    def criar_aba_forca(self):
        """Aba de avaliação de força"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Avaliação de Força")
        
        frame_selecao = ttk.LabelFrame(frame, text="Selecione Grupo Muscular", padding=10)
        frame_selecao.pack(fill=tk.X, padx=10, pady=5)
        
        self.teste_forca = tk.StringVar()
        teste_combo = ttk.Combobox(frame_selecao, textvariable=self.teste_forca,
                                   values=list(TestesOrtopedicos.TESTES_FORCA.keys()),
                                   state='readonly', width=40)
        teste_combo.pack(side=tk.LEFT, padx=5)
        teste_combo.bind('<<ComboboxSelected>>', self.carregar_teste_forca)
        
        tk.Button(frame_selecao, text="Carregar Teste",
                 command=self.carregar_teste_forca).pack(side=tk.LEFT, padx=5)
        
        frame_conteudo = ttk.Frame(frame)
        frame_conteudo.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.texto_forca = scrolledtext.ScrolledText(frame_conteudo, height=25, wrap=tk.WORD)
        self.texto_forca.pack(fill=tk.BOTH, expand=True)
        
        frame_entrada = ttk.LabelFrame(frame, text="Registrar Força", padding=10)
        frame_entrada.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_entrada, text="Grau (0-5):").pack(side=tk.LEFT, padx=5)
        self.entrada_forca = ttk.Combobox(frame_entrada, values=["0", "1", "2", "3", "4", "5"],
                                         state='readonly', width=5)
        self.entrada_forca.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_entrada, text="Lado:").pack(side=tk.LEFT, padx=5)
        self.combo_lado = ttk.Combobox(frame_entrada, values=["Direito", "Esquerdo"],
                                      state='readonly', width=10)
        self.combo_lado.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_entrada, text="Salvar",
                 command=self.salvar_forca).pack(side=tk.LEFT, padx=5)
    
    def carregar_teste_forca(self, event=None):
        """Carrega teste de força"""
        teste_nome = self.teste_forca.get()
        if not teste_nome:
            return
        
        teste = TestesOrtopedicos.TESTES_FORCA[teste_nome]
        
        conteudo = f"""
╔════════════════════════════════════════════════════════════════════╗
║              TESTE DE FORÇA: {teste_nome.upper()}
╚════════════════════════════════════════════════════════════════════╝

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
        
        conteudo += f"""

PASSOS:
"""
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
        
        self.texto_forca.delete(1.0, tk.END)
        self.texto_forca.insert(1.0, conteudo)
    
    def salvar_forca(self):
        """Salva avaliação de força"""
        teste = self.teste_forca.get()
        grau = self.entrada_forca.get()
        lado = self.combo_lado.get()
        
        if not all([teste, grau, lado]):
            messagebox.showwarning("Aviso", "Complete todos os campos!")
            return
        
        if 'Força' not in self.dados_exame:
            self.dados_exame['Força'] = []
        
        self.dados_exame['Força'].append({
            'teste': teste,
            'grau': grau,
            'lado': lado
        })
        
        messagebox.showinfo("Sucesso", f"Força salva: {teste} - {lado} = Grau {grau}")
    
    def criar_aba_sensibilidade(self):
        """Aba de testes de sensibilidade"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Sensibilidade")
        
        frame_info = ttk.LabelFrame(frame, text="Testes de Sensibilidade", padding=10)
        frame_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.texto_sensibilidade = scrolledtext.ScrolledText(frame_info, height=25, wrap=tk.WORD)
        self.texto_sensibilidade.pack(fill=tk.BOTH, expand=True)
        
        # Preencher com informações dos testes
        conteudo = "TESTES DE SENSIBILIDADE\n" + "="*70 + "\n\n"
        for nome_teste, teste in TestesOrtopedicos.TESTES_SENSIBILIDADE.items():
            conteudo += f"\n{'─'*70}\n"
            conteudo += f"{nome_teste.upper()}\n"
            conteudo += f"{'─'*70}\n"
            conteudo += f"Descrição: {teste['descricao']}\n"
            conteudo += f"Material: {teste['material']}\n"
            conteudo += f"\nPASSOS:\n"
            for passo in teste['passos']:
                conteudo += f"{passo}\n"
            conteudo += "\n"
        
        self.texto_sensibilidade.insert(1.0, conteudo)
        self.texto_sensibilidade.config(state=tk.DISABLED)
    
    def criar_aba_resumo(self):
        """Aba de resumo do exame"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Resumo do Exame")
        
        frame_info = ttk.LabelFrame(frame, text="Dados Coletados", padding=10)
        frame_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.texto_resumo = scrolledtext.ScrolledText(frame_info, height=25, wrap=tk.WORD)
        self.texto_resumo.pack(fill=tk.BOTH, expand=True)
        
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(frame_botoes, text="Atualizar Resumo", command=self.atualizar_resumo).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botoes, text="Salvar em JSON", command=self.salvar_resumo_json).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botoes, text="Limpar Dados", command=self.limpar_dados).pack(side=tk.LEFT, padx=5)
    
    def atualizar_resumo(self):
        """Atualiza resumo com dados coletados"""
        conteudo = f"""
RESUMO DO EXAME FÍSICO ORTOPÉDICO
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

{'='*70}

DADOS COLETADOS:

"""
        for categoria, dados in self.dados_exame.items():
            conteudo += f"\n{categoria}:\n"
            if isinstance(dados, list):
                for item in dados:
                    if isinstance(item, dict):
                        for chave, valor in item.items():
                            conteudo += f"  • {chave}: {valor}\n"
                    else:
                        conteudo += f"  • {item}\n"
            conteudo += "\n"
        
        self.texto_resumo.config(state=tk.NORMAL)
        self.texto_resumo.delete(1.0, tk.END)
        self.texto_resumo.insert(1.0, conteudo)
        self.texto_resumo.config(state=tk.DISABLED)
    
    def salvar_resumo_json(self):
        """Salva resumo em JSON"""
        if not self.dados_exame:
            messagebox.showwarning("Aviso", "Nenhum dado para salvar!")
            return
        
        arquivo = Path("exame_fisico_ortopedico.json")
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(self.dados_exame, f, indent=2, ensure_ascii=False)
        
        messagebox.showinfo("Sucesso", f"Resumo salvo em: {arquivo}")
    
    def limpar_dados(self):
        """Limpa todos os dados"""
        if messagebox.askyesno("Confirmação", "Deseja limpar todos os dados?"):
            self.dados_exame = {}
            self.texto_resumo.config(state=tk.NORMAL)
            self.texto_resumo.delete(1.0, tk.END)
            self.texto_resumo.config(state=tk.DISABLED)
            messagebox.showinfo("Sucesso", "Dados foram limpos!")
    
    def criar_aba_tabelas_referencia(self):
        """Aba com tabelas de referência"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Tabelas de Referência")
        
        frame_info = ttk.LabelFrame(frame, text="Valores Normais e Referências", padding=10)
        frame_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.texto_tabelas = scrolledtext.ScrolledText(frame_info, height=30, wrap=tk.WORD)
        self.texto_tabelas.pack(fill=tk.BOTH, expand=True)
        
        # Adicionar tabelas
        conteudo = self.gerar_tabelas_referencia()
        self.texto_tabelas.insert(1.0, conteudo)
        self.texto_tabelas.config(state=tk.DISABLED)
    
    def gerar_tabelas_referencia(self) -> str:
        """Gera tabelas de referência"""
        return """
╔════════════════════════════════════════════════════════════════════════════╗
║                     TABELAS DE REFERÊNCIA ORTOPÉDICA                       ║
╚════════════════════════════════════════════════════════════════════════════╝

1. ESCALA DE FORÇA MUSCULAR (Grau 0-5)
═══════════════════════════════════════════════════════════════════════════

Grau 0: Sem contração muscular visível ou palpável
Grau 1: Contração palpável do músculo sem movimento articular
Grau 2: Movimento ativo apenas sem efeito da gravidade
Grau 3: Movimento contra efeito da gravidade
Grau 4: Movimento contra resistência parcial
Grau 5: Movimento contra resistência completa (força normal)


2. AMPLITUDE DE MOVIMENTO - PUNHO
═══════════════════════════════════════════════════════════════════════════

Flexão Palmar:              0-80°
Extensão:                   0-70°
Abducção (Radial):          0-20°
Adducção (Ulnar):           0-35°
Pronação:                   0-80°
Supinação:                  0-80°


3. AMPLITUDE DE MOVIMENTO - COTOVELO
═══════════════════════════════════════════════════════════════════════════

Flexão:                     0-150°
Extensão:                   0° (posição neutra)
Pronação:                   0-80°
Supinação:                  0-80°


4. AMPLITUDE DE MOVIMENTO - OMBRO
═══════════════════════════════════════════════════════════════════════════

Abdução:                    0-180°
Adducção:                   0-45°
Flexão:                     0-180°
Extensão:                   0-45°
Rotação Interna:            0-70°
Rotação Externa:            0-90°


5. FORÇA DE PREENSÃO (Dinamômetro de Mão)
═══════════════════════════════════════════════════════════════════════════

Homens:                     35-60 kg
Mulheres:                   20-40 kg

Nota: A mão dominante é normalmente 10% mais forte


6. FORÇA DE PINÇA (Pinçômetro)
═══════════════════════════════════════════════════════════════════════════

Normal:                     8-12 kg
Importante para: Trabalhos de precisão


7. CLASSIFICAÇÃO DE SENSIBILIDADE (Monofilamento)
═══════════════════════════════════════════════════════════════════════════

Filamento 2.83:             Normal
Filamento 4.31:             Diminuída
Filamento 6.65:             Diminuída profundamente
Não sente 6.65:             Perda severa de sensibilidade


8. DISCRIMINAÇÃO DE DOIS PONTOS
═══════════════════════════════════════════════════════════════════════════

Polpa digital:              2-3 mm
Palma:                      8-10 mm
Dorso da mão:               20-30 mm
Dorso do antebraço:         30-40 mm


9. TESTES CLÁSSICOS - SENSIBILIDADE E ESPECIFICIDADE
═══════════════════════════════════════════════════════════════════════════

Teste de Tinnel:            Sensibilidade: 72-95%    Especificidade: 95%
Teste de Phalen:            Sensibilidade: 51-93%    Especificidade: 95-98%
Teste de Lachman:           Sensibilidade: 72-98%    Especificidade: 96-99%
Teste de Apprehension:      Sensibilidade: 50-72%    Especificidade: 96-98%


10. COMPARAÇÃO BILATERAL
═══════════════════════════════════════════════════════════════════════════

Redução de força > 10% é considerada significativa
Sempre comparar o lado afetado com o contralateral
Registrar assimetrias


11. ESCALA DE DOR (VAS - Visual Analogue Scale)
═══════════════════════════════════════════════════════════════════════════

0-10:       Sem dor
11-20:      Dor leve
21-40:      Dor moderada
41-70:      Dor severa
71-100:     Dor máxima intolerável


12. CLASSIFICAÇÃO DE EDEMA
═══════════════════════════════════════════════════════════════════════════

0: Ausente
+1: Leve (depressão rápida após pressão)
+2: Moderado (depressão após 2-3 segundos)
+3: Grave (depressão após 4-5 segundos)
+4: Muito grave (pouca ou nenhuma depressão)


13. TESTE DE AMPLITUDE PASSIVA VS ATIVA
═══════════════════════════════════════════════════════════════════════════

Se amplitude ativa < amplitude passiva:
  → Fraqueza muscular
  
Se amplitude ativa = amplitude passiva:
  → Contraturas, rigidez articular ou limitação estrutural

Se amplitude passiva é dolorosa:
  → Inflamação, sinovite ou possível lesão


14. COMPARAÇÃO DE ESTRUTURAS BILATERALMENTE
═══════════════════════════════════════════════════════════════════════════

SEMPRE compare:
• Amplitude de movimento
• Força muscular
• Sensibilidade
• Volume/edema
• Temperatura
• Cor da pele
• Presença de cicatrizes ou deformidades


15. DOCUMENTAÇÃO ADEQUADA
═══════════════════════════════════════════════════════════════════════════

Registre:
✓ Localização exata da lesão
✓ Amplitude encontrada (não apenas "limitado")
✓ Força: grau específico 0-5
✓ Presença/ausência de dor
✓ Comparação bilateral
✓ Achados anormais
✓ Testes positivos ou negativos
✓ Impressão clínica
✓ Recomendações (exames adicionais, etc.)


═════════════════════════════════════════════════════════════════════════════

                    "EXAME COMPLETO E BEM DOCUMENTADO
                     É FUNDAMENTAL PARA DIAGNÓSTICO PRECISO"
                                                                    
═════════════════════════════════════════════════════════════════════════════
"""

def main():
    """Função principal"""
    root = tk.Tk()
    app = InterfaceExameFisico(root)
    root.mainloop()

if __name__ == "__main__":
    main()
