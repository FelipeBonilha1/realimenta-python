"""Testes de leitura e validacao dos CSV."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from realimenta.carregamento import carregar_conexoes, carregar_locais, carregar_lotes, carregar_sistema
from realimenta.excecoes import ErroValidacao
from realimenta.modelos import Local


def gravar(pasta: Path, nome: str, conteudo: str) -> Path:
    caminho = pasta / nome
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


class TestCarregamento(unittest.TestCase):
    def test_id_duplicado(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pasta = Path(tmp)
            arquivo = gravar(
                pasta,
                "locais.csv",
                "id,nome,tipo\n1,Padaria,ESTABELECIMENTO\n1,Mercado,ESTABELECIMENTO\n",
            )
            with self.assertRaises(ErroValidacao) as contexto:
                carregar_locais(arquivo)
            self.assertIn("duplicado", str(contexto.exception))
            self.assertIn("linha 3", str(contexto.exception))

    def test_referencia_inexistente_na_conexao(self) -> None:
        locais = [Local(1, "Padaria", "ESTABELECIMENTO"), Local(2, "Instituto", "INSTITUICAO")]
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = gravar(
                Path(tmp),
                "conexoes.csv",
                "origem_id,destino_id,distancia_km\n1,99,1.5\n",
            )
            with self.assertRaises(ErroValidacao) as contexto:
                carregar_conexoes(arquivo, locais)
            self.assertIn("99", str(contexto.exception))

    def test_cabecalho_invalido(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = gravar(Path(tmp), "locais.csv", "codigo,titulo\n1,Padaria\n")
            with self.assertRaises(ErroValidacao) as contexto:
                carregar_locais(arquivo)
            self.assertIn("cabecalho invalido", str(contexto.exception))

    def test_arquivo_inexistente(self) -> None:
        with self.assertRaises(ErroValidacao) as contexto:
            carregar_locais(Path("nao_existe_locais.csv"))
        self.assertIn("nao encontrado", str(contexto.exception))

    def test_conexao_duplicada_invertida(self) -> None:
        locais = [
            Local(1, "Padaria", "ESTABELECIMENTO"),
            Local(2, "Instituto", "INSTITUICAO"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = gravar(
                Path(tmp),
                "conexoes.csv",
                "origem_id,destino_id,distancia_km\n1,2,1.5\n2,1,3.0\n",
            )
            with self.assertRaises(ErroValidacao) as contexto:
                carregar_conexoes(arquivo, locais)
            self.assertIn("duplicada", str(contexto.exception))

    def test_lote_de_nao_estabelecimento(self) -> None:
        locais = [
            Local(1, "Padaria", "ESTABELECIMENTO"),
            Local(2, "Instituto", "INSTITUICAO"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = gravar(
                Path(tmp),
                "lotes.csv",
                "id,estabelecimento_id,descricao,quantidade_kg,prazo_aproveitamento,prioridade\n"
                "1,2,pao,1.0,2026-11-11T18:00:00,5\n",
            )
            with self.assertRaises(ErroValidacao) as contexto:
                carregar_lotes(arquivo, locais)
            self.assertIn("ESTABELECIMENTO", str(contexto.exception))

    def test_linha_com_campo_extra(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = gravar(
                Path(tmp),
                "locais.csv",
                "id,nome,tipo\n1,Padaria,ESTABELECIMENTO,extra\n",
            )
            with self.assertRaises(ErroValidacao) as contexto:
                carregar_locais(arquivo)
            mensagem = str(contexto.exception)
            self.assertIn("campos excedentes", mensagem)
            self.assertIn("linha 2", mensagem)

    def test_linha_com_campo_ausente(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = gravar(
                Path(tmp),
                "locais.csv",
                "id,nome,tipo\n1,Padaria\n",
            )
            with self.assertRaises(ErroValidacao) as contexto:
                carregar_locais(arquivo)
            mensagem = str(contexto.exception)
            self.assertIn("campos ausentes", mensagem)
            self.assertIn("linha 2", mensagem)

    def test_campo_obrigatorio_vazio(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = gravar(
                Path(tmp),
                "locais.csv",
                "id,nome,tipo\n1,,ESTABELECIMENTO\n",
            )
            with self.assertRaises(ErroValidacao) as contexto:
                carregar_locais(arquivo)
            mensagem = str(contexto.exception)
            self.assertIn("campo 'nome' vazio", mensagem)
            self.assertIn("linha 2", mensagem)

    def test_arquivo_com_codificacao_invalida(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = Path(tmp) / "locais.csv"
            arquivo.write_bytes(b"id,nome,tipo\n1,\xff,ESTABELECIMENTO\n")
            with self.assertRaises(ErroValidacao) as contexto:
                carregar_locais(arquivo)
            self.assertIn("UTF-8", str(contexto.exception))

    def test_csv_com_virgula_entre_aspas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = gravar(
                Path(tmp),
                "locais.csv",
                'id,nome,tipo\n1,"Padaria da Vila, Centro",ESTABELECIMENTO\n',
            )
            locais = carregar_locais(arquivo)
            self.assertEqual(len(locais), 1)
            self.assertEqual(locais[0].nome, "Padaria da Vila, Centro")

    def test_arquivo_valido_com_bom(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = Path(tmp) / "locais.csv"
            conteudo = "id,nome,tipo\n1,Padaria,ESTABELECIMENTO\n"
            arquivo.write_bytes(b"\xef\xbb\xbf" + conteudo.encode("utf-8"))
            locais = carregar_locais(arquivo)
            self.assertEqual(locais[0].id, 1)
            self.assertEqual(locais[0].nome, "Padaria")

    def test_dados_oficiais_do_projeto_carregam(self) -> None:
        locais, conexoes, lotes, grafo, locais_por_id = carregar_sistema()
        self.assertGreaterEqual(len([item for item in locais if item.tipo == "ESTABELECIMENTO"]), 4)
        self.assertEqual(len([item for item in locais if item.tipo == "INSTITUICAO"]), 1)
        self.assertTrue(any(item.tipo == "APOIO" for item in locais))
        self.assertTrue(grafo.contem(5))
        self.assertEqual(grafo.vizinhos(5), [])
        self.assertEqual(len(lotes), 10)
        self.assertIn(6, locais_por_id)
        self.assertGreaterEqual(len(conexoes), 2)


if __name__ == "__main__":
    unittest.main()
