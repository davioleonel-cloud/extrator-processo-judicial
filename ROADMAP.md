# ROADMAP do Projeto

## Objetivo

Construir um sistema para automatizar a organização de processos judiciais em arquivo único (PDF), com foco em extração de dados processuais, identificação de quesitos, organização documental e geração de checklist e pré-laudo de estudo para perícias.

## Primeira entrega técnica limitada (implementada nesta base)

- CLI local para um PDF, texto e ordem por página, hash e aviso necessita OCR
- identificação por rótulos e candidatos de nomeação, quesitos e inicial
- revisão humana JSON versionada desde a primeira entrega, preservando fontes
- JSON e Markdown de rascunho, checklist documental genérico e pré-laudo vazio
- tipo de perícia a confirmar, informado/confirmado manualmente com objeto separado
- testes exclusivamente sintéticos; scripts legados independentes e preservados

Não inclui OCR, interface visual/upload web, inventário médico/CTPS completo,
linha do tempo, inicial exaustiva ou checklist especializado. As fases abaixo
preservam o planejamento do produto completo, **não representam entregas prontas**.
Instalação, comandos, arquitetura e limites estão no README.

## Escopo planejado do produto completo

A primeira versão será focada em entrada de um único PDF e extração estruturada dos elementos fundamentais do processo:

- número do processo
- autor
- réu
- vara judicial
- juiz
- tipo de ação / solicitação pleiteada
- nomeação do perito
- quesitos do juiz
- quesitos das partes
- petição inicial
- pedido, motivo, doença alegada, período e datas
- documentos médicos e profissionais relevantes
- classificação entre trabalhista e previdenciária confirmada por humano
- checklist para perícia
- pré-laudo de estudo com referências

## Não escopo da primeira versão

- processamento em lote multiarquivos
- integração com banco de dados externo
- interface web complexa
- diagnóstico automático definitivo
- substituir a análise profissional do perito

## Filosofia do projeto

- preservar a origem documental de cada informação
- distinguir alegação, informação documental e anotação humana; documento não comprova verdade
- permitir revisão humana antes da resposta final
- manter rastreabilidade por página, trecho e documento
- apoiar a perícia com checklist e documentação estruturada

## Sequência de entregas

### Fase 1 — Estrutura e importação do PDF

**Objetivo:** receber o arquivo PDF e tornar o conteúdo navegável e revisável.

**Entregáveis:**
- caminho local de um arquivo PDF único; interface visual em entrega futura
- paginação e visualização por página
- marcação de trechos relevantes
- origem clara de cada bloco extraído

**Critério de conclusão:**
- o usuário consegue abrir o PDF e identificar o conteúdo em páginas específicas

### Fase 2 — Identificação do processo e nomeação

**Objetivo:** extrair os dados básicos do processo e a decisão que nomeou o perito.

**Entregáveis:**
- ficha do processo
- autor, réu, vara, juiz, tipo de solicitação
- nomeação e data da perícia
- questão principal do pedido e objeto do processo

**Critério de conclusão:**
- campos localizados têm fontes e revisão; ausentes permanecem não localizados

### Fase 3 — Quesitos e petição inicial

**Objetivo:** separar os questionamentos do juiz e das partes, além do conteúdo da inicial.

**Entregáveis:**
- quesitos do juiz
- quesitos do autor
- quesitos do réu
- resumo da petição inicial
- pedido, motivo, doença alegada, ano e datas

**Critério de conclusão:**
- cada item fica identificado por origem e por parte envolvida

### Fase 4 — Documentos médicos e profissionais

**Objetivo:** organizar os anexos e o histórico relevante do caso.

**Entregáveis:**
- lista de relatórios médicos, laudos e exames
- organização cronológica
- CTPS e histórico de atividades
- diferenciação entre período anterior, durante e posterior
- indicadores de documentos faltantes ou inconclusivos

**Critério de conclusão:**
- o sistema permite mapear o histórico profissional e clínico com rastreabilidade temporal

### Fase 5 — Classificação da perícia

**Objetivo:** distinguir se o caso entra em perícia trabalhista, previdenciária ou requer confirmação.

**Entregáveis:**
- classificação do tipo de perícia confirmada por humano, objeto específico separado
- diferenciação dos pontos que se destacam em cada tipo
- checklist específico somente após confirmação humana e validação do objeto

**Critério de conclusão:**
- o humano confirma tipo e objeto; palavras-chave não definem classificação final

### Fase 6 — Checklist e pré-laudo

**Objetivo:** preparar a ferramenta de apoio ao estudo da perícia.

**Entregáveis:**
- checklist para uso durante a perícia
- pré-laudo de estudo
- relatório com evidências e referências
- área explícita de revisão/manual

**Critério de conclusão:**
- o usuário consegue produzir um resumo útil para análise e consulta antes do laudo definitivo

## Estrutura de organização do projeto

```text
.
├── ROADMAP.md
├── docs/
│   ├── requisitos.md
│   └── backlog.md
├── .github/
│   └── workflows/
│       └── python-app.yml
├── README.md
├── exemplo_uso.py
├── guia_exame_fisico_ortopedico.py
└── ...
```

## Regras de desenvolvimento

- todo dado extraído deve manter referência de origem
- alegação, informação documental e anotação humana são distintas; não inferir comprovação
- qualquer campo em dúvida deve ser marcado como "a confirmar"
- a revisão humana sempre precede a conclusão formal
- os documentos devem ser tratados de forma cronológica e auditável

## Próximo passo imediato

Validar a base limitada com os testes fictícios e revisão profissional do fluxo.
Depois ampliar localização de documentos e inicial, mantendo revisão e fontes.
Inventário médico/CTPS deve distinguir cargo de atividade real e separar datas
de emissão, atendimento e início alegado. OCR e interface visual vêm depois;
checklist especializado depende de classificação humana confirmada e objeto.

## Observação

Este roadmap não substitui a análise técnica do perito; ele organiza e facilita a coleta de informações, a revisão documental e a preparação da perícia.
