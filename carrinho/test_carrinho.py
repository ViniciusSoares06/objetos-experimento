from carrinho import adicionar, atualizar_quantidade, total


def test_adicionar_produto_novo():
    carrinho = {}
    adicionar(carrinho, "A", 450, 2)
    assert carrinho == {"A": (450, 2)}


def test_adicionar_produto_existente():
    carrinho = {"A": (450, 2)}
    adicionar(carrinho, "A", 500, 3)
    assert carrinho == {"A": (450, 5)}


def test_substituir_quantidade():
    carrinho = {"A": (450, 2)}
    atualizar_quantidade(carrinho, "A", 3)
    assert carrinho == {"A": (450, 3)}


def test_quantidade_zero_remove_produto():
    carrinho = {"A": (450, 2), "B": (120, 1)}
    atualizar_quantidade(carrinho, "A", 0)
    assert carrinho == {"B": (120, 1)}


def test_total_vazio():
    assert total({}) == 0


def test_total_com_varias_unidades():
    assert total({"A": (450, 3), "B": (120, 1)}) == 1470
