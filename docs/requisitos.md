# Requisitos do Sistema

## Visão geral

Este sistema deve permitir a análise de um processo judicial em PDF único, com organização documental e extração estruturada das informações relevantes para estudo e preparação de perícia.

## Recorte da entrega técnica atual

Os requisitos abaixo descrevem o produto completo. A base atual entrega CLI
local, leitura por página/hash, identificação por rótulos, candidatos de nomeação,
quesitos e inicial, revisão JSON auditável e relatórios JSON/Markdown de rascunho.
Sem OCR, upload web, inicial exaustiva, inventário médico/CTPS, linha do tempo ou
checklist especializado. A revisão e rastreabilidade são obrigatórias desde
esta entrega; pendências não impedem exportar rascunho, nunca rotulado validado.
Consulte README para comandos, arquitetura, esquema e limites reais.

## Requisitos funcionais

### RF01 — Entrada de PDF único

O sistema deve aceitar um único arquivo PDF como entrada principal.

**Critérios:**
- o usuário informa caminho local de exatamente um PDF; interface visual é futura
- o arquivo é lido e mantido em ordem de paginação
- o conteúdo permanece acessível para revisão

### RF02 — Identificação do processo

O sistema deve extrair e apresentar os dados básicos do processo:

- número do processo
- autor
- réu
- vara judicial
- juiz
- tipo de ação / solicitação pleiteada

**Critérios:**
- os campos devem ser exibidos em ficha organizada
- cada informação deve manter referência de origem

### RF03 — Nomeação do perito e decisão judicial

O sistema deve localizar a decisão que nomeou o perito e apresentar:

- data da nomeação
- objetivos da perícia
- quesitos do juiz
- observações relevantes da decisão

**Critérios:**
- o texto original deve ser preservado
- o usuário deve identificar facilmente a página e o documento de origem

### RF04 — Quesitos das partes

O sistema deve separar os quesitos de cada parte:

- quesitos do autor
- quesitos do réu
- demais quesitos complementares

**Critérios:**
- cada quesito deve indicar a parte que o formulou
- a fórmula original deve ser mantida

### RF05 — Petição inicial e alegações

O sistema deve extrair e organizar:

- pedido
- motivo do pedido
- doença alegada
- período alegado
- datas relevantes
- evento/episódio que fundamenta a ação

**Critérios:**
- o sistema distingue alegação, informação documental e anotação humana; documento não comprova verdade
- o campo deve ser revisável manualmente

### RF06 — Documentos médicos e profissionais

O sistema deve organizar os documentos anexados ao processo, especialmente:

- relatórios médicos
- laudos
- exames
- carteira de trabalho
- atividades realizadas antes, durante e depois do período alegado

**Critérios:**
- organização por data e tipo
- diferenciação de período temporal
- rastreabilidade para cada documento

### RF07 — Diferenciação entre perícia trabalhista e previdenciária

O tipo inicia a confirmar e deve ser informado e confirmado por humano entre:

- trabalhista
- previdenciária
- a confirmar (sem classificação automática)

E destacar os pontos diferenciadores de cada tipo, como:

- atividade laboral
- relação de trabalho
- nexo causal
- incapacidade
- benefício
- exigência processual específica

**Critérios:**
- tipo confirmado por humano e objeto específico são registrados separadamente
- palavras-chave não determinam classificação final ou conteúdo clínico
- checklist especializado depende dessa confirmação e revisão profissional

### RF08 — Checklist para perícia

O produto completo deverá gerar checklist especializado após confirmação humana
de tipo e objeto. Nesta entrega há somente checklist DOCUMENTAL genérico.

**Itens esperados:**
- pontos a esclarecer
- documentos pendentes
- aspectos da atividade profissional
- aspectos clínicos e funcionais
- informações que precisam confirmação direta no exame

### RF09 — Pré-laudo de estudo

O sistema deve gerar um pré-laudo de estudo em formato estruturado, com:

- identificação do processo
- resumo do caso
- fatos alegados
- documentos relevantes
- análise cronológica
- itens pendentes
- observações da revisão humana

**Critérios:**
- o documento deve ser editável
- deve manter referências do processo
- não deve substituir a decisão final do perito

## Requisitos não funcionais

### RNF01 — Rastreabilidade

Toda informação extraída deve manter vínculo com a origem documental:

- documento
- página
- trecho de texto
- data de referência

### RNF02 — Revisão humana

O sistema deve permitir revisão e correção manual de qualquer extração automática.

### RNF03 — Segurança e privacidade

O sistema deve trabalhar com dados sensíveis de forma responsável, sem expor informações sem necessidade.

### RNF04 — Manutenibilidade

A base deve ser organizada em módulos separados por responsabilidade, como:

- leitura do PDF
- extração de dados
- organização documental
- classificação da perícia
- geração de checklist e pré-laudo

### RNF05 — Portabilidade

A solução deve poder rodar em ambiente local e compatível com Python, sem dependência de infraestrutura complexa na primeira etapa.

## Regras de negócio

1. Alegação, informação documental e anotação humana são distintas; nenhuma extração comprova um fato.
2. O sistema deve sempre manter a origem documental.
3. A classificação trabalhista/previdenciária exige confirmação humana, com objeto específico separado.
4. Campos incompletos devem ser marcados como "a confirmar".
5. Revisão persistida desde a primeira entrega; exportação com pendências continua rascunho.
6. Não gerar diagnóstico, nexo, incapacidade, respostas aos quesitos ou conclusão jurídica automaticamente.
7. Cargo não implica atividade efetiva; datas de emissão, atendimento e início alegado são distintas.

## Prioridade

### Prioridade alta
- PDF único
- identificação do processo
- nomeação do perito
- quesitos do juiz/partes
- petição inicial
- documentos médicos e profissionais
- checklist e pré-laudo

### Prioridade média
- classificação trabalhista/previdenciária
- organização cronológica detalhada
- ampliação da revisão auditável já implementada (não adiar a revisão básica)

### Prioridade baixa
- interface visual sofisticada
- processamento em lote
- integrações externas
- automações avançadas de IA

## Resultado esperado da primeira entrega

Uma ferramenta que permita:

- importar um PDF único
- detectar os dados principais do processo
- localizar candidatos de trechos jurídicos, ainda sem inventário médico completo
- gerar checklist documental genérico, não clínico prescritivo
- preparar rascunho de pré-laudo com fontes e campos de exame/discussão/conclusão em aberto
