# Explicação do Jogo da Velha (bem passo a passo)

Este documento explica o código do arquivo `jogo_velha_dificuldades.py`, a parte
do **jogo** (não o algoritmo Minimax — esse tem um `.md` só dele:
`EXPLICACAO_MINIMAX.md`).

A ideia aqui é explicar **devagar e com detalhes**, sem assumir que você já
sabe nada. Se você nunca programou em Python, tudo bem: leia na ordem.

---

## 1. A ideia geral do jogo

É um Jogo da Velha (aquele do `#`, `X` e `O`) jogado no **terminal** (a telinha
preta de texto). Você é o **X** e o computador é o **O**.

O tabuleiro é uma grade 3x3:

```
    0   1   2
0   #   #   #
1   #   #   #
2   #   #   #
```

- `#` quer dizer "casa vazia" (ninguém jogou ali ainda).
- `X` é você.
- `O` é o computador.

Os números em cima (`0 1 2`) são as **colunas** e os números do lado esquerdo
(`0 1 2`) são as **linhas**. Para jogar você diz "linha 1, coluna 2", por
exemplo, e o seu `X` vai parar naquela casa.

> **Detalhe importante:** em programação a contagem começa no **0**, não no 1.
> Então as linhas são 0, 1 e 2 (e não 1, 2, 3). A primeira casa do canto
> superior esquerdo é "linha 0, coluna 0".

---

## 2. As três "etiquetas" lá no topo do arquivo

Logo no começo do código tem isto:

```python
LIVRE = '#'
HUMANO = 'X'      # MIN no minimax
COMPUTADOR = 'O'  # MAX no minimax
```

Isso é só dar **nomes bonitos** para os símbolos. Em vez de o programa ficar
escrevendo `'#'`, `'X'` e `'O'` o tempo todo (e a gente esquecer o que cada um
significa), criamos três "apelidos":

- `LIVRE` = a casa vazia `#`
- `HUMANO` = você, o `X`
- `COMPUTADOR` = a máquina, o `O`

> **Detalhe:** isso se chama **constante**. É um valor que não muda durante o
> jogo. Escrever `HUMANO` no código é mais fácil de entender do que `'X'`. Os
> comentários `# MIN no minimax` e `# MAX no minimax` só interessam para o
> algoritmo Minimax — ignore por enquanto.

---

## 3. O "molde" do jogo: a classe `JogoVelhaDificuldades`

Em Python, uma **classe** é como um molde/forma que junta:

- os **dados** do jogo (o tabuleiro, a dificuldade escolhida), e
- as **ações** do jogo (jogar, mostrar o tabuleiro, ver quem ganhou).

A nossa classe se chama `JogoVelhaDificuldades`. Tudo que é função dentro dela
(`def alguma_coisa(self, ...)`) é chamado de **método** — é só uma ação que o
jogo sabe fazer.

> **Detalhe sobre o `self`:** você vai ver `self` aparecendo em todo método.
> Pense no `self` como "este jogo específico". Quando o código diz
> `self.tabuleiro`, ele quer dizer "o tabuleiro **deste** jogo". É assim que o
> Python sabe de qual tabuleiro estamos falando.

### 3.1. O começo: `__init__` (nascimento do jogo)

```python
def __init__(self):
    self.tabuleiro = [[LIVRE] * 3 for _ in range(3)]
    self.prob_minimax = 1.0
    self.nome_dificuldade = ""
```

O `__init__` é um método **especial**: ele roda automaticamente quando o jogo
é criado. É o "momento do nascimento". Aqui ele prepara três coisas:

1. **`self.tabuleiro`** — cria a grade 3x3 toda vazia.
   - `[LIVRE] * 3` cria uma linha com três `#`: `['#', '#', '#']`.
   - O `for _ in range(3)` repete isso **três vezes**, formando 3 linhas.
   - Resultado: uma "lista de listas", que é a nossa grade.

   > **Detalhe:** o `_` (underline) é um nome de variável que quer dizer
   > "não me importo com esse valor, só quero repetir 3 vezes". É costume em
   > Python usar `_` quando o valor em si não interessa.

2. **`self.prob_minimax = 1.0`** — a chance de o computador usar o "cérebro"
   (Minimax). Começa em `1.0` (100%), mas vai ser trocada quando você escolher
   a dificuldade.

3. **`self.nome_dificuldade = ""`** — só um texto vazio por enquanto ("Facil",
   "Medio" ou "Dificil" entra aqui depois).

---

## 4. O coração do jogo: o método `iniciar`

```python
def iniciar(self):
    print("JOGO DA VELHA")
    print("Voce e o X. O computador e o O.")
    self._escolhe_dificuldade()

    print(f"\nDificuldade escolhida: {self.nome_dificuldade}")
    print("Tabuleiro inicial:")
    self._exibe()

    vez_x = True
    while True:
        if vez_x:
            self.jogada_x()
        else:
            self.jogada_O()

        self._exibe()

        resultado = self._verifica_fim()
        if resultado is not None:
            self._anuncia_resultado(resultado)
            break
        vez_x = not vez_x
```

Esse é o método que **conduz a partida do início ao fim**. Vamos por partes.

1. Mostra as boas-vindas com `print(...)` (escrever na tela).
2. `self._escolhe_dificuldade()` — pergunta se você quer Fácil, Médio ou
   Difícil (explicado na seção 5).
3. `self._exibe()` — desenha o tabuleiro vazio na tela.

Depois vem a parte mais importante, o **laço do jogo**:

- **`vez_x = True`** — uma plaquinha que diz "é a vez do X?". Começa como
  `True` (verdadeiro), porque **você joga primeiro**.

- **`while True:`** — isso é um **loop infinito**: "repita para sempre". Cada
  volta do loop é **uma jogada**. O loop só termina quando alguém ganha ou
  dá empate (com o `break` lá embaixo).

  > **Detalhe:** `True` significa "verdadeiro/sim" e `False` significa
  > "falso/não". O `while True` repete enquanto a condição for verdadeira — e
  > como ela é sempre `True`, só paramos manualmente com `break`.

- Dentro do loop:
  - **`if vez_x:`** — se for a vez do X, chama `self.jogada_x()` (sua jogada).
  - **`else:`** — senão, chama `self.jogada_O()` (jogada do computador).
  - `self._exibe()` — redesenha o tabuleiro depois da jogada.
  - **`resultado = self._verifica_fim()`** — checa se o jogo acabou.
  - **`if resultado is not None:`** — se o jogo **acabou** (tem um resultado),
    anuncia quem ganhou e usa `break` para **sair do loop** (fim de jogo).

    > **Detalhe:** `None` em Python quer dizer "nada", "vazio". O
    > `_verifica_fim()` devolve `None` quando o jogo **ainda não acabou**.
    > Então `is not None` quer dizer "se NÃO for nada", ou seja, "se realmente
    > tem um resultado (alguém ganhou ou empatou)".

  - **`vez_x = not vez_x`** — **troca a vez**. O `not` inverte: se era `True`
    (vez do X) vira `False` (vez do O) e vice-versa. É como passar a vez para
    o outro jogador.

---

## 5. Escolher a dificuldade: `_escolhe_dificuldade`

```python
def _escolhe_dificuldade(self):
    opcoes = {1: (0.25, "Facil"), 2: (0.50, "Medio"), 3: (1.00, "Dificil")}
    while True:
        print("\nEscolha a dificuldade:")
        print("  1 - Facil")
        print("  2 - Medio")
        print("  3 - Dificil")
        opcao = self._ler_inteiro("Opcao: ")
        if opcao in opcoes:
            self.prob_minimax, self.nome_dificuldade = opcoes[opcao]
            return
        print("Opcao invalida")
```

Aqui o programa pergunta qual nível você quer.

- **`opcoes = {...}`** — isso é um **dicionário**. Pense nele como uma
  tabelinha de "de–para": a chave `1` aponta para `(0.25, "Facil")`, a `2`
  para `(0.50, "Medio")` e a `3` para `(1.00, "Dificil")`.
  - O primeiro número é a **probabilidade de o computador usar o Minimax**:
    - Fácil: `0.25` = 25% das jogadas com o "cérebro", 75% no chute.
    - Médio: `0.50` = metade e metade.
    - Difícil: `1.00` = 100% pensando (joga perfeito, é quase impossível
      ganhar dele).

- **`while True:`** — repete a pergunta até você digitar uma opção válida.
- **`opcao = self._ler_inteiro("Opcao: ")`** — lê o número que você digitou
  (explicado na seção 9).
- **`if opcao in opcoes:`** — confere se o número digitado é 1, 2 ou 3.
  - Se for, **`self.prob_minimax, self.nome_dificuldade = opcoes[opcao]`**
    pega os dois valores da tabelinha de uma vez (a probabilidade e o nome) e
    guarda no jogo. Depois `return` encerra o método (escolha feita).
  - Se **não** for, mostra "Opcao invalida" e o `while` faz a pergunta de novo.

---

## 6. A sua jogada: `jogada_x`

```python
def jogada_x(self):
    while True:
        print("\nSua vez (X).")
        l = self._ler_inteiro("Informe a linha: ")
        c = self._ler_inteiro("Informe a coluna: ")
        if 0 <= l <= 2 and 0 <= c <= 2 and self.tabuleiro[l][c] == LIVRE:
            self.tabuleiro[l][c] = HUMANO
            return
        print("Coordenadas invalidas ou celula ocupada!")
```

Aqui você joga.

- **`l = self._ler_inteiro("Informe a linha: ")`** — lê a linha (0, 1 ou 2).
- **`c = self._ler_inteiro("Informe a coluna: ")`** — lê a coluna.
- **O `if` é uma verificação tripla** (tudo precisa ser verdade ao mesmo tempo,
  por causa do `and`):
  1. `0 <= l <= 2` — a linha está entre 0 e 2? (não pode ser 5, -1, etc.)
  2. `0 <= c <= 2` — a coluna está entre 0 e 2?
  3. `self.tabuleiro[l][c] == LIVRE` — aquela casa está **vazia**? (não pode
     jogar em cima de uma casa já ocupada).
  - Se as **três** forem verdadeiras: `self.tabuleiro[l][c] = HUMANO` coloca o
    seu `X` na casa, e `return` termina (jogada feita).
  - Se qualquer uma falhar: mostra o aviso e o `while True` pede tudo de novo.

> **Detalhe:** `self.tabuleiro[l][c]` quer dizer "a casa na linha `l`, coluna
> `c`". O `[l]` escolhe a linha e o `[c]` escolhe a posição dentro dela. O
> sinal `==` (dois iguais) **pergunta** se dois valores são iguais; o sinal `=`
> (um só) **guarda** um valor. São coisas diferentes!

---

## 7. A jogada do computador: `jogada_O`

```python
def jogada_O(self):
    print("\nVez do O")

    if random.random() < self.prob_minimax:
        l, c, valor = Minimax(self.tabuleiro).get_melhor()
        print(f"[MINIMAX] Linha {l}, Coluna {c}  (utilidade = {valor})")
    else:
        l, c = random.choice(Minimax._posicoes_livres(self.tabuleiro))
        print(f"[ALEATORIO] Linha {l}, Coluna {c}")

    self.tabuleiro[l][c] = COMPUTADOR
```

Aqui o computador decide entre **pensar** ou **chutar** — e é isso que cria as
dificuldades.

- **`random.random()`** — sorteia um número aleatório entre 0 e 1 (tipo 0.07,
  0.83...). Imagine como jogar um dado bem fininho.
- **`if random.random() < self.prob_minimax:`** — compara o sorteio com a
  probabilidade da dificuldade. Exemplo no **Fácil** (`prob_minimax = 0.25`):
  só quando o sorteio cai abaixo de 0.25 (uma chance de 25%) é que o computador
  pensa. Nas outras vezes, chuta.

  - **Se "pensar" (Minimax):**
    `l, c, valor = Minimax(self.tabuleiro).get_melhor()` — chama o cérebro, que
    devolve a melhor linha, a melhor coluna e a "nota" da jogada (`valor`).
    Depois imprime `[MINIMAX] ...` para você **ver no terminal** que ali ele
    pensou. (O detalhe de **como** ele pensa está no outro `.md`.)

  - **Se "chutar" (aleatório):**
    `Minimax._posicoes_livres(...)` devolve a lista de todas as casas vazias, e
    `random.choice(...)` **sorteia uma** delas. Imprime `[ALEATORIO] ...`.

- No fim, **`self.tabuleiro[l][c] = COMPUTADOR`** coloca o `O` na casa
  escolhida (não importa se foi pensando ou chutando).

> **Detalhe:** é por isso que os prints começam com `[MINIMAX]` ou `[ALEATORIO]`
> — é o "registro" pedido, para você acompanhar quando a máquina jogou usando o
> algoritmo e quando ela jogou no chute.

---

## 8. Quem ganhou? `_verifica_fim` e `_anuncia_resultado`

```python
def _verifica_fim(self):
    if Minimax._venceu(self.tabuleiro, HUMANO):
        return HUMANO
    if Minimax._venceu(self.tabuleiro, COMPUTADOR):
        return COMPUTADOR
    if Minimax._livres(self.tabuleiro) == 0:
        return "EMPATE"
    return None
```

Depois de **cada** jogada, o jogo pergunta: "já acabou?". Esse método responde:

1. **`if Minimax._venceu(self.tabuleiro, HUMANO):`** — o X fez três em linha
   (horizontal, vertical ou diagonal)? Se sim, devolve `HUMANO` (você ganhou).
2. Senão, **`... COMPUTADOR`** — o O fez três em linha? Devolve `COMPUTADOR`.
3. Senão, **`if Minimax._livres(...) == 0:`** — não tem mais nenhuma casa
   vazia? Então deu **empate** ("velha"), e devolve `"EMPATE"`.
4. Se nada disso aconteceu, devolve **`None`** = "o jogo continua".

> **Detalhe:** repare que o código **reaproveita** funções do Minimax
> (`_venceu` e `_livres`) para não reescrever a lógica de "três em linha" e de
> "contar casas vazias". É o mesmo conhecimento usado em dois lugares.

```python
def _anuncia_resultado(self, resultado):
    if resultado == HUMANO:
        print(" X venceu!")
    elif resultado == COMPUTADOR:
        print(" O venceu!")
    else:
        print(" Deu velha")
```

Esse só **traduz** o resultado para uma frase na tela: "X venceu!",
"O venceu!" ou "Deu velha" (empate).

---

## 9. As ajudinhas: `_exibe` e `_ler_inteiro`

```python
def _exibe(self):
    print()
    print("    0   1   2")
    for i in range(3):
        print(f"{i}   " + "   ".join(self.tabuleiro[i][j] for j in range(3)))
```

Desenha o tabuleiro na tela.

- `print("    0   1   2")` escreve o cabeçalho das colunas.
- O `for i in range(3)` repete uma vez para cada linha (0, 1, 2).
- `"   ".join(...)` junta os três símbolos da linha com espaços entre eles, e
  o `f"{i}   "` coloca o número da linha na frente.

```python
@staticmethod
def _ler_inteiro(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Digite um numero valido")
```

Esse pega o que você digita e garante que é um **número**.

- **`input(prompt)`** mostra a pergunta e espera você digitar.
- **`int(...)`** transforma o texto digitado em número.
- **`try / except`** é uma "rede de segurança": se você digitar algo que não é
  número (tipo a letra "a"), o `int(...)` daria erro e o programa quebraria.
  Com o `try/except`, em vez de quebrar, ele mostra "Digite um numero valido" e
  pergunta de novo.

  > **Detalhe:** `ValueError` é o nome do erro específico que acontece quando
  > você tenta transformar um texto-que-não-é-número em número. O `except
  > ValueError` significa "se acontecer ESSE erro, faça isto aqui em vez de
  > quebrar".

---

## 10. A última linha do arquivo

```python
if __name__ == "__main__":
    JogoVelhaDificuldades().iniciar()
```

Essa parte quer dizer: "se este arquivo foi executado diretamente (e não
importado por outro), **comece o jogo**".

- `JogoVelhaDificuldades()` cria um jogo novo (chama o `__init__`).
- `.iniciar()` aperta o "play" e a partida começa.

> **Detalhe:** o `if __name__ == "__main__":` é uma frase padrão do Python.
> Ela evita que o jogo comece sozinho caso outro arquivo só queira
> **reaproveitar** as classes daqui sem rodar a partida.

---

## 11. Resumindo em uma frase

O jogo monta uma grade 3x3, fica num laço alternando **sua jogada** e a
**jogada do computador**, e a cada rodada confere se alguém ganhou ou empatou.
A "dificuldade" é só a **chance** de o computador usar o cérebro (Minimax) em
vez de chutar — quanto maior a chance, mais difícil de ganhar dele.
