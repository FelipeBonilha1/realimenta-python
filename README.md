# Ficha CitizenTech

- **Nome da solução:** ReAlimenta SP — Planejador de Coletas
- **Cidade / bairro:** São Paulo / PENDENTE
- **Cidadão beneficiado:** pessoas atendidas por instituições sociais que recebem alimentos excedentes de estabelecimentos (descrição de público-alvo do cenário acadêmico; não há entrevista nem usuário real neste repositório)
- **Problema:** estabelecimentos com alimento ainda aproveitável precisam decidir como chegar até uma instituição e quais lotes cabem em um veículo de capacidade limitada
- **Como funciona (visão geral):** o módulo Python lê locais, conexões e lotes fictícios, calcula o menor caminho entre dois pontos com Dijkstra e seleciona lotes com mochila 0/1 por tabulação
- **Responsabilidade deste módulo Python:** apoiar duas decisões algorítmicas de planejamento; não substitui a API Java, o banco Oracle nem o módulo de Data Science de outro integrante
- **Objetivos potenciais da proposta do grupo:** reduzir o desperdício de alimentos e apoiar instituições sociais em São Paulo. São intenções da iniciativa, não impacto ambiental ou social medido por este programa
- **Indicador demonstrável (neste código):** distância do menor caminho em km; soma das prioridades e peso em kg da seleção de lotes. São indicadores do algoritmo, não comprovação de impacto social ou ambiental
- **ODS relacionados (proposta do grupo):** 2 (Fome zero), 11 (Cidades e comunidades sustentáveis), 12 (Consumo e produção responsáveis), 13 (Ação contra a mudança global do clima)
- **Repositório:** PENDENTE
- **Integrantes e RMs:**
  - Felipe Senteio Bonilha – RM 562356
  - Felipe Rodrigues Viana de Andrade – RM 565341
  - Joan Ferreira Campos – RM 562913

---

# ReAlimenta SP — Planejador de Coletas

Projeto acadêmico da disciplina **Dynamic Programming**, 2º ano de Engenharia de Software da FIAP.

O programa é um planejador em linha de comando. Ele **não** treina modelos, **não** faz regressão e **não** depende de internet, Java, Oracle ou bibliotecas externas.

## O que este programa decide — e o que ele não decide

1. **Menor caminho entre dois locais** (grafo + Dijkstra).
2. **Quais lotes indivisíveis transportar** em um veículo com capacidade limitada (mochila 0/1 por tabulação).

Cada algoritmo resolve um problema distinto:

- Dijkstra **não** é programação dinâmica. É um algoritmo **guloso** aplicado a grafos com pesos positivos.
- A mochila 0/1 com tabela bidimensional **é** a parte de programação dinâmica.
- Menor caminho entre dois locais **não** é a melhor sequência de visita a todos os estabelecimentos.
- A seleção de lotes **não** otimiza simultaneamente rota, combustível, tempo e capacidade.
- Os pesos do grafo e os lotes são **simulados**. Os resultados demonstram o funcionamento dos algoritmos e **não** comprovam impacto real.

## Requisitos

- Python 3.11 ou superior
- Somente biblioteca padrão (`csv`, `heapq`, `decimal`, `datetime`, `pathlib`, `argparse`, `itertools`, `unittest`)

Não é necessário instalar pacotes com `pip`.

## Instalação

Não há instalação de dependências. Extraia o ZIP (ou clone o repositório) e, na pasta do projeto, execute os comandos abaixo com o interpretador Python 3.11+.

Os arquivos CSV são lidos a partir da pasta `dados/` relativa à localização do projeto, não do diretório atual do terminal.

## Execução do menu

```text
python main.py
```

A referência temporal padrão da demonstração é **2026-11-11T12:00:00**. O programa **não** usa silenciosamente o relógio da máquina.

**Convenção de datas:** todos os horários (argumento `--referencia` e coluna `prazo_aproveitamento`) representam **hora civil de São Paulo, sem fuso explícito**.

- Aceito: `2026-11-11T12:00:00`
- Rejeitado: `2026-11-11T12:00:00-03:00` e `2026-11-11T12:00:00Z`

O fuso **não** é removido silenciosamente. A mensagem de erro informa o formato aceito e o programa encerra sem traceback.

Para outra referência:

```text
python main.py --referencia 2026-11-12T09:00:00
```

Para a demonstração guiada sem abrir o menu:

```text
python main.py --demonstracao
```

Menu:

1. Listar locais e conexões
2. Consultar menor caminho
3. Listar lotes e sua elegibilidade para uma instituição
4. Selecionar lotes conforme a capacidade do veículo
5. Executar demonstração guiada dos algoritmos
0. Sair

A instituição usada nos dados de exemplo tem **id 6**.

## Testes

```text
python -m unittest discover -s tests -v
```

## Formato e origem dos dados

Pasta `dados/`, arquivos UTF-8, ponto decimal e datas ISO 8601.

| Arquivo | Conteúdo |
| --- | --- |
| `dados/locais.csv` | id, nome, tipo (`ESTABELECIMENTO`, `INSTITUICAO`, `APOIO`) |
| `dados/conexoes.csv` | origem_id, destino_id, distancia_km (deslocamento de mão dupla) |
| `dados/lotes.csv` | id, estabelecimento_id, descricao, quantidade_kg, prazo_aproveitamento, prioridade |

Os nomes lembram bairros de São Paulo apenas para o cenário didático. As distâncias **não** são medições verificadas. Não há dados pessoais reais.

A prioridade (inteiro de 1 a 10) é uma **pontuação didática de urgência** definida no cenário. Não é previsão por IA nem avaliação sanitária.

Quantidades estão em kg, aceitas somente como múltiplos de 0,1 kg (unidades internas de 100 g). Exemplo: 2,5 kg = 25 unidades. 1,25 kg é rejeitado; não há arredondamento silencioso.

## Limitações

- Sem interface web, login, mapas externos ou banco de dados.
- Sem integração com a API Java ou com o Oracle.
- Dijkstra encontra o menor caminho entre **dois** vértices, não um roteiro TSP.
- A filtragem por conectividade só evita lote de estabelecimento inacessível; não otimiza a ordem das coletas.
- A mochila maximiza a **soma das prioridades**, não quilos, pessoas atendidas nem economia de combustível.
- O limite de 1.000.000 de células da tabela (`(n + 1) × (C + 1)`) controla o tamanho do problema; não promete consumo exato de memória.
- O desempate da mochila (ordenar por id e, em empate de pontuação, não incluir o item atual) é determinístico. Não afirmamos que ele minimize o peso.

## Estrutura do projeto

```text
main.py
realimenta/
    __init__.py
    modelos.py
    excecoes.py
    validacoes.py
    carregamento.py
    grafo.py
    dijkstra.py
    mochila.py
    elegibilidade.py
    selecao.py
dados/
    locais.csv
    conexoes.csv
    lotes.csv
tests/
docs/
    algoritmos.md
    roteiro-demonstracao.md
    checklist-entrega.md
README.md
prompts.md
.gitignore
```

Detalhes dos algoritmos: `docs/algoritmos.md`.  
Roteiro de apresentação: `docs/roteiro-demonstracao.md`.  
Itens da entrega: `docs/checklist-entrega.md`.
