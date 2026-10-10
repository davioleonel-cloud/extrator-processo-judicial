# Roteiro de teste completo — extrator judicial

Roteiro para conferir, com **dados exclusivamente fictícios**, todo o fluxo da
CLI: extrair → listar → revisar → classificar → exportar. Instalação,
arquitetura e limites estão no `README.md`.

Toda saída continua sendo **RASCUNHO — REVISÃO NECESSÁRIA**. O teste confere o
funcionamento documental; não valida conteúdo pericial.

## 1. Teste automático (recomendado)

Na raiz do clone, com Python 3.10+:

```bash
bash scripts_teste/teste_completo.sh                 # Linux/macOS
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts_teste\teste_completo.ps1   # Windows
```

O roteiro usa o `extrator-judicial` já instalado; se não houver, cria `.venv`
e instala o pacote e o pytest. Em seguida roda os testes automatizados, gera um
PDF fictício em diretório temporário, percorre todos os comandos, confere as
proteções e apaga os temporários. `entradas/` e `saidas/` não são lidos nem
alterados. Termina com código 0 somente se todas as etapas passarem; o mesmo
roteiro bash roda no CI.

## 2. Teste manual, passo a passo

### 2.1 Ambiente

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -e . pytest flake8
python -m pytest
python -m flake8 src tests --max-line-length=127
extrator-judicial --help
```

### 2.2 PDF fictício

```bash
mkdir -p entradas saidas
python teste_pdfs/gerar_pdf_ficticio.py entradas/processo_ficticio.pdf
```

O gerador usa apenas pypdf e funciona offline. O PDF tem 3 páginas: rótulos de
identificação, nomeação, quesitos do juiz, do autor e da ré, e a petição
inicial; a página 2 não tem texto, para conferir o aviso **necessita OCR**.
PDFs são ignorados pelo Git; não versione o arquivo gerado.

### 2.3 Extrair e listar

```bash
extrator-judicial extrair entradas/processo_ficticio.pdf --saida saidas/revisao-01.json
extrator-judicial listar entradas/processo_ficticio.pdf --revisao saidas/revisao-01.json
```

`listar` mostra ID, campo, estado, origem e página de cada candidato, o tipo
de perícia e o número de pendências. Ele **não imprime valores nem trechos**;
para lê-los, abra o JSON em editor local (`valor`, `original`, `fonte`).

Esperado com o PDF fictício: `c0001` a `c0012`, quesitos com origem `juiz`,
`autor` e `reu`, e `Tipo de perícia: a_confirmar.`

### 2.4 Revisar

```bash
extrator-judicial revisar entradas/processo_ficticio.pdf --revisao saidas/revisao-01.json \
  --candidato c0001 --acao confirmar --saida saidas/revisao-02.json
extrator-judicial revisar entradas/processo_ficticio.pdf --revisao saidas/revisao-02.json \
  --candidato c0002 --acao corrigir --valor "Valor corrigido no teste" --saida saidas/revisao-03.json
extrator-judicial revisar entradas/processo_ficticio.pdf --revisao saidas/revisao-03.json \
  --candidato c0003 --acao rejeitar --saida saidas/revisao-04.json
extrator-judicial listar entradas/processo_ficticio.pdf --revisao saidas/revisao-04.json
```

Esperado: `c0001 confirmado`, `c0002 corrigido`, `c0003 rejeitado`. No JSON, o
`c0002` mantém `original` e `fonte`, passa a `natureza: anotacao_humana` e
registra o evento em `historico`.

### 2.5 Classificar (confirmação humana)

```bash
extrator-judicial classificar entradas/processo_ficticio.pdf --revisao saidas/revisao-04.json \
  --tipo trabalhista --objeto "Objeto fictício informado pelo perito" --saida saidas/revisao-05.json
```

Tipos aceitos: `trabalhista` ou `previdenciaria`. Nada é classificado
automaticamente.

### 2.6 Exportar

```bash
extrator-judicial exportar entradas/processo_ficticio.pdf --revisao saidas/revisao-05.json \
  --json saidas/relatorio.json --markdown saidas/rascunho.md
```

Esperado: Markdown com ficha, candidatos, fontes, avisos, pendências, checklist
documental genérico e Exame/Discussão/Conclusão "A preencher pelo perito".
O JSON exportado é relatório; para continuar revisando, reabra `revisao-05.json`.

### 2.7 Proteções e erros

| Ação | Resultado esperado (código 1) |
|---|---|
| Repetir a exportação acima sem `--sobrescrever` | `Saída já existe; escolha outro nome ou use --sobrescrever.` |
| `--saida` igual ao `--revisao` de entrada, mesmo com `--sobrescrever` | `Saída não pode substituir PDF ou revisão de entrada.` |
| `extrair` de arquivo que não é PDF | `Arquivo inválido: esperado um PDF.` |
| `extrair` de caminho inexistente | `PDF não encontrado.` |
| Saída em diretório inexistente | `Diretório de saída não existe; crie-o antes.` |
| `--revisao` de outro PDF | `Revisão vinculada a outro PDF (hash diferente).` |

Argumentos faltando ou inválidos (por exemplo, `exportar` sem `--markdown`)
terminam com código 2 e `Erro: argumentos inválidos. Consulte --help.`

## 3. Checklist

- [ ] `pytest` e `flake8` sem falhas
- [ ] Roteiro automático termina com "TESTE PONTA A PONTA CONCLUÍDO"
- [ ] Página sem texto aparece como necessita OCR
- [ ] `listar` não mostra nomes nem trechos
- [ ] Confirmar, corrigir e rejeitar ficam no histórico; original e fonte preservados
- [ ] Tipo de perícia só muda pelo comando `classificar`
- [ ] Exportação rotulada como rascunho, sem conclusão automática
- [ ] Sobrescrita recusada sem `--sobrescrever`; entradas nunca substituídas

## 4. Problemas comuns

- `extrator-judicial: command not found`: ative o ambiente (`source .venv/bin/activate`).
- `ModuleNotFoundError: extrator_judicial` ou `pypdf`: `python -m pip install -e .`
- PDF real com páginas digitalizadas: o texto não é extraído (sem OCR nesta
  entrega); as páginas aparecem como necessita OCR.

Não use PDFs reais neste roteiro nem anexe saídas a issues ou PRs.
