# Objeto E — Cupons e promoções

Corrija o módulo `promocoes.py` conforme as regras abaixo. Mantenha a suíte de testes original.

## Comportamento esperado

O catálogo associa cada código de cupom a um par (subtotal mínimo em centavos, percentual inteiro de desconto entre 0 e 100). Subtotais e mínimos são inteiros não negativos. Use um único cupom por compra.

- `cupom_valido(catalogo, codigo, subtotal)` verifica se o código existe e se o subtotal é igual ou superior ao mínimo.
- `valor_desconto(subtotal, percentual)` devolve o desconto em centavos, descartando frações de centavo.
- `total_com_cupom(catalogo, codigo, subtotal)` devolve o subtotal menos o desconto de um cupom válido. Se o cupom for inválido, devolve o subtotal integral.

## Testes

A partir desta pasta, com o Pytest instalado, execute:

```console
python -m pytest -q test_promocoes.py
```
