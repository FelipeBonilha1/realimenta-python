"""Excecoes de dominio usadas pelos algoritmos e pelo carregamento."""


class ErroValidacao(Exception):
    """Erro de dados ou de entrada, com arquivo e linha quando possivel."""

    def __init__(
        self,
        mensagem: str,
        arquivo: str | None = None,
        linha: int | None = None,
    ) -> None:
        self.mensagem = mensagem
        self.arquivo = arquivo
        self.linha = linha
        super().__init__(self.formatar())

    def formatar(self) -> str:
        partes: list[str] = []
        if self.arquivo:
            partes.append(f"arquivo '{self.arquivo}'")
        if self.linha is not None:
            partes.append(f"linha {self.linha}")
        if partes:
            return f"{' '.join(partes)}: {self.mensagem}"
        return self.mensagem


class ErroConsulta(Exception):
    """Erro de consulta aos algoritmos (local inexistente, capacidade invalida)."""


class TabelaMuitoGrande(ErroConsulta):
    """A tabela de programacao dinamica ultrapassaria o limite de celulas."""
