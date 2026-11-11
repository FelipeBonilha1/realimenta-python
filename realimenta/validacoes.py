"""Validacoes de campos. Separadas dos algoritmos para facilitar os testes."""

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from realimenta.excecoes import ErroValidacao
from realimenta.modelos import PASSO_KG, PRIORIDADE_MAXIMA, PRIORIDADE_MINIMA, TIPOS_LOCAL

FORMATO_DATA_ACEITO = "2026-11-11T12:00:00"
# Deslocamento ISO no final do texto (nao confundir com o hifen da data YYYY-MM-DD).
_FUSO_NO_FINAL = re.compile(r"[Tt ].*[+-]\d{2}:?\d{2}(:\d{2})?$")
_MENSAGEM_DATA = (
    "deve representar hora civil de Sao Paulo, sem fuso explicito. "
    f"Formato aceito: {FORMATO_DATA_ACEITO}. "
    "Nao use sufixo Z nem deslocamento como -03:00; o fuso nao e removido silenciosamente"
)


def exigir_nao_vazio(valor: str, campo: str, arquivo: str | None = None, linha: int | None = None) -> str:
    texto = valor.strip() if valor is not None else ""
    if texto == "":
        raise ErroValidacao(f"campo '{campo}' vazio", arquivo, linha)
    return texto


def interpretar_id(valor: str, campo: str, arquivo: str | None = None, linha: int | None = None) -> int:
    texto = exigir_nao_vazio(valor, campo, arquivo, linha)
    try:
        numero = int(texto)
    except ValueError as erro:
        raise ErroValidacao(
            f"campo '{campo}' deve ser um inteiro positivo, recebido '{texto}'",
            arquivo,
            linha,
        ) from erro
    if numero <= 0:
        raise ErroValidacao(
            f"campo '{campo}' deve ser um inteiro positivo, recebido '{texto}'",
            arquivo,
            linha,
        )
    return numero


def interpretar_tipo_local(valor: str, arquivo: str | None = None, linha: int | None = None) -> str:
    texto = exigir_nao_vazio(valor, "tipo", arquivo, linha)
    if texto not in TIPOS_LOCAL:
        permitidos = ", ".join(TIPOS_LOCAL)
        raise ErroValidacao(
            f"tipo de local invalido '{texto}'. Use um de: {permitidos}",
            arquivo,
            linha,
        )
    return texto


def interpretar_decimal(valor: str, campo: str, arquivo: str | None = None, linha: int | None = None) -> Decimal:
    """Converte texto em Decimal sem passar por float."""
    texto = exigir_nao_vazio(valor, campo, arquivo, linha)
    if "," in texto:
        raise ErroValidacao(
            f"campo '{campo}' deve usar ponto decimal, nao virgula. Recebido '{texto}'",
            arquivo,
            linha,
        )
    try:
        numero = Decimal(texto)
    except InvalidOperation as erro:
        raise ErroValidacao(
            f"campo '{campo}' nao e um numero decimal valido: '{texto}'",
            arquivo,
            linha,
        ) from erro
    if not numero.is_finite():
        raise ErroValidacao(
            f"campo '{campo}' nao pode ser NaN nem infinito. Recebido '{texto}'",
            arquivo,
            linha,
        )
    return numero


def interpretar_distancia_km(valor: str, arquivo: str | None = None, linha: int | None = None) -> Decimal:
    distancia = interpretar_decimal(valor, "distancia_km", arquivo, linha)
    if distancia <= 0:
        raise ErroValidacao(
            f"distancia_km deve ser positiva. Recebido '{distancia}'",
            arquivo,
            linha,
        )
    return distancia


def kg_para_unidades(
    quantidade_kg: Decimal,
    arquivo: str | None = None,
    linha: int | None = None,
) -> int:
    """Converte kg em unidades de 100 g. Rejeita valores que nao sejam multiplos de 0,1 kg."""
    if quantidade_kg <= 0:
        raise ErroValidacao(
            f"quantidade deve ser positiva. Recebido '{quantidade_kg}'",
            arquivo,
            linha,
        )
    quociente = quantidade_kg / PASSO_KG
    # to_integral_value() so e igual ao proprio numero se ele ja for inteiro.
    if quociente != quociente.to_integral_value():
        raise ErroValidacao(
            f"quantidade '{quantidade_kg}' kg nao e multiplo de {PASSO_KG} kg; "
            "nao ha arredondamento silencioso nesta discretizacao",
            arquivo,
            linha,
        )
    return int(quociente)


def unidades_para_kg(unidades: int) -> Decimal:
    return PASSO_KG * Decimal(unidades)


def interpretar_quantidade_kg(valor: str, arquivo: str | None = None, linha: int | None = None) -> Decimal:
    quantidade = interpretar_decimal(valor, "quantidade_kg", arquivo, linha)
    kg_para_unidades(quantidade, arquivo, linha)
    return quantidade


def interpretar_prioridade(valor: str, arquivo: str | None = None, linha: int | None = None) -> int:
    texto = exigir_nao_vazio(valor, "prioridade", arquivo, linha)
    try:
        numero = int(texto)
    except ValueError as erro:
        raise ErroValidacao(
            f"prioridade deve ser inteiro entre {PRIORIDADE_MINIMA} e {PRIORIDADE_MAXIMA}. "
            f"Recebido '{texto}'",
            arquivo,
            linha,
        ) from erro
    if numero < PRIORIDADE_MINIMA or numero > PRIORIDADE_MAXIMA:
        raise ErroValidacao(
            f"prioridade fora da faixa {PRIORIDADE_MINIMA} a {PRIORIDADE_MAXIMA}. Recebido '{numero}'",
            arquivo,
            linha,
        )
    return numero


def _possui_fuso_explicito(texto: str) -> bool:
    """Detecta Z ou deslocamento. Nao remove o fuso: a chamada deve rejeitar o texto."""
    compacto = texto.strip()
    if compacto.endswith(("Z", "z")):
        return True
    return _FUSO_NO_FINAL.search(compacto) is not None


def interpretar_data_iso(valor: str, campo: str, arquivo: str | None = None, linha: int | None = None) -> datetime:
    """Interpreta data naive de hora civil de Sao Paulo. Rejeita fuso explicito."""
    texto = exigir_nao_vazio(valor, campo, arquivo, linha)
    if _possui_fuso_explicito(texto):
        raise ErroValidacao(
            f"campo '{campo}' {_MENSAGEM_DATA}. Recebido '{texto}'",
            arquivo,
            linha,
        )
    try:
        data = datetime.fromisoformat(texto)
    except ValueError as erro:
        raise ErroValidacao(
            f"campo '{campo}' {_MENSAGEM_DATA}. Recebido '{texto}'",
            arquivo,
            linha,
        ) from erro
    # fromisoformat pode devolver datetime com tzinfo; nao convertermos nem removermos o fuso.
    if data.tzinfo is not None:
        raise ErroValidacao(
            f"campo '{campo}' {_MENSAGEM_DATA}. Recebido '{texto}'",
            arquivo,
            linha,
        )
    return data


def interpretar_capacidade_kg(valor: str) -> Decimal:
    """Capacidade do veiculo: zero e permitido; negativo, nao."""
    quantidade = interpretar_decimal(valor, "capacidade_kg")
    if quantidade < 0:
        raise ErroValidacao(f"capacidade nao pode ser negativa. Recebido '{quantidade}'")
    if quantidade == 0:
        return quantidade
    kg_para_unidades(quantidade)
    return quantidade
