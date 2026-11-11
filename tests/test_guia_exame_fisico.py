from guia_exame_fisico import TestesOrtopedicos, gerar_tabelas_referencia


def test_bases_de_testes_carregadas():
    assert len(TestesOrtopedicos.TESTES_AMPLITUDE) == 10
    assert len(TestesOrtopedicos.TESTES_ESPECIAIS) == 7
    assert len(TestesOrtopedicos.TESTES_FORCA) == 4
    assert len(TestesOrtopedicos.TESTES_SENSIBILIDADE) == 2


def test_campos_usados_pela_interface():
    for teste in TestesOrtopedicos.TESTES_AMPLITUDE.values():
        for campo in ('descricao', 'normal', 'posicao_paciente', 'posicao_examinador',
                      'referencia_anatomica', 'passos'):
            assert campo in teste
    for teste in TestesOrtopedicos.TESTES_SENSIBILIDADE.values():
        assert {'descricao', 'material', 'passos'} <= teste.keys()


def test_tabelas_referencia():
    tabelas = gerar_tabelas_referencia()
    assert 'TABELAS DE REFERÊNCIA ORTOPÉDICA' in tabelas
    assert '15. DOCUMENTAÇÃO ADEQUADA' in tabelas
