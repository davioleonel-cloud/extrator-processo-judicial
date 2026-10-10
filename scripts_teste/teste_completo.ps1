# TESTE PONTA A PONTA — extrator judicial (Windows PowerShell)
#
# Equivalente a scripts_teste/teste_completo.sh. Gera um PDF fictício e percorre
# extrair -> listar -> revisar -> classificar -> exportar, conferindo proteções.
# Tudo acontece em diretório temporário: entradas\ e saidas\ não são tocados.
#
# Uso, na raiz do clone:
#   powershell -ExecutionPolicy Bypass -File scripts_teste\teste_completo.ps1

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

function Sucesso([string]$msg) { Write-Host "OK  $msg" -ForegroundColor Green }
function Erro([string]$msg) { Write-Host "ERRO $msg" -ForegroundColor Red; exit 1 }
function Info([string]$msg) { Write-Host "    $msg" -ForegroundColor Yellow }
function Fase([string]$msg) { Write-Host ""; Write-Host $msg -ForegroundColor Cyan; Write-Host ("-" * 60) }

# Executa a CLI e devolve $true quando o código de saída é 0.
function Cli {
    # Erros esperados vão para stderr; não devem interromper o roteiro (PowerShell 5.1).
    $ErrorActionPreference = "Continue"
    & extrator-judicial @args 2>$null | Out-Host
    return ($LASTEXITCODE -eq 0)
}

Fase "FASE 0: Ambiente"
if (-not (Get-Command extrator-judicial -ErrorAction SilentlyContinue)) {
    if (-not (Test-Path ".venv")) {
        Info "Criando ambiente virtual .venv"
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { Erro "Python 3.10+ não encontrado (comando python)" }
    }
    & ".venv\Scripts\Activate.ps1"
    Info "Instalando pacote e pytest"
    python -m pip install -q -e . pytest
    if ($LASTEXITCODE -ne 0) { Erro "Falha na instalação" }
}
python -c "import sys; assert sys.version_info >= (3, 10)"
if ($LASTEXITCODE -ne 0) { Erro "Necessário Python 3.10+" }
if (-not (Cli --help)) { Erro "CLI não responde" }
Sucesso "CLI disponível"

$Tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("extrator-teste-" + [guid]::NewGuid())
$S = Join-Path $Tmp "saidas"
New-Item -ItemType Directory -Path $S -Force | Out-Null
$Pdf = Join-Path $Tmp "processo_ficticio.pdf"

try {
    Fase "FASE 1: Testes automatizados"
    python -m pytest --version *> $null
    if ($LASTEXITCODE -eq 0) {
        python -m pytest -q
        if ($LASTEXITCODE -ne 0) { Erro "Testes automatizados falharam" }
        Sucesso "pytest passou"
    } else {
        Info "pytest não instalado; fase pulada (pip install pytest)"
    }

    Fase "FASE 2: PDF fictício"
    python teste_pdfs\gerar_pdf_ficticio.py $Pdf | Out-Null
    if ($LASTEXITCODE -ne 0) { Erro "Falha ao gerar PDF fictício" }
    Sucesso "PDF sintético gerado em diretório temporário"

    Fase "FASE 3: Extração e listagem"
    if (-not (Cli extrair $Pdf --saida "$S\revisao-01.json")) { Erro "Extração falhou" }
    $Lista = (& extrator-judicial listar $Pdf --revisao "$S\revisao-01.json") -join "`n"
    if ($LASTEXITCODE -ne 0) { Erro "Listagem falhou" }
    Write-Host $Lista
    if ($Lista -notmatch "a_confirmar") { Erro "Tipo de perícia deveria iniciar a_confirmar" }
    if ($Lista -match "Pessoa") { Erro "Listagem não pode exibir conteúdo documental" }
    Sucesso "Extração e listagem concluídas"

    Fase "FASE 4: Revisão humana"
    if (-not (Cli revisar $Pdf --revisao "$S\revisao-01.json" --candidato c0001 --acao confirmar --saida "$S\revisao-02.json")) { Erro "Confirmar falhou" }
    if (-not (Cli revisar $Pdf --revisao "$S\revisao-02.json" --candidato c0002 --acao corrigir --valor "Valor corrigido no teste" --saida "$S\revisao-03.json")) { Erro "Corrigir falhou" }
    if (-not (Cli revisar $Pdf --revisao "$S\revisao-03.json" --candidato c0003 --acao rejeitar --saida "$S\revisao-04.json")) { Erro "Rejeitar falhou" }
    $Dados = Get-Content "$S\revisao-04.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    $C = $Dados.candidatos
    if ($C[0].estado -ne "confirmado" -or $C[1].estado -ne "corrigido" -or $C[2].estado -ne "rejeitado") { Erro "Estados de revisão inesperados" }
    if ($C[1].original -eq $C[1].valor -or $C[1].historico.Count -ne 1) { Erro "Original ou histórico não preservados" }
    Sucesso "Confirmação, correção e rejeição registradas com histórico"

    Fase "FASE 5: Classificação humana"
    if (-not (Cli classificar $Pdf --revisao "$S\revisao-04.json" --tipo trabalhista --objeto "Objeto fictício informado pelo perito" --saida "$S\revisao-05.json")) { Erro "Classificação falhou" }
    Sucesso "Tipo e objeto confirmados manualmente"

    Fase "FASE 6: Exportação"
    if (-not (Cli exportar $Pdf --revisao "$S\revisao-05.json" --json "$S\relatorio.json" --markdown "$S\rascunho.md")) { Erro "Exportação falhou" }
    $Md = Get-Content "$S\rascunho.md" -Raw -Encoding UTF8
    if ($Md -notmatch "RASCUNHO" -or $Md -notmatch "necessita OCR") { Erro "Rascunho incompleto" }
    Sucesso "JSON e Markdown exportados como rascunho"

    Fase "FASE 7: Proteções"
    if (Cli exportar $Pdf --revisao "$S\revisao-05.json" --json "$S\relatorio.json" --markdown "$S\rascunho.md") { Erro "Sobrescrita sem --sobrescrever deveria ser recusada" }
    Sucesso "Sobrescrita sem autorização recusada"
    if (-not (Cli exportar $Pdf --revisao "$S\revisao-05.json" --json "$S\relatorio.json" --markdown "$S\rascunho.md" --sobrescrever)) { Erro "--sobrescrever falhou" }
    Sucesso "Sobrescrita explícita aceita"
    if (Cli revisar $Pdf --revisao "$S\revisao-05.json" --candidato c0001 --acao confirmar --saida "$S\revisao-05.json" --sobrescrever) { Erro "Revisão de entrada não pode ser sobrescrita" }
    Sucesso "Revisão de entrada protegida mesmo com --sobrescrever"
    Set-Content -Path "$Tmp\invalido.pdf" -Value "não é PDF"
    if (Cli extrair "$Tmp\invalido.pdf" --saida "$S\x.json") { Erro "Arquivo que não é PDF deveria ser recusado" }
    Sucesso "Arquivo inválido recusado"

    Write-Host ""
    Write-Host "TESTE PONTA A PONTA CONCLUÍDO (dados fictícios; arquivos temporários removidos)." -ForegroundColor Green
} finally {
    Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
}
