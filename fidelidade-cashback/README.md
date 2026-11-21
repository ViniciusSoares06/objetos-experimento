# Objeto F: Módulo de Aplicação de Cupons e Sistema de Cashback (`loyalty.py`)

Bem-vindo ao experimento de engenharia de software focado em depuração colaborativa de código (programação em pares).

---

> [!WARNING]
> ### AVISO CRÍTICO AOS PARTICIPANTES
> **O arquivo de testes automatizados (`test_loyalty.py`) é RIGOROSAMENTE IMUTÁVEL.**  
> Você **NÃO** deve modificar, renomear, comentar ou excluir nenhuma linha de código em `test_loyalty.py`.  
> Toda a análise, depuração e correção de código deve ser realizada exclusivamente no arquivo **`loyalty.py`**.

---

## 1. Visão Geral do Sistema

O módulo `loyalty.py` é responsável pelo processamento financeiro e de fidelidade durante a etapa de checkout de um e-commerce. Suas principais responsabilidades envolvem:
1. Validação de cupons de desconto (fixos e percentuais) com regras de valor mínimo;
2. Limitação de descontos para prevenir totais negativos;
3. Resgate de saldo acumulado de cashback da carteira do cliente com validação estrita de limites;
4. Apuração e crédito de novos pontos/cashback com base no valor líquido efetivo faturado.

---

## 2. Regras de Negócio e Especificação Funcional

### 2.1. Cupons de Desconto (`Coupon`) e Função `calculate_coupon_discount`
- **Tipos de Cupom:**
  - `CouponType.PERCENTAGE`: Concede desconto percentual sobre o subtotal (ex: 10% de R$ 200,00 = R$ 20,00).
  - `CouponType.FIXED`: Concede um abatimento em valor monetário fixo (ex: R$ 15,00 ou R$ 50,00).
- **Valor Mínimo de Compra (`min_purchase`):**
  - O cupom só é ativado se o subtotal do pedido for **maior ou igual** a `coupon.min_purchase`.
  - Caso o subtotal seja estritamente inferior ao valor mínimo, o desconto concedido deve ser exatamente `0.0`.
- **Prevenção de Total Negativo:**
  - Cupons de valor fixo **nunca** podem exceder o valor do subtotal do pedido.
  - Se um cupom fixo for de R$ 50,00 e o subtotal for de R$ 35,00, o desconto máximo aplicado deve ser de R$ 35,00, garantindo que o valor pós-desconto não seja inferior a zero:
    $$\text{desconto} = \min(\text{subtotal}, \text{coupon.value})$$

---

### 2.2. Carteira e Resgate de Cashback (`redeem_cashback`)
- **Saldo Disponível:** Cada cliente possui uma carteira (`CustomerWallet`) com o saldo disponível `cashback_balance`.
- **Validação de Valor Negativo ou Nulo:** Resgates com valor $\le 0.0$ retornam `0.0` e não debitam o saldo.
- **Validação de Limite de Saldo:**
  - O cliente **não pode** resgatar um valor maior do que o saldo disponível em sua carteira.
  - Se $\text{requested\_amount} > \text{wallet.cashback_balance}$, o sistema deve **lançar uma exceção `ValueError("Saldo insuficiente...")`** e manter o saldo inalterado.
  - Em nenhuma circunstância o saldo da carteira do cliente pode ficar negativo.
- **Débito:** Quando a solicitação for válida, o saldo da carteira é subtraído da quantia resgatada.

---

### 2.3. Cálculo do Novo Cashback Creditado (`calculate_cashback_earned`)
- **Base de Incidência:**
  - O novo cashback creditado ao cliente é calculado aplicando-se a alíquota (padrão de 5%, ou seja, taxa 0.05) **estritamente sobre o valor líquido faturado após o desconto do cupom** ($\text{subtotal} - \text{desconto}$).
  - O novo cashback **NÃO incide sobre o valor bruto/subtotal** caso tenha ocorrido desconto de cupom, evitando bonificação sobre quantias não faturadas.
  - Exemplo: Pedido bruto de R$ 100,00 com cupom de R$ 20,00 de desconto resulta em base de faturamento de R$ 80,00. O novo cashback gerado (a 5%) deve ser de **R$ 4,00** ($80 \times 0.05$), e **não** R$ 5,00 ($100 \times 0.05$).

---

### 2.4. Checkout Consolidado (`process_order`)
O fluxo do checkout segue as seguintes etapas:
1. Valida se o subtotal não é negativo (lança `ValueError` se for menor que zero).
2. Calcula o desconto do cupom (`calculate_coupon_discount`).
3. Calcula o valor remanescente pós-desconto:
   $$\text{amount\_after\_coupon} = \text{subtotal} - \text{discount}$$
4. Processa o resgate de cashback solicitado:
   - O resgate é limitado ao saldo disponível e ao valor residual da compra ($\text{amount\_after\_coupon}$), impedindo pagamentos negativos.
5. Calcula o valor final líquido a pagar pelo cliente:
   $$\text{final\_payable} = \text{amount\_after\_coupon} - \text{cashback\_redeemed}$$
6. Calcula o novo cashback a ser gerado sobre $\text{amount\_after\_coupon}$ e o credita na carteira do cliente (`wallet.cashback_balance`).
7. Retorna o objeto `OrderSummary` com o detalhamento completo.

---

## 3. Como Executar os Testes Automatizados

No terminal, certifique-se de estar no diretório raiz do projeto e execute:

```bash
python -m pytest test_loyalty.py
```

ou (caso o comando `pytest` esteja mapeado no PATH do sistema):

```bash
pytest test_loyalty.py
```

### Critério de Aceite e Conclusão
- **Estado Inicial:** A suíte de testes executa 8 testes automatizados, dos quais **4 falham** devido aos defeitos lógicos existentes na implementação atual de `loyalty.py`.
- **Estado Concluído:** Após a identificação e correção de todos os defeitos lógicos exclusivamente em `loyalty.py`, **100% dos testes devem ser aprovados (8 passed)**.
