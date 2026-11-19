"""Interface local em português, sem logs documentais."""

import argparse
import sys

from .extracao import extrair
from .modelos import TIPOS_PERICIA
from .ocr import DPI_PADRAO, IDIOMA_PADRAO, aplicar_ocr, incorporar_ocr
from .pdf import ErroExtrator, ler_pdf
from .perfil import carregar_perfil
from .persistencia import carregar, json_texto, salvar_arquivos
from .pre_laudo import MODELO_POR_TIPO, MODELOS, gerar_pre_laudo
from .relatorios import exportacao
from .revisao import classificar, revisar, validar


class ParserPortugues(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._positionals.title = "argumentos posicionais"
        self._optionals.title = "opções"

    def format_usage(self):
        return super().format_usage().replace("usage:", "uso:", 1)

    def format_help(self):
        return super().format_help().replace("usage:", "uso:", 1)

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, "Erro: argumentos inválidos. Consulte --help.\n")


def parser():
    raiz = ParserPortugues(
        description="Extrator judicial local — candidatos documentais para revisão.",
        add_help=False,
    )
    raiz.add_argument("-h", "--help", action="help", help="mostrar ajuda e sair")
    comandos = raiz.add_subparsers(dest="comando", required=True, title="comandos")
    for nome, ajuda in (
        ("extrair", "ler exatamente um PDF e salvar candidatos"),
        ("revisar", "confirmar, corrigir ou rejeitar candidato"),
        ("classificar", "confirmar manualmente tipo e objeto da perícia"),
        ("exportar", "exportar JSON e Markdown de rascunho"),
        ("listar", "listar IDs, campos e estados, sem conteúdo documental"),
        ("pre-laudo", "extrair e gerar de uma vez a revisão JSON e o pré-laudo Word"),
    ):
        comando = comandos.add_parser(nome, help=ajuda, description=ajuda, add_help=False)
        comando.add_argument("-h", "--help", action="help", help="mostrar ajuda e sair")
        comando.add_argument("pdf", help="caminho local de um único PDF")
        if nome != "listar":
            comando.add_argument("--sobrescrever", action="store_true", help="substituir saídas explicitamente")
        if nome not in ("extrair", "pre-laudo"):
            comando.add_argument("--revisao", required=True, help="JSON de revisão a reabrir")
        if nome in ("extrair", "pre-laudo"):
            comando.add_argument("--ocr", action="store_true",
                                 help="ler por OCR (Tesseract local) as páginas sem texto")
            comando.add_argument("--ocr-idioma", default=IDIOMA_PADRAO, help="idioma do Tesseract (padrão: por)")
            comando.add_argument("--ocr-dpi", type=int, default=DPI_PADRAO, help="resolução do OCR (padrão: 300)")
        if nome == "listar":
            continue
        if nome == "exportar":
            comando.add_argument("--json", help="saída JSON estruturada")
            comando.add_argument("--markdown", help="saída Markdown editável")
        if nome in ("exportar", "pre-laudo"):
            comando.add_argument("--docx", required=nome == "pre-laudo", help="saída Word do pré-laudo")
            comando.add_argument("--modelo", choices=MODELOS,
                                 help="modelo do pré-laudo; padrão: conforme o tipo de perícia confirmado")
            comando.add_argument("--perfil", help="JSON com cabeçalho do perito (padrão: perfil embutido)")
            comando.add_argument("--logo", help="logotipo PNG/JPEG do cabeçalho (altura 90 px)")
        if nome != "exportar":
            comando.add_argument("--saida", required=True, help="novo arquivo JSON de revisão")
        if nome == "revisar":
            comando.add_argument("--candidato", required=True, help="identificador, por exemplo c0001")
            comando.add_argument("--acao", required=True, choices=["confirmar", "corrigir", "rejeitar"])
            comando.add_argument("--valor", help="novo valor para correção; preserva o original")
        if nome == "classificar":
            comando.add_argument("--tipo", required=True, choices=list(TIPOS_PERICIA))
            comando.add_argument("--objeto", required=True, help="objeto específico informado pelo perito")
    return raiz


def listagem(dados):
    """Somente metadados de revisão: nunca valores, trechos ou nomes."""
    linhas = [f'{"ID":<6} {"campo":<16} {"estado":<10} {"origem":<10} página']
    for candidato in dados["candidatos"]:
        linhas.append(
            f'{candidato["id"]:<6} {candidato["campo"]:<16} {candidato["estado"]:<10} '
            f'{candidato["origem"]:<10} {candidato["fonte"]["pagina"]}'
        )
    linhas.append(f'Tipo de perícia: {dados["pericia"]["tipo"]}.')
    linhas.append(f'Pendências: {len(dados["pendencias"])}. Valores e trechos: consulte o JSON local.')
    return "\n".join(linhas)


def _modelo(argumentos, dados):
    if argumentos.modelo:
        return argumentos.modelo
    if dados["pericia"]["tipo"] in MODELO_POR_TIPO:
        return MODELO_POR_TIPO[dados["pericia"]["tipo"]]
    raise ErroExtrator("Informe --modelo (previdenciario, trabalhista ou curatela) ou confirme o tipo da perícia.")


def _docx(argumentos, dados):
    perfil = carregar_perfil(argumentos.perfil)
    return gerar_pre_laudo(dados, _modelo(argumentos, dados), perfil, argumentos.logo)


def main(argv=None):
    argumentos = parser().parse_args(argv)
    try:
        if argumentos.comando == "exportar" and not (argumentos.json or argumentos.markdown or argumentos.docx):
            raise ErroExtrator("Informe ao menos uma saída: --json, --markdown ou --docx.")
        if argumentos.comando in ("extrair", "pre-laudo") and not 70 <= argumentos.ocr_dpi <= 600:
            raise ErroExtrator("Resolução de OCR deve estar entre 70 e 600 dpi.")
        documento, paginas = ler_pdf(argumentos.pdf)
        protegidos = [argumentos.pdf]
        if argumentos.comando in ("extrair", "pre-laudo"):
            if argumentos.ocr:
                aplicar_ocr(argumentos.pdf, paginas, argumentos.ocr_idioma, argumentos.ocr_dpi)
            dados = extrair(documento, paginas)
        else:
            protegidos.append(argumentos.revisao)
            revisao = carregar(argumentos.revisao)
            dados = extrair(documento, incorporar_ocr(paginas, revisao))
            dados = validar(revisao, dados)
        if argumentos.comando == "revisar":
            revisar(dados, argumentos.candidato, argumentos.acao, argumentos.valor)
        elif argumentos.comando == "classificar":
            classificar(dados, argumentos.tipo, argumentos.objeto)
        elif argumentos.comando == "listar":
            print(listagem(dados))
            return 0
        if argumentos.comando == "exportar":
            texto_json, texto_markdown = exportacao(dados)
            saidas = [(caminho, conteudo) for caminho, conteudo in (
                (argumentos.json, texto_json), (argumentos.markdown, texto_markdown),
            ) if caminho]
            if argumentos.docx:
                saidas.append((argumentos.docx, _docx(argumentos, dados)))
        elif argumentos.comando == "pre-laudo":
            saidas = [(argumentos.saida, json_texto(dados)), (argumentos.docx, _docx(argumentos, dados))]
        else:
            saidas = [(argumentos.saida, json_texto(dados))]
        salvar_arquivos(saidas, protegidos, argumentos.sobrescrever)
    except ErroExtrator as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    except (OSError, RuntimeError):
        print("Erro: não foi possível acessar os caminhos locais informados.", file=sys.stderr)
        return 1
    print("Resultado local salvo. RASCUNHO — REVISÃO NECESSÁRIA.")
    return 0
