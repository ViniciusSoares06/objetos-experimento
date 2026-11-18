import pytest
from src.pagamentos import TransacaoCartao, StatusTransacao, validar_cartao_credito


CARTAO_VALIDO_VISA = "4532015112830366"
CARTAO_INVALIDO_DIGITO = "4532015112830367"


def test_validacao_cartao_valido_luhn():
    assert validar_cartao_credito(CARTAO_VALIDO_VISA) is True
    assert validar_cartao_credito("4532 0151 1283 0366") is True


def test_recusa_cartao_invalido_luhn():
    # Cartão com dígito verificador incorreto deve ser recusado
    assert validar_cartao_credito(CARTAO_INVALIDO_DIGITO) is False


def test_recusa_cartao_com_caracteres_invalidos():
    with pytest.raises(ValueError):
        validar_cartao_credito("4532-0151-ABCD-0366")


def test_recusa_cartao_com_tamanho_invalido():
    with pytest.raises(ValueError):
        validar_cartao_credito("45320151")  # Apenas 8 dígitos


def test_pagamento_a_vista_sem_juros():
    transacao = TransacaoCartao(
        id_transacao="TX-101",
        valor=500.00,
        numero_cartao=CARTAO_VALIDO_VISA,
        parcelas=1
    )
    assert transacao.calcular_valor_parcela() == 500.00
    assert transacao.calcular_total_com_juros() == 500.00


def test_parcelamento_juros_simples_ate_6x():
    # 4 parcelas com juros simples de 1.5% ao mês:
    # Montante = 600 * (1 + 0.015 * 4) = 600 * 1.06 = 636.00
    # Parcela = 636.00 / 4 = 159.00
    transacao = TransacaoCartao(
        id_transacao="TX-102",
        valor=600.00,
        numero_cartao=CARTAO_VALIDO_VISA,
        parcelas=4
    )
    assert transacao.calcular_valor_parcela() == 159.00
    assert transacao.calcular_total_com_juros() == 636.00


def test_parcelamento_juros_compostos_acima_de_6x():
    # 10 parcelas com juros compostos de 2.0% ao mês:
    # Montante = 1000 * (1.02 ** 10) = 1218.9944...
    # Parcela esperada = round(1218.9944 / 10, 2) = 121.90
    transacao = TransacaoCartao(
        id_transacao="TX-103",
        valor=1000.00,
        numero_cartao=CARTAO_VALIDO_VISA,
        parcelas=10
    )
    assert transacao.calcular_valor_parcela() == 121.90
    assert transacao.calcular_total_com_juros() == 1219.00


def test_rejeita_parcelas_invalidas_fora_do_intervalo_1_a_12():
    with pytest.raises(ValueError):
        TransacaoCartao("TX-104", 300.00, CARTAO_VALIDO_VISA, parcelas=0)

    with pytest.raises(ValueError):
        TransacaoCartao("TX-105", 300.00, CARTAO_VALIDO_VISA, parcelas=13)


def test_rejeita_estorno_em_transacao_recusada():
    transacao = TransacaoCartao(
        id_transacao="TX-106",
        valor=200.00,
        numero_cartao=CARTAO_INVALIDO_DIGITO,
        parcelas=1
    )
    with pytest.raises(ValueError):
        transacao.autorizar()

    assert transacao.status == StatusTransacao.RECUSADA
    with pytest.raises(ValueError):
        transacao.estornar(100.00)


def test_rejeita_estornos_acumulados_que_excedem_total_ou_valor_negativo():
    transacao = TransacaoCartao(
        id_transacao="TX-107",
        valor=600.00,
        numero_cartao=CARTAO_VALIDO_VISA,
        parcelas=4
    )
    transacao.autorizar()
    total = transacao.calcular_total_com_juros()  # 636.00

    # Estorno negativo deve ser rejeitado
    with pytest.raises(ValueError):
        transacao.estornar(-10.00)

    # Primeiro estorno parcial de 400.00 (resta 236.00)
    transacao.estornar(400.00)
    assert transacao.status == StatusTransacao.ESTORNADA_PARCIAL

    # Segundo estorno de 300.00 excede o total (400 + 300 = 700 > 636)
    with pytest.raises(ValueError):
        transacao.estornar(300.00)
