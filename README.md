# Extrator de processo judicial

Base técnica **nova e independente**, para organização documental local de
**um único PDF**. Interface e saídas em português, compatível com Python 3.10+.
Não importa `exemplo_uso.py` nem `guia_exame_fisico_ortopedico.py`; os scripts
legados permanecem preservados e não fazem parte desta instalação.

## O que funciona nesta entrega

- Leitura de texto página a página, na ordem original, com numeração iniciada em
  1, nome do arquivo e SHA-256. O PDF original não é dividido nem alterado.
- Páginas sem texto permanecem na saída como **necessita OCR**, inclusive em PDFs
  mistos. Isso não significa ausência de informação. **Não há OCR implementado.**
- Candidatos conservadores para número do processo, autores, réus, vara, juiz,
  tipo de ação e pedido, por rótulos em português (`Autor:`, `Requerente:`,
  `Réu:`, `Reclamada:`, `Classe processual:`, entre outros).
  Diferentes ocorrências são mantidas; não há seleção silenciosa nem score.
- Localização inicial de **possíveis** nomeações com indicadores explícitos,
  quesitos do juiz/autor/réu/origem indefinida e petição inicial.
  São candidatos, **não segmentação perfeita**. Texto e numeração dos quesitos
  permanecem originais; origens diferentes não são concatenadas.
- Revisão por comandos, com confirmação, correção e rejeição persistidas.
- Exportação JSON e Markdown editável, com ficha, fontes, páginas, avisos,
  pendências, checklist **documental genérico** e esqueleto de pré-laudo.

Toda exportação é **RASCUNHO — REVISÃO NECESSÁRIA**, mesmo após revisar campos.
Informação documental não significa verdade comprovada; confirmação significa
revisão humana do candidato, não comprovação do conteúdo. Não são produzidos
diagnóstico, nexo, incapacidade, resposta aos quesitos ou conclusão jurídica.
Exame, discussão e conclusão ficam vazios no JSON e a preencher no Markdown.

## Instalação e verificações

Na raiz do clone:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install pytest flake8
python -m pytest
python -m flake8 src tests --max-line-length=127
```

Dependência de execução: **pypdf 6.20.0**, biblioteca mantida, licença
**BSD-3-Clause** ([projeto](https://pypdf.readthedocs.io/)). A versão está explícita
em `pyproject.toml`; parsing binário não é reinventado. A instalação pode acessar
o índice de pacotes; **a execução do produto é inteiramente local**, sem IA,
servidor, banco externo, telemetria, upload ou chamadas externas.
Os testes geram PDFs sintéticos fictícios nos diretórios temporários do pytest.

Teste ponta a ponta (gera PDF fictício em diretório temporário e percorre todos
os comandos, sem tocar `entradas/` ou `saidas/`; também roda no CI):

```bash
bash scripts_teste/teste_completo.sh        # Windows: scripts_teste\teste_completo.ps1
python teste_pdfs/gerar_pdf_ficticio.py entradas/ficticio.pdf   # só o PDF fictício
```

Roteiro manual detalhado e resultados esperados: `TESTE_COMPLETO.md`.

## Uso, revisão e exportação

Use um PDF **sintético** para experimentar. Os nomes a seguir são ilustrativos;
nenhum processo ou pessoa real é fornecido no repositório.

```bash
mkdir -p entradas saidas
extrator-judicial --help
extrator-judicial extrair entradas/ficticio.pdf --saida saidas/revisao-01.json
```

Para ver os IDs, campos, estados, origens e páginas dos candidatos sem abrir
o JSON, use `listar`. Ele não grava arquivos e **não imprime valores nem trechos**:

```bash
extrator-judicial listar entradas/ficticio.pdf --revisao saidas/revisao-01.json
```

Abra o JSON em um editor local: consulte `candidatos`, seus IDs, valores,
estados e `fonte` (hash, página e trecho), e confira o PDF original. Os comandos
sempre recebem **exatamente um PDF** e revalidam o vínculo com ele:

```bash
extrator-judicial revisar entradas/ficticio.pdf --revisao saidas/revisao-01.json \
  --candidato c0001 --acao corrigir --valor "Número fictício corrigido" \
  --saida saidas/revisao-02.json
extrator-judicial revisar entradas/ficticio.pdf --revisao saidas/revisao-02.json \
  --candidato c0002 --acao confirmar --saida saidas/revisao-03.json
extrator-judicial revisar entradas/ficticio.pdf --revisao saidas/revisao-03.json \
  --candidato c0003 --acao rejeitar --saida saidas/revisao-04.json
```

Escolha IDs efetivamente presentes no seu JSON. Cada saída é uma nova revisão,
que pode ser reaberta no próximo comando. Correções não apagam original nem
fonte; o histórico registra valor/estado/natureza anteriores e novos e data UTC.
Campos ausentes ficam `nao_localizado`: esta versão não permite criar candidatos
sem fonte. Valores distintos continuam `conflitante` mesmo após confirmação;
rejeite o candidato inaplicável ou mantenha a divergência para estudo.

O tipo da perícia inicia `a_confirmar`. Somente um comando humano o confirma,
com **objeto específico separado**; nenhuma palavra-chave classifica o caso:

```bash
extrator-judicial classificar entradas/ficticio.pdf --revisao saidas/revisao-04.json \
  --tipo previdenciaria --objeto "Objeto fictício informado pelo perito" \
  --saida saidas/revisao-05.json
extrator-judicial exportar entradas/ficticio.pdf --revisao saidas/revisao-05.json \
  --json saidas/dossie.json --markdown saidas/rascunho.md
```

Tipos permitidos: `trabalhista` e `previdenciaria` (grafia da CLI).
É permitido exportar a revisão inicial, sem confirmar tudo: pendências continuam
visíveis e o rascunho nunca é rotulado como validado.
JSON exportado é um **relatório**, não o arquivo de revisão a reabrir; guarde
também `revisao-05.json`. Editar Markdown não altera o histórico JSON.

Saídas existentes são recusadas. `--sobrescrever` autoriza explicitamente
substituir **somente saídas**; PDF e JSON de entrada nunca podem ser substituídos,
mesmo com essa opção. Diretórios devem existir. Escrita UTF-8, com permissões
restritas e publicação atômica por arquivo. A exportação dupla pré-valida ambas
as saídas, mas **não é transação**: em erro de disco, confira eventual saída parcial.
Erros de leitura/gravação/revisão retornam código 1; argumentos inválidos, 2.
PDFs inválidos, corrompidos, ausentes e protegidos recebem mensagens sem conteúdo
ou caminho absoluto. Nesta etapa, **qualquer PDF criptografado é recusado**,
inclusive proteção com senha vazia; use uma cópia sem proteção obtida com autorização.

## Arquitetura e modelo de revisão

Pacote em `src/extrator_judicial/`, com responsabilidades separadas:

| Módulo | Responsabilidade |
|---|---|
| `modelos.py` | Esquema versão 1, ficha, estados, avisos e pendências |
| `pdf.py` | Leitura somente em modo binário de leitura, hash em blocos e páginas |
| `extracao.py` | Rótulos e indicadores textuais, sem inferência clínica |
| `revisao.py` | Transições auditáveis, confirmação humana e validação |
| `persistencia.py` | JSON UTF-8 e proteção contra sobrescrita |
| `relatorios.py` | Relatórios de rascunho e checklist documental |
| `cli.py` | Comandos `extrair`, `listar`, `revisar`, `classificar`, `exportar` (também `python -m extrator_judicial`) |

O JSON de revisão contém `versao_esquema`, `documento`, `paginas`, `candidatos`,
`pericia`, `ficha`, `avisos`, `pendencias` e `status`. Cada candidato tem ID,
campo, origem, original, valor atual, natureza original/atual, fonte imutável,
estado (`a_revisar`, `confirmado`, `corrigido`, `rejeitado`) e histórico.
Naturezas: `alegacao`, `informacao_documental`, `anotacao_humana`.
Pedido e inicial são tratados como alegação; correções são anotações humanas.
Nenhuma dessas naturezas é uma verdade pericial automática.

Ao reabrir, a CLI lê o PDF novamente, verifica SHA-256, reconstitui os candidatos
e reproduz o histórico. Fontes/páginas/trechos/originais inconsistentes são
recusados. Renomear o mesmo PDF é permitido; trocar seu conteúdo, não.
Essa validação assegura consistência documental, **não autentica identidade do
revisor** nem protege contra alguém que forje deliberadamente todo o histórico.

O hash é calculado sem carregar o binário inteiro; o texto é armazenado por
página para revisão/exportação, portanto memória e tamanho do JSON crescem com
o conteúdo. Não há limite garantido de recursos para PDFs hostis. Utilize PDFs
de origem confiável, em ambiente local com recursos e permissões adequados.

## Limitações e próximas etapas

Indicadores dependem de rótulos explícitos e layout do PDF. Não há reconhecimento
de tabelas, segmentação exaustiva, resumo completo da inicial ou busca semântica.
Blocos são limitados à página e ao próximo indicador reconhecido:
**confira continuações e atribuição de origem no original**.
Ausência de candidato não demonstra ausência do documento.

Próximas entregas: inicial completa (pedido, motivo, doença alegada, datas),
inventário médico/CTPS, datas separadas de emissão/atendimento/início alegado,
histórico e linha do tempo, OCR e interface visual local. Cargo não deve virar
atividade efetiva inferida. Evidências contraditórias e informações a esclarecer
devem permanecer rastreáveis. Checklist especializado depende de classificação
**confirmada por humano**, objeto e validação profissional; ainda não é gerado.
Veja `ROADMAP.md`, `docs/requisitos.md` e `docs/backlog.md`.

## Dados sensíveis — repositório público

**Não adicione PDFs reais, dados de pacientes/processos, credenciais ou saídas
identificáveis ao Git.** Mantenha entradas e resultados em diretórios locais
`entradas/` e `saidas/` (ignorados), ou preferencialmente fora do clone.
PDFs e JSON também são ignorados globalmente; Markdown de relatórios deve ficar
em `saidas/` ou fora do clone. Não use `git add -f` para esses dados.
Confira `git status` antes de qualquer commit, controle acesso local e backups
e não publique relatórios em issues/PRs. Os relatórios contêm texto documental
sensível; não são anonimizados automaticamente. Nome do arquivo também pode
identificar pessoas: prefira nome neutro. A CLI não imprime conteúdo documental.
Essas medidas **não são garantia de conformidade legal**.
