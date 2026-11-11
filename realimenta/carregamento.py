"""Leitura dos CSV a partir da pasta do projeto, independente do diretorio atual."""

import csv
from pathlib import Path

from realimenta.excecoes import ErroValidacao
from realimenta.grafo import Grafo, construir_grafo
from realimenta.modelos import Conexao, Local, Lote
from realimenta.validacoes import (
    exigir_nao_vazio,
    interpretar_data_iso,
    interpretar_distancia_km,
    interpretar_id,
    interpretar_prioridade,
    interpretar_quantidade_kg,
    interpretar_tipo_local,
)

RegistroCsv = tuple[int, dict[str, str]]

CABECALHO_LOCAIS = ("id", "nome", "tipo")
CABECALHO_CONEXOES = ("origem_id", "destino_id", "distancia_km")
CABECALHO_LOTES = (
    "id",
    "estabelecimento_id",
    "descricao",
    "quantidade_kg",
    "prazo_aproveitamento",
    "prioridade",
)


def diretorio_projeto() -> Path:
    """Pasta raiz do projeto (onde estao main.py e dados/), a partir deste arquivo."""
    return Path(__file__).resolve().parent.parent


def diretorio_dados() -> Path:
    return diretorio_projeto() / "dados"


def _ler_csv(caminho: Path, esperado: tuple[str, ...]) -> tuple[str, list[RegistroCsv]]:
    """Le CSV UTF-8 (com ou sem BOM). Valida cabecalho antes das linhas.

    Campos vazios sao preservados para as validacoes de cada coluna.
    Campos a mais ou a menos geram ErroValidacao com arquivo e linha.
    """
    nome = str(caminho)
    if not caminho.exists():
        raise ErroValidacao(f"arquivo nao encontrado: {caminho}", arquivo=nome)

    try:
        arquivo = caminho.open("r", encoding="utf-8-sig", newline="")
    except OSError as erro:
        raise ErroValidacao(f"nao foi possivel abrir o arquivo: {erro}", arquivo=nome) from erro

    try:
        with arquivo:
            try:
                leitor = csv.reader(arquivo)
                try:
                    cabecalho_bruto = next(leitor)
                except StopIteration:
                    raise ErroValidacao("arquivo sem cabecalho", arquivo=nome, linha=1)
                numero_cabecalho = leitor.line_num
                cabecalhos = [coluna.strip() for coluna in cabecalho_bruto]
                if tuple(cabecalhos) != esperado:
                    raise ErroValidacao(
                        f"cabecalho invalido. Esperado {list(esperado)}; encontrado {cabecalhos}",
                        arquivo=nome,
                        linha=numero_cabecalho,
                    )

                registros: list[RegistroCsv] = []
                for registro in leitor:
                    numero_linha = leitor.line_num
                    encontrados = len(registro)
                    esperados = len(cabecalhos)
                    if encontrados > esperados:
                        raise ErroValidacao(
                            f"linha com campos excedentes: esperados {esperados}, encontrados {encontrados}",
                            arquivo=nome,
                            linha=numero_linha,
                        )
                    if encontrados < esperados:
                        raise ErroValidacao(
                            f"linha com campos ausentes: esperados {esperados}, encontrados {encontrados}",
                            arquivo=nome,
                            linha=numero_linha,
                        )
                    # Nao usa strip() no valor: campo vazio permanece vazio para as validacoes.
                    linha = {cabecalhos[indice]: registro[indice] for indice in range(esperados)}
                    registros.append((numero_linha, linha))
            except csv.Error as erro:
                numero = getattr(leitor, "line_num", None)
                raise ErroValidacao(
                    f"erro ao interpretar o CSV: {erro}",
                    arquivo=nome,
                    linha=numero,
                ) from erro
    except UnicodeDecodeError as erro:
        raise ErroValidacao(
            "arquivo nao esta em UTF-8 valido (aceito UTF-8 com ou sem BOM)",
            arquivo=nome,
        ) from erro

    return nome, registros


def carregar_locais(caminho: Path | None = None) -> list[Local]:
    arquivo = caminho or (diretorio_dados() / "locais.csv")
    nome, registros = _ler_csv(arquivo, CABECALHO_LOCAIS)

    locais: list[Local] = []
    vistos: set[int] = set()
    for indice, linha in registros:
        local_id = interpretar_id(linha.get("id", ""), "id", nome, indice)
        if local_id in vistos:
            raise ErroValidacao(f"id de local duplicado: {local_id}", nome, indice)
        vistos.add(local_id)
        nome_local = exigir_nao_vazio(linha.get("nome", ""), "nome", nome, indice)
        tipo = interpretar_tipo_local(linha.get("tipo", ""), nome, indice)
        locais.append(Local(id=local_id, nome=nome_local, tipo=tipo))
    if not locais:
        raise ErroValidacao("nenhum local cadastrado", nome, 1)
    return locais


def carregar_conexoes(caminho: Path | None, locais: list[Local]) -> list[Conexao]:
    arquivo = caminho or (diretorio_dados() / "conexoes.csv")
    nome, registros = _ler_csv(arquivo, CABECALHO_CONEXOES)

    ids_locais = {local.id for local in locais}
    pares: set[tuple[int, int]] = set()
    conexoes: list[Conexao] = []

    for indice, linha in registros:
        origem_id = interpretar_id(linha.get("origem_id", ""), "origem_id", nome, indice)
        destino_id = interpretar_id(linha.get("destino_id", ""), "destino_id", nome, indice)
        distancia = interpretar_distancia_km(linha.get("distancia_km", ""), nome, indice)

        if origem_id not in ids_locais:
            raise ErroValidacao(f"origem_id {origem_id} nao existe em locais.csv", nome, indice)
        if destino_id not in ids_locais:
            raise ErroValidacao(f"destino_id {destino_id} nao existe em locais.csv", nome, indice)
        if origem_id == destino_id:
            raise ErroValidacao(
                f"conexao de um local para ele mesmo (id {origem_id}) nao e permitida",
                nome,
                indice,
            )

        par = tuple(sorted((origem_id, destino_id)))
        if par in pares:
            raise ErroValidacao(
                f"conexao duplicada entre {origem_id} e {destino_id} (sentido invertido tambem conta)",
                nome,
                indice,
            )
        pares.add(par)
        conexoes.append(Conexao(origem_id=origem_id, destino_id=destino_id, distancia_km=distancia))
    return conexoes


def carregar_lotes(caminho: Path | None, locais: list[Local]) -> list[Lote]:
    arquivo = caminho or (diretorio_dados() / "lotes.csv")
    nome, registros = _ler_csv(arquivo, CABECALHO_LOTES)

    estabelecimentos = {local.id for local in locais if local.tipo == "ESTABELECIMENTO"}
    vistos: set[int] = set()
    lotes: list[Lote] = []

    for indice, linha in registros:
        lote_id = interpretar_id(linha.get("id", ""), "id", nome, indice)
        if lote_id in vistos:
            raise ErroValidacao(f"id de lote duplicado: {lote_id}", nome, indice)
        vistos.add(lote_id)

        estabelecimento_id = interpretar_id(
            linha.get("estabelecimento_id", ""),
            "estabelecimento_id",
            nome,
            indice,
        )
        if estabelecimento_id not in estabelecimentos:
            raise ErroValidacao(
                f"estabelecimento_id {estabelecimento_id} nao referencia um local do tipo ESTABELECIMENTO",
                nome,
                indice,
            )

        descricao = exigir_nao_vazio(linha.get("descricao", ""), "descricao", nome, indice)
        quantidade = interpretar_quantidade_kg(linha.get("quantidade_kg", ""), nome, indice)
        prazo = interpretar_data_iso(
            linha.get("prazo_aproveitamento", ""),
            "prazo_aproveitamento",
            nome,
            indice,
        )
        prioridade = interpretar_prioridade(linha.get("prioridade", ""), nome, indice)
        lotes.append(
            Lote(
                id=lote_id,
                estabelecimento_id=estabelecimento_id,
                descricao=descricao,
                quantidade_kg=quantidade,
                prazo_aproveitamento=prazo,
                prioridade=prioridade,
            )
        )
    return lotes


def carregar_sistema(
    pasta_dados: Path | None = None,
) -> tuple[list[Local], list[Conexao], list[Lote], Grafo, dict[int, Local]]:
    pasta = pasta_dados or diretorio_dados()
    locais = carregar_locais(pasta / "locais.csv")
    conexoes = carregar_conexoes(pasta / "conexoes.csv", locais)
    lotes = carregar_lotes(pasta / "lotes.csv", locais)
    grafo = construir_grafo(locais, conexoes)
    locais_por_id = {local.id: local for local in locais}
    return locais, conexoes, lotes, grafo, locais_por_id
