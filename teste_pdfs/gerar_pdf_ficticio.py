#!/usr/bin/env python3
"""
Gera um PDF fictício para teste do extrator judicial.
Útil para testar sem dados reais sensíveis.
"""

import os
from pathlib import Path

# Tentar usar reportlab, mas funcionar sem ela também
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("⚠️  reportlab não está instalado. Use:")
    print("   pip install reportlab")
    print()

def criar_pdf_com_reportlab():
    """Cria PDF usando reportlab (melhor qualidade)"""
    output_dir = Path("teste_pdfs")
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / "processo_ficticio.pdf"
    
    c = canvas.Canvas(str(filepath), pagesize=letter)
    width, height = letter
    
    # Página 1 - Cabeçalho
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "PROCESSO JUDICIAL FICTÍCIO")
    c.drawString(50, y - 30, "Para Fins de Teste")
    
    y -= 70
    c.setFont("Helvetica", 10)
    
    # Dados básicos
    campos = [
        ("Número do Processo:", "0000001-00.0000.0.00000.0000000"),
        ("Autor:", "João da Silva Santos"),
        ("Réu:", "Empresa XYZ Indústria LTDA"),
        ("Vara Judicial:", "1ª Vara do Trabalho"),
        ("Juiz:", "Desembargador Dr. Carlos Alberto"),
        ("Tipo de Ação:", "Reclamação Trabalhista"),
        ("Data de Ajuizamento:", "12 de março de 2023"),
        ("Perito Judicial Nomeado:", "Dr. Med. Silva Pereira (CRM 123456)"),
        ("Data da Nomeação do Perito:", "15 de janeiro de 2024"),
        ("Objeto do Processo:", "Indenização por danos morais e materiais"),
    ]
    
    for label, value in campos:
        c.drawString(50, y, f"{label}")
        c.drawString(280, y, value)
        y -= 20
    
    # Quesitos
    y -= 30
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "QUESITOS PROPOSTOS PELO JUIZ:")
    
    y -= 25
    c.setFont("Helvetica", 10)
    
    quesitos_juiz = [
        "1. O autor foi diagnosticado com doença ocupacional? Qual?",
        "2. Há nexo causal comprovado entre o trabalho e a doença?",
        "3. Qual é o grau de incapacidade laboral?",
        "4. A incapacidade é temporária ou permanente?",
        "5. Há comprovação documental adequada?",
    ]
    
    for q in quesitos_juiz:
        c.drawString(60, y, q)
        y -= 18
    
    # Quesitos das partes
    y -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "QUESITOS DO AUTOR:")
    
    y -= 25
    c.setFont("Helvetica", 10)
    
    quesitos_autor = [
        "1. Qual é a data precisa do acidente/adoecimento?",
        "2. Houve atendimento médico imediato? Qual hospital/clínica?",
        "3. O empregador realizou as investigações obrigatórias?",
    ]
    
    for q in quesitos_autor:
        c.drawString(60, y, q)
        y -= 18
    
    # Página 2
    c.showPage()
    y = height - 50
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "PETIÇÃO INICIAL")
    
    y -= 40
    c.setFont("Helvetica", 10)
    
    texto_inicial = (
        "O reclamante, João da Silva Santos, por intermédio de seu procurador constituído, "
        "vem respeitosamente perante esta Corte apresentar RECLAMAÇÃO TRABALHISTA contra a "
        "empresa XYZ Indústria LTDA, com fundamento nos direitos garantidos pela Consolidação "
        "das Leis do Trabalho (CLT) e pela Constituição Federal.\n\n"
        "O autor alega ter sofrido acidente de trabalho em 10 de fevereiro de 2023, resultando "
        "em lesão no braço direito. Consta ter recebido atendimento médico na Clínica ABC em "
        "São Paulo, sendo diagnosticado com fratura exposta e posteriores sequelas incapacitantes.\n\n"
        "Apresenta os seguintes documentos em anexo:\n"
        "- Atestado médico de 10/02/2023\n"
        "- Radiografia de braço direito\n"
        "- Relatório técnico da segurança do trabalho\n"
        "- Fotografia das lesões (10/02/2023)\n"
        "- Recibos de salário (período afastado)\n\n"
        "Pelo exposto, requer:\n"
        "a) A condenação da ré ao pagamento de indenização por danos morais no valor de R$ 50.000,00\n"
        "b) Indenização por danos materiais (falta de repouso) no valor de R$ 15.000,00\n"
        "c) Custas processuais e honorários advocatícios\n\n"
        "Respeitosamente submetido para análise."
    )
    
    # Quebrar texto em linhas
    palavras = texto_inicial.split()
    linha_atual = ""
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 > 85:  # ~85 caracteres por linha
            c.drawString(50, y, linha_atual)
            y -= 15
            linha_atual = palavra
            if y < 50:
                c.showPage()
                y = height - 50
        else:
            linha_atual += " " + palavra if linha_atual else palavra
    
    if linha_atual:
        c.drawString(50, y, linha_atual)
    
    c.save()
    return filepath

def criar_pdf_com_pypdf():
    """Cria PDF usando pypdf (mais leve)"""
    try:
        from pypdf import PdfWriter
        from io import BytesIO
        
        output_dir = Path("teste_pdfs")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / "processo_ficticio.pdf"
        
        # Criar um PDF vazio com pypdf é limitado
        # Melhor usar reportlab ou criar arquivo de texto
        writer = PdfWriter()
        
        # Não é prático criar PDF do zero com pypdf
        # Vamos apenas informar ao usuário
        return None
    except:
        return None

def criar_arquivo_instrucoes():
    """Cria arquivo de instruções para gerar PDF"""
    output_dir = Path("teste_pdfs")
    output_dir.mkdir(exist_ok=True)
    
    instrucoes = output_dir / "COMO_GERAR_PDF.txt"
    
    conteudo = """COMO GERAR PDF FICTÍCIO PARA TESTE
================================

Opção 1: Instalar reportlab e rodar este script
  pip install reportlab
  python teste_pdfs/gerar_pdf_ficticio.py

Opção 2: Usar ferramenta online
  - Acesse: https:/smallpdf.com/pt/txt-para-pdf
  - Crie um arquivo TXT com os dados do processo
  - Converta para PDF
  - Salve em: entradas/processo_ficticio.pdf

Opção 3: Usar LibreOffice
  - Crie documento em Writer
  - Arquivo > Exportar como PDF
  - Salve em: entradas/processo_ficticio.pdf

Opção 4: Usar Google Docs
  - Crie documento no Google Docs
  - Arquivo > Download > PDF
  - Salve em: entradas/processo_ficticio.pdf

Opção 5: Usar Python puro (sem dependências)
  pip install reportlab
  python -c "from reportlab.pdfgen import canvas; c = canvas.Canvas('entradas/processo_ficticio.pdf'); c.drawString(100, 750, 'Teste'); c.save()"

---

Dados sugeridos para o PDF fictício:

Número: 0000001-00.0000.0.00000.0000000
Autor: João da Silva
Réu: Empresa XYZ LTDA
Vara: 1ª Vara do Trabalho
Juiz: Desembargador Carlos Alberto
Tipo: Reclamação Trabalhista
Perito: Dr. Med. Silva (CRM 123456)
Data da Nomeação: 15 de janeiro de 2024
"""
    
    with open(instrucoes, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    
    return instrucoes

if __name__ == "__main__":
    print("🧪 Gerador de PDF Fictício para Testes")
    print("=" * 50)
    print()
    
    if HAS_REPORTLAB:
        print("✓ reportlab detectado")
        print()
        filepath = criar_pdf_com_reportlab()
        print(f"✅ PDF criado: {filepath}")
        print()
        print("Próximos passos:")
        print(f"  1. mkdir -p entradas")
        print(f"  2. cp {filepath} entradas/")
        print(f"  3. extrator-judicial extrair entradas/processo_ficticio.pdf --saida saidas/r01.json")
    else:
        print("⚠️  reportlab não detectado")
        print()
        instrucoes = criar_arquivo_instrucoes()
        print(f"✓ Arquivo de instruções criado: {instrucoes}")
        print()
        print("Instale reportlab:")
        print("  pip install reportlab")
        print()
        print("Ou siga as instruções em:")
        print(f"  {instrucoes}")
