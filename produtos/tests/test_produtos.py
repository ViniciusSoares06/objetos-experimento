import pytest
from src.produtos import Produto, CatalogoEstoque


def test_cadastro_produto_com_sucesso():
    catalogo = CatalogoEstoque()
    prod = Produto("INF-001", "Mouse Óptico", "INFORMATICA", 50.00, 10, 5, 50)
    catalogo.cadastrar_produto(prod)
    assert "INF-001" in catalogo.produtos
    assert catalogo.produtos["INF-001"].nome == "Mouse Óptico"


def test_rejeita_cadastro_com_sku_duplicado():
    catalogo = CatalogoEstoque()
    p1 = Produto("INF-001", "Mouse Óptico", "INFORMATICA", 50.00, 10, 5, 50)
    p2 = Produto("INF-001", "Mouse Gamer", "INFORMATICA", 90.00, 5, 2, 20)

    catalogo.cadastrar_produto(p1)
    with pytest.raises(ValueError):
        catalogo.cadastrar_produto(p2)


def test_rejeita_preco_ou_quantidade_negativos():
    with pytest.raises(ValueError):
        Produto("INF-002", "Teclado", "INFORMATICA", -10.00, 5, 2, 20)

    with pytest.raises(ValueError):
        Produto("INF-003", "Teclado", "INFORMATICA", 80.00, -3, 2, 20)


def test_rejeita_estoque_maximo_menor_ou_igual_ao_minimo():
    # estoque_maximo não pode ser menor nem igual ao estoque_minimo
    with pytest.raises(ValueError):
        Produto("INF-004", "Webcam", "INFORMATICA", 120.00, 10, 15, 10)

    with pytest.raises(ValueError):
        Produto("INF-005", "Webcam", "INFORMATICA", 120.00, 10, 15, 15)


def test_adicionar_estoque_com_sucesso():
    catalogo = CatalogoEstoque()
    prod = Produto("INF-006", "Headset", "INFORMATICA", 150.00, 5, 2, 30)
    catalogo.cadastrar_produto(prod)

    novo_saldo = catalogo.adicionar_estoque("INF-006", 10)
    assert novo_saldo == 15
    assert catalogo.produtos["INF-006"].quantidade == 15


def test_rejeita_adicionar_estoque_acima_do_maximo():
    catalogo = CatalogoEstoque()
    prod = Produto("INF-007", "Monitor", "INFORMATICA", 800.00, 8, 2, 10)
    catalogo.cadastrar_produto(prod)

    with pytest.raises(ValueError):
        catalogo.adicionar_estoque("INF-007", 5)  # 8 + 5 = 13 > 10


def test_remover_estoque_com_sucesso():
    catalogo = CatalogoEstoque()
    prod = Produto("INF-008", "Cabo HDMI", "INFORMATICA", 25.00, 20, 5, 50)
    catalogo.cadastrar_produto(prod)

    novo_saldo = catalogo.remover_estoque("INF-008", 7)
    assert novo_saldo == 13
    assert catalogo.produtos["INF-008"].quantidade == 13


def test_rejeita_remover_estoque_insuficiente_saldo_negativo():
    catalogo = CatalogoEstoque()
    prod = Produto("INF-009", "Pen Drive", "INFORMATICA", 30.00, 4, 2, 20)
    catalogo.cadastrar_produto(prod)

    with pytest.raises(ValueError):
        catalogo.remover_estoque("INF-009", 5)  # Saldo atual é 4, não pode retirar 5

    # O saldo original deve ser preservado intacto
    assert catalogo.produtos["INF-009"].quantidade == 4


def test_alerta_estoque_baixo_inclui_limite_exato_minimo():
    catalogo = CatalogoEstoque()
    # p1 está exatamente no estoque mínimo (5 == 5)
    p1 = Produto("INF-010", "Hub USB", "INFORMATICA", 40.00, 5, 5, 30)
    # p2 está acima do mínimo (8 > 5)
    p2 = Produto("INF-011", "Adaptador", "INFORMATICA", 20.00, 8, 5, 30)

    catalogo.cadastrar_produto(p1)
    catalogo.cadastrar_produto(p2)

    alertas = catalogo.obter_produtos_em_alerta()
    skus_em_alerta = [p.sku for p in alertas]

    assert "INF-010" in skus_em_alerta
    assert "INF-011" not in skus_em_alerta


def test_reajuste_em_lote_por_categoria_exata_e_arredondamento():
    catalogo = CatalogoEstoque()
    # Preço 19.90 reajustado em +10% -> 19.90 * 1.10 = 21.89
    p1 = Produto("INF-012", "Mousepad Simples", "INFORMATICA", 19.90, 10, 2, 50)
    # Produto de categoria similar mas diferente não deve ser reajustado
    p2 = Produto("INF-013", "Mesa Gamer", "INFORMATICA_MOVEIS", 500.00, 3, 1, 10)

    catalogo.cadastrar_produto(p1)
    catalogo.cadastrar_produto(p2)

    total_afetados = catalogo.reajustar_precos_categoria("INFORMATICA", 10.0)

    assert total_afetados == 1
    assert catalogo.produtos["INF-012"].preco == 21.89
    assert isinstance(catalogo.produtos["INF-012"].preco, float)
    assert catalogo.produtos["INF-013"].preco == 500.00
