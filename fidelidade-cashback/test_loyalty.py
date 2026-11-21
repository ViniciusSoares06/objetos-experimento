"""Suíte de Testes Automatizados para o Módulo de Fidelidade e Cashback (loyalty.py).

AVISO AOS PARTICIPANTES:
ESTE ARQUIVO É ESTRITAMENTE IMUTÁVEL. NÃO FAÇA ALTERAÇÕES NESTE ARQUIVO.
Todas as correções devem ser efetuadas exclusivamente no arquivo loyalty.py.
"""

import pytest
from loyalty import (
    Coupon,
    CouponType,
    CustomerWallet,
    OrderSummary,
    calculate_coupon_discount,
    calculate_cashback_earned,
    redeem_cashback,
    process_order,
)


def test_calculate_percentage_coupon_discount():
    """Valida o cálculo de desconto para cupom percentual legítimo."""
    coupon = Coupon(
        code="DESC10",
        discount_type=CouponType.PERCENTAGE,
        value=10.0,
        min_purchase=50.0
    )
    discount = calculate_coupon_discount(subtotal=200.0, coupon=coupon)
    assert discount == 20.0


def test_reject_coupon_below_minimum_purchase():
    """Garante que nenhum desconto é aplicado se o subtotal for inferior ao mínimo."""
    coupon = Coupon(
        code="MINIMO100",
        discount_type=CouponType.FIXED,
        value=20.0,
        min_purchase=100.0
    )
    discount = calculate_coupon_discount(subtotal=80.0, coupon=coupon)
    assert discount == 0.0


def test_fixed_coupon_discount_cannot_exceed_subtotal():
    """Garante que cupom de valor fixo maior que o subtotal é limitado ao próprio subtotal."""
    coupon = Coupon(
        code="SUPERFIXO50",
        discount_type=CouponType.FIXED,
        value=50.0,
        min_purchase=0.0
    )
    # Subtotal de 35.0 com cupom de 50.0 deve conceder no máximo 35.0 de desconto
    discount = calculate_coupon_discount(subtotal=35.0, coupon=coupon)
    assert discount == 35.0


def test_fixed_coupon_normal_application():
    """Valida aplicação de cupom fixo quando o subtotal é superior ao desconto."""
    coupon = Coupon(
        code="FIXO15",
        discount_type=CouponType.FIXED,
        value=15.0,
        min_purchase=50.0
    )
    discount = calculate_coupon_discount(subtotal=100.0, coupon=coupon)
    assert discount == 15.0


def test_redeem_cashback_rejects_amount_greater_than_balance():
    """Valida que tentar resgatar quantia superior ao saldo disponível lança ValueError."""
    wallet = CustomerWallet(customer_id="cli_01", cashback_balance=25.0)
    
    with pytest.raises(ValueError, match="(?i)saldo insuficiente"):
        redeem_cashback(wallet, requested_amount=30.0)
        
    # O saldo do cliente não pode sofrer mutação após tentativa inválida
    assert wallet.cashback_balance == 25.0


def test_redeem_cashback_successful_debit():
    """Valida débito correto no saldo de cashback para resgates válidos."""
    wallet = CustomerWallet(customer_id="cli_02", cashback_balance=50.0)
    redeemed = redeem_cashback(wallet, requested_amount=20.0)
    
    assert redeemed == 20.0
    assert wallet.cashback_balance == 30.0


def test_cashback_earned_calculated_on_net_amount_after_coupon():
    """Valida que o novo cashback é calculado estritamente sobre o valor líquido pós-desconto."""
    # Subtotal R$ 100,00 com cupom de 20% (R$ 20,00 de desconto).
    # Valor líquido a pagar: R$ 80,00.
    # Com cashback de 5%, o novo cashback gerado deve ser R$ 4,00 (80 * 0.05), NÃO R$ 5,00 (100 * 0.05).
    coupon = Coupon(
        code="PROMO20",
        discount_type=CouponType.PERCENTAGE,
        value=20.0,
        min_purchase=50.0
    )
    wallet = CustomerWallet(customer_id="cli_03", cashback_balance=0.0)

    summary = process_order(
        subtotal=100.0,
        coupon=coupon,
        wallet=wallet,
        cashback_to_redeem=0.0,
        cashback_rate=0.05
    )

    assert summary.subtotal == 100.0
    assert summary.discount_amount == 20.0
    assert summary.final_payable == 80.0
    assert summary.cashback_earned == 4.0
    assert summary.wallet_balance_after == 4.0


def test_complete_order_processing_integration():
    """Teste de integração do fluxo completo: cupom, resgate de saldo e novo cashback creditado."""
    # Subtotal: R$ 200,00
    # Cupom fixo de R$ 50,00 (mínimo de R$ 150,00) -> valor pós-cupom = R$ 150,00
    # Carteira do cliente possui R$ 30,00 de saldo e solicita resgate integral de R$ 30,00
    # Total final a pagar pelo cliente: R$ 120,00
    # Novo cashback gerado (5% sobre R$ 150,00 líquido faturado pelo cupom): R$ 7,50
    # Saldo final da carteira: 30.0 - 30.0 (resgate) + 7.50 (novo ganho) = R$ 7,50
    coupon = Coupon(
        code="BLACK50",
        discount_type=CouponType.FIXED,
        value=50.0,
        min_purchase=150.0
    )
    wallet = CustomerWallet(customer_id="cli_04", cashback_balance=30.0)

    summary = process_order(
        subtotal=200.0,
        coupon=coupon,
        wallet=wallet,
        cashback_to_redeem=30.0,
        cashback_rate=0.05
    )

    assert summary.subtotal == 200.0
    assert summary.discount_amount == 50.0
    assert summary.cashback_redeemed == 30.0
    assert summary.final_payable == 120.0
    assert summary.cashback_earned == 7.50
    assert summary.wallet_balance_after == 7.50
