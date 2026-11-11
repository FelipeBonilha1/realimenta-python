"""Testes de prazo e conectividade antes da mochila."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime
from decimal import Decimal

from realimenta.elegibilidade import MOTIVO_DESCONECTADO, MOTIVO_PRAZO, classificar_lotes
from realimenta.excecoes import ErroConsulta
from realimenta.modelos import Lote
from tests.auxiliar import grafo_de, locais_simples


def lote(
    lote_id: int,
    estabelecimento_id: int,
    prazo: str,
    quantidade: str = "1.0",
    prioridade: int = 5,
) -> Lote:
    return Lote(
        id=lote_id,
        estabelecimento_id=estabelecimento_id,
        descricao=f"lote {lote_id}",
        quantidade_kg=Decimal(quantidade),
        prazo_aproveitamento=datetime.fromisoformat(prazo),
        prioridade=prioridade,
    )


class TestElegibilidade(unittest.TestCase):
    def setUp(self) -> None:
        self.referencia = datetime.fromisoformat("2026-11-11T12:00:00")
        self.locais = locais_simples()
        # 6-7-1 e 6-7-2; 5 fica desconectado.
        self.grafo = grafo_de([(6, 7, "1.0"), (7, 1, "1.0"), (7, 2, "1.0")])
        self.grafo.adicionar_vertice(5)

    def test_lote_vencido(self) -> None:
        lotes = [lote(1, 1, "2026-11-11T11:00:00")]
        elegiveis, excluidos = classificar_lotes(
            lotes, self.locais, self.grafo, 6, self.referencia
        )
        self.assertEqual(elegiveis, [])
        self.assertEqual(len(excluidos), 1)
        self.assertEqual(excluidos[0].motivo, MOTIVO_PRAZO)

    def test_prazo_igual_a_referencia(self) -> None:
        lotes = [lote(1, 1, "2026-11-11T12:00:00")]
        elegiveis, excluidos = classificar_lotes(
            lotes, self.locais, self.grafo, 6, self.referencia
        )
        self.assertEqual(elegiveis, [])
        self.assertEqual(excluidos[0].motivo, MOTIVO_PRAZO)

    def test_estabelecimento_desconectado(self) -> None:
        lotes = [lote(1, 5, "2026-11-11T18:00:00")]
        elegiveis, excluidos = classificar_lotes(
            lotes, self.locais, self.grafo, 6, self.referencia
        )
        self.assertEqual(elegiveis, [])
        self.assertEqual(excluidos[0].motivo, MOTIVO_DESCONECTADO)

    def test_referencia_temporal_alterada(self) -> None:
        lotes = [lote(1, 1, "2026-11-11T15:00:00")]
        elegiveis, _excluidos = classificar_lotes(
            lotes, self.locais, self.grafo, 6, self.referencia
        )
        self.assertEqual(len(elegiveis), 1)

        depois = datetime.fromisoformat("2026-11-11T16:00:00")
        elegiveis_depois, excluidos_depois = classificar_lotes(
            lotes, self.locais, self.grafo, 6, depois
        )
        self.assertEqual(elegiveis_depois, [])
        self.assertEqual(excluidos_depois[0].motivo, MOTIVO_PRAZO)

    def test_instituicao_com_tipo_errado(self) -> None:
        lotes = [lote(1, 1, "2026-11-11T18:00:00")]
        with self.assertRaises(ErroConsulta):
            classificar_lotes(lotes, self.locais, self.grafo, 1, self.referencia)

    def test_lote_elegivel(self) -> None:
        lotes = [lote(1, 1, "2026-11-11T18:00:00")]
        elegiveis, excluidos = classificar_lotes(
            lotes, self.locais, self.grafo, 6, self.referencia
        )
        self.assertEqual([item.id for item in elegiveis], [1])
        self.assertEqual(excluidos, [])


if __name__ == "__main__":
    unittest.main()
