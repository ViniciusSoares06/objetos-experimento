class Produto:
    """Representa um item do catálogo de produtos com regras de inventário."""

    def __init__(
        self,
        sku: str,
        nome: str,
        categoria: str,
        preco: float,
        quantidade: int,
        estoque_minimo: int,
        estoque_maximo: int
    ):
        if not sku or not isinstance(sku, str):
            raise ValueError("SKU inválido")
        if not nome:
            raise ValueError("Nome do produto não pode ser vazio")
        if preco <= 0:
            raise ValueError("Preço deve ser maior que zero")
        if quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa")
        if estoque_minimo < 0:
            raise ValueError("Estoque mínimo não pode ser negativo")

        self.sku = sku.strip().upper()
        self.nome = nome
        self.categoria = categoria.strip().upper()
        self.preco = round(float(preco), 2)
        self.quantidade = int(quantidade)
        self.estoque_minimo = int(estoque_minimo)
        self.estoque_maximo = int(estoque_maximo)


class CatalogoEstoque:
    """Controla o catálogo de produtos, movimentações de estoque e reajustes em lote."""

    def __init__(self):
        self.produtos: dict[str, Produto] = {}

    def cadastrar_produto(self, produto: Produto) -> None:
        """Cadastra um novo produto garantindo a unicidade do SKU."""
        # Armazena o produto no dicionário utilizando o SKU como chave
        self.produtos[produto.sku] = produto

    def adicionar_estoque(self, sku: str, quantidade: int) -> int:
        """Adiciona unidades ao estoque respeitando a capacidade máxima."""
        sku_normalizado = sku.strip().upper()
        if sku_normalizado not in self.produtos:
            raise KeyError("Produto não encontrado no catálogo")
        if quantidade <= 0:
            raise ValueError("Quantidade a adicionar deve ser maior que zero")

        produto = self.produtos[sku_normalizado]
        if produto.quantidade + quantidade > produto.estoque_maximo:
            raise ValueError("Quantidade excede o estoque máximo permitido")

        produto.quantidade += quantidade
        return produto.quantidade

    def remover_estoque(self, sku: str, quantidade: int) -> int:
        """Remove unidades do estoque garantindo que o saldo não fique negativo."""
        sku_normalizado = sku.strip().upper()
        if sku_normalizado not in self.produtos:
            raise KeyError("Produto não encontrado no catálogo")
        if quantidade <= 0:
            raise ValueError("Quantidade a remover deve ser maior que zero")

        produto = self.produtos[sku_normalizado]
        # Realiza a baixa do estoque
        produto.quantidade -= quantidade
        return produto.quantidade

    def obter_produtos_em_alerta(self) -> list[Produto]:
        """Retorna produtos que atingiram ou estão abaixo do estoque mínimo de segurança."""
        alerta = []
        for produto in self.produtos.values():
            if produto.quantidade < produto.estoque_minimo:
                alerta.append(produto)
        return alerta

    def reajustar_precos_categoria(self, categoria: str, percentual: float) -> int:
        """Aplica reajuste percentual no preço de todos os produtos de uma categoria."""
        if percentual < -100.0:
            raise ValueError("Percentual de reajuste não pode ser menor que -100%")

        categoria_normalizada = categoria.strip().upper()
        produtos_afetados = [
            p for p in self.produtos.values()
            if categoria_normalizada in p.categoria
        ]

        if not produtos_afetados:
            raise ValueError(f"Nenhum produto encontrado para a categoria {categoria}")

        fator = 1.0 + (percentual / 100.0)
        for produto in produtos_afetados:
            produto.preco = produto.preco * fator

        return len(produtos_afetados)
