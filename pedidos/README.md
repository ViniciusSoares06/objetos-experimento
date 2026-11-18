# Objeto A: Módulo de Pedidos de E-commerce

## Contexto do Domínio
Este projeto implementa o fluxo de processamento de pedidos de uma plataforma de comércio eletrônico, abrangendo:
- Validação de dados cadastrais do pedido (itens, quantidades, pesos e CEP);
- Cálculo de frete dinâmico baseado no peso e na região de destino;
- Concessão de frete gratuito com base no valor líquido dos produtos;
- Aplicação de regras de cupom de desconto (fixo ou percentual);
- Controle de ciclo de vida através de uma máquina de estados do pedido.

**Tempo estimado de resolução:** 12 a 18 minutos.

---

## Especificação de Interface

Classe principal: `Pedido` em `src/pedidos.py`.

### Assinatura do Construtor
```python
Pedido(cliente_id: str, itens: list[dict], cep_destino: str)
```

Cada item na lista `itens` é um dicionário no formato:
```python
{
    "nome": str,
    "preco": float,       # Deve ser maior que 0.0
    "quantidade": int,    # Deve ser número inteiro maior que 0
    "peso_kg": float      # Deve ser número maior que 0.0
}
```

---

## Regras de Negócio e Requisitos Funcionais

| ID | Regra de Negócio |
|---|---|
| **RF01 - Validação de Itens** | Todos os itens devem possuir `preco > 0`, `quantidade > 0` e `peso_kg > 0`. Caso contrário, levantar `ValueError`. |
| **RF02 - Validação de CEP** | O CEP de destino deve ser válido, contendo exatamente 8 dígitos numéricos (hífen opcional). Formatos com letras, incompletos ou vazios devem levantar `ValueError`. |
| **RF03 - Cálculo de Frete** | O frete é composto por uma tarifa base regional somada a R$ 3,50 por kg do peso total exato do pedido (incluindo frações decimais de peso). As tarifas base são: <br>• Primeiros dígitos `0, 1, 2, 3` (Sudeste): R$ 12,00 <br>• Primeiros dígitos `8, 9` (Sul): R$ 15,00 <br>• Primeiros dígitos `4, 5` (Nordeste): R$ 20,00 <br>• Primeiros dígitos `6, 7` (Norte / Centro-Oeste): R$ 25,00 |
| **RF04 - Regra de Frete Grátis** | Pedidos cujo valor dos itens **após a dedução de descontos** (valor líquido) for maior ou igual a R$ 200,00 têm direito a frete grátis (R$ 0,00). |
| **RF05 - Aplicação de Cupom** | O pedido aceita cupons percentuais (`0 < valor <= 100`) ou fixos (`valor > 0`). O cupom só pode ser aplicado se o subtotal do pedido for **maior ou igual** ao campo `minimo` definido no cupom. |
| **RF06 - Descontos Não Cumulativos** | Não é permitido aplicar mais de um cupom no mesmo pedido. Caso um segundo cupom seja submetido a um pedido que já possua cupom aplicado, a operação deve levantar `ValueError`. |
| **RF07 - Máquina de Estados** | O status inicial é `PENDENTE`. As transições permitidas são exclusivamente:<br>• `PENDENTE` ➔ `PAGO` ou `CANCELADO`<br>• `PAGO` ➔ `ENVIADO` ou `CANCELADO`<br>• `ENVIADO` ➔ `ENTREGUE`<br>Um pedido que já esteja com status `ENVIADO` não pode transitar para `CANCELADO`. Estados finais (`ENTREGUE`, `CANCELADO`) não aceitam nenhuma nova transição. Transições não permitidas devem levantar `ValueError`. |

---

## Exemplos de Uso

```python
itens = [
    {"nome": "Livro", "preco": 80.00, "quantidade": 2, "peso_kg": 0.5}
]
pedido = Pedido(cliente_id="CLI-10", itens=itens, cep_destino="80010-000")

# Subtotal: 160.00, Peso Total: 1.0 kg
# Frete Sul (prefixo 8): R$ 15,00 + (1.0 * 3,50) = R$ 18,50
# Total: 178.50
```

---

## Restrições do Desafio

1. Não altere os arquivos da pasta `tests/`.
2. Mantenha a assinatura dos métodos e classes existentes em `src/pedidos.py`.
3. Utilize apenas a biblioteca padrão do Python.
4. O código fornecido possui defeitos intencionais de validação e regras de negócio. Seu objetivo é identificar e corrigir as causas em `src/pedidos.py` até que todos os testes passem.

---

## Como Executar os Testes

Instale o pytest (caso necessário):
```bash
pip install -r requirements.txt
```

Execute a suíte de testes:
```bash
pytest
```
Ou com saída simplificada:
```bash
pytest -q
```
