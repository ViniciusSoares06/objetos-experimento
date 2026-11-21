# Objeto F — Cancelamento de pedidos

Corrija o módulo `cancelamentos.py` conforme as regras abaixo. Mantenha a suíte de testes original.

## Comportamento esperado

Cada pedido é um dicionário com as chaves `estado`, `produtos` e `frete`. Os valores de produtos e frete são inteiros não negativos em centavos.

- `pode_cancelar(estado)` devolve verdadeiro para `pendente` e `pago`. Os estados `enviado` e `cancelado` impedem o cancelamento.
- `valor_restituicao(pedido)` devolve, para um pedido pago, a soma de produtos e frete. Nos demais estados, devolve zero.
- `cancelar(pedido)` devolve a restituição calculada com base no estado anterior e muda o estado para `cancelado`. Se o pedido não puder ser cancelado, devolve zero e mantém o pedido como está.

## Testes

A partir desta pasta, com o Pytest instalado, execute:

```console
python -m pytest -q test_cancelamentos.py
```
