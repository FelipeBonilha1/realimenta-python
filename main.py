"""Menu do ReAlimenta SP — Planejador de Coletas.

A entrada e a saida do terminal ficam neste arquivo. Os algoritmos
(Dijkstra e mochila) nao imprimem nada.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from decimal import Decimal

from realimenta.carregamento import carregar_sistema
from realimenta.dijkstra import menor_caminho
from realimenta.elegibilidade import classificar_lotes
from realimenta.excecoes import ErroConsulta, ErroValidacao, TabelaMuitoGrande
from realimenta.grafo import Grafo
from realimenta.mochila import mochila_0_1
from realimenta.modelos import (
    Conexao,
    ItemMochila,
    Local,
    Lote,
    REFERENCIA_DEMONSTRACAO,
    ResultadoSelecao,
)
from realimenta.selecao import selecionar_lotes
from realimenta.validacoes import (
    interpretar_capacidade_kg,
    interpretar_data_iso,
    interpretar_id,
    unidades_para_kg,
)


def formatar_decimal(valor: Decimal) -> str:
    texto = format(valor, "f")
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto if texto else "0"


def formatar_data(valor: datetime) -> str:
    return valor.strftime("%Y-%m-%dT%H:%M:%S")


def nome_local(locais_por_id: dict[int, Local], local_id: int) -> str:
    local = locais_por_id.get(local_id)
    if local is None:
        return f"id {local_id}"
    return f"{local.id} - {local.nome} ({local.tipo})"


def imprimir_referencia(referencia: datetime) -> None:
    print()
    print("Referencia temporal:", formatar_data(referencia))
    print("Essa data/hora e hora civil de Sao Paulo (nao usa o relogio da maquina).")
    print("Lotes com prazo menor ou igual a essa referencia sao considerados fora do prazo.")


def ler_linha(prompt: str) -> str | None:
    try:
        return input(prompt)
    except EOFError:
        print("\nEntrada encerrada (EOF).")
        return None
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuario.")
        return None


def pedir_id(prompt: str) -> int | None:
    bruto = ler_linha(prompt)
    if bruto is None:
        return None
    try:
        return interpretar_id(bruto, "id")
    except ErroValidacao as erro:
        print(f"Entrada invalida: {erro}")
        return None


def listar_locais_e_conexoes(
    locais: list[Local],
    conexoes: list[Conexao],
    grafo: Grafo,
) -> None:
    print()
    print("=== Locais ===")
    for local in locais:
        print(f"  id {local.id}: {local.nome} [{local.tipo}]")
    print()
    print("=== Conexoes (mao dupla, distancias simuladas em km) ===")
    if not conexoes:
        print("  nenhuma conexao cadastrada")
    for conexao in conexoes:
        print(
            f"  {conexao.origem_id} <-> {conexao.destino_id}: "
            f"{formatar_decimal(conexao.distancia_km)} km"
        )
    print()
    print(f"Vertices no grafo: {len(grafo.vertices())}")
    print(f"Arestas unicas: {grafo.quantidade_arestas()}")
    print("As distancias sao ficticias para o exercicio; nao sao medicoes verificadas.")


def consultar_menor_caminho(grafo: Grafo, locais_por_id: dict[int, Local]) -> None:
    origem = pedir_id("ID de origem: ")
    if origem is None:
        return
    destino = pedir_id("ID de destino: ")
    if destino is None:
        return
    _exibir_caminho(grafo, locais_por_id, origem, destino)


def _exibir_caminho(
    grafo: Grafo,
    locais_por_id: dict[int, Local],
    origem: int,
    destino: int,
) -> None:
    try:
        resultado = menor_caminho(grafo, origem, destino)
    except ErroConsulta as erro:
        print(f"Nao foi possivel consultar o caminho: {erro}")
        return

    print()
    print(f"Origem : {nome_local(locais_por_id, origem)}")
    print(f"Destino: {nome_local(locais_por_id, destino)}")
    if not resultado.alcancavel:
        print("Resultado: NAO EXISTE CAMINHO entre esses locais.")
        print("A distancia nao e zero; o destino e inacessivel no grafo.")
        return

    nomes = " -> ".join(nome_local(locais_por_id, item) for item in resultado.caminho)
    ids = " -> ".join(str(item) for item in resultado.caminho)
    print(f"Caminho (ids): {ids}")
    print(f"Caminho      : {nomes}")
    print(f"Distancia    : {formatar_decimal(resultado.distancia_km)} km")
    print(resultado.mensagem)
    print("Este resultado e o menor caminho entre DOIS locais, nao a melhor volta por todos.")


def listar_lotes_elegibilidade(
    lotes: list[Lote],
    locais_por_id: dict[int, Local],
    grafo: Grafo,
    referencia: datetime,
    instituicao_id: int | None = None,
) -> None:
    if instituicao_id is None:
        instituicao_id = pedir_id("ID da instituicao: ")
        if instituicao_id is None:
            return
    try:
        elegiveis, excluidos = classificar_lotes(
            lotes, locais_por_id, grafo, instituicao_id, referencia
        )
    except ErroConsulta as erro:
        print(f"Nao foi possivel classificar os lotes: {erro}")
        return

    print()
    print(f"Instituicao: {nome_local(locais_por_id, instituicao_id)}")
    imprimir_referencia(referencia)
    print()
    print("=== Lotes elegiveis ===")
    if not elegiveis:
        print("  nenhum lote elegivel")
    for lote in elegiveis:
        _imprimir_lote(lote, locais_por_id, "elegivel")
    print()
    print("=== Lotes excluidos ===")
    if not excluidos:
        print("  nenhum lote excluido")
    for item in excluidos:
        _imprimir_lote(item.lote, locais_por_id, item.motivo)
    print()
    print("A filtragem por conexao apenas evita estabelecimento inacessivel.")
    print("Ela nao escolhe a ordem de visitas nem otimiza combustivel ou tempo.")


def _imprimir_lote(lote: Lote, locais_por_id: dict[int, Local], situacao: str) -> None:
    print(
        f"  lote {lote.id}: {lote.descricao} | "
        f"{formatar_decimal(lote.quantidade_kg)} kg | "
        f"prioridade {lote.prioridade} | "
        f"prazo {formatar_data(lote.prazo_aproveitamento)} | "
        f"{nome_local(locais_por_id, lote.estabelecimento_id)} | "
        f"{situacao}"
    )


def selecionar_para_veiculo(
    lotes: list[Lote],
    locais_por_id: dict[int, Local],
    grafo: Grafo,
    referencia: datetime,
    instituicao_id: int | None = None,
    capacidade_kg: Decimal | None = None,
) -> None:
    if instituicao_id is None:
        instituicao_id = pedir_id("ID da instituicao: ")
        if instituicao_id is None:
            return
    if capacidade_kg is None:
        bruto = ler_linha("Capacidade do veiculo em kg (multiplo de 0.1; zero gera selecao vazia): ")
        if bruto is None:
            return
        try:
            capacidade_kg = interpretar_capacidade_kg(bruto)
        except ErroValidacao as erro:
            print(f"Capacidade invalida: {erro}")
            return
    try:
        resultado = selecionar_lotes(
            lotes,
            locais_por_id,
            grafo,
            instituicao_id,
            capacidade_kg,
            referencia,
        )
    except (ErroConsulta, ErroValidacao, TabelaMuitoGrande) as erro:
        print(f"Nao foi possivel selecionar os lotes: {erro}")
        return
    _exibir_selecao(resultado, locais_por_id, referencia)


def _exibir_selecao(
    resultado: ResultadoSelecao,
    locais_por_id: dict[int, Local],
    referencia: datetime,
) -> None:
    print()
    print(f"Instituicao: {nome_local(locais_por_id, resultado.instituicao_id)}")
    imprimir_referencia(referencia)
    print(f"Capacidade do veiculo: {formatar_decimal(resultado.capacidade_kg)} kg")
    print()
    print("=== Lotes escolhidos (mochila 0/1) ===")
    if not resultado.escolhidos:
        print("  nenhum lote selecionado")
    for lote in resultado.escolhidos:
        _imprimir_lote(lote, locais_por_id, "selecionado")
    print()
    print(f"Peso total          : {formatar_decimal(resultado.peso_total_kg)} kg")
    print(f"Soma das prioridades: {resultado.soma_prioridades}")
    print(f"Capacidade restante : {formatar_decimal(resultado.capacidade_restante_kg)} kg")
    print()
    print("A prioridade e uma pontuacao didatica de urgencia (1 a 10), definida no cenario.")
    print("Nao e previsao por IA nem avaliacao sanitaria.")
    print("A mochila maximiza a SOMA DAS PRIORIDADES sem ultrapassar a capacidade.")
    print("Ela nao maximiza quilos, pessoas atendidas nem economia de combustivel.")
    print()
    print("=== Excluidos por prazo ou falta de conexao ===")
    if not resultado.excluidos:
        print("  nenhum")
    for item in resultado.excluidos:
        _imprimir_lote(item.lote, locais_por_id, item.motivo)
    print()
    print("=== Elegiveis nao selecionados ===")
    if not resultado.elegiveis_nao_selecionados:
        print("  nenhum")
    for lote in resultado.elegiveis_nao_selecionados:
        _imprimir_lote(lote, locais_por_id, "elegivel, nao entrou na combinacao otima")
    print()
    print("Lote elegivel nao selecionado nao significa que ele, sozinho, fosse inviavel.")
    print("Apenas que a combinacao otima de prioridades nao o incluiu.")


def demonstracao_guiada(
    locais: list[Local],
    conexoes: list[Conexao],
    lotes: list[Lote],
    grafo: Grafo,
    locais_por_id: dict[int, Local],
    referencia: datetime,
) -> None:
    print()
    print("========== DEMONSTRACAO GUIADA ==========")
    print("Os dois calculos sao independentes. Nao ha roteiro global de visitas.")
    imprimir_referencia(referencia)

    print()
    print("--- 1) Grafo e Dijkstra (algoritmo guloso em grafo) ---")
    listar_locais_e_conexoes(locais, conexoes, grafo)

    print()
    print("Exemplo A: menor caminho da instituicao 6 ate a padaria 1")
    _exibir_caminho(grafo, locais_por_id, 6, 1)

    print()
    print("Exemplo B: caminho indireto menor que a ligacao direta (1 ate 4)")
    print("Ha aresta direta 1 <-> 4 com 12 km (simulada). O Dijkstra deve achar rota menor.")
    _exibir_caminho(grafo, locais_por_id, 1, 4)

    print()
    print("Exemplo C: origem igual ao destino")
    _exibir_caminho(grafo, locais_por_id, 6, 6)

    print()
    print("Exemplo D: estabelecimento desconectado (padaria 5)")
    _exibir_caminho(grafo, locais_por_id, 6, 5)

    print()
    print("--- 2) Mochila 0/1 por tabulacao (programacao dinamica) ---")
    print("Exemplo didatico que refuta a estrategia gulosa 'pegar o de maior prioridade':")
    print("  Capacidade: 10 kg")
    print("  Lote A id=101: 6 kg, prioridade 10")
    print("  Lote B id=102: 5 kg, prioridade 9")
    print("  Lote C id=103: 5 kg, prioridade 9")
    print("  Guloso por prioridade individual pegaria A (total 10).")
    print("  A PD escolhe B e C (total 18).")
    didatico = [
        ItemMochila(id=101, peso=60, valor=10),
        ItemMochila(id=102, peso=50, valor=9),
        ItemMochila(id=103, peso=50, valor=9),
    ]
    resultado_didatico = mochila_0_1(didatico, 100)
    print(
        f"  Resultado da PD: ids={resultado_didatico.ids_escolhidos}, "
        f"prioridade={resultado_didatico.valor_total}, "
        f"peso={formatar_decimal(unidades_para_kg(resultado_didatico.peso_total))} kg"
    )

    print()
    print("Agora a selecao sobre os lotes do cenario, capacidade 10 kg, instituicao 6.")
    selecionar_para_veiculo(
        lotes,
        locais_por_id,
        grafo,
        referencia,
        instituicao_id=6,
        capacidade_kg=Decimal("10.0"),
    )
    print()
    print("Lembrete: Dijkstra responde 'como ir de um local a outro'.")
    print("A mochila responde 'quais lotes cabem na capacidade com maior soma de prioridade'.")
    print("Juntar os dois nao produz, neste projeto, a melhor sequencia de coleta.")
    print("========== FIM DA DEMONSTRACAO ==========")


def exibir_menu() -> None:
    print()
    print("ReAlimenta SP - Planejador de Coletas")
    print("1. Listar locais e conexoes")
    print("2. Consultar menor caminho")
    print("3. Listar lotes e elegibilidade para uma instituicao")
    print("4. Selecionar lotes conforme a capacidade do veiculo")
    print("5. Executar demonstracao guiada dos algoritmos")
    print("0. Sair")


def interpretar_argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ReAlimenta SP — Planejador de Coletas (Dijkstra + mochila 0/1)"
    )
    parser.add_argument(
        "--referencia",
        default=formatar_data(REFERENCIA_DEMONSTRACAO),
        help="hora civil de Sao Paulo sem fuso (padrao: 2026-11-11T12:00:00; nao use Z nem -03:00)",
    )
    parser.add_argument(
        "--demonstracao",
        action="store_true",
        help="executa a demonstracao guiada e encerra, sem abrir o menu",
    )
    return parser.parse_args(argv)


def loop_menu(
    locais: list[Local],
    conexoes: list[Conexao],
    lotes: list[Lote],
    grafo: Grafo,
    locais_por_id: dict[int, Local],
    referencia: datetime,
) -> None:
    while True:
        exibir_menu()
        escolha = ler_linha("Opcao: ")
        if escolha is None:
            return
        opcao = escolha.strip()
        if opcao == "1":
            listar_locais_e_conexoes(locais, conexoes, grafo)
        elif opcao == "2":
            consultar_menor_caminho(grafo, locais_por_id)
        elif opcao == "3":
            listar_lotes_elegibilidade(lotes, locais_por_id, grafo, referencia)
        elif opcao == "4":
            selecionar_para_veiculo(lotes, locais_por_id, grafo, referencia)
        elif opcao == "5":
            demonstracao_guiada(locais, conexoes, lotes, grafo, locais_por_id, referencia)
        elif opcao == "0":
            print("Encerrando.")
            return
        else:
            print("Opcao invalida. Digite 0, 1, 2, 3, 4 ou 5.")


def main(argv: list[str] | None = None) -> int:
    args = interpretar_argumentos(argv)
    try:
        referencia = interpretar_data_iso(args.referencia, "referencia")
        locais, conexoes, lotes, grafo, locais_por_id = carregar_sistema()
    except ErroValidacao as erro:
        print(f"Falha ao iniciar: {erro}", file=sys.stderr)
        return 1

    print("ReAlimenta SP - Planejador de Coletas")
    print("Modulo academico de grafos (Dijkstra) e programacao dinamica (mochila 0/1).")
    print("Funciona sem API Java, sem Oracle e sem bibliotecas externas.")
    imprimir_referencia(referencia)
    print("A referencia padrao e fixa para demonstracao, salvo se --referencia for informado.")

    if args.demonstracao:
        demonstracao_guiada(locais, conexoes, lotes, grafo, locais_por_id, referencia)
        return 0

    loop_menu(locais, conexoes, lotes, grafo, locais_por_id, referencia)
    return 0


if __name__ == "__main__":
    sys.exit(main())
