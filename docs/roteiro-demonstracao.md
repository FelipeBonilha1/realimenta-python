# Roteiro de demonstração

Apresentação curta para a disciplina Dynamic Programming. Os números abaixo correspondem ao código e aos CSV deste repositório, com a referência **2026-11-11T12:00:00** (hora civil de São Paulo).

Não invente um roteiro único que “visite todos os estabelecimentos na ordem ótima”. Mostre **dois cálculos separados**.

## Antes de começar

```text
python -m unittest discover -s tests -v
python main.py --demonstracao
```

Ou abra o menu:

```text
python main.py
```

Instituição de exemplo: **id 6** (Instituto Social do Centro).

---

## Sequência sugerida (cerca de 8 a 10 minutos)

### 1. Contexto (1 min)

- ReAlimenta SP conecta estabelecimentos com excedente a instituições sociais.
- Este módulo Python apoia duas decisões: menor caminho entre dois locais e seleção de lotes com capacidade limitada.
- Dados fictícios inspirados em São Paulo. Distâncias simuladas.

### 2. Menu opção 1 — locais e conexões (1 min)

Entrada: `1`

Esperado:

- Quatro estabelecimentos conectados (ids 1 a 4), um desconectado (id 5), uma instituição (id 6), três pontos de apoio (7, 8, 9).
- Arestas de mão dupla.

Fale: o estabelecimento 5 existe no cadastro e no grafo, mas não tem aresta.

### 3. Menu opção 2 — Dijkstra (2 min)

**Consulta A** — origem `6`, destino `1`

Esperado:

- Caminho `6 -> 9 -> 1`
- Distância `7.6 km`

**Consulta B** — origem `1`, destino `4`

Esperado:

- Há aresta direta `1 <-> 4` com `12.0 km`
- Menor caminho `1 -> 9 -> 8 -> 7 -> 4` com `7.9 km`

**Consulta C** — origem `6`, destino `6`

Esperado: caminho `[6]`, distância `0`

**Consulta D** — origem `6`, destino `5`

Esperado: sem caminho; distância **não** é zero.

Fale: Dijkstra é guloso em grafo. Não é programação dinâmica. O resultado é o menor caminho entre **dois** pontos.

### 4. Menu opção 3 — elegibilidade (1 min)

Entrada: instituição `6`

Esperado na referência padrão:

- Elegíveis: lotes 1, 2, 3, 4, 5, 6, 9
- Lote 7: prazo 11:00, vencido
- Lote 10: prazo exatamente 12:00, também fora
- Lote 8: padaria isolada, sem conexão

Fale: filtrar local inacessível **não** é otimizar a rota.

Opcional: encerrar, rodar `python main.py --referencia 2026-11-12T09:00:00` e repetir a opção 3. Vários lotes do dia 11 saem da lista.

### 5. Menu opção 4 — mochila (3 min)

Entrada: instituição `6`, capacidade `10`

Esperado:

- Escolhidos: lotes **2, 3, 4, 9**
- Peso total: **9.6 kg**
- Soma das prioridades: **29**
- Capacidade restante: **0.4 kg**
- Excluídos: 7 (prazo), 8 (desconectado), 10 (prazo igual à referência)
- Elegíveis não selecionados: 1, 5, 6 — não diga que cada um era inviável sozinho

Mostre o contraexemplo guloso (também na opção 5):

- Capacidade 10 kg; A 6 kg/10; B 5 kg/9; C 5 kg/9
- Guloso por maior prioridade: só A, total 10
- PD: B e C, total 18

Fale o estado `dp[i][c]`, o caso-base e a recorrência. Diga que a complexidade O(n × C) é pseudopolinomial.

### 6. Fechamento (1 min)

Os algoritmos não comprovam impacto real. Não há mapa, login nem banco neste escopo.

---

## Diferença entre os algoritmos (frase pronta)

> “Dijkstra responde como ir de um local a outro com a menor soma de km no grafo. A mochila responde quais lotes indivisíveis cabem no veículo com a maior soma de prioridades. Juntar as duas respostas neste projeto não produz a melhor sequência de coleta.”

---

## Perguntas prováveis do professor

**Dijkstra é programação dinâmica?**  
Não. É guloso. A PD deste trabalho é a mochila 0/1 por tabulação. Código: `realimenta/dijkstra.py` e `realimenta/mochila.py`.

**Por que heapq e não uma matriz de distâncias Floyd-Warshall?**  
O enunciado pede menor caminho entre dois locais e permite grafos. Dijkstra com heap atende pesos positivos e a implementação pedida. Floyd-Warshall resolveria todos os pares, o que não é o problema deste menu.

**O que acontece no empate de caminhos?**  
O heap compara `(distancia, id)`. Em relaxamento com custo igual, o predecessor antigo permanece. Teste: `tests/test_dijkstra.py`, `test_empate_deterministico`.

**Destino inacessível devolve zero?**  
Não. `distancia_km` fica `None` e `alcancavel=False`.

**A mochila usa memoização recursiva?**  
Não. Tabulação com tabela `dp[i][c]` bidimensional e reconstrução dos ids.

**Por que unidades de 100 g?**  
Para a capacidade da tabela ser inteira sem `float`. 1,25 kg não é múltiplo de 0,1 kg e é rejeitado.

**Por que não arredondar 1,25 kg?**  
O enunciado pede rejeição explícita. Arredondar alteraria o peso sem o usuário perceber.

**A prioridade veio de um modelo de IA?**  
Não. É um inteiro de 1 a 10 escrito no CSV do cenário.

**Vocês maximizam o aproveitamento em kg?**  
Não. O objetivo da PD é a soma das prioridades.

**Por que não escolher sempre o lote de maior prioridade?**  
O exemplo A/B/C mostra que essa regra gulosa obtém 10 e a PD obtém 18.

**O desempate minimiza o peso?**  
Não está implementado um critério de menor peso. Em empate de valor, o código simplesmente não inclui o item atual.

**Filtrar pelo grafo já não é otimizar a rota?**  
Não. Só evita lote cujo estabelecimento não tem caminho até a instituição.

**Qual a complexidade da mochila?**  
O(n × C) em tempo e espaço para a tabela. C é a capacidade em unidades de 100 g. É pseudopolinomial.

**E se a tabela ficar enorme?**  
Se `(n + 1) * (C + 1)` passar de 1.000.000, o programa recusa com mensagem clara. Isso limita o tamanho da instância, não mede RAM real. A tabela tem `n + 1` linhas (incluindo o caso-base sem itens).

**Por que a data não é a de hoje?**  
A demonstração precisa ser reproduzível. A referência padrão é 2026-11-11T12:00:00. Pode ser trocada com `--referencia`.

**Funciona sem Oracle / Java?**  
Sim. Biblioteca padrão e três CSV.

**Onde estão os nomes e RMs?**  
No início do README, na ficha CitizenTech: Felipe Senteio Bonilha (RM 562356), Felipe Rodrigues Viana de Andrade (RM 565341) e Joan Ferreira Campos (RM 562913).
