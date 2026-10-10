"""JSON UTF-8 e gravação atômica por arquivo, exclusiva por padrão."""

import json
import os
import tempfile
from pathlib import Path

from .pdf import ErroExtrator


def carregar(caminho):
    try:
        with Path(caminho).open(encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (OSError, ValueError, RecursionError):
        raise ErroExtrator("Não foi possível abrir a revisão JSON UTF-8 válida.") from None


def json_texto(dados):
    return json.dumps(dados, ensure_ascii=False, indent=2) + "\n"


def salvar_arquivos(saidas, protegidos=(), sobrescrever=False):
    """Pré-valida o conjunto; não promete transação entre múltiplos arquivos."""
    caminhos = [Path(caminho) for caminho, _ in saidas]
    reservados = [Path(caminho).resolve() for caminho in protegidos]
    resolvidos = [caminho.resolve() for caminho in caminhos]
    if len(set(resolvidos)) != len(resolvidos):
        raise ErroExtrator("As saídas devem ter caminhos distintos.")
    for caminho, resolvido in zip(caminhos, resolvidos):
        if resolvido in reservados or any(
            caminho.exists() and p.exists() and os.path.samefile(caminho, p)
            for p in reservados
        ):
            raise ErroExtrator("Saída não pode substituir PDF ou revisão de entrada.")
        if caminho.is_symlink() or caminho.is_dir():
            raise ErroExtrator("Saída inválida: use arquivo regular, não link ou diretório.")
        if caminho.exists() and not sobrescrever:
            raise ErroExtrator("Saída já existe; escolha outro nome ou use --sobrescrever.")
        if not caminho.parent.is_dir():
            raise ErroExtrator("Diretório de saída não existe; crie-o antes.")
    temporarios = []
    try:
        for (caminho, texto) in saidas:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=Path(caminho).parent, delete=False
            ) as arquivo:
                temporarios.append(arquivo.name)
                arquivo.write(texto)
                arquivo.flush()
                os.fsync(arquivo.fileno())
        for caminho, temporario in zip(caminhos, temporarios):
            if sobrescrever:
                os.replace(temporario, caminho)
            else:
                # Link atômico falha se outro processo criou a saída após a pré-validação.
                os.link(temporario, caminho)
    except OSError:
        raise ErroExtrator(
            "Não foi possível gravar saída; confira permissões e arquivos existentes. "
            "Em exportação dupla, confira se alguma saída foi criada."
        ) from None
    finally:
        for temporario in temporarios:
            if os.path.exists(temporario):
                os.unlink(temporario)
