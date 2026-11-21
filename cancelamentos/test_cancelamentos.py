from cancelamentos import cancelar, pode_cancelar, valor_restituicao


def test_pedido_pago_pode_ser_cancelado():
    assert pode_cancelar("pago")


def test_pedido_enviado_nao_pode_ser_cancelado():
    assert not pode_cancelar("enviado")


def test_pedido_pendente_nao_tem_restituicao():
    pedido = {"estado": "pendente", "produtos": 900, "frete": 100}
    assert valor_restituicao(pedido) == 0


def test_pedido_pago_restitui_produtos_e_frete():
    pedido = {"estado": "pago", "produtos": 900, "frete": 100}
    assert valor_restituicao(pedido) == 1000


def test_cancelamento_preserva_pedido_ja_cancelado():
    pedido = {"estado": "cancelado", "produtos": 900, "frete": 100}
    assert cancelar(pedido) == 0
    assert pedido == {"estado": "cancelado", "produtos": 900, "frete": 100}


def test_cancelamento_atualiza_estado():
    pedido = {"estado": "pago", "produtos": 900, "frete": 0}
    assert cancelar(pedido) == 900
    assert pedido["estado"] == "cancelado"
