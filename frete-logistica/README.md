# Módulo de Cálculo de Frete e Prazos de Entrega (`shipping.py`)

Bem-vindo ao experimento de engenharia de software e depuração de código!

---

> [!WARNING]
> ### AVISO IMPORTANTE AOS PARTICIPANTES
> **O arquivo de testes automatizados (`test_shipping.py`) é rigorosamente IMUTÁVEL.**  
> Você **NÃO** deve modificar, renomear, comentar ou excluir nenhuma linha de código ou teste contido em `test_shipping.py`.  
> Toda a depuração, análise e correção de código deve ser realizada exclusivamente no arquivo **`shipping.py`**.

---

## 1. Contexto do Sistema

O arquivo `shipping.py` é responsável pela lógica de cotação de fretes e estimativas de prazos para uma plataforma de e-commerce. O sistema recebe os dados de um pedido (CEP de destino, valor total, peso em kg, dimensões da embalagem e modalidade de envio) e retorna os valores tarifários e prazos de entrega calculados.

---

## 2. Regras de Negócio e Fórmulas

### 2.1. Tabela de Regiões, Tarifas Base e Prazos

A identificação da região é feita pelos primeiros dígitos do CEP (após desconsiderar caracteres não numéricos como hífens):

| Região | Faixa de CEP (numérica) | Tarifa Base Econômica | Prazo Base Econômico |
| :--- | :--- | :--- | :--- |
| **SUDESTE** | `01000-000` a `39999-999` (`1000000` a `39999999`) | R\$ 15,00 | 4 dias úteis |
| **NORDESTE** | `40000-000` a `65999-999` (`40000000` a `65999999`) | R\$ 30,00 | 9 dias úteis |
| **NORTE** | `66000-000` a `69999-999` (`66000000` a `69999999`) | R\$ 40,00 | 12 dias úteis |
| **CENTRO_OESTE** | `70000-000` a `79999-999` (`70000000` a `79999999`) | R\$ 25,00 | 7 dias úteis |
| **SUL** | `80000-000` a `99999-999` (`80000000` a `99999999`) | R\$ 20,00 | 6 dias úteis |

Se o CEP informado for inválido ou estiver fora dessas faixas, o sistema deve levantar uma exceção `ValueError`.

---

### 2.2. Peso Tarifável e Acréscimo por Peso Excedente

1. **Peso Volumétrico (Cubagem):**
   $$\text{peso\_volumétrico (kg)} = \frac{\text{comprimento (cm)} \times \text{largura (cm)} \times \text{altura (cm)}}{6000}$$
2. **Peso Tarifável:**  
   É o maior valor entre o **peso real** do produto e o **peso volumétrico**.
3. **Franquia de Peso:**  
   Até `1.0 kg` tarifável, não há custo adicional de peso (franquia inclusa na tarifa base).
4. **Taxa Adicional por Peso Excedente:**  
   Para pesos tarifáveis superiores a `1.0 kg`, é cobrado **R\$ 2,50 por kg excedente**, de forma proporcional e precisa:
   $$\text{acréscimo} = (\text{peso\_tarifável} - 1.0) \times 2.50$$
   *(Arredondado para 2 casas decimais).*

---

### 2.3. Regra de Frete Grátis

- Aplicável **apenas** para a modalidade **`economico`**.
- Um pedido torna-se elegível ao frete grátis quando o valor total do pedido for **maior ou igual a R\$ 250,00** (`valor_pedido >= 250.00`).
- Pedidos com valor inferior a R\$ 250,00 (`valor_pedido < 250.00`) **não** recebem frete grátis e pagam o frete normal.

---

### 2.4. Modalidades de Envio

#### A) Econômico (`modalidade = 'economico'`)
- **Valor do Frete:**  
  - Se elegível a frete grátis: `R$ 0,00`.
  - Caso contrário: $\text{tarifa\_base} + \text{acréscimo\_peso}$.
- **Prazo:** Igual ao prazo base da região.

#### B) Expresso (`modalidade = 'expresso'`)
- **Valor do Frete:**  
  - Custo com sobretaxa de 50% sobre a tarifa base mais o acréscimo de peso:
    $$\text{valor\_frete} = (\text{tarifa\_base} \times 1.5) + \text{acréscimo\_peso}$$
  - **Nota:** O frete expresso **nunca** recebe gratuidade, independentemente do valor da compra.
- **Prazo de Entrega:**  
  - O prazo do frete expresso é sempre reduzido em **2 dias úteis** em relação ao prazo base da região ($\text{prazo} = \text{prazo\_base} - 2$).
  - O prazo nunca pode ser inferior a 1 dia útil ($\max(1, \text{prazo\_base} - 2)$).

---

## 3. Como Executar os Testes Automatizados

Certifique-se de estar no diretório raiz do projeto e execute a suíte de testes com o Pytest:

```bash
pytest test_shipping.py
```

Ou, caso utilize o módulo diretamente pelo interpretador Python:

```bash
python -m pytest test_shipping.py
```

### Critério de Conclusão da Tarefa
- **Estado Inicial:** A suíte executará 8 testes, dos quais 4 falharão de forma determinística devido a defeitos lógicos introduzidos na implementação.
- **Estado Concluído:** Após a correta identificação e resolução dos defeitos lógicos em `shipping.py`, **100% dos testes devem passar (8 passed)**.
