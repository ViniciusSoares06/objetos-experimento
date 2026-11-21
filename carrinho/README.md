# Objeto D — Carrinho de compras

Corrija o módulo `carrinho.py` conforme as regras abaixo. Mantenha a suíte de testes original.

## Comportamento esperado

O carrinho é um dicionário que associa cada código de produto a um par (preço unitário em centavos, quantidade).

- `adicionar(carrinho, codigo, preco, quantidade)` inclui um produto com quantidade positiva. Se o código já existir, soma a quantidade e preserva o preço cadastrado.
- `atualizar_quantidade(carrinho, codigo, quantidade)` substitui a quantidade de um produto existente. A quantidade é um inteiro não negativo. Zero remove o item.
- `total(carrinho)` soma o preço unitário multiplicado pela quantidade de cada item. O carrinho vazio totaliza zero.

As operações recebem códigos e valores dentro desses domínios. As duas primeiras alteram o dicionário recebido.

## Testes

A partir desta pasta, com o Pytest instalado, execute:

```console
python -m pytest -q test_carrinho.py
```
