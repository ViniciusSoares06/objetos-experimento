from enum import Enum


class StatusPedido(str, Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    ENVIADO = "ENVIADO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


class Pedido:
    """Representa um pedido de e-commerce com cálculo de frete, descontos e status."""

    def __init__(self, cliente_id: str, itens: list[dict], cep_destino: str):
        if not cliente_id:
            raise ValueError("cliente_id não pode ser vazio")
        if not itens:
            raise ValueError("A lista de itens não pode estar vazia")

        self.cliente_id = cliente_id
        self.itens = itens
        self.cep_destino = str(cep_destino).strip()
        self.status = StatusPedido.PENDENTE
        self.cupom = None

        self._validar_cep()
        self._validar_itens()

    def _validar_cep(self) -> None:
        cep_limpo = self.cep_destino.replace("-", "")
        if len(cep_limpo) == 0:
            raise ValueError("CEP não pode ser vazio")

    def _validar_itens(self) -> None:
        for item in self.itens:
            if "preco" not in item or "quantidade" not in item or "peso_kg" not in item:
                raise ValueError("Item incompleto")
            if item["preco"] <= 0:
                raise ValueError("Preço unitário deve ser maior que zero")

    def calcular_subtotal(self) -> float:
        subtotal = sum(item["preco"] * item["quantidade"] for item in self.itens)
        return round(subtotal, 2)

    def calcular_peso_total(self) -> float:
        peso_total = sum(item["peso_kg"] * item["quantidade"] for item in self.itens)
        return round(peso_total, 3)

    def aplicar_cupom(self, cupom: dict) -> None:
        """Aplica cupom de desconto com regras de valor mínimo e não cumulatividade."""
        if not cupom or "codigo" not in cupom or "tipo" not in cupom or "valor" not in cupom:
            raise ValueError("Formato de cupom inválido")

        subtotal = self.calcular_subtotal()
        minimo = cupom.get("minimo", 0.0)

        if subtotal <= minimo:
            raise ValueError(f"Subtotal {subtotal} não atinge o valor mínimo de {minimo}")

        if cupom["tipo"] == "percentual" and not (0 < cupom["valor"] <= 100):
            raise ValueError("Percentual de desconto deve estar entre 0 e 100")
        if cupom["tipo"] == "fixo" and cupom["valor"] <= 0:
            raise ValueError("Valor de desconto fixo deve ser positivo")

        self.cupom = cupom

    def calcular_desconto(self) -> float:
        if not self.cupom:
            return 0.0

        subtotal = self.calcular_subtotal()
        if self.cupom["tipo"] == "percentual":
            desconto = subtotal * (self.cupom["valor"] / 100.0)
        elif self.cupom["tipo"] == "fixo":
            desconto = self.cupom["valor"]
        else:
            desconto = 0.0

        desconto = min(desconto, subtotal)
        return round(desconto, 2)

    def calcular_frete(self) -> float:
        """Calcula o frete baseado na região do CEP e peso total da encomenda."""
        cep_limpo = self.cep_destino.replace("-", "")
        prefixo = cep_limpo[0] if cep_limpo else "0"

        # Tabela base por região pelo primeiro dígito do CEP:
        # 0 a 3: Sudeste (R$ 12,00)
        # 8 e 9: Sul (R$ 15,00)
        # 4 e 5: Nordeste (R$ 20,00)
        # Outros (6 e 7): Norte / Centro-Oeste (R$ 25,00)
        if prefixo in "0123":
            tarifa_base = 12.0
        elif prefixo in "89":
            tarifa_base = 15.0
        elif prefixo in "45":
            tarifa_base = 20.0
        else:
            tarifa_base = 25.0

        peso_total = self.calcular_peso_total()
        valor_peso = int(peso_total) * 3.50
        frete = tarifa_base + valor_peso

        if self.calcular_subtotal() >= 200.0:
            return 0.0

        return round(frete, 2)

    def calcular_total(self) -> float:
        subtotal = self.calcular_subtotal()
        desconto = self.calcular_desconto()
        frete = self.calcular_frete()
        total = (subtotal - desconto) + frete
        return round(total, 2)

    def atualizar_status(self, novo_status: StatusPedido) -> None:
        """Controla a máquina de estados do pedido."""
        transicoes_validas = {
            StatusPedido.PENDENTE: [StatusPedido.PAGO, StatusPedido.CANCELADO],
            StatusPedido.PAGO: [StatusPedido.ENVIADO, StatusPedido.CANCELADO],
            StatusPedido.ENVIADO: [StatusPedido.ENTREGUE, StatusPedido.CANCELADO],
            StatusPedido.ENTREGUE: [],
            StatusPedido.CANCELADO: [],
        }

        if novo_status not in transicoes_validas.get(self.status, []):
            raise ValueError(f"Transição inválida de {self.status.value} para {novo_status.value}")

        self.status = novo_status
