"""Testes da mochila 0/1 por tabulacao."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from decimal import Decimal

from realimenta.excecoes import ErroConsulta, ErroValidacao, TabelaMuitoGrande
from realimenta.mochila import mochila_0_1
from realimenta.modelos import ItemMochila
from realimenta.validacoes import kg_para_unidades, unidades_para_kg
from tests.auxiliar import valor_otimo_por_enumeracao


class TestMochila(unittest.TestCase):
    def test_solucao_otima_conhecida(self) -> None:
        itens = [
            ItemMochila(id=1, peso=25, valor=8),
            ItemMochila(id=2, peso=15, valor=6),
            ItemMochila(id=3, peso=50, valor=9),
        ]
        resultado = mochila_0_1(itens, 40)
        self.assertEqual(resultado.valor_total, 14)
        self.assertEqual(set(resultado.ids_escolhidos), {1, 2})
        self.assertEqual(resultado.peso_total, 40)

    def test_capacidade_zero(self) -> None:
        itens = [ItemMochila(id=1, peso=10, valor=5)]
        resultado = mochila_0_1(itens, 0)
        self.assertEqual(resultado.ids_escolhidos, [])
        self.assertEqual(resultado.valor_total, 0)
        self.assertEqual(resultado.peso_total, 0)
        self.assertEqual(resultado.capacidade_restante, 0)

    def test_lista_vazia(self) -> None:
        resultado = mochila_0_1([], 50)
        self.assertEqual(resultado.ids_escolhidos, [])
        self.assertEqual(resultado.valor_total, 0)
        self.assertEqual(resultado.capacidade_restante, 50)

    def test_nenhum_lote_cabe(self) -> None:
        itens = [
            ItemMochila(id=1, peso=80, valor=9),
            ItemMochila(id=2, peso=90, valor=10),
        ]
        resultado = mochila_0_1(itens, 50)
        self.assertEqual(resultado.ids_escolhidos, [])
        self.assertEqual(resultado.valor_total, 0)
        self.assertEqual(resultado.capacidade_restante, 50)

    def test_preenchimento_exato(self) -> None:
        itens = [
            ItemMochila(id=1, peso=40, valor=5),
            ItemMochila(id=2, peso=60, valor=6),
        ]
        resultado = mochila_0_1(itens, 100)
        self.assertEqual(set(resultado.ids_escolhidos), {1, 2})
        self.assertEqual(resultado.peso_total, 100)
        self.assertEqual(resultado.capacidade_restante, 0)

    def test_cada_lote_no_maximo_uma_vez(self) -> None:
        # Se o item pudesse repetir, 3 vezes o item 1 caberiam (valor 30).
        itens = [ItemMochila(id=1, peso=30, valor=10)]
        resultado = mochila_0_1(itens, 90)
        self.assertEqual(resultado.ids_escolhidos, [1])
        self.assertEqual(resultado.valor_total, 10)

    def test_peso_nao_ultrapassa_capacidade(self) -> None:
        itens = [
            ItemMochila(id=1, peso=40, valor=8),
            ItemMochila(id=2, peso=50, valor=9),
            ItemMochila(id=3, peso=30, valor=6),
            ItemMochila(id=4, peso=20, valor=5),
        ]
        resultado = mochila_0_1(itens, 70)
        self.assertLessEqual(resultado.peso_total, 70)
        self.assertEqual(resultado.capacidade_restante, 70 - resultado.peso_total)

    def test_prioridade_corresponde_aos_itens(self) -> None:
        itens = [
            ItemMochila(id=1, peso=20, valor=4),
            ItemMochila(id=2, peso=30, valor=7),
            ItemMochila(id=3, peso=25, valor=5),
        ]
        resultado = mochila_0_1(itens, 50)
        por_id = {item.id: item for item in itens}
        soma = sum(por_id[item_id].valor for item_id in resultado.ids_escolhidos)
        self.assertEqual(resultado.valor_total, soma)

    def test_enumeracao_independente_em_instancia_pequena(self) -> None:
        itens = [
            ItemMochila(id=1, peso=12, valor=4),
            ItemMochila(id=2, peso=7, valor=3),
            ItemMochila(id=3, peso=11, valor=5),
            ItemMochila(id=4, peso=8, valor=6),
            ItemMochila(id=5, peso=5, valor=2),
        ]
        capacidade = 20
        resultado = mochila_0_1(itens, capacidade)
        otimo = valor_otimo_por_enumeracao(itens, capacidade)
        self.assertEqual(resultado.valor_total, otimo)
        # Nao comparamos o conjunto exato: pode haver mais de uma solucao otima.

    def test_guloso_por_maior_prioridade_e_pior(self) -> None:
        """Capacidade 10 kg. Guloso pega A (10); o otimo pega B e C (18)."""
        itens = [
            ItemMochila(id=1, peso=kg_para_unidades(Decimal("6")), valor=10),
            ItemMochila(id=2, peso=kg_para_unidades(Decimal("5")), valor=9),
            ItemMochila(id=3, peso=kg_para_unidades(Decimal("5")), valor=9),
        ]
        resultado = mochila_0_1(itens, kg_para_unidades(Decimal("10")))
        self.assertEqual(resultado.valor_total, 18)
        self.assertEqual(set(resultado.ids_escolhidos), {2, 3})
        self.assertNotEqual(resultado.ids_escolhidos, [1])

    def test_desempate_deterministico_nao_inclui_item_atual(self) -> None:
        # Dois itens de mesmo valor e mesmo peso: empate na transicao mantem o de menor id,
        # porque o item atual so entra se melhorar o valor.
        itens = [
            ItemMochila(id=1, peso=10, valor=5),
            ItemMochila(id=2, peso=10, valor=5),
        ]
        resultado = mochila_0_1(itens, 10)
        self.assertEqual(resultado.ids_escolhidos, [1])
        self.assertEqual(resultado.valor_total, 5)
        repetido = mochila_0_1(list(reversed(itens)), 10)
        self.assertEqual(repetido.ids_escolhidos, [1])

    def test_limite_de_celulas(self) -> None:
        itens = [
            ItemMochila(id=1, peso=1, valor=1),
            ItemMochila(id=2, peso=1, valor=1),
        ]
        with self.assertRaises(TabelaMuitoGrande):
            mochila_0_1(itens, 100, limite_celulas=10)

    def test_tabela_exatamente_no_limite_e_aceita(self) -> None:
        # n=1, C=4 -> (1+1)*(4+1) = 10 celulas.
        itens = [ItemMochila(id=1, peso=1, valor=1)]
        resultado = mochila_0_1(itens, 4, limite_celulas=10)
        self.assertEqual(resultado.ids_escolhidos, [1])

    def test_tabela_uma_celula_acima_do_limite_e_rejeitada(self) -> None:
        itens = [ItemMochila(id=1, peso=1, valor=1)]
        with self.assertRaises(TabelaMuitoGrande) as contexto:
            mochila_0_1(itens, 4, limite_celulas=9)
        self.assertIn("10 celulas", str(contexto.exception))

    def test_um_item_capacidade_4_limite_5_rejeita(self) -> None:
        itens = [ItemMochila(id=1, peso=1, valor=1)]
        with self.assertRaises(TabelaMuitoGrande) as contexto:
            mochila_0_1(itens, 4, limite_celulas=5)
        mensagem = str(contexto.exception)
        self.assertIn("10 celulas", mensagem)
        self.assertIn("(n+1)*(C+1)", mensagem)

    def test_capacidade_negativa(self) -> None:
        with self.assertRaises(ErroConsulta):
            mochila_0_1([], -1)


class TestConversaoKg(unittest.TestCase):
    def test_conversao_exata(self) -> None:
        self.assertEqual(kg_para_unidades(Decimal("2.5")), 25)
        self.assertEqual(kg_para_unidades(Decimal("0.1")), 1)
        self.assertEqual(unidades_para_kg(25), Decimal("2.5"))
        self.assertEqual(unidades_para_kg(1), Decimal("0.1"))

    def test_rejeita_precisao_incompativel(self) -> None:
        with self.assertRaises(ErroValidacao):
            kg_para_unidades(Decimal("1.25"))

    def test_nao_usa_float_no_texto(self) -> None:
        # Decimal construido de texto preserva 0.1; float nao e usado.
        self.assertEqual(kg_para_unidades(Decimal("0.3")), 3)


if __name__ == "__main__":
    unittest.main()
