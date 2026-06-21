# Trabalho A* — Respostas

Respostas fundamentadas no código que está no diretório (`AlgoritmoAStar.java`, `Cidades.java`, `Nodo.java`, `cidades.txt`).

---

## 1. Em que tipo de aplicações o A* é usado? Qual seu propósito? Exemplos.

**Propósito:** encontrar o **caminho de menor custo** entre um nó inicial e um nó objetivo em um espaço de busca, combinando duas informações:
- o custo **já percorrido** (`g(n)`),
- uma **estimativa do custo restante** até o objetivo (`h(n)`).

Garante a **solução ótima** desde que a heurística seja **admissível** (nunca superestime o custo real).

**Aplicações típicas:**
- **Navegação / GPS:** Google Maps, Waze, roteamento de veículos.
- **Jogos:** movimentação de NPCs, RTS (StarCraft, Age of Empires), RPGs, pathfinding em grids.
- **Robótica:** planejamento de trajetórias de robôs móveis e drones, desviando de obstáculos.
- **Redes de computadores:** roteamento de pacotes em redes com custos heterogêneos.
- **Resolução de problemas/puzzles:** 8-puzzle, 15-puzzle, cubo mágico, labirintos.
- **Planejamento em IA:** sequência de ações em sistemas de planejamento clássico.

---

## 2. Papel da função heurística — o que o A* faz para melhorar o Dijkstra

Rodando o programa em anexo (`java -classpath . AlgoritmoAStar cidades.txt 1 6` → `Caminho: 1 3 5 6   Distancia: 14`) observa-se o seguinte no código:

No método `proximoNo()` (linhas 89–109) o critério para escolher o próximo nó a expandir é:

```
f(n) = cur.getPeso() + heuristica(coord1[0], coord1[1], coord2[0], coord2[1])
       └── g(n) ──┘   └────────────── h(n) ──────────────┘
```

E em `heuristica()` (linhas 111–113):
```java
return Math.abs(lat1-lat2) + Math.abs(lon1-lon2);  // Distância de Manhattan
```

**Diferença para o Dijkstra:**
- **Dijkstra** escolhe o próximo nó usando **apenas `g(n)`** — o custo acumulado desde a origem. Como não sabe onde fica o objetivo, expande em todas as direções igualmente (busca "cega" guiada por custo).
- **A\*** acrescenta a heurística `h(n)` — uma estimativa do quanto ainda falta até o destino. A escolha passa a ser `f(n) = g(n) + h(n)`.

**Como isso melhora o desempenho:**
A heurística funciona como uma **bússola**: orienta a busca em direção ao objetivo, fazendo o algoritmo preferir nós geograficamente mais próximos do destino. Resultado:
- **Menos nós expandidos** (menos memória e menos tempo).
- **Mantém a otimalidade** se `h(n)` for admissível — é o caso da distância de Manhattan usada no código, pois ela nunca superestima a distância real em um grafo cujas arestas têm custo ≥ distância em linha reta.
- Quando `h(n) = 0` para todos os nós, o A\* **degenera em Dijkstra**.

---

## 3. Lógica do A\* passo a passo

Mapeando para as estruturas do código:
- `desconhecidos` — nós ainda não descobertos
- `conexoes` — **lista aberta** (fronteira: nós descobertos mas não expandidos)
- `visitados` — **lista fechada** (já expandidos)
- `noCorrente` — nó sendo expandido na iteração

**Passos (método `encontraCaminho`, linhas 38–57):**

1. **Inicialização** (`carregaDados`): lê o arquivo, cria todos os nós em `desconhecidos`, define `noInicial` e `noFinal`, e `noCorrente = noInicial`.

2. **Laço principal** (`while(noFinal != noCorrente)`):
   - **2.1.** Marca `noCorrente` como visitado (`visitados.add(noCorrente)`).
   - **2.2.** Remove `noCorrente` da lista aberta (`conexoes.remove(noCorrente)`).
   - **2.3. Expansão** (`insereconexoes`, linhas 60–86): para cada vizinho `i` com `matrizDistancias[id][i] > 0`:
     - Calcula `novoPeso = matrizDistancias[id][i] + noCorrente.getPeso()` (este é o `g(n)` do vizinho).
     - Se o vizinho ainda está em `desconhecidos` e não em `visitados`: atribui peso, define `setAnt(noCorrente)` (para reconstruir o caminho depois) e move-o para `conexoes`.
     - Se já está em `conexoes`: **só atualiza se o novo `g` for menor** que o atual (relaxamento).
   - **2.4. Seleção do próximo nó** (`proximoNo`, linhas 89–109): percorre `conexoes` e escolhe o nó com **menor `f(n) = g(n) + h(n)`**. Se `conexoes` está vazia → retorna `null` → "Não existe caminho".

3. **Reconstrução do caminho** (linhas 50–55): partindo de `noFinal`, segue os ponteiros `getAnt()` (ancestral) até a origem, imprimindo o caminho em ordem.

4. **Saída:** `Caminho: 1 3 5 6   Distancia: 14`.

**Em resumo conceitual:** A\* sempre **expande o nó mais promissor** da fronteira (menor `f = g + h`), até alcançar o objetivo; mantém ponteiros de pai para reconstruir o caminho ótimo no final.

---

## 4. A\* só funciona em grafo? E em árvore?

**Sim, funciona em árvore.** Uma árvore é um **caso particular de grafo** (conexo, acíclico, sem múltiplos caminhos entre dois nós).

Distinções práticas:
- **Em grafo:** é necessária a **lista fechada (`visitados`)** para evitar reexpandir nós e tratar ciclos / múltiplos caminhos para o mesmo estado. O código exemplifica isso ao checar `!visitados.contains(aux)`.
- **Em árvore:** como há **um único caminho** entre cada par de nós e não existem ciclos, a lista fechada é **dispensável** — basta a fronteira (lista aberta). A versão simplificada é chamada **"A\* tree search"**, enquanto a versão completa do código é a **"A\* graph search"**.

De forma mais ampla, o A\* serve para **qualquer espaço de estados representável como grafo de busca** — incluindo grades (jogos), árvores de jogadas, espaços contínuos discretizados etc.

---

## 5. Diferença entre A\* e IDA\* (Iterative Deepening A\*)

| Aspecto | A\* | IDA\* |
|---|---|---|
| **Estratégia** | Best-first search guiada por `f = g + h` | Busca em profundidade iterativa com **limite de `f`** |
| **Memória** | **O(b^d)** — guarda lista aberta + fechada | **O(d)** — apenas a pilha do caminho atual |
| **Tempo** | Geralmente mais rápido | Mais lento (revisita nós em cada iteração) |
| **Estruturas** | Open list (priority queue) + Closed list | Apenas pilha de recursão |
| **Quando usar** | Espaços de busca pequenos/médios | Espaços enormes onde A\* estoura a memória |

**Como o IDA\* funciona:**
1. Define um **limite inicial** `threshold = h(início)`.
2. Faz uma **DFS** expandindo só nós com `f(n) ≤ threshold`.
3. Se acha o objetivo → retorna o caminho.
4. Se não acha → atualiza `threshold` para o **menor `f` que excedeu o limite** na iteração anterior e repete.
5. Continua até encontrar a solução.

**Trade-off:** IDA\* sacrifica tempo (reexpansões) para ganhar memória. É usado em problemas como o **15-puzzle, cubo de Rubik** e outros espaços de estado gigantescos onde uma lista aberta de A\* não caberia em memória. Ambos preservam **otimalidade** com heurística admissível.
