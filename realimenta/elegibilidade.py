"""Filtro de lotes antes da mochila. Nao e otimizacao de rota."""

from datetime import datetime

from realimenta.dijkstra import ids_alcancaveis
from realimenta.excecoes import ErroConsulta
from realimenta.grafo import Grafo
from realimenta.modelos import Local, Lote, MotivoExclusao

MOTIVO_PRAZO = "prazo vencido na referencia temporal (prazo menor ou igual a referencia)"
MOTIVO_DESCONECTADO = "estabelecimento sem caminho ate a instituicao no grafo"


def lote_dentro_do_prazo(lote: Lote, referencia: datetime) -> bool:
    """Prazo igual a referencia ja esta fora. So permanece se o prazo for posterior."""
    return lote.prazo_aproveitamento > referencia


def classificar_lotes(
    lotes: list[Lote],
    locais_por_id: dict[int, Local],
    grafo: Grafo,
    instituicao_id: int,
    referencia: datetime,
) -> tuple[list[Lote], list[MotivoExclusao]]:
    """Separa elegiveis e excluidos. A conectividade so evita local inacessivel."""
    instituicao = locais_por_id.get(instituicao_id)
    if instituicao is None:
        raise ErroConsulta(f"instituicao inexistente: id {instituicao_id}")
    if instituicao.tipo != "INSTITUICAO":
        raise ErroConsulta(
            f"local {instituicao_id} ({instituicao.nome}) nao e INSTITUICAO; tipo={instituicao.tipo}"
        )

    alcancaveis = ids_alcancaveis(grafo, instituicao_id)
    elegiveis: list[Lote] = []
    excluidos: list[MotivoExclusao] = []

    for lote in lotes:
        if not lote_dentro_do_prazo(lote, referencia):
            excluidos.append(MotivoExclusao(lote=lote, motivo=MOTIVO_PRAZO))
            continue
        if lote.estabelecimento_id not in alcancaveis:
            excluidos.append(MotivoExclusao(lote=lote, motivo=MOTIVO_DESCONECTADO))
            continue
        elegiveis.append(lote)

    return elegiveis, excluidos
