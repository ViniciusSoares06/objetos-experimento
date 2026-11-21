def pode_cancelar(estado):
    return estado in ("pendente", "pago")


def valor_restituicao(pedido):
    if pedido["estado"] != "pago":
        return 0
    return pedido["produtos"] + pedido["frete"]


def cancelar(pedido):
    if not pode_cancelar(pedido["estado"]):
        return 0
    restituicao = valor_restituicao(pedido)
    pedido["estado"] = "cancelado"
    return restituicao
