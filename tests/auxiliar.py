"""Utilitarios dos testes, inclusive enumeracao independente da mochila."""

import itertools
from decimal import Decimal

from realimenta.grafo import Grafo
from realimenta.modelos import ItemMochila, Local


def grafo_de(pares: list[tuple[int, int, str]]) -> Grafo:
    grafo = Grafo()
    vertices: set[int] = set()
    for origem, destino, _peso in pares:
        vertices.add(origem)
        vertices.add(destino)
    for vertice in vertices:
        grafo.adicionar_vertice(vertice)
    for origem, destino, peso in pares:
        grafo.adicionar_aresta(origem, destino, Decimal(peso))
    return grafo


def locais_simples() -> dict[int, Local]:
    return {
        1: Local(1, "Padaria", "ESTABELECIMENTO"),
        2: Local(2, "Hortifruti", "ESTABELECIMENTO"),
        5: Local(5, "Isolada", "ESTABELECIMENTO"),
        6: Local(6, "Instituto", "INSTITUICAO"),
        7: Local(7, "Apoio", "APOIO"),
        8: Local(8, "Mercado", "ESTABELECIMENTO"),
    }


def valor_otimo_por_enumeracao(itens: list[ItemMochila], capacidade: int) -> int:
    """Verifica o valor otimo percorrendo todos os subconjuntos (so para n pequeno)."""
    melhor = 0
    n = len(itens)
    for tamanho in range(n + 1):
        for combo in itertools.combinations(itens, tamanho):
            peso = sum(item.peso for item in combo)
            if peso <= capacidade:
                valor = sum(item.valor for item in combo)
                if valor > melhor:
                    melhor = valor
    return melhor
