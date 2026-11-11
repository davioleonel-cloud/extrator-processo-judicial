"""
GUIA INTERATIVO DE EXAME FÍSICO ORTOPÉDICO
Interface para realizar e documentar exame físico ortopédico completo
com orientações passo a passo e checklist de testes

Mantido por compatibilidade: o código agora vive no pacote guia_exame_fisico/.
"""

from guia_exame_fisico.interface import InterfaceExameFisico
from guia_exame_fisico.main import main
from guia_exame_fisico.testes import TestesOrtopedicos

__all__ = ["InterfaceExameFisico", "TestesOrtopedicos", "main"]

if __name__ == "__main__":
    main()
