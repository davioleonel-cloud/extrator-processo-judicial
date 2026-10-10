# Requisitos do Sistema

## Visão geral

Este sistema deve permitir a análise de um processo judicial em PDF único, com organização documental e extração estruturada das informações relevantes para estudo e preparação de perícia.

## Requisitos funcionais

### RF01 — Upload de PDF único

O sistema deve aceitar um único arquivo PDF como entrada principal.

**Critérios:**
- o usuário consegue enviar um arquivo PDF
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
- o sistema deve diferenciar alegação de fato comprovado
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

O sistema deve classificar o caso de forma preliminar entre:

- trabalhista
- previdenciária
- confirmar

E destacar os pontos diferenciadores de cada tipo, como:

- atividade laboral
- relação de trabalho
- nexo causal
- incapacidade
- benefício
- exigência processual específica

**Critérios:**
- a classificação deve ser explicada com base em documento e contexto
- o sistema deve informar que é uma classificação preliminar, não conclusão final

### RF08 — Checklist para perícia

O sistema deve gerar um checklist de apoio para a perícia, com base no caso e nos quesitos.

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

1. O que foi alegado deve ser distinto do que foi comprovado.
2. O sistema deve sempre manter a origem documental.
3. A classificação trabalhista/previdenciária é preliminar e revisável.
4. Campos incompletos devem ser marcados como "a confirmar".
5. O usuário deve poder revisar ao menos os blocos mais importantes antes de gerar o pré-laudo final.

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
- revisão manual avançada

### Prioridade baixa
- interface visual sofisticada
- processamento em lote
- integrações externas
- automações avançadas de IA

## Resultado esperado da primeira entrega

Uma ferramenta que permita:

- importar um PDF único
- detectar os dados principais do processo
- organizar a documentação jurídica e médica
- gerar um checklist útil para a perícia
- preparar um pré-laudo de estudo com referência documental

