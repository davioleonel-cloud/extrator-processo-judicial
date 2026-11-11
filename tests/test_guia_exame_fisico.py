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


def test_aba_sensibilidade_exibe_referencias_e_interpretacao():
    from guia_exame_fisico.formatacao import formatar_testes_sensibilidade

    testes = TestesOrtopedicos.TESTES_SENSIBILIDADE
    texto = formatar_testes_sensibilidade(testes)
    dois_pontos = testes['Teste de Discriminação de Dois Pontos']
    assert f"Normal (polpa digital): {dois_pontos['normal_polpa_digital']}" in texto
    assert f"Normal (dorso da mão): {dois_pontos['normal_dorso_mao']}" in texto
    for teste in testes.values():
        assert teste['interpretacao'] in texto
        for passo in teste['passos']:
            assert passo in texto


def test_aba_sensibilidade_omite_referencias_ausentes():
    from guia_exame_fisico.formatacao import formatar_testes_sensibilidade

    texto = formatar_testes_sensibilidade(
        {'Teste X': {'descricao': 'd', 'material': 'm', 'passos': ['1. p']}})
    assert 'VALORES DE REFERÊNCIA' not in texto
    assert 'INTERPRETAÇÃO' not in texto


def test_todos_os_testes_especiais_renderizam():
    """Regressão: o teste de rotação interna não tem 'positivo' e dava KeyError."""
    from guia_exame_fisico.formatacao import formatar_teste_especial

    for nome, teste in TestesOrtopedicos.TESTES_ESPECIAIS.items():
        texto = formatar_teste_especial(nome, teste)
        assert nome.upper() in texto
        for passo in teste['passos']:
            assert passo in texto


def test_todos_os_testes_de_amplitude_e_forca_renderizam():
    from guia_exame_fisico.formatacao import formatar_teste_amplitude, formatar_teste_forca

    for nome, teste in TestesOrtopedicos.TESTES_AMPLITUDE.items():
        assert teste['normal'] in formatar_teste_amplitude(nome, teste)
    for nome, teste in TestesOrtopedicos.TESTES_FORCA.items():
        texto = formatar_teste_forca(nome, teste)
        assert teste['descricao'] in texto
        for passo in teste['passos']:
            assert passo in texto


def test_resumo_lista_dados_coletados():
    from datetime import datetime
    from guia_exame_fisico.formatacao import formatar_resumo

    texto = formatar_resumo({'Força': [{'teste': 'Cotovelo - Flexor', 'grau': '4'}]},
                            datetime(2026, 11, 10, 23, 0))
    assert '10/11/2026 23:00' in texto
    assert 'teste: Cotovelo - Flexor' in texto


def test_nome_do_teste_de_tinel():
    assert any('Tinel' in n and 'Tinnel' not in n for n in TestesOrtopedicos.TESTES_ESPECIAIS)
