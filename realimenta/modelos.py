"""Estruturas simples dos dados do planejador."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

TIPOS_LOCAL = ("ESTABELECIMENTO", "INSTITUICAO", "APOIO")
PRIORIDADE_MINIMA = 1
PRIORIDADE_MAXIMA = 10
# Unidade interna da mochila: 100 g, ou seja, 0,1 kg.
PASSO_KG = Decimal("0.1")
LIMITE_CELULAS_PADRAO = 1_000_000
REFERENCIA_DEMONSTRACAO = datetime(2026, 11, 11, 12, 0, 0)


@dataclass(frozen=True)
class Local:
    id: int
    nome: str
    tipo: str


@dataclass(frozen=True)
class Conexao:
    origem_id: int
    destino_id: int
    distancia_km: Decimal


@dataclass(frozen=True)
class Lote:
    id: int
    estabelecimento_id: int
    descricao: str
    quantidade_kg: Decimal
    prazo_aproveitamento: datetime
    prioridade: int


@dataclass(frozen=True)
class ItemMochila:
    """Item generico da mochila 0/1: peso em unidades de 100 g e valor inteiro."""

    id: int
    peso: int
    valor: int


@dataclass(frozen=True)
class ResultadoCaminho:
    origem_id: int
    destino_id: int
    alcancavel: bool
    caminho: list[int]
    distancia_km: Decimal | None
    mensagem: str


@dataclass(frozen=True)
class ResultadoMochila:
    ids_escolhidos: list[int]
    valor_total: int
    peso_total: int
    capacidade: int
    capacidade_restante: int


@dataclass(frozen=True)
class MotivoExclusao:
    lote: Lote
    motivo: str


@dataclass(frozen=True)
class ResultadoSelecao:
    instituicao_id: int
    capacidade_kg: Decimal
    escolhidos: list[Lote]
    peso_total_kg: Decimal
    soma_prioridades: int
    capacidade_restante_kg: Decimal
    excluidos: list[MotivoExclusao]
    elegiveis_nao_selecionados: list[Lote]
