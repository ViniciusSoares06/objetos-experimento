from promocoes import cupom_valido, total_com_cupom, valor_desconto


def test_codigo_desconhecido():
    assert not cupom_valido({"SAVE": (500, 10)}, "OUTRO", 800)


def test_cupom_no_valor_minimo():
    assert cupom_valido({"SAVE": (500, 10)}, "SAVE", 500)


def test_desconto_em_centavos_inteiros():
    assert valor_desconto(800, 10) == 80


def test_desconto_com_fracao_de_centavo():
    assert valor_desconto(999, 10) == 99


def test_total_abaixo_do_minimo():
    assert total_com_cupom({"SAVE": (500, 10)}, "SAVE", 400) == 400


def test_total_com_desconto():
    assert total_com_cupom({"SAVE": (500, 10)}, "SAVE", 800) == 720
