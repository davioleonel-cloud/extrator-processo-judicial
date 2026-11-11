"""Interface gráfica (tkinter) para realização do exame físico."""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime
from pathlib import Path

from .testes import TestesOrtopedicos
from .tabelas_referencia import gerar_tabelas_referencia


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
        return gerar_tabelas_referencia()
