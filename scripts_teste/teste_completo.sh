#!/usr/bin/env bash
################################################################################
# TESTE PONTA A PONTA — extrator judicial (Linux/macOS)
#
# Gera um PDF fictício e percorre extrair → listar → revisar → classificar →
# exportar, conferindo também as proteções. Tudo acontece em um diretório
# temporário: entradas/ e saidas/ do usuário não são lidos nem apagados.
#
# Uso, na raiz do clone:  bash scripts_teste/teste_completo.sh
# Se o comando extrator-judicial não estiver disponível, cria .venv e instala.
################################################################################

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"

VERDE='\033[0;32m'; VERMELHO='\033[0;31m'; AMARELO='\033[1;33m'; SEM_COR='\033[0m'
sucesso() { echo -e "${VERDE}✓${SEM_COR} $1"; }
erro() { echo -e "${VERMELHO}✗${SEM_COR} $1"; exit 1; }
info() { echo -e "${AMARELO}ℹ${SEM_COR} $1"; }
fase() { echo; echo "$1"; echo "─────────────────────────────────────────────────────────────"; }

fase "FASE 0: Ambiente"
if ! command -v extrator-judicial > /dev/null 2>&1; then
    command -v python3 > /dev/null 2>&1 || erro "Python 3.10+ não encontrado"
    if [[ ! -d .venv ]]; then
        info "Criando ambiente virtual .venv"
        python3 -m venv .venv
    fi
    # shellcheck disable=SC1091
    source .venv/bin/activate
    info "Instalando pacote e pytest"
    python -m pip install -q -e . pytest
fi
PYTHON="$(command -v python || command -v python3)"
"$PYTHON" -c 'import sys; assert sys.version_info >= (3, 10)' || erro "Necessário Python 3.10+"
extrator-judicial --help > /dev/null || erro "CLI não responde"
sucesso "CLI disponível ($("$PYTHON" --version))"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
PDF="$TMP/processo_ficticio.pdf"
S="$TMP/saidas"
mkdir -p "$S"

fase "FASE 1: Testes automatizados"
if "$PYTHON" -m pytest --version > /dev/null 2>&1; then
    "$PYTHON" -m pytest -q || erro "Testes automatizados falharam"
    sucesso "pytest passou"
else
    info "pytest não instalado; fase pulada (pip install pytest)"
fi

fase "FASE 2: PDF fictício"
"$PYTHON" teste_pdfs/gerar_pdf_ficticio.py "$PDF" > /dev/null || erro "Falha ao gerar PDF fictício"
sucesso "PDF sintético gerado em diretório temporário"

fase "FASE 3: Extração e listagem"
extrator-judicial extrair "$PDF" --saida "$S/revisao-01.json" || erro "Extração falhou"
LISTA="$(extrator-judicial listar "$PDF" --revisao "$S/revisao-01.json")" || erro "Listagem falhou"
echo "$LISTA"
grep -q "a_confirmar" <<< "$LISTA" || erro "Tipo de perícia deveria iniciar a_confirmar"
grep -q "Fictícia" <<< "$LISTA" && erro "Listagem não pode exibir conteúdo documental"
sucesso "Extração e listagem concluídas"

fase "FASE 4: Revisão humana"
extrator-judicial revisar "$PDF" --revisao "$S/revisao-01.json" \
    --candidato c0001 --acao confirmar --saida "$S/revisao-02.json" || erro "Confirmar falhou"
extrator-judicial revisar "$PDF" --revisao "$S/revisao-02.json" \
    --candidato c0002 --acao corrigir --valor "Valor corrigido no teste" \
    --saida "$S/revisao-03.json" || erro "Corrigir falhou"
extrator-judicial revisar "$PDF" --revisao "$S/revisao-03.json" \
    --candidato c0003 --acao rejeitar --saida "$S/revisao-04.json" || erro "Rejeitar falhou"
"$PYTHON" - "$S/revisao-04.json" <<'PY' || erro "Histórico ou original não preservados"
import json, sys
dados = json.load(open(sys.argv[1], encoding="utf-8"))
c1, c2, c3 = dados["candidatos"][:3]
assert c1["estado"] == "confirmado" and len(c1["historico"]) == 1
assert c2["estado"] == "corrigido" and c2["valor"] == "Valor corrigido no teste"
assert c2["original"] != c2["valor"] and c2["natureza"] == "anotacao_humana"
assert c3["estado"] == "rejeitado"
PY
sucesso "Confirmação, correção e rejeição registradas com histórico"

fase "FASE 5: Classificação humana"
extrator-judicial classificar "$PDF" --revisao "$S/revisao-04.json" \
    --tipo trabalhista --objeto "Objeto fictício informado pelo perito" \
    --saida "$S/revisao-05.json" || erro "Classificação falhou"
sucesso "Tipo e objeto confirmados manualmente"

fase "FASE 6: Exportação"
extrator-judicial exportar "$PDF" --revisao "$S/revisao-05.json" \
    --json "$S/relatorio.json" --markdown "$S/rascunho.md" || erro "Exportação falhou"
grep -q "RASCUNHO — REVISÃO NECESSÁRIA" "$S/rascunho.md" || erro "Rascunho sem aviso de revisão"
grep -q "necessita OCR" "$S/rascunho.md" || erro "Página sem texto deveria indicar OCR"
sucesso "JSON e Markdown exportados como rascunho"

fase "FASE 7: Proteções"
if extrator-judicial exportar "$PDF" --revisao "$S/revisao-05.json" \
    --json "$S/relatorio.json" --markdown "$S/rascunho.md" 2> /dev/null; then
    erro "Sobrescrita sem --sobrescrever deveria ser recusada"
fi
sucesso "Sobrescrita sem autorização recusada"
extrator-judicial exportar "$PDF" --revisao "$S/revisao-05.json" \
    --json "$S/relatorio.json" --markdown "$S/rascunho.md" --sobrescrever || erro "--sobrescrever falhou"
sucesso "Sobrescrita explícita aceita"
if extrator-judicial revisar "$PDF" --revisao "$S/revisao-05.json" \
    --candidato c0001 --acao confirmar --saida "$S/revisao-05.json" --sobrescrever 2> /dev/null; then
    erro "Revisão de entrada não pode ser sobrescrita"
fi
sucesso "Revisão de entrada protegida mesmo com --sobrescrever"
echo "não é PDF" > "$TMP/invalido.pdf"
if extrator-judicial extrair "$TMP/invalido.pdf" --saida "$S/x.json" 2> /dev/null; then
    erro "Arquivo que não é PDF deveria ser recusado"
fi
sucesso "Arquivo inválido recusado"

echo
echo "✅ TESTE PONTA A PONTA CONCLUÍDO (dados fictícios; arquivos temporários removidos)."
