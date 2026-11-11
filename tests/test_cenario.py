"""Confere os exemplos do cenario de demonstracao contra os algoritmos."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime
from decimal import Decimal

from realimenta.carregamento import carregar_sistema
from realimenta.dijkstra import menor_caminho
from realimenta.modelos import ItemMochila, REFERENCIA_DEMONSTRACAO
from realimenta.selecao import selecionar_lotes
from realimenta.validacoes import kg_para_unidades
from tests.auxiliar import valor_otimo_por_enumeracao


class TestCenarioDemonstracao(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.locais, cls.conexoes, cls.lotes, cls.grafo, cls.locais_por_id = carregar_sistema()

    def test_menor_caminho_instituto_padaria(self) -> None:
        resultado = menor_caminho(self.grafo, 6, 1)
        self.assertTrue(resultado.alcancavel)
        self.assertEqual(resultado.caminho, [6, 9, 1])
        self.assertEqual(resultado.distancia_km, Decimal("7.6"))

    def test_indireto_menor_que_aresta_direta(self) -> None:
        resultado = menor_caminho(self.grafo, 1, 4)
        self.assertEqual(resultado.caminho, [1, 9, 8, 7, 4])
        self.assertEqual(resultado.distancia_km, Decimal("7.9"))

    def test_padaria_isolada_inacessivel(self) -> None:
        resultado = menor_caminho(self.grafo, 6, 5)
        self.assertFalse(resultado.alcancavel)
        self.assertIsNone(resultado.distancia_km)

    def test_selecao_10kg_na_referencia_padrao(self) -> None:
        resultado = selecionar_lotes(
            self.lotes,
            self.locais_por_id,
            self.grafo,
            instituicao_id=6,
            capacidade_kg=Decimal("10.0"),
            referencia=REFERENCIA_DEMONSTRACAO,
        )
        self.assertEqual(resultado.soma_prioridades, 29)
        self.assertEqual([lote.id for lote in resultado.escolhidos], [2, 3, 4, 9])
        self.assertEqual(resultado.peso_total_kg, Decimal("9.6"))
        excluidos_ids = {item.lote.id for item in resultado.excluidos}
        self.assertEqual(excluidos_ids, {7, 8, 10})
        nao_selecionados = {lote.id for lote in resultado.elegiveis_nao_selecionados}
        self.assertEqual(nao_selecionados, {1, 5, 6})

        itens = [
            ItemMochila(id=lote.id, peso=kg_para_unidades(lote.quantidade_kg), valor=lote.prioridade)
            for lote in resultado.escolhidos + resultado.elegiveis_nao_selecionados
        ]
        self.assertEqual(
            resultado.soma_prioridades,
            valor_otimo_por_enumeracao(itens, kg_para_unidades(Decimal("10.0"))),
        )

    def test_referencia_posterior_reduz_elegiveis(self) -> None:
        depois = datetime.fromisoformat("2026-11-12T09:00:00")
        resultado = selecionar_lotes(
            self.lotes,
            self.locais_por_id,
            self.grafo,
            instituicao_id=6,
            capacidade_kg=Decimal("10.0"),
            referencia=depois,
        )
        ids_escolhidos = {lote.id for lote in resultado.escolhidos}
        ids_excluidos = {item.lote.id for item in resultado.excluidos}
        self.assertNotIn(1, ids_escolhidos)
        self.assertIn(1, ids_excluidos)


class TestImportacaoNaoAbreMenu(unittest.TestCase):
    def test_importar_main_nao_dispara_menu(self) -> None:
        import main as modulo_main

        self.assertTrue(hasattr(modulo_main, "main"))
        self.assertTrue(callable(modulo_main.main))


if __name__ == "__main__":
    unittest.main()
