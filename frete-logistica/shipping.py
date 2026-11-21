"""Módulo de cálculo de frete, prazos e regras de logística de entrega.

Este módulo implementa cálculos de frete econômico e expresso,
considerando peso real, peso volumétrico, faixas de CEP de destino,
regras de frete grátis e prazos estimados de entrega.
"""

from typing import Dict, Tuple, Union

# Fator padrão do mercado para cálculo de peso volumétrico (kg/m³)
FATOR_CUBAGEM = 6000

# Faixas de CEP simplificadas por região (intervalos numéricos inclusivos)
# Estrutura: 'REGIAO': (cep_inicio, cep_fim, tarifa_base, prazo_economico_dias)
TABELA_REGIOES = {
    "SUDESTE": (1000000, 39999999, 15.00, 4),
    "SUL": (80000000, 99999999, 20.00, 6),
    "CENTRO_OESTE": (70000000, 79999999, 25.00, 7),
    "NORDESTE": (40000000, 65999999, 30.00, 9),
    "NORTE": (66000000, 69999999, 40.00, 12),
}

# Configurações globais
VALOR_MINIMO_FRETE_GRATIS = 250.00
ADICIONAL_POR_KG = 2.50
FRANQUIA_PESO_KG = 1.00


def normalizar_cep(cep: Union[str, int]) -> int:
    """Converte um CEP formatado ou string em inteiro limpo."""
    if isinstance(cep, int):
        return cep
    cep_limpo = "".join(caractere for caractere in str(cep) if caractere.isdigit())
    if len(cep_limpo) != 8:
        raise ValueError(f"CEP inválido: {cep}")
    return int(cep_limpo)


def identificar_regiao(cep: Union[str, int]) -> Tuple[str, float, int]:
    """Identifica região, tarifa base e prazo econômico com base no CEP."""
    cep_num = normalizar_cep(cep)
    for regiao, (inicio, fim, tarifa, prazo) in TABELA_REGIOES.items():
        if inicio <= cep_num <= fim:
            return regiao, tarifa, prazo
    raise ValueError(f"CEP fora da área de cobertura: {cep}")


def calcular_peso_tarifavel(
    peso_real_kg: float,
    comprimento_cm: float,
    largura_cm: float,
    altura_cm: float,
) -> float:
    """Calcula o peso tarifável: o maior entre o peso real e o peso volumétrico.

    Fórmula do peso volumétrico: (comprimento * largura * altura) / FATOR_CUBAGEM
    """
    peso_volumetrico = (comprimento_cm * largura_cm * altura_cm) / FATOR_CUBAGEM
    return max(peso_real_kg, peso_volumetrico)


def calcular_acrescimo_peso(peso_tarifavel_kg: float) -> float:
    """Calcula o valor adicional para pesos excedentes à franquia inicial."""
    if peso_tarifavel_kg <= FRANQUIA_PESO_KG:
        return 0.00

    peso_excedente = peso_tarifavel_kg - FRANQUIA_PESO_KG

    # DEFEITO LÓGICO 2:
    # Em vez de multiplicar diretamente o peso excedente fracionário pela taxa
    # (peso_excedente * ADICIONAL_POR_KG), o cálculo realiza divisão inteira (//)
    # ou truncamento inadequado distorcendo o cálculo do peso fracionado.
    adicional = (int(peso_excedente) // 1) * ADICIONAL_POR_KG
    return round(float(adicional), 2)


def verificar_elegibilidade_frete_gratis(valor_pedido: float) -> bool:
    """Verifica se o pedido atinge o valor mínimo necessário para frete grátis."""
    # DEFEITO LÓGICO 1:
    # A regra correta de negócio é: valor_pedido >= VALOR_MINIMO_FRETE_GRATIS
    # O código inverteu a lógica, concedendo frete grátis apenas para pedidos menores.
    return valor_pedido < VALOR_MINIMO_FRETE_GRATIS


def calcular_frete_e_prazo(
    cep_destino: Union[str, int],
    valor_pedido: float,
    peso_kg: float,
    dimensoes_cm: Tuple[float, float, float],
    modalidade: str = "economico",
) -> Dict[str, Union[float, int, str, bool]]:
    """Calcula o custo final do frete e o prazo de entrega.

    Modalidades aceitas:
    - 'economico': tarifa_base + acrescimo_peso (elegível a frete grátis)
    - 'expresso': (tarifa_base * 1.5) + acrescimo_peso (não elegível a frete grátis;
      reduz prazo econômico em 2 dias, respeitando o mínimo de 1 dia).
    """
    modalidade = modalidade.lower().strip()
    if modalidade not in ("economico", "expresso"):
        raise ValueError(f"Modalidade inválida: {modalidade}")

    regiao, tarifa_base, prazo_base = identificar_regiao(cep_destino)
    comprimento, largura, altura = dimensoes_cm
    peso_tarifavel = calcular_peso_tarifavel(peso_kg, comprimento, largura, altura)
    acrescimo = calcular_acrescimo_peso(peso_tarifavel)

    if modalidade == "economico":
        frete_gratis_aplicado = verificar_elegibilidade_frete_gratis(valor_pedido)
        custo_frete = 0.00 if frete_gratis_aplicado else (tarifa_base + acrescimo)
        prazo_final = prazo_base
    else:
        frete_gratis_aplicado = False
        custo_frete = round((tarifa_base * 1.5) + acrescimo, 2)

        # DEFEITO LÓGICO 3:
        # Para frete expresso, o prazo deveria ser reduzido em 2 dias (prazo_base - 2).
        # Aqui, o código soma 2 dias para regiões específicas como 'SUDESTE' ou em geral.
        if regiao == "SUDESTE":
            prazo_final = prazo_base + 2
        else:
            prazo_final = max(1, prazo_base - 2)

    return {
        "regiao": regiao,
        "modalidade": modalidade,
        "peso_tarifavel_kg": round(peso_tarifavel, 3),
        "valor_frete": round(custo_frete, 2),
        "prazo_dias": prazo_final,
        "frete_gratis": frete_gratis_aplicado,
    }
