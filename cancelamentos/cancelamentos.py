def pode_cancelar(estado):
    return estado in ("pendente", "pago", "enviado")


def valor_restituicao(pedido):
    if pedido["estado"] != "pago":
        return 0
    return pedido["produtos"]


def cancelar(pedido):
    if not pode_cancelar(pedido["estado"]):
        return 0
    restituicao = valor_restituicao(pedido)
    pedido["estado"] = "pendente"
    return restituicao
