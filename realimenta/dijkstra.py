"""Menor caminho em grafo com pesos positivos: Dijkstra com heapq.

Este algoritmo e guloso: em cada passo extrai o vertice de menor distancia
conhecida. Nao e programacao dinamica. A parte de PD do projeto e a mochila.
"""

from decimal import Decimal
from heapq import heappop, heappush

from realimenta.excecoes import ErroConsulta
from realimenta.grafo import Grafo
from realimenta.modelos import ResultadoCaminho


def menor_caminho(grafo: Grafo, origem_id: int, destino_id: int) -> ResultadoCaminho:
    """Calcula um menor caminho de origem_id ate destino_id.

    Nao altera o grafo. Distancia zero so e devolvida quando origem == destino.
    Destino inacessivel vem com alcancavel=False e distancia None, nunca zero.
    """
    if not grafo.contem(origem_id):
        raise ErroConsulta(f"origem inexistente: id {origem_id}")
    if not grafo.contem(destino_id):
        raise ErroConsulta(f"destino inexistente: id {destino_id}")

    if origem_id == destino_id:
        return ResultadoCaminho(
            origem_id=origem_id,
            destino_id=destino_id,
            alcancavel=True,
            caminho=[origem_id],
            distancia_km=Decimal("0"),
            mensagem="origem igual ao destino: caminho trivial com distancia zero",
        )

    # Distancia infinita e representada por ausencia na tabela.
    distancias: dict[int, Decimal] = {origem_id: Decimal("0")}
    anterior: dict[int, int | None] = {origem_id: None}
    # Chave (distancia, id) torna o empate deterministico: menor id sai primeiro.
    # Insercoes repetidas substituem decrease-key: entradas velhas sao ignoradas.
    heap: list[tuple[Decimal, int]] = [(Decimal("0"), origem_id)]
    visitados: set[int] = set()

    while heap:
        distancia_atual, atual = heappop(heap)
        if atual in visitados:
            continue
        visitados.add(atual)

        if atual == destino_id:
            break

        for vizinho, peso in grafo.vizinhos(atual):
            candidato = distancia_atual + peso
            conhecido = distancias.get(vizinho)
            # So atualiza se for estritamente menor. Empate: mantem o predecessor ja registrado.
            if conhecido is None or candidato < conhecido:
                distancias[vizinho] = candidato
                anterior[vizinho] = atual
                heappush(heap, (candidato, vizinho))

    if destino_id not in distancias:
        return ResultadoCaminho(
            origem_id=origem_id,
            destino_id=destino_id,
            alcancavel=False,
            caminho=[],
            distancia_km=None,
            mensagem=f"nao existe caminho entre {origem_id} e {destino_id}",
        )

    caminho = _reconstruir(anterior, destino_id)
    return ResultadoCaminho(
        origem_id=origem_id,
        destino_id=destino_id,
        alcancavel=True,
        caminho=caminho,
        distancia_km=distancias[destino_id],
        mensagem="menor caminho encontrado",
    )


def _reconstruir(anterior: dict[int, int | None], destino_id: int) -> list[int]:
    caminho: list[int] = []
    atual: int | None = destino_id
    while atual is not None:
        caminho.append(atual)
        atual = anterior.get(atual)
    caminho.reverse()
    return caminho


def ids_alcancaveis(grafo: Grafo, origem_id: int) -> set[int]:
    """Conjunto de locais com caminho a partir da origem, incluindo a propria origem."""
    if not grafo.contem(origem_id):
        raise ErroConsulta(f"origem inexistente: id {origem_id}")

    alcancados: set[int] = set()
    heap: list[tuple[Decimal, int]] = [(Decimal("0"), origem_id)]
    distancias: dict[int, Decimal] = {origem_id: Decimal("0")}

    while heap:
        distancia_atual, atual = heappop(heap)
        if atual in alcancados:
            continue
        alcancados.add(atual)
        for vizinho, peso in grafo.vizinhos(atual):
            candidato = distancia_atual + peso
            conhecido = distancias.get(vizinho)
            if conhecido is None or candidato < conhecido:
                distancias[vizinho] = candidato
                heappush(heap, (candidato, vizinho))
    return alcancados
