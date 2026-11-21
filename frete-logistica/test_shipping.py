"""Suíte de testes automatizados para validação do módulo shipping.py.

AVISO AOS PARTICIPANTES:
ESTE ARQUIVO É UMA SUÍTE DE TESTES IMUTÁVEL.
NÃO EDITE NEM ALTERE NENHUMA LINHA OU TESTE DESTE ARQUIVO.
TODA A DEPURAÇÃO DEVE SER REALIZADA EXCLUSIVAMENTE NO ARQUIVO shipping.py.
"""

import pytest
from shipping import (
    calcular_acrescimo_peso,
    calcular_frete_e_prazo,
    calcular_peso_tarifavel,
    identificar_regiao,
    verificar_elegibilidade_frete_gratis,
)


def test_identificar_regiao_e_tarifas_padrao():
    """Valida a identificação correta de região e tarifa base por CEP."""
    # CEP de São Paulo (Sudeste: 01000-000 até 39999-999)
    regiao, tarifa, prazo = identificar_regiao("01310-100")
    assert regiao == "SUDESTE"
    assert tarifa == 15.00
    assert prazo == 4

    # CEP de Porto Alegre (Sul: 80000-000 até 99999-999)
    regiao, tarifa, prazo = identificar_regiao("90010-150")
    assert regiao == "SUL"
    assert tarifa == 20.00
    assert prazo == 6


def test_calculo_peso_tarifavel_real_vs_volumetrico():
    """Valida o cálculo do peso tarifável selecionando o maior valor entre real e volumétrico."""
    # Dimensões 30x20x10 cm = 6000 cm³ -> peso volumétrico = 6000 / 6000 = 1.0 kg
    # Caso 1: peso real (2.5 kg) maior que volumétrico (1.0 kg)
    peso_calc = calcular_peso_tarifavel(2.5, 30.0, 20.0, 10.0)
    assert peso_calc == 2.5

    # Caso 2: peso volumétrico (50x40x30 / 6000 = 10.0 kg) maior que real (3.0 kg)
    peso_calc_vol = calcular_peso_tarifavel(3.0, 50.0, 40.0, 30.0)
    assert peso_calc_vol == 10.0


def test_elegibilidade_frete_gratis_limites():
    """Valida as regras de negócio para concessão de frete grátis (limiar de R$ 250,00)."""
    # Pedido abaixo do limite: NÃO elegível
    assert not verificar_elegibilidade_frete_gratis(249.90)

    # Pedido exatamente no limite: ELEGÍVEL
    assert verificar_elegibilidade_frete_gratis(250.00)

    # Pedido acima do limite: ELEGÍVEL
    assert verificar_elegibilidade_frete_gratis(350.00)


def test_acrescimo_por_peso_excedente_fracionado():
    """Valida a cobrança proporcional de peso adicional acima da franquia de 1 kg.

    Franquia: 1.0 kg gratuito. Adicional: R$ 2,50 por kg excedente.
    Para 3.4 kg tarifáveis: excedente de 2.4 kg * R$ 2,50 = R$ 6,00.
    """
    # Sem excedente (<= 1.0 kg)
    assert calcular_acrescimo_peso(1.0) == 0.00
    assert calcular_acrescimo_peso(0.8) == 0.00

    # Excedente fracionado: 3.4 kg -> 2.4 kg excedente * 2.50 = 6.00
    assert calcular_acrescimo_peso(3.4) == 6.00


def test_frete_economico_com_gratuidade_aplicada():
    """Valida cálculo completo para entrega econômica com pedido acima de R$ 250,00."""
    resultado = calcular_frete_e_prazo(
        cep_destino="01310-100",  # Sudeste
        valor_pedido=300.00,
        peso_kg=2.0,
        dimensoes_cm=(20.0, 20.0, 15.0),
        modalidade="economico",
    )

    assert resultado["regiao"] == "SUDESTE"
    assert resultado["modalidade"] == "economico"
    assert resultado["frete_gratis"] is True
    assert resultado["valor_frete"] == 0.00
    assert resultado["prazo_dias"] == 4


def test_frete_expresso_sul_prazo_e_tarifa():
    """Valida acréscimo tarifário e prazo em entrega expressa para a região Sul."""
    # Sul: base R$ 20.00 * 1.5 = R$ 30.00. Prazo: 6 - 2 = 4 dias.
    resultado = calcular_frete_e_prazo(
        cep_destino="80010-000",  # Sul (Curitiba)
        valor_pedido=120.00,
        peso_kg=1.0,
        dimensoes_cm=(15.0, 10.0, 10.0),
        modalidade="expresso",
    )

    assert resultado["regiao"] == "SUL"
    assert resultado["modalidade"] == "expresso"
    assert resultado["valor_frete"] == 30.00
    assert resultado["prazo_dias"] == 4
    assert resultado["frete_gratis"] is False


def test_frete_expresso_sudeste_prazo_reduzido():
    """Valida que frete expresso para Sudeste reduz o prazo em 2 dias."""
    # Sudeste: base 4 dias -> expresso deve ser 2 dias (4 - 2).
    resultado = calcular_frete_e_prazo(
        cep_destino="04571-010",  # Sudeste (SP)
        valor_pedido=100.00,
        peso_kg=1.0,
        dimensoes_cm=(15.0, 15.0, 10.0),
        modalidade="expresso",
    )

    assert resultado["regiao"] == "SUDESTE"
    assert resultado["modalidade"] == "expresso"
    assert resultado["prazo_dias"] == 2


def test_excecao_para_cep_invalido():
    """Valida tratamento de exceção para formatos de CEP inválidos."""
    with pytest.raises(ValueError):
        calcular_frete_e_prazo(
            cep_destino="123",
            valor_pedido=100.00,
            peso_kg=1.0,
            dimensoes_cm=(10.0, 10.0, 10.0),
        )
