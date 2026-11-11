# Checklist de entrega — Dynamic Programming

Entrega prevista pelo enunciado da disciplina: **código-fonte completo e README em um único ZIP**. Não gerar PDF neste escopo.

## Código completo

- [x] `main.py` com menu 0–5, argumentos `--referencia` e `--demonstracao`
- [x] Pacote `realimenta/` com modelos, validações, carregamento, grafo, Dijkstra, mochila, elegibilidade e seleção
- [x] Algoritmos separados da entrada/saída do terminal
- [x] `if __name__ == "__main__"` impede o menu na importação
- [x] Caminhos dos CSV resolvidos a partir da pasta do projeto
- [x] Type hints simples e nomes em português sem acento nos identificadores

## Dados necessários

- [x] `dados/locais.csv`
- [x] `dados/conexoes.csv`
- [x] `dados/lotes.csv`
- [x] Pelo menos quatro estabelecimentos, uma instituição, pontos de apoio
- [x] Caminhos alternativos e um estabelecimento desconectado
- [x] Lotes com pesos e prioridades variados e um lote vencido na referência padrão
- [x] UTF-8, ponto decimal, datas ISO
- [x] Dados fictícios, sem informação pessoal real

## README com integrantes e RMs

- [x] Ficha CitizenTech no início do `README.md`
- [x] Nomes e RMs da equipe no README
- [ ] **PENDENTE:** bairro
- [ ] **PENDENTE:** URL do repositório

## Testes executados

Rodar na pasta do projeto:

```text
python -m unittest discover -s tests -v
```

Preencher após a execução real:

- [x] Quantidade de testes: **62**
- [x] Resultado: **OK** (`Ran 62 tests in 0.275s`)
- [x] Versão do `python` utilizada: **Python 3.12.10**

## Execução validada após extrair o ZIP

No computador da entrega, depois de extrair o ZIP para uma pasta **nova**:

```text
python main.py --demonstracao
python main.py
```

Conferir:

- [x] Menu abre sem traceback (percorrido com entradas de exemplo neste computador)
- [x] Opção 2 com 6 → 1 devolve `6 -> 9 -> 1` e `7.6 km`
- [x] Opção 2 com 6 → 5 informa que não há caminho
- [x] Opção 4 com instituição 6 e capacidade 10 escolhe lotes 2, 3, 4, 9 (prioridade 29, peso 9.6 kg)
- [x] Não pede Oracle, Java, API nem `pip install`
- [x] ZIP extraído em pasta temporária nesta máquina: 62 testes OK e demonstração com os números do cenário
- [ ] Conferir de novo no computador da entrega, depois de extrair o ZIP enviado à disciplina

## Pendências reais

- Completar bairro no README (ainda PENDENTE; não inventar)
- Completar URL do repositório no README (ainda PENDENTE; não inventar)
- Se a disciplina exigir capa, vídeo ou outros itens fora de Dynamic Programming, isso está **fora** deste ZIP de código

O ZIP gerado nesta revisão não inclui `__pycache__`, `.pyc`, `.git`, ambientes virtuais nem arquivos de IDE.

## Arquivos que devem ir no ZIP

```text
main.py
README.md
prompts.md
.gitignore
realimenta/__init__.py
realimenta/modelos.py
realimenta/excecoes.py
realimenta/validacoes.py
realimenta/carregamento.py
realimenta/grafo.py
realimenta/dijkstra.py
realimenta/mochila.py
realimenta/elegibilidade.py
realimenta/selecao.py
dados/locais.csv
dados/conexoes.csv
dados/lotes.csv
tests/__init__.py
tests/auxiliar.py
tests/test_dijkstra.py
tests/test_mochila.py
tests/test_elegibilidade.py
tests/test_carregamento.py
tests/test_cenario.py
tests/test_datas.py
docs/algoritmos.md
docs/roteiro-demonstracao.md
docs/checklist-entrega.md
```

Não incluir: `.venv/`, `__pycache__/`, `.pyc`, PDF, credenciais, dumps do Oracle.
