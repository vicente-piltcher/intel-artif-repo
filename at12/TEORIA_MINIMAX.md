# Minimax — Fundamentação Teórica

## 1. Onde o Minimax se encaixa

O Minimax é um algoritmo de **decisão sequencial em ambientes adversariais**.
Ele pertence à teoria dos jogos e à IA clássica de busca. Aplica-se a uma classe
específica de jogos: os **jogos de soma zero, de dois jogadores, com informação
perfeita e determinísticos**. Vale destrinchar cada uma dessas condições, porque
são elas que justificam o algoritmo:

- **Dois jogadores:** há exatamente dois agentes que se alternam.
- **Soma zero:** o ganho de um é exatamente a perda do outro. Não existe
  cooperação possível nem resultado "bom para os dois". Isso permite descrever o
  jogo inteiro com **uma única função de valor**: o que um jogador quer
  maximizar, o outro quer minimizar.
- **Informação perfeita:** ambos enxergam o estado completo a todo momento. Não
  há cartas escondidas, dados ou incerteza oculta.
- **Determinístico:** uma ação leva sempre ao mesmo estado seguinte; não há
  aleatoriedade.

Quando essas condições valem, existe um resultado teórico forte que dá base ao
algoritmo.

## 2. A base teórica: o teorema minimax e o valor do jogo

A fundação vem do **teorema minimax de von Neumann (1928)**. A ideia central é o
**valor do jogo**: para jogos de soma zero com informação perfeita, existe um
valor ótimo garantido que o jogador MAX consegue assegurar independentemente do
que MIN faça, e esse valor coincide com o que MIN consegue limitar
independentemente do que MAX faça. Formalmente, os dois "pontos de vista" se
encontram:

$$\max_{a}\min_{b} \; U(a,b) \;=\; \min_{b}\max_{a} \; U(a,b)$$

Onde $U$ é a função de utilidade (o resultado). A consequência prática é
profunda: **existe uma estratégia ótima determinística para cada jogador**, e
jogá-la garante o melhor resultado *no pior caso*. O Minimax é simplesmente o
procedimento que **calcula essa estratégia** percorrendo o jogo.

Em termos de teoria dos jogos, essa estratégia ótima é um **equilíbrio**:
nenhum jogador melhora seu resultado desviando unilateralmente. Por isso se diz
que o Minimax joga "perfeitamente" — não no sentido de sempre vencer, mas de
nunca obter menos do que o valor do jogo permite.

## 3. A modelagem: árvore de jogo

O Minimax representa o jogo como uma **árvore de busca**:

- A **raiz** é o estado atual.
- Cada **nó** é um estado possível do jogo.
- Cada **aresta** é uma ação (jogada legal) que leva de um estado a outro.
- Os **nós folha** são estados terminais (o jogo acabou), e a eles se atribui
  uma utilidade numérica via a **função de utilidade** $U$.
- Os **níveis se alternam** entre os dois jogadores: um nível é de MAX, o
  seguinte é de MIN, e assim por diante.

Essa alternância é o coração do método. Não basta perguntar "qual jogada me dá o
melhor estado seguinte?" — é preciso perguntar "qual jogada me dá o melhor
estado seguinte *dado que, depois, meu oponente jogará para me prejudicar ao
máximo, e depois eu reajo otimamente, e assim por diante até o fim*".

## 4. A regra de propagação (a recursão minimax)

O valor de um nó é definido **recursivamente**, de baixo para cima (das folhas
em direção à raiz):

$$
\text{minimax}(n) =
\begin{cases}
U(n) & \text{se } n \text{ é terminal} \\[4pt]
\max_{s \,\in\, \text{sucessores}(n)} \text{minimax}(s) & \text{se } n \text{ é nó MAX} \\[4pt]
\min_{s \,\in\, \text{sucessores}(n)} \text{minimax}(s) & \text{se } n \text{ é nó MIN}
\end{cases}
$$

Lê-se assim:

- Nas **folhas**, o valor é dado diretamente pela utilidade (quem ganhou, quem
  perdeu, ou empate).
- Num **nó MAX**, o jogador escolhe a ação que **maximiza** o valor — então o
  valor do nó é o *maior* entre os valores dos filhos.
- Num **nó MIN**, o oponente escolhe a ação que **minimiza** o valor — então o
  valor do nó é o *menor* entre os valores dos filhos.

O algoritmo desce até as folhas, avalia-as, e **propaga os valores para cima**:
cada nó "herda" o valor do filho que seu respectivo jogador escolheria. Ao
chegar à raiz, o valor obtido é o valor do jogo, e a ação que leva ao filho com
esse valor é a **jogada ótima**.

A premissa embutida é forte e essencial: **o adversário também joga otimamente**.
O Minimax é pessimista por construção — ele nunca conta com o erro do oponente.
Por isso o resultado que ele garante é um *limite inferior*: se o oponente
errar, o resultado real pode ser ainda melhor, nunca pior.

## 5. Complexidade e o problema do tamanho

O Minimax puro é uma busca **em profundidade** que precisa, em princípio, visitar
toda a árvore. Se o **fator de ramificação** (número médio de jogadas por estado)
é $b$ e a **profundidade** (número de jogadas até o fim) é $d$, o custo de tempo
é:

$$O(b^d)$$

Esse crescimento **exponencial** é a limitação central. Para jogos pequenos a
árvore inteira cabe na memória e o Minimax resolve o jogo de forma exata. Para
jogos grandes (xadrez, Go), $b^d$ é astronômico e a busca completa é inviável.
Duas técnicas atacam esse problema.

### (a) Poda Alfa-Beta

Uma otimização que produz **exatamente o mesmo resultado** do Minimax, mas
evitando explorar ramos que comprovadamente não podem influenciar a decisão. Ela
mantém dois limites durante a busca:

- **α (alfa):** o melhor valor que MAX já consegue garantir até aqui.
- **β (beta):** o melhor valor que MIN já consegue garantir até aqui.

Sempre que, num nó, esses limites se cruzam (**α ≥ β**), o restante daquele ramo
é **podado** (ignorado), porque um dos jogadores nunca permitiria que o jogo
chegasse ali — ele escolheria outro caminho antes. A poda não muda a jogada
escolhida; só economiza trabalho. No melhor caso (filhos ordenados do melhor
para o pior), a complexidade cai para:

$$O(b^{d/2})$$

o que efetivamente **dobra a profundidade** alcançável com o mesmo esforço.

### (b) Corte por profundidade + função de avaliação

Quando nem com poda dá para chegar às folhas, interrompe-se a busca a uma
profundidade limitada e usa-se uma **função heurística de avaliação** que
*estima* o valor de um estado não-terminal (em vez da utilidade exata). Essa é a
base de praticamente todos os motores de jogos de tabuleiro clássicos. O preço é
que a otimalidade teórica se perde — a qualidade do jogo passa a depender da
qualidade da heurística.

## 6. Resumo conceitual

| Conceito | O que é |
|---|---|
| **Premissa** | Jogo de soma zero, 2 jogadores, informação perfeita, determinístico |
| **Garantia teórica** | Teorema minimax: existe valor e estratégia ótima do jogo |
| **Estrutura** | Árvore de jogo com níveis alternados MAX/MIN |
| **Regra** | MAX maximiza, MIN minimiza, valores propagam das folhas à raiz |
| **Postura** | Pessimista: assume oponente ótimo → garante o pior caso |
| **Custo** | $O(b^d)$, exponencial |
| **Otimizações** | Poda Alfa-Beta (exata, $O(b^{d/2})$); corte + heurística (aproximada) |

Em uma frase: **o Minimax calcula a estratégia ótima de um jogo adversarial de
soma zero modelando-o como uma árvore de decisões alternadas e propagando, de
baixo para cima, o melhor resultado que cada jogador consegue garantir contra um
oponente igualmente racional.**
