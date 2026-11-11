# Registro de prompts e decisões

Documento pedido no enunciado da disciplina: o pedido original deve ficar registrado integralmente, junto das decisões de implementação.

---

## Pedido original (integral)

Implemente nesta pasta o projeto acadêmico “ReAlimenta SP — Planejador de Coletas”, para a disciplina Dynamic Programming, do segundo ano de Engenharia de Software da FIAP.

Crie os arquivos, implemente as funcionalidades, execute os testes e documente o resultado. Não encerre apenas com um planejamento.

O código deve ser organizado e tecnicamente correto, mas compreensível para um estudante do segundo ano. Prefira funções claras e estruturas simples.

1. CONTEXTO E REQUISITOS

O ReAlimenta SP conecta estabelecimentos com alimentos excedentes a instituições sociais.

Este projeto Python deve apoiar duas decisões:
- Qual é o menor caminho entre dois locais?
- Quais lotes transportar quando o veículo possui capacidade limitada?

O enunciado da disciplina prevê técnicas dentre memoização, tabulação e grafos, exigindo:
- Escolha coerente do algoritmo ou estrutura.
- Funcionamento correto.
- Noção de eficiência.
- Código-fonte completo.
- README com nomes, RMs, descrição dos algoritmos e funcionalidades.
- Entrega em um único ZIP.

Usaremos grafos com Dijkstra e programação dinâmica com tabulação para mochila 0/1.

Não implementar Data Science, regressão ou treinamento de modelos. Essa disciplina pertence a outro integrante.

Este projeto deve funcionar independentemente da API Java e do Oracle.

2. LIMITES DO ESCOPO

Explicar corretamente na documentação:
- Dijkstra é um algoritmo guloso aplicado a grafos.
- Mochila 0/1 com tabulação é a parte de programação dinâmica.
- Cada algoritmo resolve um problema distinto.
- Menor caminho entre dois locais não equivale à melhor sequência de visita a todos os estabelecimentos.
- A seleção de lotes não otimiza simultaneamente rota, combustível, tempo e capacidade.
- Os pesos do grafo e os dados de exemplo são simulados.
- Os resultados demonstram o funcionamento dos algoritmos e não comprovam impacto real.

Não implementar interface web, login, mapas externos ou integração com banco neste escopo.

3. TECNOLOGIA E ORGANIZAÇÃO

Usar Python 3.11 ou superior e somente a biblioteca padrão, salvo necessidade concreta e justificada.

Bibliotecas permitidas incluem:
csv, heapq, decimal, datetime, pathlib, argparse, itertools e unittest.

Não utilizar bibliotecas que já implementem Dijkstra ou mochila.

Estrutura sugerida:
- main.py
- realimenta/__init__.py
- realimenta/modelos.py
- realimenta/carregamento.py
- realimenta/grafo.py
- realimenta/dijkstra.py
- realimenta/mochila.py
- realimenta/validacoes.py
- dados/locais.csv
- dados/conexoes.csv
- dados/lotes.csv
- tests/
- README.md
- docs/algoritmos.md
- docs/roteiro-demonstracao.md
- docs/checklist-entrega.md
- prompts.md
- .gitignore

Pode simplificar a estrutura se isso melhorar a clareza.

Usar nomes em português sem acentos nos identificadores.
Utilizar type hints simples.
Comentários devem explicar decisões e raciocínio.
Separar entrada/saída do terminal dos algoritmos.
Não executar o menu quando um módulo for importado.

Resolver caminhos dos arquivos a partir da localização do projeto, evitando dependência do diretório atual do terminal.

4. MODELO E DADOS

Locais:
- id
- nome
- tipo: ESTABELECIMENTO, INSTITUICAO ou APOIO

Conexões:
- origem_id
- destino_id
- distancia_km

Lotes:
- id
- estabelecimento_id
- descricao
- quantidade_kg
- prazo_aproveitamento
- prioridade

Os identificadores podem ser inteiros positivos.
Estabelecimentos dos lotes devem referenciar locais existentes do tipo ESTABELECIMENTO.

Validar:
- Cabeçalhos obrigatórios.
- IDs duplicados.
- Referências inexistentes.
- Campos vazios.
- Tipos de local inválidos.
- Distâncias não positivas, NaN ou infinitas.
- Quantidades inválidas.
- Datas inválidas.
- Prioridade fora da faixa definida.

Utilizar UTF-8, ponto decimal e datas em formato ISO.
Mensagens de erro devem identificar arquivo e linha quando possível.

Usar dados fictícios inspirados em São Paulo:
- Pelo menos quatro estabelecimentos.
- Uma instituição.
- Pontos de apoio.
- Caminhos alternativos.
- Um estabelecimento desconectado.
- Lotes de pesos e prioridades variados.
- Um lote vencido.

Essas quantidades são escolhas da demonstração, não exigências mínimas do professor.

Não usar informações pessoais reais nem apresentar as distâncias como medições verificadas.

5. TEMPO REPRODUZÍVEL

Criar um modo de demonstração com data/hora fixa, por exemplo:
2026-11-11T12:00:00.

Preparar os lotes de demonstração em relação a esse instante.

Exibir claramente a referência utilizada e informar que os horários representam hora civil de São Paulo.

Permitir fornecer outra referência por argumento de linha de comando, por exemplo:
python main.py --referencia 2026-11-12T09:00:00

O funcionamento padrão pode utilizar a referência fixa demonstrativa, desde que isso fique explícito.

Não depender silenciosamente da data atual da máquina.
Um lote cujo prazo seja igual à referência já deve ser considerado fora do prazo.

6. GRAFO E DIJKSTRA

Implementar grafo ponderado não direcionado com lista de adjacência.
Cada conexão representa deslocamento de mão dupla.
Rejeitar conexões duplicadas, inclusive quando origem e destino vierem invertidos.
Definir e documentar o tratamento de uma conexão de um local para ele mesmo.

Implementar Dijkstra manualmente com heapq.

Retornar:
- Sequência de locais do caminho.
- Distância total.
- Indicação explícita quando não existir caminho.

Tratar:
- Origem igual ao destino: caminho com um local e distância zero.
- Origem inexistente.
- Destino inexistente.
- Destino desconectado.
- Caminhos alternativos.
- Empates com comportamento determinístico.

Não devolver distância zero para destino inacessível.
Não modificar o grafo recebido durante o cálculo.

7. SELEÇÃO DE LOTES — MOCHILA 0/1

Implementar tabulação com tabela bidimensional e reconstrução dos itens selecionados.

Cada lote:
- É indivisível.
- Pode ser escolhido no máximo uma vez.
- Tem como peso sua quantidade.
- Tem como valor sua prioridade.

Usar prioridade inteira entre 1 e 10, atribuída manualmente nos dados.
Explicar que se trata de uma pontuação didática de urgência definida no cenário, não de uma previsão por IA ou avaliação sanitária.

Objetivo:
Maximizar a soma das prioridades sem ultrapassar a capacidade.

Não afirmar que essa função maximiza quilos, número de pessoas atendidas ou economia de combustível.

Antes da seleção, considerar elegíveis apenas:
- Lotes dentro do prazo na referência escolhida.
- Lotes de estabelecimentos alcançáveis a partir da instituição selecionada.

A filtragem por conectividade não significa otimização da rota: apenas evita selecionar lotes de locais inacessíveis no grafo.

Separar essa filtragem da função genérica de mochila.

QUANTIDADES

Usar unidades inteiras de 100 gramas.
Converter kg com Decimal a partir de texto, sem passar por float.
Aceitar apenas quantidades múltiplas de 0,1 kg.
Não arredondar silenciosamente.

Lotes devem ter peso positivo.
Capacidade pode ser zero e deve produzir seleção vazia.
Capacidade negativa é inválida.

Exemplos:
- 2,5 kg corresponde a 25 unidades.
- 0,1 kg corresponde a 1 unidade.
- 1,25 kg deve ser rejeitado nessa discretização.

TABELA E RECONSTRUÇÃO

Explicar:
dp[i][c] representa a maior prioridade obtida usando os primeiros i lotes com capacidade c.

Caso-base:
Sem lotes ou capacidade zero, prioridade total zero.

Transição:
Se o lote não cabe, repetir a solução anterior.
Se cabe, comparar não selecionar com selecionar o lote mais a melhor solução anterior para a capacidade restante.

Reconstruir os IDs dos lotes escolhidos.
Definir desempate determinístico: ordenar por ID e, em igualdade de pontuação, manter a opção de não incluir o item atual.

Não afirmar que esse desempate minimiza peso, a menos que isso seja implementado explicitamente.

Antes da alocação, limitar o número de células da tabela, por exemplo a 1.000.000.
Documentar que esse limite controla o tamanho do problema, sem prometer consumo exato de memória.
Retornar mensagem clara se o limite for ultrapassado.

Resultado:
- Lotes escolhidos.
- Peso total em kg.
- Soma das prioridades.
- Capacidade restante.
- Lotes excluídos por prazo ou falta de conexão, com motivo.
- Lotes elegíveis que não foram selecionados, sem afirmar que eram individualmente inviáveis.

8. MENU

Implementar:
1. Listar locais e conexões.
2. Consultar menor caminho.
3. Listar lotes e sua elegibilidade para uma instituição.
4. Selecionar lotes conforme a capacidade do veículo.
5. Executar demonstração guiada dos algoritmos.
0. Sair.

Solicitar a instituição quando necessário e validar seu tipo.
Permitir repetir operações.
Tratar entradas inválidas sem encerrar com traceback.
Tratar encerramento por EOF ou interrupção do usuário de forma simples.

Exibir unidades, referência temporal e IDs claramente.

A demonstração deve apresentar os dois cálculos separadamente, sem inventar um roteiro global de visitas.

9. TESTES AUTOMATIZADOS

Usar unittest.

Dijkstra:
- Menor caminho conhecido.
- Caminho indireto menor que uma ligação direta.
- Origem igual ao destino.
- Destino inacessível.
- Identificador inexistente.
- Empate determinístico.
- Rejeição de pesos inválidos.

Mochila:
- Solução ótima conhecida.
- Capacidade zero.
- Lista vazia.
- Nenhum lote cabe.
- Preenchimento exato.
- Cada lote aparece no máximo uma vez.
- Peso total não ultrapassa a capacidade.
- Prioridade retornada corresponde aos itens selecionados.
- Conversão exata de kg.
- Rejeição de precisão incompatível.
- Limite de células.
- Desempate determinístico.

Elegibilidade:
- Lote vencido.
- Prazo exatamente igual à referência.
- Lote de estabelecimento desconectado.
- Referência temporal alterada.

Carregamento:
- ID duplicado.
- Referência inexistente.
- Arquivo ou cabeçalho inválido.
- Conexão duplicada invertida.

Para instâncias pequenas de mochila, usar enumeração de subconjuntos nos testes como verificação independente do valor ótimo.
Não comparar uma seleção exata quando existirem múltiplas soluções ótimas, salvo para testar o desempate.

Criar um exemplo didático em que escolher primeiro o lote de maior prioridade seja pior que a programação dinâmica:
- Capacidade: 10 kg.
- Lote A: 6 kg, prioridade 10.
- Lote B: 5 kg, prioridade 9.
- Lote C: 5 kg, prioridade 9.

A escolha gulosa por prioridade individual pega A e totaliza 10.
A solução ótima escolhe B e C, totalizando 18.
Deixar claro que o exemplo refuta essa estratégia gulosa específica.

10. DOCUMENTAÇÃO

README com:
- Ficha da CitizenTech no início.
- Nome da solução.
- Cidade e bairro, deixando o bairro como PENDENTE se não definido.
- Cidadão beneficiado.
- Problema e funcionamento.
- Responsabilidade do módulo Python.
- Indicador demonstrável.
- ODS relacionados.
- Campo de repositório.
- Nomes e RMs como PENDENTE.
- Instalação e versão necessária.
- Execução do menu.
- Referência temporal.
- Comando para testes.
- Formato e origem fictícia dos dados.
- Limitações.
- Estrutura do projeto.

Não inventar entrevistas, usuários reais ou resultados medidos.

docs/algoritmos.md:
- Explicação de Dijkstra.
- Explicação de mochila com estado, caso-base e recorrência.
- Reconstrução dos itens.
- Exemplo resolvido manualmente.
- Complexidade de tempo e espaço.

Para mochila:
O(n × C) em tempo e espaço para a tabela proposta.
Explicar que C é a capacidade discretizada e que a complexidade é pseudopolinomial.

Para Dijkstra:
Descrever a complexidade correspondente à implementação real com heapq, considerando inserções repetidas no heap caso existam.

Não inventar benchmarks.

docs/roteiro-demonstracao.md:
- Sequência curta de apresentação.
- Entradas e resultados esperados.
- Explicação das diferenças entre os algoritmos.
- Perguntas prováveis do professor e respostas baseadas no código.

docs/checklist-entrega.md:
- Código completo.
- Dados necessários.
- README com integrantes e RMs.
- Testes executados.
- Execução validada após extrair o ZIP.
- Pendências reais.
- Relação dos arquivos que devem ser entregues.

prompts.md:
Registrar integralmente este pedido e as decisões relevantes.

.gitignore:
Ignorar __pycache__, arquivos .pyc, ambientes virtuais e arquivos de IDE.

Não gerar PDF, pois a entrega descrita de Dynamic Programming exige código e README no ZIP.

11. VERIFICAÇÃO E ENTREGA

Execute os testes e percorra o menu com entradas de exemplo.
Confirme que funciona sem Oracle, Java, APIs externas ou dependências de terceiros.
Confira os exemplos numéricos e o roteiro contra o resultado efetivo.

Não declare sucesso sem executar.
Se o ambiente impedir alguma verificação, informe exatamente o motivo.

Ao finalizar, apresente:
- Funcionalidades implementadas.
- Arquivos principais.
- Versão do Python realmente utilizada.
- Comandos para executar e testar.
- Quantidade real de testes e resultados.
- Exemplo de menor caminho.
- Exemplo de seleção ótima de lotes.
- Limitações.
- Pendências para entrega.

Não crie funcionalidades extras antes de concluir e verificar esse escopo.

---

## Decisões relevantes

1. **Algoritmos.** Dijkstra com `heapq` para o menor caminho; mochila 0/1 por tabulação bidimensional para os lotes. Sem memoização recursiva na mochila, porque o enunciado pedia tabulação.

2. **Módulos extras.** Foram acrescentados `excecoes.py`, `elegibilidade.py` e `selecao.py` para não misturar validação, filtro de prazo/grafo e a função genérica da mochila. A estrutura sugerida foi mantida.

3. **Laço no grafo.** Conexão de um local para ele mesmo é rejeitada na carga e em `Grafo.adicionar_aresta` como simplificação deste modelo (só há deslocamento entre locais distintos). Isso não se justifica por uma suposta ambiguidade do menor caminho: um laço de peso positivo não tornaria a consulta ambígua. Origem igual ao destino na consulta continua válida e devolve distância zero.

4. **Empate no Dijkstra.** Chave do heap `(distancia, id)` e relaxamento apenas com custo estritamente menor. Vizinhos ordenados por id.

5. **Empate na mochila.** Itens ordenados por id; se incluir não melhorar o valor, o item atual fica de fora.

6. **Tempo.** Referência padrão fixa `2026-11-11T12:00:00`. Argumento `--referencia`. Prazo igual à referência exclui o lote. Horários são hora civil de São Paulo **sem fuso explícito**. Textos com `Z` ou deslocamento (`-03:00`) são rejeitados; o fuso não é removido silenciosamente. Aplica-se a `--referencia` e a `prazo_aproveitamento`.

7. **Unidades.** `Decimal` e passo de `0.1` kg. Sem `float` na conversão.

8. **Limite da tabela.** `(n + 1) * (C + 1) > 1_000_000` levanta `TabelaMuitoGrande` antes de alocar, porque a tabela tem linhas `0..n`. Lista vazia e capacidade zero não criam tabela.

9. **Menu.** Entrada/saída só em `main.py`. Flag extra `--demonstracao` apenas dispara a opção 5 e encerra, para apresentação e verificação. Não adiciona algoritmo novo.

10. **Dados.** Nove locais fictícios em São Paulo, treze conexões simuladas, dez lotes. Padaria id 5 sem arestas. Lote 7 vencido; lote 10 com prazo igual à referência; lote 8 no estabelecimento isolado.

11. **Fora de escopo.** Sem web, login, mapa, banco, Java, Oracle, Data Science, PDF ou biblioteca de grafo/mochila pronta.

12. **Pendências.** Bairro e URL do repositório continuam PENDENTE. Nomes e RMs foram preenchidos depois, com os dados informados pela equipe:
    Felipe Senteio Bonilha (RM 562356), Felipe Rodrigues Viana de Andrade (RM 565341) e Joan Ferreira Campos (RM 562913).

13. **ODS da ficha.** A proposta do grupo cita ODS 2, 12, 11 e 13. O ODS 17 isolado foi removido. As contribuições aparecem como objetivos potenciais, sem impacto ambiental medido por este programa.

14. **CSV.** `_ler_csv` usa `csv.reader` (não `DictReader`) para detectar campos a mais/a menos antes de montar o dicionário, valida o cabeçalho primeiro, preserva vazios e trata UnicodeDecodeError, OSError e csv.Error com `ErroValidacao`. Não há `except Exception`.

---

## Pedido de revisão (integral)

Revise e corrija o projeto ReAlimenta SP — Planejador de Coletas existente nesta pasta.

Não recrie o projeto, não amplie o escopo e não adicione dependências externas. Preserve os nomes e RMs que acabei de informar nesta conversa, assim como qualquer identificação já preenchida corretamente.

Uma revisão executou os 47 testes existentes com sucesso, mas reproduziu três problemas que precisam de correção e testes de regressão.

1. DATAS COM FUSO HORÁRIO

Este comando provoca TypeError ao comparar datas com e sem fuso:

python main.py --demonstracao --referencia 2026-11-11T12:00:00-03:00

Adote uma política simples e consistente:
- As datas representam hora civil de São Paulo, sem fuso explícito.
- Rejeite datas com deslocamento, como -03:00, ou terminadas em Z.
- Não remova o fuso silenciosamente.
- Aplique a validação ao argumento --referencia e aos prazos dos CSVs.
- Informe o formato aceito com uma mensagem clara, sem traceback.

Adicione testes para:
- Data válida sem fuso.
- Data com -03:00.
- Data com Z.
- Data inválida.
- Prazo com fuso dentro de um CSV.
- Execução do comando problemático, comprovando saída controlada e ausência de traceback.

Atualize o README com essa convenção.

2. CARREGAMENTO DE CSV COM CAMPOS EXCEDENTES

Em realimenta/carregamento.py, _abrir_csv() chama strip() nas chaves retornadas por DictReader. Quando uma linha tem campos excedentes, aparece uma chave None e ocorre AttributeError.

Exemplo que reproduz o problema em locais.csv:

id,nome,tipo
1,Padaria,ESTABELECIMENTO,extra

Corrija o carregamento para:
- Detectar campos excedentes antes de tratar as chaves.
- Detectar campos ausentes.
- Retornar ErroValidacao com arquivo e linha.
- Preservar campos vazios para as validações apropriadas.
- Tratar erros de leitura, codificação e parsing CSV com mensagens compreensíveis.
- Validar o cabeçalho antes de processar as linhas.
- Usar a posição de linha fornecida pelo leitor quando possível.
- Continuar aceitando arquivos UTF-8 com ou sem BOM.

Não esconda erros de programação usando um except Exception genérico.

Adicione testes para:
- Linha com campo extra.
- Linha com campo ausente.
- Campo obrigatório vazio.
- Arquivo com codificação inválida.
- Cabeçalho incorreto.
- CSV válido com campo entre aspas contendo vírgula.
- Arquivo válido com BOM.

3. LIMITE DE CÉLULAS DA MOCHILA

Em realimenta/mochila.py, o código verifica:

celulas = n * (capacidade + 1)

Porém, a tabela alocada tem n + 1 linhas.

Corrija para:

celulas = (n + 1) * (capacidade + 1)

Faça essa verificação antes da alocação.
Preserve os retornos imediatos para lista vazia e capacidade zero, que não precisam criar tabela.

Adicione testes de fronteira:
- Tabela exatamente no limite: aceita.
- Tabela com uma célula acima do limite: rejeitada.
- Um item, capacidade 4 e limite 5: deve rejeitar, pois a tabela teria 10 células.

Atualize a documentação e as mensagens para corresponderem à contagem real.

4. DOCUMENTAÇÃO E IDENTIFICAÇÃO

- Preserve e confira os nomes e RMs já fornecidos.
- Não invente bairro, URL de repositório ou outros dados ausentes.
- Liste somente as informações que realmente continuarem pendentes.
- Corrija a afirmação de que um laço de peso positivo torna o menor caminho ambíguo. A rejeição de laços é uma simplificação escolhida para este modelo.
- Alinhe a Ficha CitizenTech à proposta do grupo, que cita ODS 2, 12, 11 e 13.
- Explique as contribuições como objetivos potenciais, sem alegar impacto ambiental medido pelo programa.
- Remova a inclusão isolada do ODS 17, salvo se houver uma decisão posterior explícita do grupo.
- Atualize prompts.md com este pedido e as alterações feitas.

5. VERIFICAÇÃO FINAL

Execute novamente:
python -m unittest discover -s tests -v
python main.py --demonstracao

Percorra o menu com:
- Consulta 6 → 1.
- Consulta 6 → 5, sem caminho.
- Seleção para instituição 6 e capacidade 10 kg.
- Capacidade zero.
- Capacidade negativa.
- Capacidade incompatível com unidades de 0,1 kg.
- Entrada inválida.
- Encerramento normal.

Confirme que os resultados do cenário continuam:
- 6 → 9 → 1: 7,6 km.
- 1 → 9 → 8 → 7 → 4: 7,9 km.
- Seleção de 10 kg: lotes 2, 3, 4 e 9, peso 9,6 kg, prioridade 29 e sobra de 0,4 kg.

Se houver divergência, investigue antes de alterar resultados esperados.

6. PACOTE DE ENTREGA

Prepare um ZIP limpo com código, dados, testes, README e documentação auxiliar.

Excluir:
- __pycache__
- Arquivos .pyc
- Ambientes virtuais
- Pasta .git
- Arquivos de IDE
- ZIPs anteriores

Não suponha que o .gitignore controle a compactação: aplique as exclusões ao criar o ZIP.

Extraia o pacote em uma pasta temporária e execute a demonstração e os testes a partir dessa cópia para verificar que não falta nenhum arquivo.

Não gerar PDF: a entrega desta disciplina é código completo e README em ZIP.

## Alterações feitas nesta revisão

- `interpretar_data_iso` rejeita Z e deslocamento; `main.py` já captura `ErroValidacao` e imprime em stderr sem traceback.
- `_ler_csv` substituiu `_abrir_csv`/`DictReader`.
- Limite da mochila passou a `(n + 1) * (C + 1)`.
- Ficha CitizenTech: ODS 2, 11, 12 e 13; objetivos potenciais; nomes e RMs preservados.
- Laço documentado como simplificação do modelo.
- Testes novos em `tests/test_datas.py`, `tests/test_carregamento.py` e `tests/test_mochila.py`.
