"""Orquestra filtro de elegibilidade e mochila, sem misturar os dois algoritmos."""

from datetime import datetime
from decimal import Decimal

from realimenta.elegibilidade import classificar_lotes
from realimenta.grafo import Grafo
from realimenta.mochila import mochila_0_1
from realimenta.modelos import (
    LIMITE_CELULAS_PADRAO,
    ItemMochila,
    Local,
    Lote,
    ResultadoSelecao,
)
from realimenta.validacoes import kg_para_unidades, unidades_para_kg


def selecionar_lotes(
    lotes: list[Lote],
    locais_por_id: dict[int, Local],
    grafo: Grafo,
    instituicao_id: int,
    capacidade_kg: Decimal,
    referencia: datetime,
    limite_celulas: int = LIMITE_CELULAS_PADRAO,
) -> ResultadoSelecao:
    """Aplica o filtro e depois a mochila 0/1 sobre os lotes elegiveis."""
    if capacidade_kg < 0:
        raise ValueError("capacidade negativa e invalida")

    elegiveis, excluidos = classificar_lotes(
        lotes,
        locais_por_id,
        grafo,
        instituicao_id,
        referencia,
    )

    capacidade_unidades = 0 if capacidade_kg == 0 else kg_para_unidades(capacidade_kg)
    itens = [
        ItemMochila(
            id=lote.id,
            peso=kg_para_unidades(lote.quantidade_kg),
            valor=lote.prioridade,
        )
        for lote in elegiveis
    ]
    resultado = mochila_0_1(itens, capacidade_unidades, limite_celulas=limite_celulas)

    escolhidos_ids = set(resultado.ids_escolhidos)
    por_id = {lote.id: lote for lote in elegiveis}
    escolhidos = [por_id[item_id] for item_id in resultado.ids_escolhidos]
    nao_selecionados = [lote for lote in elegiveis if lote.id not in escolhidos_ids]

    return ResultadoSelecao(
        instituicao_id=instituicao_id,
        capacidade_kg=capacidade_kg,
        escolhidos=escolhidos,
        peso_total_kg=unidades_para_kg(resultado.peso_total),
        soma_prioridades=resultado.valor_total,
        capacidade_restante_kg=unidades_para_kg(resultado.capacidade_restante),
        excluidos=excluidos,
        elegiveis_nao_selecionados=nao_selecionados,
    )
