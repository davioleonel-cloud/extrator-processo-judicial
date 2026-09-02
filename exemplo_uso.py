"""
EXEMPLOS DE USO DO EXTRATOR DE PROCESSOS JUDICIAIS
Diferentes formas de usar o script
"""

from extrator_principal import ExtractorProcessoJudicial
from ocr_extrator import OCRExtrator, AnalisadorDocumento
import json

# ============================================================
# EXEMPLO 1: Uso Básico - Extrair Processo Completo
# ============================================================

def exemplo_1_basico():
    """Exemplo básico de extração"""
    print("\n" + "="*60)
    print("EXEMPLO 1: Extração Básica")
    print("="*60)
    
    # Criar extrator
    extrator = ExtractorProcessoJudicial('./processo_exemplo')
    
    # Executar pipeline completo
    relatorio = extrator.executar_completo()
    
    # Exibir resultados
    print("\nRESULTADO:")
    print(json.dumps(relatorio['informacoes_extraidas'], indent=2, ensure_ascii=False))

# ============================================================
# EXEMPLO 2: Processar Apenas Textos
# ============================================================

def exemplo_2_apenas_textos():
    """Exemplo processando apenas textos"""
    print("\n" + "="*60)
    print("EXEMPLO 2: Processamento de Textos")
    print("="*60)
    
    extrator = ExtractorProcessoJudicial('./processo_exemplo')
    extrator.buscar_arquivos()
    
    # Filtrar apenas PDFs
    pdfs = [f for f in extrator.arquivos_encontrados if f.endswith('.pdf')]
    
    print(f"\nPDFs encontrados: {len(pdfs)}")
    for pdf in pdfs:
        print(f"  - {pdf}")
    
    # Processar
    textos, _ = extrator.processar_todos_arquivos()
    
    print(f"\nDocumentos de texto processados: {len(textos)}")
    for doc in textos:
        print(f"  - {doc['fonte']} ({doc['tipo']}): {len(doc['conteudo'])} caracteres")

# ============================================================
# EXEMPLO 3: OCR em Imagens Digitalizadas
# ============================================================

def exemplo_3_ocr():
    """Exemplo usando OCR em imagens"""
    print("\n" + "="*60)
    print("EXEMPLO 3: OCR em Imagens")
    print("="*60)
    
    # Criar OCR
    ocr = OCRExtrator(lingua='por')
    
    # Extrair de uma imagem
    imagem = './processo_exemplo/documentos_digitalizados/pagina_1.png'
    
    print(f"\nExtraindo texto de: {imagem}")
    print("Processando com preprocessamento...")
    
    texto = ocr.extrair_com_preprocessamento(imagem)
    
    print(f"\nTexto extraído ({len(texto)} caracteres):")
    print(texto[:500])  # Primeiros 500 caracteres
    
    # Análise
    print("\n" + "-"*60)
    print("ANÁLISE:")
    print(f"  Qualidade OCR: {AnalisadorDocumento.calcular_qualidade_ocr(texto)}%")
    print(f"  Total de palavras: {AnalisadorDocumento.contar_palavras(texto)}")
    print(f"  Datas encontradas: {AnalisadorDocumento.encontrar_datas(texto)}")
    print(f"  Valores monetários: {AnalisadorDocumento.encontrar_valores_monetarios(texto)}")

# ============================================================
# EXEMPLO 4: Extrair Múltiplas Imagens com OCR
# ============================================================

def exemplo_4_ocr_multiplo():
    """Exemplo processando múltiplas imagens"""
    print("\n" + "="*60)
    print("EXEMPLO 4: OCR Múltiplas Imagens")
    print("="*60)
    
    ocr = OCRExtrator(lingua='por')
    
    print("\nExtraindo texto de todas as imagens...")
    resultados = ocr.extrair_multiplas_imagens('./processo_exemplo/imagens')
    
    print(f"\nImagens processadas: {len(resultados)}")
    
    for arquivo, texto in resultados.items():
        print(f"\n{arquivo}:")
        print(f"  - Caracteres: {len(texto)}")
        print(f"  - Qualidade: {AnalisadorDocumento.calcular_qualidade_ocr(texto)}%")
        print(f"  - Preview: {texto[:100]}...")

# ============================================================
# EXEMPLO 5: Análise Personalizada
# ============================================================

def exemplo_5_analise_personalizada():
    """Exemplo com análise personalizada"""
    print("\n" + "="*60)
    print("EXEMPLO 5: Análise Personalizada")
    print("="*60)
    
    extrator = ExtractorProcessoJudicial('./processo_exemplo')
    extrator.buscar_arquivos()
    textos, imagens = extrator.processar_todos_arquivos()
    
    # Combinar todos os textos
    texto_completo = "\n".join([
        item['conteudo'] for item in textos
    ])
    
    print(f"\nAnalisando {len(texto_completo)} caracteres...")
    
    # Análise detalhada
    print("\n" + "-"*60)
    print("INFORMAÇÕES EXTRAÍDAS:")
    print("-"*60)
    
    # Datas
    datas = AnalisadorDocumento.encontrar_datas(texto_completo)
    print(f"\nDatas encontradas: {len(datas)}")
    for data in sorted(datas):
        print(f"  - {data}")
    
    # Valores
    valores = AnalisadorDocumento.encontrar_valores_monetarios(texto_completo)
    print(f"\nValores monetários: {len(valores)}")
    for valor in valores:
        print(f"  - {valor}")
    
    # Nomes
    nomes = AnalisadorDocumento.encontrar_nomes_proprios(texto_completo)
    print(f"\nNomes próprios encontrados: {len(nomes)}")
    for nome in nomes[:10]:
        print(f"  - {nome}")

# ============================================================
# EXEMPLO 6: Salvar Resultados em Diferentes Formatos
# ============================================================

def exemplo_6_salvar_resultados():
    """Exemplo salvando resultados"""
    print("\n" + "="*60)
    print("EXEMPLO 6: Salvando Resultados")
    print("="*60)
    
    extrator = ExtractorProcessoJudicial('./processo_exemplo')
    relatorio = extrator.executar_completo()
    
    # JSON
    with open('relatorio_processo.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    print("\n✓ Relatório JSON salvo: relatorio_processo.json")
    
    # TXT
    with open('relatorio_processo.txt', 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE PROCESSO JUDICIAL\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Data: {relatorio['data_extracao']}\n")
        f.write(f"Pasta: {relatorio['pasta_origem']}\n")
        f.write(f"Arquivos: {relatorio['quantidade_arquivos']}\n\n")
        
        f.write("INFORMAÇÕES:\n")
        for chave, valor in relatorio['informacoes_extraidas'].items():
            f.write(f"{chave.upper()}: {valor}\n")
    
    print("✓ Relatório TXT salvo: relatorio_processo.txt")
    
    # CSV com dados estruturados
    import csv
    
    with open('relatorio_processo.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Campo', 'Valor'])
        for chave, valor in relatorio['informacoes_extraidas'].items():
            writer.writerow([chave, valor])
    
    print("✓ Relatório CSV salvo: relatorio_processo.csv")

# ============================================================
# EXEMPLO 7: Processamento Filtrado
# ============================================================

def exemplo_7_filtrado():
    """Exemplo processando apenas tipos específicos"""
    print("\n" + "="*60)
    print("EXEMPLO 7: Processamento Filtrado")
    print("="*60)
    
    extrator = ExtractorProcessoJudicial('./processo_exemplo')
    extrator.buscar_arquivos()
    
    # Filtrar por extensão
    print("\nArquivos por tipo:")
    pdfs = [f for f in extrator.arquivos_encontrados if f.endswith('.pdf')]
    docx = [f for f in extrator.arquivos_encontrados if f.endswith('.docx')]
    imagens = [f for f in extrator.arquivos_encontrados if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    print(f"  PDFs: {len(pdfs)}")
    print(f"  DOCX: {len(docx)}")
    print(f"  Imagens: {len(imagens)}")
    
    print(f"\nTotal de arquivos: {len(extrator.arquivos_encontrados)}")

# ============================================================
# MENU PRINCIPAL
# ============================================================

def menu():
    """Menu interativo"""
    print("\n" + "="*60)
    print("EXEMPLOS DE USO - EXTRATOR DE PROCESSOS JUDICIAIS")
    print("="*60)
    print("\n1. Extração Básica")
    print("2. Processamento de Textos")
    print("3. OCR em Imagens")
    print("4. OCR Múltiplas Imagens")
    print("5. Análise Personalizada")
    print("6. Salvar Resultados")
    print("7. Processamento Filtrado")
    print("0. Sair")
    
    escolha = input("\nEscolha um exemplo (0-7): ").strip()
    
    exemplos = {
        '1': exemplo_1_basico,
        '2': exemplo_2_apenas_textos,
        '3': exemplo_3_ocr,
        '4': exemplo_4_ocr_multiplo,
        '5': exemplo_5_analise_personalizada,
        '6': exemplo_6_salvar_resultados,
        '7': exemplo_7_filtrado,
    }
    
    if escolha in exemplos:
        try:
            exemplos[escolha]()
        except FileNotFoundError:
            print("\n⚠️  Erro: Pasta './processo_exemplo' não encontrada!")
            print("   Crie uma pasta de exemplo com documentos antes de rodar os exemplos.")
        except Exception as e:
            print(f"\n❌ Erro: {e}")
    elif escolha != '0':
        print("Opção inválida!")

if __name__ == "__main__":
    menu()
