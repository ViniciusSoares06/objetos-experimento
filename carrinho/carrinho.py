def adicionar(carrinho, codigo, preco, quantidade):
    if codigo in carrinho:
        preco_atual, quantidade_atual = carrinho[codigo]
        carrinho[codigo] = (preco_atual, quantidade)
    else:
        carrinho[codigo] = (preco, quantidade)


def atualizar_quantidade(carrinho, codigo, quantidade):
    if quantidade < 0:
        del carrinho[codigo]
    else:
        preco, _ = carrinho[codigo]
        carrinho[codigo] = (preco, quantidade)


def total(carrinho):
    return sum(preco for preco, quantidade in carrinho.values())
