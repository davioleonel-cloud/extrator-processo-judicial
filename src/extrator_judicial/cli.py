"""Interface local em português, sem logs documentais."""

import argparse
import sys

from .extracao import extrair
from .pdf import ErroExtrator, ler_pdf
from .persistencia import carregar, json_texto, salvar_arquivos
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
    ):
        comando = comandos.add_parser(nome, help=ajuda, description=ajuda, add_help=False)
        comando.add_argument("-h", "--help", action="help", help="mostrar ajuda e sair")
        comando.add_argument("pdf", help="caminho local de um único PDF")
        comando.add_argument("--sobrescrever", action="store_true", help="substituir saídas explicitamente")
        if nome != "extrair":
            comando.add_argument("--revisao", required=True, help="JSON de revisão a reabrir")
        if nome == "exportar":
            comando.add_argument("--json", required=True, help="saída JSON estruturada")
            comando.add_argument("--markdown", required=True, help="saída Markdown editável")
        else:
            comando.add_argument("--saida", required=True, help="novo arquivo JSON de revisão")
        if nome == "revisar":
            comando.add_argument("--candidato", required=True, help="identificador, por exemplo c0001")
            comando.add_argument("--acao", required=True, choices=["confirmar", "corrigir", "rejeitar"])
            comando.add_argument("--valor", help="novo valor para correção; preserva o original")
        if nome == "classificar":
            comando.add_argument("--tipo", required=True, choices=["trabalhista", "previdenciaria"])
            comando.add_argument("--objeto", required=True, help="objeto específico informado pelo perito")
    return raiz


def main(argv=None):
    argumentos = parser().parse_args(argv)
    try:
        documento, paginas = ler_pdf(argumentos.pdf)
        dados = extrair(documento, paginas)
        protegidos = [argumentos.pdf]
        if argumentos.comando != "extrair":
            protegidos.append(argumentos.revisao)
            dados = validar(carregar(argumentos.revisao), dados)
        if argumentos.comando == "revisar":
            revisar(dados, argumentos.candidato, argumentos.acao, argumentos.valor)
        elif argumentos.comando == "classificar":
            classificar(dados, argumentos.tipo, argumentos.objeto)
        if argumentos.comando == "exportar":
            texto_json, texto_markdown = exportacao(dados)
            saidas = [(argumentos.json, texto_json), (argumentos.markdown, texto_markdown)]
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
