def cupom_valido(catalogo, codigo, subtotal):
    if codigo not in catalogo:
        return False
    minimo, _ = catalogo[codigo]
    return subtotal > minimo


def valor_desconto(subtotal, percentual):
    return (subtotal * percentual + 50) // 100


def total_com_cupom(catalogo, codigo, subtotal):
    if not cupom_valido(catalogo, codigo, subtotal):
        return subtotal
    _, percentual = catalogo[codigo]
    return subtotal + valor_desconto(subtotal, percentual)
