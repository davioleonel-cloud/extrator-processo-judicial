"""Agrupa as bases de testes ortopédicos em uma única classe de consulta."""

from .dados_amplitude import TESTES_AMPLITUDE
from .dados_forca import TESTES_FORCA
from .dados_sensibilidade import TESTES_SENSIBILIDADE
from .dados_testes_especiais import TESTES_ESPECIAIS


class TestesOrtopedicos:
    """Base de dados de testes ortopédicos com instruções"""

    TESTES_AMPLITUDE = TESTES_AMPLITUDE
    TESTES_ESPECIAIS = TESTES_ESPECIAIS
    TESTES_FORCA = TESTES_FORCA
    TESTES_SENSIBILIDADE = TESTES_SENSIBILIDADE
