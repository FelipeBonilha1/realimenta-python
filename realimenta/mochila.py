"""Mochila 0/1 por tabulacao (programacao dinamica).

Cada item entra no maximo uma vez. O estado dp[i][c] e a maior soma de valores
obtida com os primeiros i itens e capacidade c (em unidades de 100 g).
"""

from realimenta.excecoes import ErroConsulta, TabelaMuitoGrande
from realimenta.modelos import ItemMochila, LIMITE_CELULAS_PADRAO, ResultadoMochila


def mochila_0_1(
    itens: list[ItemMochila],
    capacidade: int,
    limite_celulas: int = LIMITE_CELULAS_PADRAO,
) -> ResultadoMochila:
    """Resolve a mochila 0/1 com tabela bidimensional e reconstrucao dos ids.

    Desempate: os itens sao ordenados por id; em igualdade de valor, a transicao
    mantem a opcao de NAO incluir o item atual. Isso deixa o resultado
    deterministico. Nao afirmamos que esse criterio minimize o peso.
    """
    if capacidade < 0:
        raise ErroConsulta(f"capacidade nao pode ser negativa. Recebido {capacidade}")

    # Ordenar por id garante reconstrucao estavel quando a chamada recebe outra ordem.
    ordenados = sorted(itens, key=lambda item: item.id)
    n = len(ordenados)

    if n == 0 or capacidade == 0:
        return ResultadoMochila(
            ids_escolhidos=[],
            valor_total=0,
            peso_total=0,
            capacidade=capacidade,
            capacidade_restante=capacidade,
        )

    # A tabela alocada e dp[0..n][0..C], portanto (n + 1) * (C + 1) celulas.
    celulas = (n + 1) * (capacidade + 1)
    if celulas > limite_celulas:
        raise TabelaMuitoGrande(
            f"tabela dp exigiria {celulas} celulas "
            f"((n+1)*(C+1) com n={n}, C={capacidade}), "
            f"acima do limite {limite_celulas}. "
            "O limite controla o tamanho do problema; nao mede o consumo exato de memoria."
        )

    # dp[i][c] = melhor valor com os primeiros i itens e capacidade c.
    dp: list[list[int]] = [[0] * (capacidade + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        peso = ordenados[i - 1].peso
        valor = ordenados[i - 1].valor
        for c in range(capacidade + 1):
            nao_incluir = dp[i - 1][c]
            if peso > c:
                dp[i][c] = nao_incluir
            else:
                incluir = dp[i - 1][c - peso] + valor
                # Empate: fica com nao_incluir (nao pega o item atual).
                if incluir > nao_incluir:
                    dp[i][c] = incluir
                else:
                    dp[i][c] = nao_incluir

    ids_escolhidos, peso_total = _reconstruir(dp, ordenados, capacidade)
    valor_total = dp[n][capacidade]
    return ResultadoMochila(
        ids_escolhidos=ids_escolhidos,
        valor_total=valor_total,
        peso_total=peso_total,
        capacidade=capacidade,
        capacidade_restante=capacidade - peso_total,
    )


def _reconstruir(
    dp: list[list[int]],
    itens: list[ItemMochila],
    capacidade: int,
) -> tuple[list[int], int]:
    """Percorre a tabela de tras para frente para recuperar os ids escolhidos."""
    escolhidos: list[int] = []
    peso_total = 0
    c = capacidade
    n = len(itens)
    for i in range(n, 0, -1):
        # Se o valor mudou ao considerar o item i, ele entrou na solucao.
        if dp[i][c] != dp[i - 1][c]:
            item = itens[i - 1]
            escolhidos.append(item.id)
            peso_total += item.peso
            c -= item.peso
    escolhidos.reverse()
    return escolhidos, peso_total
