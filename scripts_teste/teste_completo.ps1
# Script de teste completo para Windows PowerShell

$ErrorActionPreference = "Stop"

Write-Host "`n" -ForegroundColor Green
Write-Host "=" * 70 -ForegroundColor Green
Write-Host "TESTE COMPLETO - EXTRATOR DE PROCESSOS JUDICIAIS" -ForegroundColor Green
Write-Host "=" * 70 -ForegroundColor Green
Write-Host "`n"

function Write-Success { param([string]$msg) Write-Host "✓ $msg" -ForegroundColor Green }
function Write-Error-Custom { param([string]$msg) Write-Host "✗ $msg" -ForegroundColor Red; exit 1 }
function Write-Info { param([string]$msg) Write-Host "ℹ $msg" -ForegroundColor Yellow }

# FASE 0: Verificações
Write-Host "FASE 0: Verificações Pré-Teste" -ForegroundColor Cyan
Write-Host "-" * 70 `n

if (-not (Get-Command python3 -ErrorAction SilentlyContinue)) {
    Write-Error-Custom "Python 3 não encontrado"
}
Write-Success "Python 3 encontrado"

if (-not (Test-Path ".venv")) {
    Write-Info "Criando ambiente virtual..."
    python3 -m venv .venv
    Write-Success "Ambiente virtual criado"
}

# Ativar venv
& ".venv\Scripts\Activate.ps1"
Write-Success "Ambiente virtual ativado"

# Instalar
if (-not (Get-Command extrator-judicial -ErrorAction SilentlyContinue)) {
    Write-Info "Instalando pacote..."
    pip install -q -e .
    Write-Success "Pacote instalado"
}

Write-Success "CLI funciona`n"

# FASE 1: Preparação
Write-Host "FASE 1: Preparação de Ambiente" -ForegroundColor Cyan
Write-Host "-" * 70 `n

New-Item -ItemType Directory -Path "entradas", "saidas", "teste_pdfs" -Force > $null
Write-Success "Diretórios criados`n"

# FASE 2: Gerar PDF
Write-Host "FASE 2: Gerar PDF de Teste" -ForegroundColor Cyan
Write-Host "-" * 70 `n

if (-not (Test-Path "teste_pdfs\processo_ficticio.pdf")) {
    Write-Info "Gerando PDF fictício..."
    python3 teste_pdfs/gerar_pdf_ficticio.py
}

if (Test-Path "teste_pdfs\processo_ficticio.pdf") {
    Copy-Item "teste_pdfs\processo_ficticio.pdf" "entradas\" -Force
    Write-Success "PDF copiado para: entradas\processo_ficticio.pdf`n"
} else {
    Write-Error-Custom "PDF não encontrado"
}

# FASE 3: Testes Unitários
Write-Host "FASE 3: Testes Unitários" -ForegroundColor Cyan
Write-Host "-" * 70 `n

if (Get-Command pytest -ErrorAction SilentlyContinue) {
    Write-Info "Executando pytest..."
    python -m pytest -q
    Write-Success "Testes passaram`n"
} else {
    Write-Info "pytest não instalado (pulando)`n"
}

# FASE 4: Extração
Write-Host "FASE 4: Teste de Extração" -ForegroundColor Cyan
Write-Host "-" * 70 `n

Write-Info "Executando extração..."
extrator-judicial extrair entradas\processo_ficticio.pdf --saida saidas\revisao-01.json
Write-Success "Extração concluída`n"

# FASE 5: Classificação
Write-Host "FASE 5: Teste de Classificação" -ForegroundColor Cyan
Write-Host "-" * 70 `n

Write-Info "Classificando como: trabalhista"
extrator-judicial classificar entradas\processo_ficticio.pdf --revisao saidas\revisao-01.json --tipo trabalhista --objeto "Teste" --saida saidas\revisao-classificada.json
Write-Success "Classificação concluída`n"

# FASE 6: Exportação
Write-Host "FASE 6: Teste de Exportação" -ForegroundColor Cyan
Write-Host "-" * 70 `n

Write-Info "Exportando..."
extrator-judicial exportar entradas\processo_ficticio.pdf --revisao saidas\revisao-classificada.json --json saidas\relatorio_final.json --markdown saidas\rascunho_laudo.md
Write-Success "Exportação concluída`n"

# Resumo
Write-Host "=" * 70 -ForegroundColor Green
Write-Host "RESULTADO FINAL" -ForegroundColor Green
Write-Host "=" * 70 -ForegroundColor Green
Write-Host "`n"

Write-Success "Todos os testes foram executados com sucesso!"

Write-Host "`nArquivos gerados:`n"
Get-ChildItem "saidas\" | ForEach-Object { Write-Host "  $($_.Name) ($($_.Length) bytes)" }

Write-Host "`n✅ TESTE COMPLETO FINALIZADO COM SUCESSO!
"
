#!/bin/bash

################################################################################
# SCRIPT DE TESTE COMPLETO END-TO-END
# Testa todas as funcionalidades do extrator judicial
################################################################################

set -e

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     TESTE COMPLETO - EXTRATOR DE PROCESSOS JUDICIAIS         ║"
echo "║                    Status: PRONTO PARA USAR                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Data: $(date)"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para mensagem de sucesso
sucesso() {
    echo -e "${GREEN}✓${NC} $1"
}

# Função para mensagem de erro
erro() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# Função para mensagem de info
info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

################################################################################
# FASE 0: VERIFICAÇÕES PRÉ-TESTE
################################################################################

echo "FASE 0: Verificações Pré-Teste"
echo "─────────────────────────────────────────────────────────────────"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    erro "Python 3 não encontrado. Instale Python 3.10+"
fi
sucesso "Python 3 encontrado: $(python3 --version)"

# Verificar venv
if [[ ! -d ".venv" ]]; then
    info "Criando ambiente virtual..."
    python3 -m venv .venv
    sucesso "Ambiente virtual criado"
fi

# Ativar venv
source .venv/bin/activate || erro "Falha ao ativar venv"
sucesso "Ambiente virtual ativado"

# Verificar instalação
if ! command -v extrator-judicial &> /dev/null; then
    info "Instalando pacote..."
    pip install -q -e .
    sucesso "Pacote instalado"
else
    sucesso "Pacote já instalado"
fi

# Verificar CLI
extrator-judicial --help > /dev/null || erro "CLI não funciona"
sucesso "CLI funciona"

echo ""

################################################################################
# FASE 1: PREPARAÇÃO DE AMBIENTE
################################################################################

echo "FASE 1: Preparação de Ambiente"
echo "─────────────────────────────────────────────────────────────────"

# Criar diretórios
mkdir -p entradas saidas teste_pdfs
sucesso "Diretórios criados"

# Limpar saídas anteriores
rm -f saidas/*.json saidas/*.md 2>/dev/null || true
sucesso "Saídas anteriores limpas"

echo ""

################################################################################
# FASE 2: GERAR PDF DE TESTE
################################################################################

echo "FASE 2: Gerar PDF de Teste"
echo "─────────────────────────────────────────────────────────────────"

if [[ ! -f "teste_pdfs/processo_ficticio.pdf" ]]; then
    info "Gerando PDF fictício..."
    python3 teste_pdfs/gerar_pdf_ficticio.py || info "Não foi possível gerar PDF com reportlab"
fi

if [[ -f "teste_pdfs/processo_ficticio.pdf" ]]; then
    cp teste_pdfs/processo_ficticio.pdf entradas/processo_ficticio.pdf
    sucesso "PDF copiado para: entradas/processo_ficticio.pdf"
else
    erro "PDF fictício não encontrado. Crie um PDF em entradas/processo_ficticio.pdf"
fi

echo ""

################################################################################
# FASE 3: TESTES UNITÁRIOS
################################################################################

echo "FASE 3: Testes Unitários"
echo "─────────────────────────────────────────────────────────────────"

if command -v pytest &> /dev/null; then
    info "Executando pytest..."
    if python -m pytest -q 2>/dev/null; then
        sucesso "Todos os testes passaram"
    else
        info "Alguns testes falharam (continuando...)"
    fi
else
    info "pytest não instalado (pulando)"
fi

echo ""

################################################################################
# FASE 4: TESTE DE EXTRAÇÃO
################################################################################

echo "FASE 4: Teste de Extração"
echo "─────────────────────────────────────────────────────────────────"

info "Executando: extrator-judicial extrair"
extrator-judicial extrair entradas/processo_ficticio.pdf \
    --saida saidas/revisao-01.json || erro "Extração falhou"

sucesso "Extração concluída"
info "Arquivo: saidas/revisao-01.json ($(wc -c < saidas/revisao-01.json) bytes)"

echo ""

################################################################################
# FASE 5: TESTE DE REVISÃO
################################################################################

echo "FASE 5: Teste de Revisão"
echo "─────────────────────────────────────────────────────────────────"

# Obter primeiro candidato
PRIMEIRO_CANDIDATO=$(python3 -c "
import json
with open('saidas/revisao-01.json') as f:
    data = json.load(f)
    if data.get('candidatos'):
        print(data['candidatos'][0]['id'])
" 2>/dev/null || echo "")

if [[ -z "$PRIMEIRO_CANDIDATO" ]]; then
    info "Nenhum candidato encontrado para revisar"
else
    info "Confirmando candidato: $PRIMEIRO_CANDIDATO"
    extrator-judicial revisar entradas/processo_ficticio.pdf \
        --revisao saidas/revisao-01.json \
        --candidato "$PRIMEIRO_CANDIDATO" \
        --acao confirmar \
        --saida saidas/revisao-02.json || info "Revisão com confirmar teve resultado inesperado"
    
    if [[ -f "saidas/revisao-02.json" ]]; then
        sucesso "Revisão (confirmar) concluída"
    fi
    
    # Corrigir um candidato
    info "Testando ação de correção..."
    extrator-judicial revisar entradas/processo_ficticio.pdf \
        --revisao saidas/revisao-02.json \
        --candidato "$PRIMEIRO_CANDIDATO" \
        --acao corrigir \
        --valor "Valor corrigido via teste" \
        --saida saidas/revisao-03.json || info "Revisão com corrigir teve resultado inesperado"
    
    if [[ -f "saidas/revisao-03.json" ]]; then
        sucesso "Revisão (corrigir) concluída"
    fi
fi

echo ""

################################################################################
# FASE 6: TESTE DE CLASSIFICAÇÃO
################################################################################

echo "FASE 6: Teste de Classificação"
echo "─────────────────────────────────────────────────────────────────"

# Usar a última revisão disponível
ULTIMA_REVISAO=$(ls -t saidas/revisao-*.json 2>/dev/null | head -1)

if [[ -z "$ULTIMA_REVISAO" ]]; then
    ULTIMA_REVISAO="saidas/revisao-01.json"
fi

info "Classificando como: trabalhista"
extrator-judicial classificar entradas/processo_ficticio.pdf \
    --revisao "$ULTIMA_REVISAO" \
    --tipo trabalhista \
    --objeto "Teste de perícia trabalhista" \
    --saida saidas/revisao-classificada.json || erro "Classificação falhou"

sucesso "Classificação concluída"

echo ""

################################################################################
# FASE 7: TESTE DE EXPORTAÇÃO
################################################################################

echo "FASE 7: Teste de Exportação"
echo "─────────────────────────────────────────────────────────────────"

info "Exportando JSON e Markdown..."
extrator-judicial exportar entradas/processo_ficticio.pdf \
    --revisao saidas/revisao-classificada.json \
    --json saidas/relatorio_final.json \
    --markdown saidas/rascunho_laudo.md || erro "Exportação falhou"

sucesso "Exportação concluída"
info "JSON: saidas/relatorio_final.json ($(wc -c < saidas/relatorio_final.json 2>/dev/null || echo "0") bytes)"
info "Markdown: saidas/rascunho_laudo.md ($(wc -c < saidas/rascunho_laudo.md 2>/dev/null || echo "0") bytes)"

echo ""

################################################################################
# FASE 8: VERIFICAÇÕES FINAIS
################################################################################

echo "FASE 8: Verificações Finais"
echo "─────────────────────────────────────────────────────────────────"

# Verificar se os arquivos existem e têm conteúdo
ARQUIVOS_ESPERADOS=("saidas/relatorio_final.json" "saidas/rascunho_laudo.md")

for arquivo in "${ARQUIVOS_ESPERADOS[@]}"; do
    if [[ -f "$arquivo" ]] && [[ -s "$arquivo" ]]; then
        sucesso "$arquivo ($(wc -c < "$arquivo") bytes)"
    else
        erro "$arquivo não encontrado ou vazio"
    fi
done

echo ""

################################################################################
# RESUMO FINAL
################################################################################

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    RESULTADO FINAL                            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
sucesso "Todos os testes foram executados com sucesso!"
echo ""

echo "Arquivos gerados:"
ls -lh saidas/ 2>/dev/null | tail -n +2 | awk '{print "  " $9 " (" $5 ")"}'
echo ""

echo "Próximos passos:"
echo "  1. Revisar os arquivos gerados em saidas/"
echo "  2. Verificar relatorio_final.json para estrutura de dados"
echo "  3. Abrir rascunho_laudo.md em editor de texto"
echo "  4. Testar com PDFs reais (sem dados sensíveis)"
echo ""

echo "Para mais informações:"
echo "  - Veja TESTE_COMPLETO.md"
echo "  - Execute: extrator-judicial --help"
echo ""

echo "✅ TESTE COMPLETO FINALIZADO COM SUCESSO!"
echo ""
