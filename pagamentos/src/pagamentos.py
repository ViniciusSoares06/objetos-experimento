from enum import Enum


class StatusTransacao(str, Enum):
    PENDENTE = "PENDENTE"
    APROVADA = "APROVADA"
    RECUSADA = "RECUSADA"
    ESTORNADA_PARCIAL = "ESTORNADA_PARCIAL"
    ESTORNADA_TOTAL = "ESTORNADA_TOTAL"


def validar_cartao_credito(numero_cartao: str) -> bool:
    """Valida o número do cartão utilizando o algoritmo de Luhn e formato numérico."""
    numero_limpo = str(numero_cartao).replace(" ", "").replace("-", "")

    if not numero_limpo.isdigit():
        raise ValueError("Número do cartão deve conter apenas dígitos numéricos")

    if not (13 <= len(numero_limpo) <= 19):
        raise ValueError("Comprimento de cartão inválido")

    # Verificação com base no Algoritmo de Luhn
    # Itera da direita para a esquerda duplicando a cada dois dígitos a partir do penúltimo
    soma = 0
    for i, char in enumerate(reversed(numero_limpo)):
        digito = int(char)
        if i % 2 == 1:
            digito *= 2
            if digito > 9:
                digito -= 9
        soma += digito

    return soma % 10 == 0


class TransacaoCartao:
    """Gerencia autorização, cálculo de parcelas com juros e fluxo de estorno."""

    def __init__(self, id_transacao: str, valor: float, numero_cartao: str, parcelas: int = 1):
        if not id_transacao:
            raise ValueError("ID da transação não pode ser vazio")
        if valor <= 0:
            raise ValueError("Valor da transação deve ser positivo")

        self.id_transacao = id_transacao
        self.valor = round(valor, 2)
        self.numero_cartao = numero_cartao
        self.parcelas = parcelas
        self.status = StatusTransacao.PENDENTE
        self.valor_estornado = 0.0

        self._validar_parcelas()

    def _validar_parcelas(self) -> None:
        if not isinstance(self.parcelas, int):
            raise ValueError("Número de parcelas deve ser inteiro")
        if not (1 <= self.parcelas <= 12):
            raise ValueError("Número de parcelas deve estar entre 1 e 12")

    def calcular_valor_parcela(self) -> float:
        """Calcula o valor unitário da parcela considerando a política de juros:
        - 1x: sem juros
        - 2x a 6x: juros simples de 1.5% ao mês (0.015)
        - 7x a 12x: juros compostos de 2.0% ao mês (0.02)
        """
        if self.parcelas == 1:
            return round(self.valor, 2)

        if 2 <= self.parcelas <= 6:
            taxa = 0.015
            montante = self.valor * (1.0 + (taxa * self.parcelas))
            return round(montante / self.parcelas, 2)

        # Para mais de 6 parcelas, política de juros compostos
        taxa = 0.02
        montante = self.valor * ((1.0 + taxa) ** self.parcelas)
        return round(montante / self.parcelas, 2)

    def calcular_total_com_juros(self) -> float:
        valor_parcela = self.calcular_valor_parcela()
        return round(valor_parcela * self.parcelas, 2)

    def autorizar(self) -> bool:
        """Processa a validação do cartão e autorização da transação."""
        try:
            valido = validar_cartao_credito(self.numero_cartao)
            if valido:
                self.status = StatusTransacao.APROVADA
                return True
            else:
                self.status = StatusTransacao.RECUSADA
                raise ValueError("Cartão inválido pelo algoritmo de verificação")
        except ValueError:
            self.status = StatusTransacao.RECUSADA
            raise

    def estornar(self, valor_estorno: float = None) -> float:
        """Realiza estorno parcial ou total da transação autorizada."""
        if self.status not in (StatusTransacao.APROVADA, StatusTransacao.ESTORNADA_PARCIAL):
            raise ValueError(f"Não é permitido estornar transação com status {self.status}")

        total_transacao = self.calcular_total_com_juros()

        if valor_estorno is None:
            valor_estorno = total_transacao - self.valor_estornado

        if valor_estorno <= 0:
            raise ValueError("Valor do estorno deve ser estritamente positivo")

        # Validação do limite de estorno
        if self.valor_estornado + valor_estorno > total_transacao:
            raise ValueError("Valor de estorno excede o valor permitido")

        self.valor_estornado += valor_estorno

        if self.valor_estornado >= total_transacao:
            self.status = StatusTransacao.ESTORNADA_TOTAL
        else:
            self.status = StatusTransacao.ESTORNADA_PARCIAL

        return round(self.valor_estornado, 2)
