# 🧪 TESTE COMPLETO - Extrator de Processos Judiciais

## Status: PRONTO PARA USAR

Este documento fornece um roteiro passo a passo para testar a versão nova do extrator (`copilot/nova-base-tecnica-extrator-judicial`).

---

## ✅ PRÉ-REQUISITOS

```bash
# Python 3.10+
python3 --version

# Git
git --version
```

---

## 📥 PASSO 1: Preparar Ambiente

### 1.1 Clonar repositório
```bash
git clone https://github.com/davioleonel-cloud/extrator-processo-judicial.git
cd extrator-processo-judicial
```

### 1.2 Ir para branch de desenvolvimento
```bash
git checkout copilot/nova-base-tecnica-extrator-judicial
# ou
git checkout teste-final-completo
```

### 1.3 Criar ambiente virtual
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 1.4 Instalar pacotes
```bash
pip install --upgrade pip
pip install -e .
pip install pytest flake8
```

### 1.5 Verificar instalação
```bash
extrator-judicial --help
```

✅ Se vir a ajuda do CLI, tudo está instalado!

---

## 🧪 PASSO 2: Testes Unitários

### 2.1 Rodar testes
```bash
python -m pytest -v
```

### 2.2 Verificar cobertura
```bash
python -m pytest --cov=src/extrator_judicial tests/
```

### 2.3 Lint do código
```bash
python -m flake8 src tests --max-line-length=127
```

✅ Se todos os testes passarem, o código está estruturalmente ok.

---

## 📄 PASSO 3: Teste de Extração (Use o PDF Fictício)

### 3.1 Preparar diretórios
```bash
mkdir -p entradas saidas
```

### 3.2 Gerar PDF fictício para teste
Os testes sintéticos já criam PDFs. Você pode usar um deles ou criar manualmente:

```bash
# Opção A: Usar script Python para criar PDF de teste
python3 -c "
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas('entradas/processo_ficticio.pdf', pagesize=letter)
c.drawString(100, 750, 'PROCESSO JUDICIAL FICTÍCIO')
c.drawString(100, 730, 'Número do Processo: 0000001-00.0000.0.00000.0000000')
c.drawString(100, 710, 'Autor: João Silva')
c.drawString(100, 690, 'Réu: Empresa XYZ LTDA')
c.drawString(100, 670, 'Vara Judicial: 1ª Vara do Trabalho')
c.drawString(100, 650, 'Juiz: Desembargador ABC')
c.drawString(100, 630, 'Tipo de Ação: Reclamação Trabalhista')
c.drawString(100, 610, 'Pedido: Indenização por danos morais')
c.drawString(100, 590, 'Data da Nomeação: 15 de janeiro de 2024')
c.drawString(100, 570, 'Perito: Dr. Med. Silva (CRM 123456)')
c.drawString(100, 550, '')
c.drawString(100, 530, 'QUESITOS DO JUIZ:')
c.drawString(100, 510, '1. Qual a doença alegada?')
c.drawString(100, 490, '2. Há nexo causal com o trabalho?')
c.drawString(100, 470, '3. Qual o grau de incapacidade?')
c.drawString(100, 450, '')
c.drawString(100, 430, 'PETIÇÃO INICIAL:')
c.drawString(100, 410, 'O autor alega ter sofrido acidente no trabalho em 2023.')
c.drawString(100, 390, 'Apresenta atestados e exames que comprovam a lesão.')
c.drawString(100, 370, 'Solicita indenização por danos morais e materiais.')
c.save()
print('✓ PDF fictício criado: entradas/processo_ficticio.pdf')
"
```

**OU use este arquivo direto (pré-gerado):**
```bash
cp teste_pdfs/processo_ficticio.pdf entradas/
```

### 3.3 Executar extração
```bash
extrator-judicial extrair entradas/processo_ficticio.pdf --saida saidas/revisao-01.json
```

**Saída esperada:**
```
✓ Extração concluída
✓ JSON salvo: saidas/revisao-01.json
```

### 3.4 Inspecionar resultado
```bash
cat saidas/revisao-01.json | python -m json.tool | head -100
```

✅ Deve mostrar estrutura JSON com candidatos, páginas, e avisos.

---

## ✏️ PASSO 4: Teste de Revisão

### 4.1 Ver candidatos disponíveis
```bash
python3 -c "
import json
with open('saidas/revisao-01.json') as f:
    data = json.load(f)
    for c in data['candidatos'][:5]:
        print(f\"ID: {c['id']} | Campo: {c['campo']} | Valor: {c['valor_atual']}\") 
"
```

### 4.2 Confirmar um candidato
```bash
extrator-judicial revisar entradas/processo_ficticio.pdf \
  --revisao saidas/revisao-01.json \
  --candidato c0001 \
  --acao confirmar \
  --saida saidas/revisao-02.json
```

### 4.3 Corrigir um candidato
```bash
extrator-judicial revisar entradas/processo_ficticio.pdf \
  --revisao saidas/revisao-02.json \
  --candidato c0002 \
  --acao corrigir \
  --valor "Número corrigido: 0000001-00.0000.0.00000.9999999" \
  --saida saidas/revisao-03.json
```

### 4.4 Rejeitar um candidato
```bash
extrator-judicial revisar entradas/processo_ficticio.pdf \
  --revisao saidas/revisao-03.json \
  --candidato c0003 \
  --acao rejeitar \
  --saida saidas/revisao-04.json
```

### 4.5 Verificar histórico
```bash
python3 -c "
import json
with open('saidas/revisao-04.json') as f:
    data = json.load(f)
    for c in data['candidatos'][:3]:
        print(f\"\n{c['id']}: {c['campo']}\") 
        print(f\"  Estado: {c['estado']}\") 
        print(f\"  Histórico: {c['historico'][-1] if c['historico'] else 'N/A'}\") 
"
```

✅ Deve mostrar confirmações, correções e rejeições no histórico.

---

## 🎯 PASSO 5: Teste de Classificação

### 5.1 Classificar como trabalhista
```bash
extrator-judicial classificar entradas/processo_ficticio.pdf \
  --revisao saidas/revisao-04.json \
  --tipo trabalhista \
  --objeto "Reclamação trabalhista com lesão ocupacional" \
  --saida saidas/revisao-05.json
```

### 5.2 Verificar classificação
```bash
python3 -c "
import json
with open('saidas/revisao-05.json') as f:
    data = json.load(f)
    print(f\"Tipo: {data['pericia']['tipo']}\") 
    print(f\"Objeto: {data['pericia']['objeto']}\") 
"
```

✅ Deve mostrar tipo e objeto confirmados.

---

## 📊 PASSO 6: Teste de Exportação

### 6.1 Exportar JSON e Markdown
```bash
extrator-judicial exportar entradas/processo_ficticio.pdf \
  --revisao saidas/revisao-05.json \
  --json saidas/relatorio_final.json \
  --markdown saidas/rascunho_laudo.md
```

### 6.2 Inspecionar relatório JSON
```bash
cat saidas/relatorio_final.json | python -m json.tool | head -50
```

### 6.3 Ver rascunho Markdown
```bash
cat saidas/rascunho_laudo.md
```

✅ Deve ter ficha, checklist documental e pré-laudo vazio.

---

## 🔒 PASSO 7: Teste de Segurança

### 7.1 Verificar proteção contra sobrescrita
```bash
# Tenta sobrescrever sem permissão (deve falhar)
extrator-judicial exportar entradas/processo_ficticio.pdf \
  --revisao saidas/revisao-05.json \
  --json saidas/relatorio_final.json \
  --markdown saidas/rascunho_laudo.md
```

**Resultado esperado:** Erro de arquivo já existe

### 7.2 Autorizar sobrescrita
```bash
extrator-judicial exportar entradas/processo_ficticio.pdf \
  --revisao saidas/revisao-05.json \
  --json saidas/relatorio_final.json \
  --markdown saidas/rascunho_laudo.md \
  --sobrescrever
```

✅ Deve completar com sucesso.

---

## 📋 PASSO 8: Teste de Validação

### 8.1 PDF inválido
```bash
echo "isso não é um PDF" > entradas/invalido.txt
extrator-judicial extrair entradas/invalido.txt --saida saidas/teste.json
```

**Resultado esperado:** Erro "PDF inválido ou corrompido"

### 8.2 Arquivo não encontrado
```bash
extrator-judicial extrair entradas/nao_existe.pdf --saida saidas/teste.json
```

**Resultado esperado:** Erro "Arquivo não encontrado"

### 8.3 Diretório de saída não existe
```bash
extrator-judicial exportar entradas/processo_ficticio.pdf \
  --revisao saidas/revisao-05.json \
  --json saidas_inexistentes/relatorio.json
```

**Resultado esperado:** Erro "Diretório de saída não existe"

✅ Tratamento de erros funcionando corretamente.

---

## 📈 PASSO 9: Teste de Performance

### 9.1 Medir tempo de extração
```bash
time extrator-judicial extrair entradas/processo_ficticio.pdf --saida saidas/perf.json
```

**Esperado:** < 1 segundo

### 9.2 Verificar uso de memória
```bash
# Linux/Mac
/usr/bin/time -v extrator-judicial extrair entradas/processo_ficticio.pdf --saida saidas/perf.json

# Windows (use Task Manager)
```

✅ Deve ser eficiente mesmo com PDFs maiores.

---

## 🎓 PASSO 10: Teste Completo End-to-End

### Script completo de teste

```bash
#!/bin/bash

echo "🧪 INICIANDO TESTE COMPLETO END-TO-END..."
echo ""

# Limpar saídas anteriores
rm -rf saidas/*
mkdir -p saidas

echo "✓ Ambiente preparado"
echo ""

# 1. Extração
echo "📥 FASE 1: Extração"
extrator-judicial extrair entradas/processo_ficticio.pdf --saida saidas/r01.json || exit 1
echo "✓ Extração completa"
echo ""

# 2. Revisão
echo "✏️  FASE 2: Revisão"
extrator-judicial revisar entradas/processo_ficticio.pdf --revisao saidas/r01.json --candidato c0001 --acao confirmar --saida saidas/r02.json || exit 1
echo "✓ Revisão completa"
echo ""

# 3. Classificação
echo "🎯 FASE 3: Classificação"
extrator-judicial classificar entradas/processo_ficticio.pdf --revisao saidas/r02.json --tipo trabalhista --objeto "Teste" --saida saidas/r03.json || exit 1
echo "✓ Classificação completa"
echo ""

# 4. Exportação
echo "📊 FASE 4: Exportação"
extrator-judicial exportar entradas/processo_ficticio.pdf --revisao saidas/r03.json --json saidas/relatorio.json --markdown saidas/laudo.md || exit 1
echo "✓ Exportação completa"
echo ""

# 5. Verificação
echo "🔍 FASE 5: Verificação"
echo "Arquivos gerados:"
ls -lh saidas/
echo ""

echo "✅ TESTE COMPLETO COM SUCESSO!"
```

Salve como `teste_completo.sh` e execute:
```bash
chmod +x teste_completo.sh
./teste_completo.sh
```

---

## 📝 CHECKLIST DE TESTE

- [ ] Ambiente instalado
- [ ] Testes unitários passam
- [ ] Extração funciona
- [ ] Revisão (confirmar) funciona
- [ ] Revisão (corrigir) funciona
- [ ] Revisão (rejeitar) funciona
- [ ] Classificação funciona
- [ ] Exportação JSON funciona
- [ ] Exportação Markdown funciona
- [ ] Validação de erros funciona
- [ ] Performance aceitável
- [ ] Histórico preservado
- [ ] Proteção contra sobrescrita

---

## 🚀 PRÓXIMOS PASSOS (Se todos os testes passarem)

1. **Merge para main**
   ```bash
   git checkout main
   git pull origin main
   git merge teste-final-completo
   git push origin main
   ```

2. **Criar release**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. **Documentar em produção**
   - Atualizar README.md
   - Adicionar guia de uso
   - Incluir exemplos de casos reais (sem dados sensíveis)

---

## ❓ TROUBLESHOOTING

### Erro: "ModuleNotFoundError: No module named 'extrator_judicial'"
```bash
# Solução
pip install -e .
```

### Erro: "Command 'extrator-judicial' not found"
```bash
# Solução
source .venv/bin/activate
```

### Erro: "PDF inválido"
```bash
# Solução: Use o PDF fictício fornecido
ls entradas/
```

### Teste falha com timeout
```bash
# Aumentar timeout (Linux/Mac)
timeout 30 python -m pytest
```

---

## 📞 SUPORTE

Se encontrar problemas:
1. Verifique o Python 3.10+
2. Verifique dependências: `pip list`
3. Veja os logs: `cat .log` (se existir)
4. Abra uma issue no GitHub

---

**Última atualização:** 2026-10-10  
**Status:** ✅ PRONTO PARA TESTE
