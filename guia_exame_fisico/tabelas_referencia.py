"""Tabelas de referência ortopédica exibidas na aba de referências."""

TABELAS_REFERENCIA = """
╔════════════════════════════════════════════════════════════════════════════╗
║                     TABELAS DE REFERÊNCIA ORTOPÉDICA                       ║
╚════════════════════════════════════════════════════════════════════════════╝

1. ESCALA DE FORÇA MUSCULAR (Grau 0-5)
═══════════════════════════════════════════════════════════════════════════

Grau 0: Sem contração muscular visível ou palpável
Grau 1: Contração palpável do músculo sem movimento articular
Grau 2: Movimento ativo apenas sem efeito da gravidade
Grau 3: Movimento contra efeito da gravidade
Grau 4: Movimento contra resistência parcial
Grau 5: Movimento contra resistência completa (força normal)


2. AMPLITUDE DE MOVIMENTO - PUNHO
═══════════════════════════════════════════════════════════════════════════

Flexão Palmar:              0-80°
Extensão:                   0-70°
Abducção (Radial):          0-20°
Adducção (Ulnar):           0-35°
Pronação:                   0-80°
Supinação:                  0-80°


3. AMPLITUDE DE MOVIMENTO - COTOVELO
═══════════════════════════════════════════════════════════════════════════

Flexão:                     0-150°
Extensão:                   0° (posição neutra)
Pronação:                   0-80°
Supinação:                  0-80°


4. AMPLITUDE DE MOVIMENTO - OMBRO
═══════════════════════════════════════════════════════════════════════════

Abdução:                    0-180°
Adducção:                   0-45°
Flexão:                     0-180°
Extensão:                   0-45°
Rotação Interna:            0-70°
Rotação Externa:            0-90°


5. FORÇA DE PREENSÃO (Dinamômetro de Mão)
═══════════════════════════════════════════════════════════════════════════

Homens:                     35-60 kg
Mulheres:                   20-40 kg

Nota: A mão dominante é normalmente 10% mais forte


6. FORÇA DE PINÇA (Pinçômetro)
═══════════════════════════════════════════════════════════════════════════

Normal:                     8-12 kg
Importante para: Trabalhos de precisão


7. CLASSIFICAÇÃO DE SENSIBILIDADE (Monofilamento)
═══════════════════════════════════════════════════════════════════════════

Filamento 2.83:             Normal
Filamento 4.31:             Diminuída
Filamento 6.65:             Diminuída profundamente
Não sente 6.65:             Perda severa de sensibilidade


8. DISCRIMINAÇÃO DE DOIS PONTOS
═══════════════════════════════════════════════════════════════════════════

Polpa digital:              2-3 mm
Palma:                      8-10 mm
Dorso da mão:               20-30 mm
Dorso do antebraço:         30-40 mm


9. TESTES CLÁSSICOS - SENSIBILIDADE E ESPECIFICIDADE
═══════════════════════════════════════════════════════════════════════════

Teste de Tinnel:            Sensibilidade: 72-95%    Especificidade: 95%
Teste de Phalen:            Sensibilidade: 51-93%    Especificidade: 95-98%
Teste de Lachman:           Sensibilidade: 72-98%    Especificidade: 96-99%
Teste de Apprehension:      Sensibilidade: 50-72%    Especificidade: 96-98%


10. COMPARAÇÃO BILATERAL
═══════════════════════════════════════════════════════════════════════════

Redução de força > 10% é considerada significativa
Sempre comparar o lado afetado com o contralateral
Registrar assimetrias


11. ESCALA DE DOR (VAS - Visual Analogue Scale)
═══════════════════════════════════════════════════════════════════════════

0-10:       Sem dor
11-20:      Dor leve
21-40:      Dor moderada
41-70:      Dor severa
71-100:     Dor máxima intolerável


12. CLASSIFICAÇÃO DE EDEMA
═══════════════════════════════════════════════════════════════════════════

0: Ausente
+1: Leve (depressão rápida após pressão)
+2: Moderado (depressão após 2-3 segundos)
+3: Grave (depressão após 4-5 segundos)
+4: Muito grave (pouca ou nenhuma depressão)


13. TESTE DE AMPLITUDE PASSIVA VS ATIVA
═══════════════════════════════════════════════════════════════════════════

Se amplitude ativa < amplitude passiva:
  → Fraqueza muscular
  
Se amplitude ativa = amplitude passiva:
  → Contraturas, rigidez articular ou limitação estrutural

Se amplitude passiva é dolorosa:
  → Inflamação, sinovite ou possível lesão


14. COMPARAÇÃO DE ESTRUTURAS BILATERALMENTE
═══════════════════════════════════════════════════════════════════════════

SEMPRE compare:
• Amplitude de movimento
• Força muscular
• Sensibilidade
• Volume/edema
• Temperatura
• Cor da pele
• Presença de cicatrizes ou deformidades


15. DOCUMENTAÇÃO ADEQUADA
═══════════════════════════════════════════════════════════════════════════

Registre:
✓ Localização exata da lesão
✓ Amplitude encontrada (não apenas "limitado")
✓ Força: grau específico 0-5
✓ Presença/ausência de dor
✓ Comparação bilateral
✓ Achados anormais
✓ Testes positivos ou negativos
✓ Impressão clínica
✓ Recomendações (exames adicionais, etc.)


═════════════════════════════════════════════════════════════════════════════

                    "EXAME COMPLETO E BEM DOCUMENTADO
                     É FUNDAMENTAL PARA DIAGNÓSTICO PRECISO"
                                                                    
═════════════════════════════════════════════════════════════════════════════
"""


def gerar_tabelas_referencia() -> str:
    """Gera tabelas de referência"""
    return TABELAS_REFERENCIA
