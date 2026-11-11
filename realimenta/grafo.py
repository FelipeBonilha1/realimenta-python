"""Grafo ponderado nao direcionado com lista de adjacencia."""

from decimal import Decimal

from realimenta.excecoes import ErroValidacao
from realimenta.modelos import Conexao, Local


class Grafo:
    """Cada conexao vale nos dois sentidos. Nao ha arestas de um local para ele mesmo."""

    def __init__(self) -> None:
        # lista de adjacencia: id -> lista de (vizinho_id, distancia_km)
        self._adj: dict[int, list[tuple[int, Decimal]]] = {}
        self._pares: set[tuple[int, int]] = set()

    def adicionar_vertice(self, local_id: int) -> None:
        if local_id not in self._adj:
            self._adj[local_id] = []

    def contem(self, local_id: int) -> bool:
        return local_id in self._adj

    def vertices(self) -> list[int]:
        return sorted(self._adj.keys())

    def adicionar_aresta(self, origem_id: int, destino_id: int, distancia_km: Decimal) -> None:
        """Insere aresta de mao dupla. Rejeita laco e duplicata, inclusive invertida."""
        if origem_id == destino_id:
            raise ErroValidacao(
                "conexao de um local para ele mesmo nao e permitida: "
                "simplificacao deste modelo, que so representa deslocamento entre locais distintos"
            )
        if not distancia_km.is_finite() or distancia_km <= 0:
            raise ErroValidacao(
                f"peso da aresta deve ser finito e positivo. Recebido '{distancia_km}'"
            )
        if origem_id not in self._adj or destino_id not in self._adj:
            raise ErroValidacao(
                f"conexao referencia local inexistente: {origem_id} -> {destino_id}"
            )

        par = tuple(sorted((origem_id, destino_id)))
        if par in self._pares:
            raise ErroValidacao(
                f"conexao duplicada entre {origem_id} e {destino_id} "
                "(incluindo o sentido invertido)"
            )

        self._pares.add(par)
        self._adj[origem_id].append((destino_id, distancia_km))
        self._adj[destino_id].append((origem_id, distancia_km))
        # Ordenar vizinhos por id deixa o Dijkstra deterministico em empates.
        self._adj[origem_id].sort(key=lambda item: item[0])
        self._adj[destino_id].sort(key=lambda item: item[0])

    def vizinhos(self, local_id: int) -> list[tuple[int, Decimal]]:
        """Devolve copia da lista para o calculo nao alterar o grafo."""
        return list(self._adj[local_id])

    def quantidade_arestas(self) -> int:
        return len(self._pares)


def construir_grafo(locais: list[Local], conexoes: list[Conexao]) -> Grafo:
    grafo = Grafo()
    for local in locais:
        grafo.adicionar_vertice(local.id)
    for conexao in conexoes:
        grafo.adicionar_aresta(conexao.origem_id, conexao.destino_id, conexao.distancia_km)
    return grafo
