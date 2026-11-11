"""Testes do grafo e do Dijkstra."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from decimal import Decimal

from realimenta.dijkstra import menor_caminho
from realimenta.excecoes import ErroConsulta, ErroValidacao
from realimenta.grafo import Grafo
from tests.auxiliar import grafo_de


class TestGrafo(unittest.TestCase):
    def test_rejeita_peso_nao_positivo(self) -> None:
        grafo = Grafo()
        grafo.adicionar_vertice(1)
        grafo.adicionar_vertice(2)
        with self.assertRaises(ErroValidacao):
            grafo.adicionar_aresta(1, 2, Decimal("0"))
        with self.assertRaises(ErroValidacao):
            grafo.adicionar_aresta(1, 2, Decimal("-1.5"))

    def test_rejeita_peso_infinito_ou_nan(self) -> None:
        grafo = Grafo()
        grafo.adicionar_vertice(1)
        grafo.adicionar_vertice(2)
        with self.assertRaises(ErroValidacao):
            grafo.adicionar_aresta(1, 2, Decimal("Infinity"))
        with self.assertRaises(ErroValidacao):
            grafo.adicionar_aresta(1, 2, Decimal("NaN"))

    def test_rejeita_laco(self) -> None:
        grafo = Grafo()
        grafo.adicionar_vertice(1)
        with self.assertRaises(ErroValidacao):
            grafo.adicionar_aresta(1, 1, Decimal("2.0"))

    def test_rejeita_duplicata_invertida(self) -> None:
        grafo = Grafo()
        grafo.adicionar_vertice(1)
        grafo.adicionar_vertice(2)
        grafo.adicionar_aresta(1, 2, Decimal("3.0"))
        with self.assertRaises(ErroValidacao):
            grafo.adicionar_aresta(2, 1, Decimal("4.0"))

    def test_mao_dupla(self) -> None:
        grafo = grafo_de([(1, 2, "2.5")])
        vizinhos_1 = grafo.vizinhos(1)
        vizinhos_2 = grafo.vizinhos(2)
        self.assertEqual(vizinhos_1, [(2, Decimal("2.5"))])
        self.assertEqual(vizinhos_2, [(1, Decimal("2.5"))])

    def test_calculo_nao_altera_grafo(self) -> None:
        grafo = grafo_de([(1, 2, "1.0"), (2, 3, "1.0")])
        antes = grafo.vizinhos(1)
        menor_caminho(grafo, 1, 3)
        self.assertEqual(grafo.vizinhos(1), antes)


class TestDijkstra(unittest.TestCase):
    def setUp(self) -> None:
        # 1 --2-- 2 --2-- 3
        # 1 ------10----- 3  (direto pior)
        # 4 isolado
        self.grafo = grafo_de(
            [
                (1, 2, "2.0"),
                (2, 3, "2.0"),
                (1, 3, "10.0"),
                (2, 5, "1.0"),
            ]
        )
        self.grafo.adicionar_vertice(4)

    def test_menor_caminho_conhecido(self) -> None:
        resultado = menor_caminho(self.grafo, 1, 5)
        self.assertTrue(resultado.alcancavel)
        self.assertEqual(resultado.caminho, [1, 2, 5])
        self.assertEqual(resultado.distancia_km, Decimal("3.0"))

    def test_indireto_menor_que_direto(self) -> None:
        resultado = menor_caminho(self.grafo, 1, 3)
        self.assertEqual(resultado.caminho, [1, 2, 3])
        self.assertEqual(resultado.distancia_km, Decimal("4.0"))
        self.assertNotEqual(resultado.caminho, [1, 3])

    def test_origem_igual_destino(self) -> None:
        resultado = menor_caminho(self.grafo, 3, 3)
        self.assertTrue(resultado.alcancavel)
        self.assertEqual(resultado.caminho, [3])
        self.assertEqual(resultado.distancia_km, Decimal("0"))

    def test_destino_inacessivel(self) -> None:
        resultado = menor_caminho(self.grafo, 1, 4)
        self.assertFalse(resultado.alcancavel)
        self.assertEqual(resultado.caminho, [])
        self.assertIsNone(resultado.distancia_km)

    def test_identificador_inexistente(self) -> None:
        with self.assertRaises(ErroConsulta):
            menor_caminho(self.grafo, 99, 1)
        with self.assertRaises(ErroConsulta):
            menor_caminho(self.grafo, 1, 99)

    def test_empate_deterministico(self) -> None:
        # Dois caminhos de custo 4: 1-4-2 e 1-5-2. O menor id intermediario deve vencer.
        grafo = grafo_de(
            [
                (1, 4, "2.0"),
                (4, 2, "2.0"),
                (1, 5, "2.0"),
                (5, 2, "2.0"),
            ]
        )
        primeiro = menor_caminho(grafo, 1, 2)
        segundo = menor_caminho(grafo, 1, 2)
        self.assertEqual(primeiro.caminho, segundo.caminho)
        self.assertEqual(primeiro.caminho, [1, 4, 2])
        self.assertEqual(primeiro.distancia_km, Decimal("4.0"))


if __name__ == "__main__":
    unittest.main()
