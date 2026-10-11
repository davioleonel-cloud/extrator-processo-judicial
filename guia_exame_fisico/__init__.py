"""
GUIA INTERATIVO DE EXAME FÍSICO ORTOPÉDICO
Interface para realizar e documentar exame físico ortopédico completo
com orientações passo a passo e checklist de testes
"""

from .tabelas_referencia import TABELAS_REFERENCIA, gerar_tabelas_referencia
from .testes import TestesOrtopedicos

__all__ = ["TestesOrtopedicos", "TABELAS_REFERENCIA", "gerar_tabelas_referencia"]
