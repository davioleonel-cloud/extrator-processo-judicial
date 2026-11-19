# Extrator de processo judicial

Base técnica **nova e independente**, para organização documental local de
**um único PDF**. Interface e saídas em português, compatível com Python 3.10+.
Não importa `exemplo_uso.py` nem `guia_exame_fisico_ortopedico.py`; os scripts
legados permanecem preservados e não fazem parte desta instalação.

## O que funciona nesta entrega

- Leitura de texto página a página, na ordem original, com numeração iniciada em
  1, nome do arquivo e SHA-256. O PDF original não é dividido nem alterado.
- Páginas sem texto permanecem na saída como **necessita OCR**, inclusive em PDFs
  mistos. Isso não significa ausência de informação. Com `--ocr`, essas páginas
  são lidas pelo **Tesseract local** (ver "OCR" abaixo); o texto fica marcado como OCR.
- Candidatos conservadores para número do processo, autores, réus, vara, juiz,
  tipo de ação e pedido, por rótulos em português (`Autor:`, `Requerente:`,
  `Réu:`, `Reclamada:`, `Classe processual:`, `Órgão Julgador de Origem:`,
  entre outros, inclusive cabeçalhos repetidos do PJe).
  Diferentes ocorrências são mantidas; não há seleção silenciosa nem score.
  No Markdown, a ficha agrupa ocorrências iguais (quantidade e páginas).
- Localização inicial de **possíveis** nomeações com indicadores explícitos
  (inclusive "nomeio em substituição o Dr. …" com "perito/perita" nas linhas
  vizinhas), títulos de quesitos do juiz/autor/réu/origem indefinida, também
  numerados ("II - DOS QUESITOS …"), e petição inicial. Quesitos citados no meio
  do texto corrido não são localizados.
  São candidatos, **não segmentação perfeita**. Texto e numeração dos quesitos
  permanecem originais; origens diferentes não são concatenadas.
- Petição inicial em PDFs do PJe: delimitada pelas páginas com o mesmo ID de
  assinatura da página 1 (a conferir). Dentro dela, seções numeradas em
  maiúsculas (com páginas inicial e final), cada item de "DOS PEDIDOS"
  (`a.`, `b.`…, subitens mantidos), datas citadas com a linha vizinha e CID
  citados. Tudo é **alegação** a revisar: o tipo de cada data (emissão,
  atendimento, início alegado) e a atividade real ficam para o perito; cargo
  não vira atividade. O Markdown ganha um resumo "Petição inicial".
  Sem rodapé PJe, a inicial não é delimitada e nada disso é gerado.
- Revisão por comandos, com confirmação, correção e rejeição persistidas.
- Exportação JSON e Markdown editável, com ficha, fontes, páginas, avisos,
  pendências, checklist **documental genérico** e esqueleto de pré-laudo.
- **Pré-laudo em Word (.docx)** para preencher no ato pericial, com cabeçalho do
  perito e logotipo (90 px), em três modelos: `previdenciario`, `trabalhista` e
  `curatela`. Ver "Pré-laudo Word" abaixo.

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

Dependências de execução: **pypdf 6.20.0** (BSD-3-Clause,
[projeto](https://pypdf.readthedocs.io/)) e **python-docx 1.2.0** (MIT); OCR
opcional com **pypdfium2** e o programa Tesseract (ver "OCR"). A versão está explícita
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
restritas e publicação atômica por arquivo. Em pastas sem suporte a hard link
(rede, FAT/exFAT, montagens), a gravação usa criação exclusiva: continua recusando
sobrescrita, mas sem a mesma garantia atômica. A exportação dupla pré-valida ambas
as saídas, mas **não é transação**: em erro de disco, confira eventual saída parcial.
Erros de leitura/gravação/revisão retornam código 1; argumentos inválidos, 2.
PDFs inválidos, corrompidos, ausentes e protegidos recebem mensagens sem conteúdo
ou caminho absoluto. Nesta etapa, **qualquer PDF criptografado é recusado**,
inclusive proteção com senha vazia; use uma cópia sem proteção obtida com autorização.

## Pré-laudo Word

Um passo só (extrai, grava a revisão JSON e gera o Word):

```bash
extrator-judicial pre-laudo entradas/processo.pdf --modelo previdenciario \
  --saida saidas/revisao-01.json --docx saidas/pre_laudo.docx --logo logo.png
```

Ou, após revisar e classificar (`--tipo previdenciaria|trabalhista|curatela`),
`exportar ... --docx saidas/pre_laudo.docx`; o modelo segue o tipo confirmado,
ou é escolhido com `--modelo`. `--json`/`--markdown`/`--docx` são combináveis.

Conteúdo do documento:

- Preâmbulo e tabela de identificação preenchidos com os candidatos, cada um
  com a folha de origem. Valores não revisados ou divergentes ficam **em
  amarelo com "(conferir)"**; ausentes viram `[preencher]`. Candidatos
  rejeitados são ignorados; confirmados/corrigidos têm prioridade.
- Síntese dos autos: pedidos e seções da inicial, **índice de páginas com
  possíveis documentos relevantes** (atestados, exames, CNIS, CAT, comunicação
  de decisão do INSS, CTPS, PPP; no modelo curatela, neurologia, testes
  cognitivos, estudo social), CID citados (com folhas) e datas para classificar.
- Dados específicos: laborais e previdenciários (espécie 31/91, CAT, afastamento,
  reabilitação), história ocupacional, ou dados sociais e temporalidade (curatela).
- **Exame físico direcionado pelos CID** dos autos (coluna, ombro, cotovelo,
  punho e mão, quadril, joelho, tornozelo e pé, neurológico, estado mental,
  cardiorrespiratório), com amplitudes de referência AAOS e manobras com o
  significado do achado positivo. Sem CID reconhecido, roteiro ortopédico geral.
  Curatela inclui MEEM (cortes de Brucki et al., 2003), MoCA, CDR, Pfeffer, Katz,
  Lawton e capacidades específicas para atos patrimoniais e negociais.
- Discussão com espaço para a análise do caso e **fundamentação de apoio**
  (Lei 8.213/1991, Decreto 3.048/1999, Tema 416 do STJ, Súmula 47 da TNU;
  Código Civil, Lei 13.146/2015, CPC arts. 753 e 755; Resolução CFM 2.323/2022),
  em linguagem simples e sem hífens/travessões na prosa. Conferir vigência.
- Conclusão como **roteiro de marcação**, sem resposta pré-definida; quesitos
  transcritos por origem (Juízo, autor, réu/INSS, Ministério Público), um a um,
  com "Resposta: [preencher]"; encerramento e referências.

Nada no Word é conclusão automática. Cabeçalho padrão embutido (`perfil.py`);
para outro perito ou para fixar logotipo e cidade, use `--perfil perfil.json`
(modelo em `docs/perfil_perito.exemplo.json`; `logo` relativo ao JSON).

## OCR

```bash
python -m pip install -e ".[ocr]"      # pypdfium2 (BSD-3-Clause / Apache-2.0)
# Tesseract com português: Ubuntu/Debian  sudo apt install tesseract-ocr tesseract-ocr-por
#                          macOS          brew install tesseract tesseract-lang
#                          Windows        instalador UB Mannheim, marcar "Portuguese"
extrator-judicial extrair entradas/processo.pdf --ocr --saida saidas/revisao-01.json
```

Só páginas **sem texto** passam por OCR (300 dpi, idioma `por`; ajustáveis com
`--ocr-dpi` e `--ocr-idioma`). Tudo é local. O texto e o motor/versão ficam na
revisão JSON; ao reabrir, o OCR **não é refeito**, e o texto registrado só é
aceito em páginas que de fato não têm texto no PDF. Candidatos dessas páginas
têm `fonte.texto_ocr = true` e avisos pedem conferência. No pré-laudo, CID lidos
por OCR com dígito no lugar da letra (ex.: `552.5` por `S52.5`) são recuperados e
marcados "(OCR, conferir)".

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
| `ocr.py` | OCR opcional (pypdfium2 + Tesseract local) e reaproveitamento validado |
| `pre_laudo.py` | Montagem do pré-laudo Word a partir dos candidatos revisados |
| `conteudo_pericial.py` | Roteiros de exame, índice documental, fundamentação e referências |
| `perfil.py` | Cabeçalho do perito (padrão embutido ou JSON) |
| `cli.py` | Comandos `extrair`, `listar`, `revisar`, `classificar`, `exportar`, `pre-laudo` (também `python -m extrator_judicial`) |

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
Revisões criadas antes de uma mudança nas regras de extração podem ser recusadas
na nova versão; nesse caso, extraia novamente.
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

Próximas entregas: motivo e doença alegada descritos em texto corrido na inicial,
inventário médico/CTPS, classificação humana das datas (emissão/atendimento/início alegado),
histórico e linha do tempo e interface visual local. Cargo não deve virar
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
