import pytest
from src.pedidos import Pedido, StatusPedido

# Checkpoint 8 minutos

def test_calculo_subtotal_e_peso_total():
    itens = [
        {"nome": "Teclado", "preco": 150.00, "quantidade": 1, "peso_kg": 0.8},
        {"nome": "Mousepad", "preco": 25.00, "quantidade": 2, "peso_kg": 0.2},
    ]
    pedido = Pedido(cliente_id="CLI01", itens=itens, cep_destino="80010-000")
    assert pedido.calcular_subtotal() == 200.00
    assert pedido.calcular_peso_total() == 1.200


def test_calculo_frete_com_peso_fracionario():
    itens = [
        {"nome": "Livro Técnico", "preco": 50.00, "quantidade": 1, "peso_kg": 2.4}
    ]
    # CEP 80010-000 pertence ao Sul (tarifa base 15.00)
    # Frete esperado: 15.00 + (2.4 * 3.50) = 15.00 + 8.40 = 23.40
    pedido = Pedido(cliente_id="CLI02", itens=itens, cep_destino="80010-000")
    assert pedido.calcular_frete() == pytest.approx(23.40, rel=1e-2)


def test_frete_gratis_considera_subtotal_liquido_apos_desconto():
    # Subtotal bruto: 220.00. Cupom: 30.00. Subtotal líquido: 190.00 (< 200.00)
    # Logo, NÃO deve ter frete grátis.
    itens = [
        {"nome": "Monitor", "preco": 110.00, "quantidade": 2, "peso_kg": 1.0}
    ]
    pedido = Pedido(cliente_id="CLI03", itens=itens, cep_destino="01310-100")  # Sudeste (base 12.00)
    cupom = {"codigo": "DESC30", "tipo": "fixo", "valor": 30.00, "minimo": 100.00}
    pedido.aplicar_cupom(cupom)

    # 12.00 + (2.0 * 3.50) = 19.00
    assert pedido.calcular_frete() == pytest.approx(19.00, rel=1e-2)


def test_frete_gratis_no_limite_exato_de_duzentos():
    itens = [
        {"nome": "Cadeira", "preco": 200.00, "quantidade": 1, "peso_kg": 5.0}
    ]
    pedido = Pedido(cliente_id="CLI04", itens=itens, cep_destino="01310-100")
    assert pedido.calcular_frete() == 0.0
    assert pedido.calcular_total() == 200.00


def test_lanca_erro_para_cep_com_formato_invalido():
    itens = [{"nome": "Mouse", "preco": 50.00, "quantidade": 1, "peso_kg": 0.3}]

    with pytest.raises(ValueError):
        Pedido(cliente_id="CLI05", itens=itens, cep_destino="1234")

    with pytest.raises(ValueError):
        Pedido(cliente_id="CLI05", itens=itens, cep_destino="80000-XYZ")


def test_lanca_erro_para_peso_ou_quantidade_invalida():
    itens_peso_negativo = [{"nome": "Item", "preco": 20.00, "quantidade": 1, "peso_kg": -0.5}]
    with pytest.raises(ValueError):
        Pedido(cliente_id="CLI06", itens=itens_peso_negativo, cep_destino="80010-000")

    itens_qtd_zero = [{"nome": "Item", "preco": 20.00, "quantidade": 0, "peso_kg": 1.0}]
    with pytest.raises(ValueError):
        Pedido(cliente_id="CLI06", itens=itens_qtd_zero, cep_destino="80010-000")


def test_aplicacao_cupom_no_limite_minimo_exato():
    itens = [{"nome": "Mochila", "preco": 100.00, "quantidade": 1, "peso_kg": 0.5}]
    pedido = Pedido(cliente_id="CLI07", itens=itens, cep_destino="80010-000")

    cupom = {"codigo": "VALE10", "tipo": "fixo", "valor": 10.00, "minimo": 100.00}
    pedido.aplicar_cupom(cupom)
    assert pedido.calcular_desconto() == 10.00


def test_rejeita_aplicacao_de_segundo_cupom():
    itens = [{"nome": "Headset", "preco": 150.00, "quantidade": 1, "peso_kg": 0.4}]
    pedido = Pedido(cliente_id="CLI08", itens=itens, cep_destino="80010-000")

    cupom1 = {"codigo": "PRIMEIRO", "tipo": "fixo", "valor": 10.00, "minimo": 50.00}
    cupom2 = {"codigo": "SEGUNDO", "tipo": "percentual", "valor": 5.0, "minimo": 50.00}

    pedido.aplicar_cupom(cupom1)
    with pytest.raises(ValueError):
        pedido.aplicar_cupom(cupom2)


def test_transicoes_validas_do_pedido():
    itens = [{"nome": "Suporte", "preco": 60.00, "quantidade": 1, "peso_kg": 0.6}]
    pedido = Pedido(cliente_id="CLI09", itens=itens, cep_destino="80010-000")

    assert pedido.status == StatusPedido.PENDENTE
    pedido.atualizar_status(StatusPedido.PAGO)
    assert pedido.status == StatusPedido.PAGO
    pedido.atualizar_status(StatusPedido.ENVIADO)
    assert pedido.status == StatusPedido.ENVIADO
    pedido.atualizar_status(StatusPedido.ENTREGUE)
    assert pedido.status == StatusPedido.ENTREGUE


def test_rejeita_transicao_invalida_enviado_para_cancelado():
    itens = [{"nome": "Webcam", "preco": 180.00, "quantidade": 1, "peso_kg": 0.3}]
    pedido = Pedido(cliente_id="CLI10", itens=itens, cep_destino="80010-000")

    pedido.atualizar_status(StatusPedido.PAGO)
    pedido.atualizar_status(StatusPedido.ENVIADO)

    with pytest.raises(ValueError):
        pedido.atualizar_status(StatusPedido.CANCELADO)
