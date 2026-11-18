# Objeto C: Módulo de Catálogo e Gestão de Estoque de Produtos

## Contexto do Domínio
Este projeto implementa o subsistema de inventário e gestão de catálogo de uma distribuidora de produtos, compreendendo:
- Cadastro e validação de produtos garantindo unicidade de identificador (SKU);
- Regras de consistência de parâmetros de estoque (limites mínimo e máximo);
- Movimentação de estoque (entradas e saídas/baixas com prevenção de saldo negativo);
- Mecanismo de alerta de ressuprimento de estoque;
- Aplicação de reajuste de preços em lote por categoria de produtos.

**Tempo estimado de resolução:** 12 a 18 minutos.

---

## Especificação de Interface

### Modelo de Produto
Classe: `Produto` em `src/produtos.py`.

```python
Produto(
    sku: str,
    nome: str,
    categoria: str,
    preco: float,
    quantidade: int,
    estoque_minimo: int,
    estoque_maximo: int
)
```

- `sku`: identificador alfanumérico único. Não pode ser vazio.
- `preco`: valor monetário float. Deve ser estritamente maior que zero (`preco > 0`).
- `quantidade`: número inteiro não negativo (`quantidade >= 0`).
- `estoque_minimo`: número inteiro não negativo (`estoque_minimo >= 0`).
- `estoque_maximo`: número inteiro que deve ser estritamente maior que o estoque mínimo (`estoque_maximo > estoque_minimo`). Caso contrário, levantar `ValueError`.

### Gerenciador de Estoque
Classe: `CatalogoEstoque` em `src/produtos.py`.

- `cadastrar_produto(produto: Produto) -> None`: Registra o produto no catálogo. Se o SKU já existir no catálogo, deve levantar `ValueError`.
- `adicionar_estoque(sku: str, quantidade: int) -> int`: Incrementa o estoque do produto. Não permite adicionar valores menores ou iguais a zero. Levanta `ValueError` se a nova quantidade ultrapassar `estoque_maximo`. Retorna o novo saldo.
- `remover_estoque(sku: str, quantidade: int) -> int`: Decrementa o estoque do produto. Não permite remover valores menores ou iguais a zero. Se a quantidade solicitada for maior que o saldo em estoque, a operação não deve permitir saldo negativo e deve levantar `ValueError`. Retorna o novo saldo.
- `obter_produtos_em_alerta() -> list[Produto]`: Retorna a lista de produtos cujo saldo em estoque atingiu ou está abaixo do limite de segurança (`quantidade <= estoque_minimo`).
- `reajustar_precos_categoria(categoria: str, percentual: float) -> int`: Aplica aumento ou redução percentual no preço de **exclusivamente todos** os produtos que pertencem à categoria exata informada. O preço atualizado deve ser arredondado para duas casas decimais (`round(novo_preco, 2)`). Retorna o total de produtos atualizados.

---

## Regras de Negócio e Requisitos Funcionais

| ID | Regra de Negócio |
|---|---|
| **RF01 - Unicidade de SKU** | O SKU é o identificador único do produto. Cadastros com SKU já existente devem ser recusados levantando `ValueError`. |
| **RF02 - Limites de Estoque** | No cadastro do produto, o `estoque_maximo` deve ser estritamente superior ao `estoque_minimo`. Caso `estoque_maximo <= estoque_minimo`, levantar `ValueError`. |
| **RF03 - Proteção de Estoque Negativo** | Nenhuma baixa de estoque pode deixar a quantidade de um produto com valor inferior a zero. Caso a quantidade de saída seja superior ao saldo disponível, levantar `ValueError` e não alterar o saldo. |
| **RF04 - Alerta de Ponto de Pedido** | Produtos com estoque menor ou exatamente igual ao estoque mínimo (`quantidade <= estoque_minimo`) devem ser reportados no alerta de ressuprimento. |
| **RF05 - Reajuste em Lote e Arredondamento** | O reajuste em lote deve filtrar rigorosamente pela igualdade exata da categoria (ignorando espaços e capitalização), sem atingir categorias correlatas. O valor do novo preço deve possuir precisão de 2 casas decimais. |

---

## Restrições do Desafio

1. Não altere os arquivos da pasta `tests/`.
2. Mantenha a assinatura dos métodos e classes em `src/produtos.py`.
3. Utilize exclusivamente recursos da biblioteca padrão do Python.
4. O código fornecido possui defeitos intencionais de validação, controle de integridade de estoque e precisão de arredondamento. Seu objetivo é identificar e corrigir as causas em `src/produtos.py` até que todos os testes passem.

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
