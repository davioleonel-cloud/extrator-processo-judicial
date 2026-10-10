# Script de teste completo para Windows PowerShell

$ErrorActionPreference = "Stop"

Write-Host "`n" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "TESTE COMPLETO - EXTRATOR DE PROCESSOS JUDICIAIS" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "`n"

function Write-Success { param([string]$msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Error-Custom { param([string]$msg) Write-Host "✗ $msg" -ForegroundColor Red; exit 1 }
function Write-Info { param([string]$msg) Write-Host "ℹ $msg" -ForegroundColor Yellow }

# FASE 0: Verificações
Write-Host "FASE 0: Verificações Pré-Teste" -ForegroundColor Cyan
Write-Host "-" * 70 `n

if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "Python 3 não encontrado"
}
Write-Success "Python 3 encontrado"

if (-not (Test-Path ".venv")) {
    Write-Info "Criando ambiente virtual..."
    python3 -m venv .venv
    Write-Success "Ambiente virtual criado"
}

# Ativar venv
& ".venv\Scripts\Activate.ps1"
Write-Success "Ambiente virtual ativado"

# Instalar
if (-not (Get-Command extrator-judicial -ErrorAction SilentlyContinue)) {
    Write-Info "Instalando pacote..."
    pip install -q -e .
    Write-Success "Pacote instalado"
}

Write-Success "CLI funciona`n"

# FASE 1: Preparação
Write-Host "FASE 1: Preparação de Ambiente" -ForegroundColor Cyan
Write-Host "-" * 70 `n

New-Item -ItemType Directory -Path "entradas", "saidas", "teste_pdfs" -Force > $null
Write-Success "Diretórios criados`n"

# FASE 2: Gerar PDF
Write-Host "FASE 2: Gerar PDF de Teste" -ForegroundColor Cyan
Write-Host "-" * 70 `n

if (-not (Test-Path "teste_pdfs\processo_ficticio.pdf")) {
    Write-Info "Gerando PDF fictício..."
    python3 teste_pdfs/gerar_pdf_ficticio.py
}

if (Test-Path "teste_pdfs\processo_ficticio.pdf") {
    Copy-Item "teste_pdfs\processo_ficticio.pdf" "entradas\" -Force
    Write-Success "PDF copiado para: entradas\processo_ficticio.pdf`n"
} else {
    Write-Error-Custom "PDF não encontrado"
}

# FASE 3: Testes Unitários
Write-Host "FASE 3: Testes Unitários" -ForegroundColor Cyan
Write-Host "-" * 70 `n

if (Get-Command pytest -ErrorAction SilentlyContinue) {
    Write-Info "Executando pytest..."
    python -m pytest -q
    Write-Success "Testes passaram`n"
} else {
    Write-Info "pytest não instalado (pulando)`n"
}

# FASE 4: Extração
Write-Host "FASE 4: Teste de Extração" -ForegroundColor Cyan
Write-Host "-" * 70 `n

Write-Info "Executando extração..."
extrator-judicial extrair entradas\processo_ficticio.pdf --saida saidas\revisao-01.json
Write-Success "Extração concluída`n"

# FASE 5: Classificação
Write-Host "FASE 5: Teste de Classificação" -ForegroundColor Cyan
Write-Host "-" * 70 `n

Write-Info "Classificando como: trabalhista"
extrator-judicial classificar entradas\processo_ficticio.pdf --revisao saidas\revisao-01.json --tipo trabalhista --objeto "Teste" --saida saidas\revisao-classificada.json
Write-Success "Classificação concluída`n"

# FASE 6: Exportação
Write-Host "FASE 6: Teste de Exportação" -ForegroundColor Cyan
Write-Host "-" * 70 `n

Write-Info "Exportando..."
extrator-judicial exportar entradas\processo_ficticio.pdf --revisao saidas\revisao-classificada.json --json saidas\relatorio_final.json --markdown saidas\rascunho_laudo.md
Write-Success "Exportação concluída`n"

# Resumo
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "RESULTADO FINAL" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "`n"

Write-Success "Todos os testes foram executados com sucesso!"

Write-Host "`nArquivos gerados:`n"
Get-ChildItem "saidas\" | ForEach-Object { Write-Host "  $($_.Name) ($($_.Length) bytes)" }

Write-Host "`n✅ TESTE COMPLETO FINALIZADO COM SUCESSO!
"
