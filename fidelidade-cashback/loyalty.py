"""Módulo de Aplicação de Cupons de Desconto e Sistema de Cashback.

Este módulo implementa o processamento financeiro de pedidos de compra com suporte
a cupons de desconto (fixos e percentuais), regras de valor mínimo para ativação,
resgate de saldo acumulado de cashback e apuração de novo cashback a ser creditado.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CouponType(Enum):
    """Tipos de cupom de desconto suportados."""
    PERCENTAGE = "percentage"
    FIXED = "fixed"


@dataclass
class Coupon:
    """Representa um cupom de desconto.

    Attributes:
        code: Código alfanumérico do cupom.
        discount_type: Tipo de desconto (PERCENTAGE ou FIXED).
        value: Valor percentual (ex: 15.0 para 15%) ou quantia fixa em reais (ex: 30.0).
        min_purchase: Valor mínimo bruto do pedido necessário para aplicação do cupom.
    """
    code: str
    discount_type: CouponType
    value: float
    min_purchase: float = 0.0


@dataclass
class CustomerWallet:
    """Carteira de fidelidade e cashback do cliente.

    Attributes:
        customer_id: Identificador único do cliente.
        cashback_balance: Saldo disponível de cashback em reais.
    """
    customer_id: str
    cashback_balance: float = 0.0


@dataclass
class OrderSummary:
    """Demonstrativo final do processamento financeiro do pedido.

    Attributes:
        subtotal: Valor bruto dos itens do pedido.
        discount_amount: Valor total de desconto concedido via cupom.
        cashback_redeemed: Valor de saldo de cashback resgatado nesta compra.
        final_payable: Valor líquido final a ser pago pelo cliente.
        cashback_earned: Novo valor de cashback acumulado gerado pela compra.
        wallet_balance_after: Saldo remanescente de cashback na carteira do cliente.
    """
    subtotal: float
    discount_amount: float
    cashback_redeemed: float
    final_payable: float
    cashback_earned: float
    wallet_balance_after: float


# Taxa padrão de cashback creditada sobre compras elegíveis (5%)
DEFAULT_CASHBACK_RATE = 0.05


def calculate_coupon_discount(subtotal: float, coupon: Optional[Coupon]) -> float:
    """Calcula o valor do desconto a ser aplicado baseado no cupom fornecido.

    Regras:
    - Se nenhum cupom for fornecido, o desconto é 0.0.
    - O subtotal do pedido deve atingir ou superar o valor mínimo de compra do cupom.
      Caso contrário, nenhum desconto é concedido.
    - Cupons percentuais aplicam a alíquota sobre o subtotal.
    - Cupons de valor fixo abatem a quantia diretamente, porém o desconto NUNCA
      pode exceder o valor do subtotal (o pedido não pode ficar com total negativo
      devido ao cupom).

    Args:
        subtotal: Valor bruto do pedido.
        coupon: Objeto de cupom opcional.

    Returns:
        float: Valor monetário do desconto calculado.
    """
    if not coupon:
        return 0.0

    if subtotal < coupon.min_purchase:
        return 0.0

    if coupon.discount_type == CouponType.PERCENTAGE:
        return round(subtotal * (coupon.value / 100.0), 2)
    elif coupon.discount_type == CouponType.FIXED:
        # DEFEITO LÓGICO 3 (INTENCIONAL):
        # Retorna o valor fixo do cupom diretamente, sem limitar ao valor do subtotal.
        # Correção esperada: return min(subtotal, coupon.value)
        return float(coupon.value)

    return 0.0


def redeem_cashback(wallet: CustomerWallet, requested_amount: float) -> float:
    """Realiza o resgate de parte ou totalidade do saldo de cashback da carteira.

    Regras:
    - O valor solicitado deve ser positivo (> 0.0).
    - O valor solicitado não pode ultrapassar o saldo atual disponível do cliente.
      Se for maior, lança ValueError indicando saldo insuficiente.
    - Caso válido, o saldo é debitado e o valor resgatado é retornado.

    Args:
        wallet: Carteira de cashback do cliente.
        requested_amount: Valor que o cliente deseja resgatar.

    Returns:
        float: Valor efetivamente resgatado.

    Raises:
        ValueError: Se o valor for negativo/zero ou se exceder o saldo disponível.
    """
    if requested_amount <= 0:
        return 0.0

    # DEFEITO LÓGICO 2 (INTENCIONAL):
    # Verificação incorreta do limite de saldo: o desenvolvedor usou '<' em vez de '>'
    # ou verificou a condição de forma invertida, permitindo que resgates maiores
    # que o saldo disponível passem sem levantar exceção, negativando a carteira.
    # Correção esperada:
    # if requested_amount > wallet.cashback_balance:
    #     raise ValueError("Saldo insuficiente de cashback.")
    if requested_amount < wallet.cashback_balance:
        # Erro conceitual: não lança quando requested_amount > wallet.cashback_balance
        pass

    wallet.cashback_balance = round(wallet.cashback_balance - requested_amount, 2)
    return requested_amount


def calculate_cashback_earned(net_payable: float, rate: float = DEFAULT_CASHBACK_RATE) -> float:
    """Calcula o novo cashback creditado ao cliente.

    Regras:
    - O cashback novo é calculado multiplicando a alíquota (rate) pelo valor líquido
      realmente pago pelo cliente após os descontos.
    - Não há cashback se o valor líquido for zero ou negativo.

    Args:
        net_payable: Valor líquido faturado após descontos de cupom.
        rate: Percentual de cashback (padrão 5%).

    Returns:
        float: Novo saldo de cashback a ser creditado.
    """
    if net_payable <= 0:
        return 0.0
    return round(net_payable * rate, 2)


def process_order(
    subtotal: float,
    coupon: Optional[Coupon] = None,
    wallet: Optional[CustomerWallet] = None,
    cashback_to_redeem: float = 0.0,
    cashback_rate: float = DEFAULT_CASHBACK_RATE
) -> OrderSummary:
    """Processa o checkout completo do pedido aplicando cupom, resgate e novo cashback.

    Ordem do fluxo de faturamento:
    1. Calcula o desconto do cupom aplicável.
    2. Determina o valor faturado intermediário (subtotal - desconto).
    3. Processa o resgate de cashback solicitado da carteira do cliente, se houver.
    4. O resgate de cashback também não pode fazer o total a pagar ficar abaixo de zero
       (limitado ao valor restante após o cupom).
    5. Calcula o valor final líquido a pagar.
    6. Calcula o novo cashback a ser concedido, que incide estritamente sobre o valor
       líquido pós-desconto de cupom faturado.
    7. Atualiza o saldo da carteira com o novo cashback acumulado.

    Args:
        subtotal: Valor bruto dos itens do pedido.
        coupon: Cupom de desconto opcional.
        wallet: Carteira do cliente opcional.
        cashback_to_redeem: Quantia de cashback a resgatar nesta compra.
        cashback_rate: Alíquota para cálculo do novo cashback (padrão 5%).

    Returns:
        OrderSummary: Resumo consolidado do pedido.
    """
    if subtotal < 0:
        raise ValueError("O subtotal do pedido não pode ser negativo.")

    # 1. Aplicação do cupom de desconto
    discount = calculate_coupon_discount(subtotal, coupon)
    amount_after_coupon = subtotal - discount

    # 2. Resgate de cashback
    redeemed = 0.0
    if wallet is not None and cashback_to_redeem > 0:
        # O resgate não pode exceder o valor restante a pagar após o desconto do cupom
        max_allowed_redemption = max(0.0, amount_after_coupon)
        actual_requested = min(cashback_to_redeem, max_allowed_redemption)
        redeemed = redeem_cashback(wallet, actual_requested)

    # 3. Total líquido final a pagar
    final_payable = round(amount_after_coupon - redeemed, 2)

    # 4. Cálculo de novo cashback gerado pela compra
    # DEFEITO LÓGICO 1 (INTENCIONAL):
    # O novo cashback é calculado equivocadamente sobre o subtotal bruto em vez do
    # valor líquido restante após a aplicação do cupom (amount_after_coupon).
    # Correção esperada: earned = calculate_cashback_earned(amount_after_coupon, cashback_rate)
    earned = calculate_cashback_earned(subtotal, cashback_rate)

    # 5. Atualização da carteira com o novo cashback
    if wallet is not None:
        wallet.cashback_balance = round(wallet.cashback_balance + earned, 2)
        final_wallet_balance = wallet.cashback_balance
    else:
        final_wallet_balance = 0.0

    return OrderSummary(
        subtotal=round(subtotal, 2),
        discount_amount=round(discount, 2),
        cashback_redeemed=round(redeemed, 2),
        final_payable=final_payable,
        cashback_earned=earned,
        wallet_balance_after=final_wallet_balance
    )
