# Explicação do Algoritmo Minimax (bem passo a passo)

Este documento explica **só o cérebro do computador**: a classe `Minimax` do
arquivo `jogo_velha_dificuldades.py`. A parte do jogo em si está no outro
arquivo (`EXPLICACAO_JOGO.md`).

Vou explicar **devagar, com detalhes e exemplos**, sem assumir que você já sabe
o que é Minimax. Leia na ordem.

---

## 1. Qual é a ideia? (a intuição antes do código)

O Minimax é uma forma do computador **jogar perfeitamente**, sem chutar. A ideia
é simples de dizer:

> "Antes de jogar, eu imagino **todas** as continuações possíveis do jogo até o
> final, e escolho a jogada que me leva ao melhor resultado **supondo que o
> adversário também jogue da melhor forma possível para ele**."

Ou seja, o computador é um "estrategista paranoico": ele assume que **você joga
perfeito** e mesmo assim tenta achar o melhor caminho para ele. No Jogo da
Velha isso significa que, no Difícil, **é impossível ganhar do computador** — no
máximo você empata.

O nome **Mini-max** vem disso:
- O computador quer **maximizar** (MAX) o resultado dele.
- O adversário (você) quer **minimizar** (MIN) o resultado do computador.

> **Detalhe:** "jogar perfeito" aqui não é mágica — é **força bruta inteligente**.
> O computador literalmente testa todas as possibilidades. No Jogo da Velha isso
> é viável porque o tabuleiro é pequeno (no máximo 9 casas).

---

## 2. As "notas" do jogo: a função de utilidade

Para o computador comparar resultados, ele precisa dar uma **nota** para cada
fim de jogo. No código isso está em `_utilidade`:

```python
@staticmethod
def _utilidade(estado):
    if Minimax._venceu(estado, HUMANO):
        return -1
    if Minimax._venceu(estado, COMPUTADOR):
        return 1
    if Minimax._livres(estado) == 0:
        return 0
    return None  # jogo ainda em andamento
```

As notas são:

| Situação                         | Nota (`valor`) |
|----------------------------------|----------------|
| O **humano (X)** ganhou          | `-1`           |
| O **computador (O)** ganhou      | `+1`           |
| Deu **empate** (velha)           | `0`            |
| O jogo **ainda não acabou**      | `None`         |

A lógica é:

- O computador (que é o **MAX**) **gosta de números grandes**. Para ele, `+1`
  (ele ganha) é ótimo, `0` (empate) é mais ou menos, e `-1` (ele perde) é
  péssimo.
- O humano (o **MIN**) é o contrário: "gosta" de números pequenos. Para ele,
  `-1` (você ganha) é ótimo.

> **Detalhe sobre o `None`:** quando a função devolve `None`, ela está dizendo
> "ainda não dá para dar nota, o jogo não terminou". Isso é a deixa para o
> algoritmo continuar imaginando jogadas (você vai ver isso na seção 5).

> **Detalhe sobre `@staticmethod`:** essa palavrinha em cima da função só
> significa "esta função não precisa de um jogo específico para rodar, ela
> trabalha só com o `estado` (tabuleiro) que você passar". É um detalhe técnico,
> não muda a lógica.

---

## 3. As funções auxiliares (as "ferramentas" do cérebro)

Antes do algoritmo principal, o Minimax tem três ajudantes:

### 3.1. `_livres` — conta as casas vazias

```python
@staticmethod
def _livres(estado):
    return sum(linha.count(LIVRE) for linha in estado)
```

Percorre as três linhas do tabuleiro, conta quantos `#` (casas vazias) tem em
cada uma e **soma tudo**. Resultado: "quantas casas ainda estão livres".

> Isso serve para duas coisas: saber se deu **empate** (0 casas livres) e saber
> até onde o algoritmo precisa imaginar jogadas (a "profundidade").

### 3.2. `_posicoes_livres` — lista as casas vazias

```python
@staticmethod
def _posicoes_livres(estado):
    return [(i, j) for i in range(3) for j in range(3)
            if estado[i][j] == LIVRE]
```

Devolve uma **lista de coordenadas** `(linha, coluna)` de todas as casas vazias.
Por exemplo, se só as casas do meio e do canto estiverem livres, ela devolve
algo como `[(0, 0), (1, 1)]`.

> **Detalhe:** isso é uma **"list comprehension"** — uma forma compacta do Python
> de montar uma lista. Lê-se: "para cada linha `i` (0,1,2) e cada coluna `j`
> (0,1,2), **se** aquela casa estiver livre, inclua o par `(i, j)`". São as
> jogadas que o computador **poderia** fazer agora.

### 3.3. `_venceu` — alguém fez três em linha?

```python
@staticmethod
def _venceu(estado, c):
    for i in range(3):
        if all(estado[i][j] == c for j in range(3)):   # linha
            return True
        if all(estado[j][i] == c for j in range(3)):   # coluna
            return True
    if all(estado[i][i] == c for i in range(3)):       # diagonal principal
        return True
    if all(estado[i][2 - i] == c for i in range(3)):   # diagonal secundaria
        return True
    return False
```

Recebe um símbolo `c` (que pode ser `X` ou `O`) e responde **"esse jogador
ganhou?"** (`True` = sim, `False` = não). Ele checa as 8 formas de vencer:

- **3 linhas** (`estado[i][j]` com `i` fixo) — três iguais na horizontal.
- **3 colunas** (`estado[j][i]` com `i` fixo) — três iguais na vertical.
- **A diagonal principal** (`estado[i][i]`: casas (0,0), (1,1), (2,2)).
- **A diagonal secundária** (`estado[i][2-i]`: casas (0,2), (1,1), (2,0)).

> **Detalhe sobre o `all(...)`:** `all(estado[i][j] == c for j in range(3))`
> quer dizer "**todas** as três casas dessa linha são iguais a `c`?". O `all`
> só dá `True` quando a condição vale para os três `j` (0, 1 e 2). É o jeito
> curto de checar "três em linha".

---

## 4. Como o algoritmo é chamado: `get_melhor`

```python
def get_melhor(self):
    """Devolve (linha, coluna, valor) da melhor jogada para o computador."""
    return self._algoritmo_ab(self.estado, jogador=False,
                              profundidade=self._livres(self.estado),
                              alfa=-999, beta=999)
```

Esse é o "botão" que o jogo aperta quando quer a jogada do computador. Ele
chama o algoritmo de verdade (`_algoritmo_ab`) já passando:

- **`self.estado`** — o tabuleiro de agora.
- **`jogador=False`** — começa a pensar **como o computador** (MAX). No código,
  `False` significa "vez do computador (O)" e `True` significa "vez do humano
  (X)". (É só uma convenção escolhida.)
- **`profundidade=self._livres(...)`** — quantas jogadas ainda cabem no jogo
  (= casas livres). É o "fôlego" da imaginação.
- **`alfa=-999, beta=999`** — dois valores usados na **poda Alfa-Beta**, que é
  uma otimização (explicada na seção 6). Por enquanto, pense neles como
  "começam bem abertos: -999 e 999".

No final, ele devolve três coisas: **a melhor linha, a melhor coluna e a nota**
daquela jogada.

---

## 5. O coração: o método `_algoritmo_ab` (a recursão)

Aqui está o algoritmo de verdade. Ele é **recursivo**, ou seja, **chama a si
mesmo**. Isso assusta no começo, mas a ideia é natural: "para saber se uma
jogada é boa, eu preciso imaginar a resposta do adversário a ela — e para isso
eu rodo o mesmo raciocínio um nível mais fundo".

```python
def _algoritmo_ab(self, estado, jogador, profundidade, alfa, beta):
    valor = self._utilidade(estado)
    if valor is not None:
        return (-1, -1, valor)
    ...
```

### 5.1. A "parada" (caso base)

```python
valor = self._utilidade(estado)
if valor is not None:
    return (-1, -1, valor)
```

Primeiro o algoritmo pergunta: **"esse tabuleiro já é um fim de jogo?"**

- Se a utilidade **não for `None`** (ou seja, alguém ganhou ou empatou), o jogo
  acabou nesse galho da imaginação. Ele devolve a nota (`valor`) e para. O
  `(-1, -1, ...)` é só porque aqui não há mais jogada a fazer — o que importa é
  a nota.

> **Detalhe:** todo algoritmo recursivo precisa de um **caso base**, um ponto
> de parada, senão ele se chamaria para sempre. Aqui o ponto de parada é
> "chegou num fim de jogo". É como uma árvore: as folhas são os fins de jogo.

### 5.2. Imaginar as jogadas (o caso recursivo)

Se o jogo **não** acabou, o algoritmo se divide em dois casos: a vez do humano
(MIN) ou a vez do computador (MAX). São quase espelhados. Vamos ver o do
computador (MAX), que é o que mais interessa:

```python
else:        # MAX -> computador (O)
    maior = -999
    for (i, j) in self._posicoes_livres(estado):
        estado[i][j] = COMPUTADOR
        _, _, v = self._algoritmo_ab(estado, True, profundidade - 1, alfa, beta)
        estado[i][j] = LIVRE
        if v > maior:
            maior, melhor_lin, melhor_col = v, i, j
        if maior > beta:
            return (melhor_lin, melhor_col, maior)
        alfa = max(alfa, v)
    return (melhor_lin, melhor_col, maior)
```

Passo a passo:

1. **`maior = -999`** — começa com uma nota "horrível" para o computador, para
   que **qualquer** jogada real pareça melhor. (É o "vou registrando a melhor
   que eu achar".)

2. **`for (i, j) in self._posicoes_livres(estado):`** — testa **cada casa
   vazia**, uma de cada vez. Para cada uma:

   - **`estado[i][j] = COMPUTADOR`** — finge colocar um `O` ali (jogada de
     mentirinha, só para imaginar).

   - **`_, _, v = self._algoritmo_ab(estado, True, profundidade - 1, ...)`** —
     **aqui está a mágica da recursão**: agora ele pergunta "se eu jogasse
     aqui, qual seria o melhor que o **adversário** (`True` = humano/MIN)
     consegue fazer depois?". O `v` que volta é a nota final daquele caminho,
     já considerando a melhor resposta do adversário, a resposta dele à
     resposta, e assim por diante até o fim do jogo.

     > **Detalhe sobre `profundidade - 1`:** cada nível que descemos na
     > imaginação tem **uma casa a menos** livre. Por isso passamos
     > `profundidade - 1`. É o jogo encolhendo a cada jogada imaginada.

   - **`estado[i][j] = LIVRE`** — **desfaz** a jogada de mentirinha, devolvendo
     o `#` para a casa. Isso é importantíssimo: como estamos só **imaginando**,
     precisamos deixar o tabuleiro do jeito que estava antes de testar a próxima
     casa.

     > **Detalhe:** essa dupla "colocar e depois tirar" se chama
     > **backtracking** (voltar atrás). O computador testa uma possibilidade,
     > vê no que dá, e **desfaz** para testar a próxima — como apagar uma
     > tentativa no rascunho antes de tentar outra.

   - **`if v > maior:`** — se essa jogada imaginada deu uma nota melhor (maior)
     do que a melhor até agora, ele **guarda** essa como a nova melhor:
     `maior, melhor_lin, melhor_col = v, i, j`.

3. **`return (melhor_lin, melhor_col, maior)`** — depois de testar todas as
   casas, devolve a **melhor jogada encontrada** e a nota dela.

O caso do humano (MIN) é o **espelho**: em vez de `maior` ele usa `menor = 999`
e procura a **menor** nota (`if v < menor`), porque o humano "quer" deixar a
nota do computador o mais baixa possível. Coloca `X` em vez de `O`. O resto é
igual.

> **Detalhe — por que isso funciona:** o computador (MAX) escolhe o galho de
> **maior** nota; mas dentro de cada galho ele já contou que o humano (MIN) vai
> escolher o galho de **menor** nota. Os dois se alternam, nível a nível, até o
> fim do jogo. É essa alternância "eu maximizo, você minimiza, eu maximizo..."
> que faz o computador jogar perfeito.

---

## 6. A poda Alfa-Beta (a parte do "AB" no nome)

O Minimax puro imagina **muitos** tabuleiros — às vezes mais do que o
necessário. A **poda Alfa-Beta** é um truque para **pular** ramos que com
certeza não vão importar, **sem mudar o resultado final**. É só mais rápido.

As duas variáveis:

- **`alfa`** — a melhor nota que o **MAX** (computador) já garantiu até agora.
- **`beta`** — a melhor nota que o **MIN** (humano) já garantiu até agora.

No trecho do MAX, a poda aparece aqui:

```python
if maior > beta:
    return (melhor_lin, melhor_col, maior)
alfa = max(alfa, v)
```

A intuição (em linguagem humana):

> "Eu (MAX) já achei uma jogada com nota `maior`. Se essa nota já passou do
> `beta` (o limite que o adversário toleraria lá em cima), então o adversário
> **nunca vai me deixar chegar aqui** — ele escolheria outro caminho antes. Logo,
> **não adianta** eu continuar testando as outras casas deste ramo. Paro já."

Esse "paro já" é o `return` antecipado: ele **corta** (poda) o resto do laço.

No lado do MIN é o espelho:

```python
if menor < alfa:
    return (melhor_lin, melhor_col, menor)
beta = min(beta, v)
```

> **Detalhe importante:** a poda Alfa-Beta **não muda a jogada escolhida** —
> ela chega exatamente no mesmo resultado do Minimax normal, só que **olhando
> menos possibilidades**. É puramente uma economia de tempo. Pense nela como
> "parar de ler um caminho do mapa assim que você percebe que ele não leva a
> lugar nenhum melhor do que o que você já tem".

---

## 7. Juntando tudo: o que acontece numa jogada do computador

Quando é a vez do computador e ele decide pensar, isto acontece:

1. O jogo chama `Minimax(tabuleiro).get_melhor()`.
2. `get_melhor` dispara `_algoritmo_ab` começando como **MAX** (computador).
3. O algoritmo testa cada casa livre, e para cada uma **imagina o jogo inteiro
   até o fim**, alternando MAX (computador) e MIN (humano) a cada nível,
   usando backtracking para desfazer as jogadas imaginadas.
4. A poda Alfa-Beta corta os ramos que não podem melhorar a decisão.
5. No fim, devolve `(melhor_linha, melhor_coluna, nota)`.
6. O jogo coloca o `O` na melhor casa e imprime `[MINIMAX] ...`.

---

## 8. Resumindo em uma frase

O Minimax faz o computador **imaginar todas as continuações possíveis do jogo**,
assumindo que o adversário também joga perfeito, e escolher a jogada com a
melhor nota garantida; a **poda Alfa-Beta** só faz isso mais rápido, ignorando
caminhos que comprovadamente não importam. Por isso, no Difícil, **dá no máximo
para empatar** com a máquina.
