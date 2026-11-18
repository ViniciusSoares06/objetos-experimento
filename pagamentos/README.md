# Objeto B: Módulo de Processamento de Pagamentos

## Contexto do Domínio
Este projeto gerencia transações financeiras com cartão de crédito em uma plataforma de pagamentos, contemplando:
- Validação de integridade do número do cartão via algoritmo de Luhn e formatos numéricos;
- Cálculo de parcelamento com aplicação de juros simples ou compostos conforme a quantidade de parcelas;
- Processo de autorização e controle de estornos totais e parciais.

**Tempo estimado de resolução:** 12 a 18 minutos.

---

## Especificação de Interface

### Validação de Cartão
Função: `validar_cartao_credito(numero_cartao: str) -> bool` em `src/pagamentos.py`.

- Deve aceitar strings contendo espaços ou hifens, normalizando antes de validar.
- Deve conter apenas caracteres numéricos e possuir comprimento entre 13 e 19 dígitos. Caso contrário, levantar `ValueError`.
- Deve verificar a validade do dígito verificador através do algoritmo padrão de Luhn (iniciando a duplicação a partir do segundo dígito da direita para a esquerda). Retorna `True` se válido e `False` se o dígito verificador for inválido.

### Classe de Transação
Classe: `TransacaoCartao` em `src/pagamentos.py`.

```python
TransacaoCartao(id_transacao: str, valor: float, numero_cartao: str, parcelas: int = 1)
```

- `valor`: deve ser maior que 0.0 (levantar `ValueError` caso contrário).
- `parcelas`: número inteiro estritamente entre 1 e 12 (`1 <= parcelas <= 12`). Qualquer valor fora dessa faixa deve levantar `ValueError`.

---

## Regras de Negócio e Requisitos Funcionais

| ID | Regra de Negócio |
|---|---|
| **RF01 - Política de Parcelamento** | O parcelamento segue faixas de juros mensais:<br>• **1 parcela (à vista):** Sem incidência de juros (0%).<br>• **2 a 6 parcelas:** Juros **simples** de **1,5% ao mês** ($M = C \times (1 + i \times t)$).<br>• **7 a 12 parcelas:** Juros **compostos** de **2,0% ao mês** ($M = C \times (1 + i)^t$). |
| **RF02 - Arredondamento de Parcelas** | O valor unitário da parcela deve ser arredondado para duas casas decimais (`round(montante / parcelas, 2)`). O valor total a pagar com juros é o valor da parcela multiplicado pela quantidade de parcelas. |
| **RF03 - Autorização** | O método `autorizar()` valida o cartão. Se válido, define o status como `APROVADA`. Se inválido, define o status como `RECUSADA` e levanta `ValueError`. |
| **RF04 - Validação de Estorno** | O método `estornar(valor_estorno)` só pode ser executado em transações cujo status seja `APROVADA` ou `ESTORNADA_PARCIAL`. Tentativas de estorno em transações `RECUSADA` ou `PENDENTE` devem levantar `ValueError`. |
| **RF05 - Limites de Estorno** | O valor a ser estornado deve ser estritamente positivo (`valor_estorno > 0`). Além disso, a soma acumulada de estornos não pode ultrapassar o valor total final da transação com juros. Violações devem levantar `ValueError`. |
| **RF06 - Atualização de Status de Estorno** | Se a soma dos estornos atingir o total da transação, o status deve ser atualizado para `ESTORNADA_TOTAL`. Se for inferior, deve ser `ESTORNADA_PARCIAL`. |

---

## Restrições do Desafio

1. Não altere os arquivos da pasta `tests/`.
2. Mantenha a assinatura dos métodos e funções em `src/pagamentos.py`.
3. Utilize apenas módulos da biblioteca padrão do Python.
4. O código fornecido possui defeitos intencionais de validação, cálculo financeiro e limites de transação. Seu objetivo é identificar e corrigir as causas em `src/pagamentos.py` até que todos os testes passem.

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
