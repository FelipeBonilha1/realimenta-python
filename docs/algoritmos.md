# Algoritmos do ReAlimenta SP

Este documento descreve as duas técnicas usadas no código. Elas resolvem problemas diferentes e não devem ser apresentadas como um único “otimizador de coleta”.

- **Dijkstra:** algoritmo **guloso** em grafo ponderado com pesos positivos.
- **Mochila 0/1 por tabulação:** **programação dinâmica**.

Os números do cenário são simulados. Não há benchmark medido neste repositório.

---

## 1. Grafo

Implementação: `realimenta/grafo.py`.

- Grafo **não direcionado** e ponderado.
- Representação: **lista de adjacência** (`id -> lista de (vizinho, distancia_km)`).
- Cada linha de `conexoes.csv` vira aresta de **mão dupla**.
- Conexão duplicada é rejeitada, inclusive com origem e destino invertidos.
- Conexão de um local para ele mesmo (**laço**) é rejeitada. Isso é uma **simplificação escolhida para este modelo**, que só representa deslocamento entre locais distintos. Um laço de peso positivo não tornaria o menor caminho ambíguo por si só; a consulta origem = destino continua sendo o caminho trivial de distância zero, independentemente dessa regra.

Pesos inválidos (não positivos, NaN, infinito) são recusados na construção do grafo. Dijkstra, neste projeto, pressupõe pesos positivos.

---

## 2. Dijkstra — menor caminho entre dois locais

Implementação: `realimenta/dijkstra.py`, usando `heapq` da biblioteca padrão. Não usamos biblioteca que já traga Dijkstra pronto.

### Ideia

Manter, para cada local, a menor distância conhecida a partir da origem. O algoritmo é guloso porque **sempre extrai o vértice com menor distância já confirmada** e nunca reabre um vértice extraído.

### Retorno

- Sequência de ids do caminho.
- Distância total em km.
- Se não houver caminho: `alcancavel=False`, lista vazia e `distancia_km=None`. **Não** devolvemos zero para destino inacessível.

Casos tratados:

| Situação | Comportamento |
| --- | --- |
| Origem = destino | Caminho com um único local e distância 0 |
| Origem ou destino inexistente | `ErroConsulta` |
| Destino desconectado | Sem caminho; distância `None` |
| Caminhos alternativos | Fica o de menor soma de pesos |
| Empate de distância | Determinístico: o heap usa `(distancia, id)` (menor id sai primeiro) e, em relaxamento com custo igual, **mantém o predecessor já registrado** |

O cálculo **lê** o grafo e não o altera.

### Exemplo resolvido à mão

Grafo didático (não é o CSV completo):

```text
1 --2.0-- 2 --2.0-- 3
1 ---------10.0-------- 3
```

Consulta: 1 até 3.

1. Origem 1 com distância 0.
2. Vizinhos: 2 (custo 2) e 3 (custo 10).
3. Extrai 2 (menor chave). Relaxa 3: 2 + 2 = 4, que é menor que 10.
4. Extrai 3 com distância 4.

Caminho: `1 -> 2 -> 3`, total 4. A aresta direta 1–3 existe, mas não é a menor.

No cenário de São Paulo (dados fictícios), a consulta 1 → 4 tem aresta direta 12,0 km, mas o menor caminho é `1 -> 9 -> 8 -> 7 -> 4` com 7,9 km.

### Complexidade (implementação real deste código)

Seja `n` o número de vértices e `m` o número de arestas.

- Cada vértice é extraído no máximo uma vez do conjunto de visitados.
- Em vez de *decrease-key*, o código **insere de novo** no heap quando encontra distância melhor. Um vértice pode gerar várias entradas, das quais só a primeira válida é usada.
- No pior caso o heap recebe O(m) inserções.
- Cada inserção/remoção no `heapq` custa O(log H), com H ≤ m.

Tempo: **O((n + m) log m)** nesta implementação com inserções repetidas, comumente descrito como O(m log m) em grafos conexos.  
Espaço: O(n + m) para o grafo e as tabelas, mais O(m) para o heap no pior caso.

Não medimos tempos de execução neste trabalho.

---

## 3. Mochila 0/1 por tabulação

Implementação: `realimenta/mochila.py`.

A filtragem de lotes (prazo e conectividade) **não** faz parte da função genérica. Ela ocorre antes, em `realimenta/elegibilidade.py`. A mochila recebe itens já elegíveis.

### Modelagem

Cada lote é um item 0/1:

- **indivisível**
- escolhido **no máximo uma vez**
- **peso** = quantidade convertida em unidades de 100 g
- **valor** = prioridade inteira de 1 a 10 (pontuação didática)

Objetivo: **maximizar a soma das prioridades** sem ultrapassar a capacidade.  
Não maximizamos quilos, número de pessoas nem combustível.

Capacidade zero → seleção vazia. Capacidade negativa → inválida.

### Discretização

`2,5 kg` → 25 unidades. `0,1 kg` → 1 unidade. `1,25 kg` é rejeitado. A conversão usa `Decimal` a partir de texto, sem `float`.

### Estado

`dp[i][c]` = maior prioridade obtida usando os **primeiros i lotes** (já ordenados por id) com capacidade `c`.

### Caso-base

- Sem lotes (`i = 0`): `dp[0][c] = 0` para todo `c`.
- Capacidade zero: valor total 0, nenhum item.

### Recorrência

Para o lote `i` (peso `w`, valor `v`) e capacidade `c`:

- Se `w > c`: `dp[i][c] = dp[i-1][c]` (não cabe).
- Se cabe: `dp[i][c] = max(dp[i-1][c], dp[i-1][c-w] + v)`.
- **Empate:** se os dois lados são iguais, permanece `dp[i-1][c]` (não inclui o item atual).

Os itens entram na tabela ordenados por id. Esse desempate é determinístico. **Não** afirmamos que ele minimize o peso.

### Reconstrução

Depois de preencher a tabela, percorremos `i` de `n` até 1:

- se `dp[i][c] != dp[i-1][c]`, o lote `i` foi escolhido, subtraímos o peso e continuamos;
- caso contrário, o lote `i` não entrou.

### Exemplo resolvido à mão (refuta o guloso por maior prioridade)

Capacidade: 10 kg = 100 unidades.

| Lote | Peso | Prioridade |
| --- | --- | --- |
| A (id 1) | 6 kg = 60 | 10 |
| B (id 2) | 5 kg = 50 | 9 |
| C (id 3) | 5 kg = 50 | 9 |

Estratégia gulosa “pegar o de maior prioridade individual”: escolhe A, total **10**, sobram 4 kg, B e C não cabem.

Programação dinâmica:

- Sem A, B+C pesam 10 kg e somam **18**.
- `dp[n][100] = 18`, itens 2 e 3.

O exemplo mostra que **essa** estratégia gulosa específica falha. Não diz que todo algoritmo guloso seja inútil; só que ele não resolve esta mochila 0/1.

### Limite de células

Antes de alocar a tabela, o código recusa instâncias com `(n + 1) * (C + 1) > 1.000.000`.  
Essa conta corresponde às linhas `0..n` e às colunas `0..C` realmente alocadas. Lista vazia e capacidade zero retornam imediatamente, sem criar tabela.  
O limite controla o tamanho do problema. **Não** promete o consumo exato de memória do interpretador.

### Complexidade

Com `n` itens e capacidade discretizada `C`:

- Tempo da tabela: **O(n × C)**
- Espaço da tabela: **O(n × C)**

Essa complexidade é **pseudopolinomial**: `C` é o valor numérico da capacidade, não o número de bits da entrada. Uma capacidade muito grande torna a tabela inviável mesmo com poucos lotes — por isso existe o limite de células.

Não há medição empírica de tempo neste documento.

---

## 4. Relação entre os dois cálculos

No menu, a demonstração apresenta os dois resultados **separadamente**.

A elegibilidade usa o grafo só para perguntar: “este estabelecimento tem *algum* caminho até a instituição?”. Isso **não** escolhe a ordem das visitas e **não** combina rota + capacidade em um único modelo.
