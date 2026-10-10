# Backlog do Projeto

## Entrega técnica limitada — disponível

- [x] Instalação explícita Python 3.10+, pacote independente e CLI local
- [x] Um PDF, páginas ordenadas, hash e avisos de ausência de texto/OCR necessário
- [x] Identificação inicial conservadora, múltiplos candidatos e fontes
- [x] Candidatos de nomeação, quesitos por origem ou indefinida e inicial
- [x] Revisão JSON com histórico, validação das fontes e proteção contra sobrescrita
- [x] JSON/Markdown de rascunho, checklist documental e conclusão em aberto
- [x] Confirmação humana de tipo da perícia e objeto específico separado
- [x] Testes sintéticos reais de leitura, extração, revisão, persistência e CLI
- [x] Comando `listar` (IDs, campos, estados e páginas, sem conteúdo documental)
- [x] Gerador de PDF fictício offline e roteiro ponta a ponta (bash/PowerShell, CI)

Dependência de execução: pypdf (BSD-3-Clause); comandos e arquitetura no README.
Os itens abaixo permanecem como objetivos de expansão, não concluídos.

## Produto completo planejado

### 1. Importação e leitura do PDF
- aceitar um PDF único
- identificar páginas e ordem
- permitir seleção de trechos
- manter referência da origem documental

### 2. Extração dos dados básicos do processo
- número do processo
- autor
- réu
- vara judicial
- juiz
- tipo de ação

### 3. Extração da nomeação e dos quesitos
- decisão que nomeou o perito
- quesitos do juiz
- quesitos das partes
- petição inicial

### 4. Organização dos documentos relevantes
- relatórios médicos
- laudos e exames
- CTPS
- atividades realizadas antes, durante e depois do período alegado

### 5. Geração de checklist e pré-laudo
- checklist para perícia
- resumo documental
- pré-laudo de estudo
- revisão manual da estrutura

## Fase 2

### Organização estrutural avançada
- separar documentos por categoria
- marcar dados incompletos ou conflitantes
- ampliar a revisão persistida já disponível, sem perder versões ou fontes

### Classificação do tipo de perícia
- trabalhista/previdenciária somente com confirmação humana
- a confirmar como estado inicial, sem inferência final por palavra-chave
- destacar pontos específicos de cada tipo

## Fase 3

### Aprimoramento de análise documental
- leitura de documentos digitais anexados
- identificação de datas e eventos-chave
- resumo cronológico do caso
- cruzamento de documentos e alegações

## Fase 4

### Funcionalidades de produção
- ampliar exportação JSON já disponível e Markdown editável
- exportação em PDF/texto estruturado
- relatórios por processo
- exportação para revisão humana e edição final

## Pendências técnicas

- ampliar leitura textual pypdf e segmentação com fontes por página
- selecionar OCR em futura entrega, com dependências/licença e revisão
- criar checklist especializado só após tipo e objeto confirmados por humano
- ampliar inicial, inventário médico/CTPS e linha do tempo com datas separadas
- não inferir atividade real pelo cargo; manter contradições e pontos a esclarecer
- implementar interface visual local depois da CLI; upload web não entregue
- validar novos comportamentos com exemplos exclusivamente sintéticos no repositório público

## Critérios de pronto

Uma tarefa está pronta quando:
- tem objetivo claro
- tem origem documental identificada
- tem resultado esperado definido
- tem dependências reconhecidas
- passa por revisão humana antes de ser considerada entregue
