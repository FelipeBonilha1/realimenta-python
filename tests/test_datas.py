"""Testes da convencao de data sem fuso e do argumento --referencia."""

import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from realimenta.carregamento import carregar_lotes
from realimenta.excecoes import ErroValidacao
from realimenta.modelos import Local
from realimenta.validacoes import interpretar_data_iso

RAIZ = Path(__file__).resolve().parent.parent


class TestDatasSemFuso(unittest.TestCase):
    def test_data_valida_sem_fuso(self) -> None:
        data = interpretar_data_iso("2026-11-11T12:00:00", "referencia")
        self.assertEqual(data, datetime(2026, 11, 11, 12, 0, 0))
        self.assertIsNone(data.tzinfo)

    def test_data_com_deslocamento_menos_tres(self) -> None:
        with self.assertRaises(ErroValidacao) as contexto:
            interpretar_data_iso("2026-11-11T12:00:00-03:00", "referencia")
        mensagem = str(contexto.exception)
        self.assertIn("sem fuso", mensagem)
        self.assertIn("2026-11-11T12:00:00", mensagem)
        self.assertIn("-03:00", mensagem)

    def test_data_com_sufixo_z(self) -> None:
        with self.assertRaises(ErroValidacao) as contexto:
            interpretar_data_iso("2026-11-11T12:00:00Z", "referencia")
        mensagem = str(contexto.exception)
        self.assertIn("sem fuso", mensagem)
        self.assertIn("Z", mensagem)

    def test_data_invalida(self) -> None:
        with self.assertRaises(ErroValidacao) as contexto:
            interpretar_data_iso("11/11/2026 12:00", "referencia")
        mensagem = str(contexto.exception)
        self.assertIn("Formato aceito", mensagem)
        self.assertIn("11/11/2026", mensagem)

    def test_prazo_com_fuso_no_csv(self) -> None:
        locais = [Local(1, "Padaria", "ESTABELECIMENTO")]
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = Path(tmp) / "lotes.csv"
            arquivo.write_text(
                "id,estabelecimento_id,descricao,quantidade_kg,prazo_aproveitamento,prioridade\n"
                "1,1,pao,1.0,2026-11-11T18:00:00-03:00,5\n",
                encoding="utf-8",
            )
            with self.assertRaises(ErroValidacao) as contexto:
                carregar_lotes(arquivo, locais)
            mensagem = str(contexto.exception)
            self.assertIn("prazo_aproveitamento", mensagem)
            self.assertIn("sem fuso", mensagem)
            self.assertIn("linha 2", mensagem)

    def test_comando_referencia_com_fuso_sem_traceback(self) -> None:
        processo = subprocess.run(
            [
                sys.executable,
                str(RAIZ / "main.py"),
                "--demonstracao",
                "--referencia",
                "2026-11-11T12:00:00-03:00",
            ],
            cwd=str(RAIZ),
            capture_output=True,
            text=True,
        )
        saida = processo.stdout + processo.stderr
        self.assertNotEqual(processo.returncode, 0)
        self.assertIn("Falha ao iniciar", saida)
        self.assertIn("sem fuso", saida)
        self.assertNotIn("Traceback", saida)
        self.assertNotIn("TypeError", saida)


if __name__ == "__main__":
    unittest.main()
