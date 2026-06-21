# Conceitos — Fundamentos do Algoritmo Genético aplicado ao T2

Este documento explica os **conceitos teóricos** que a implementação exigiu e
relaciona cada um deles aos trechos correspondentes de [`main.py`](main.py). Para a
explicação prática do código, ver [`DOCUMENTACAO_CODIGO.md`](DOCUMENTACAO_CODIGO.md).

---

## 1. O problema como busca com informação

O enunciado pede um **algoritmo de busca com informação** (heurística). Distribuir
alunos em quartos duplos heterogêneos é, na prática, um **problema de atribuição
(assignment)** entre dois conjuntos do mesmo tamanho — muito próximo do clássico
**Problema do Casamento Estável** (Gale–Shapley): cada aluno de A tem uma ordem de
preferência sobre os de B e vice-versa.

O número de soluções possíveis é **N!** (todas as permutações). Para `N=10` já são
3.628.800 combinações; para `N` maior, a busca exaustiva é inviável. Por isso usamos
uma **meta-heurística populacional** — o **Algoritmo Genético** — que explora o
espaço de forma guiada pela função de aptidão, sem garantir o ótimo, mas convergindo
para soluções de alta qualidade em tempo razoável.

> No nosso problema o **ótimo teórico** seria todos com a 1ª escolha mútua (custo
> `2*N`), mas ele nem sempre é atingível — as preferências podem ser conflitantes.

---

## 2. Codificação (representação cromossômica)

> **Conceito.** Um *cromossomo* é uma representação compacta de uma solução candidata.
> A escolha da codificação determina quais operadores fazem sentido.

Usamos **codificação por permutação**: o indivíduo é uma lista `perm` onde `perm[i]`
é o aluno B alocado ao aluno A `i`. Como cada B deve ser usado **exatamente uma vez**
(quartos duplos, um de cada escola), a representação natural é uma **permutação de
`0..N-1`** — toda permutação é, automaticamente, um emparelhamento perfeito e
heterogêneo.

- **No código:** comentários da Seção 2; `individuo_aleatorio()` gera permutações.
- **Por que não um vetor binário/inteiro livre?** Porque geraria soluções inválidas
  (dois A no mesmo B, ou B sem par), exigindo muito mais reparo/penalidade.

---

## 3. População inicial

> **Conceito.** O AG trabalha com uma *população* de soluções simultâneas, o que
> favorece a diversidade e reduz o risco de ficar preso em ótimos locais.

A população inicial é gerada **aleatoriamente** (`inicializa_populacao`), com
`pop = 100` indivíduos por padrão. Uma população maior aumenta a diversidade (melhor
exploração) ao custo de mais processamento por geração. 100 é um equilíbrio adequado
para os tamanhos de `N` deste trabalho.

---

## 4. Função de aptidão (heurística)

> **Conceito.** A *função de aptidão* mede a qualidade de cada indivíduo e **guia toda
> a busca**. É, segundo o próprio enunciado, "fundamental para o sucesso" do AG.

Definimos um **custo de insatisfação** a ser **minimizado**:

```
custo(perm) = Σ_i  [ rank_A(i, perm[i]) + 1 ]  +  [ rank_B(perm[i], i) + 1 ]
```

Cada dupla contribui com a soma dos **rankings mútuos** (posição na lista de
preferência, base 1). Intuição: se A e B se escolhem como 1ª opção, a dupla custa
`1+1 = 2` (mínimo); quanto pior a posição na preferência, maior o custo.

Propriedades que tornam essa heurística adequada:

- **Independe da quantidade de duplas:** funciona para qualquer `N` (basta somar sobre
  as duplas existentes). Reportamos também o **custo médio por dupla** para comparação
  entre instâncias de tamanhos diferentes.
- **Simétrica e justa:** considera as preferências dos **dois** lados.
- **Monotônica:** melhorar qualquer dupla nunca piora o custo total.

- **No código:** `aptidao()` e a **matriz de custo pré-computada** `prefs.custo`
  (Seções 1 e 2). Guardar `custo[i][j] = (rankA+1) + (rankB+1)` uma única vez na
  leitura torna a avaliação **O(N)** por indivíduo e o **delta** da busca local
  **O(1)** por troca (ver §9).

### Sem penalidade
Todos os operadores (**Order Crossover**, **mutação por swap** e **busca local**)
**preservam a permutação** — nunca surge um indivíduo inválido. Por isso a
`aptidao` é simplesmente a **soma dos custos das duplas**, sem nenhum termo de
penalidade (versões anteriores usavam corte simples + reparo, que exigia essa
rede de segurança; ver §7).

---

## 5. Seleção

> **Conceito.** A *seleção* decide quais indivíduos se reproduzem, dando mais chances
> aos melhores (pressão seletiva), sem eliminar a diversidade cedo demais.

Usamos **seleção por torneio** (`selecao_torneio`): sorteiam-se `k` indivíduos
(`torneio = 2`) e o de **menor custo** vence. Vantagens sobre a roleta:

- não exige aptidões normalizadas nem positivas (lidamos com **custo**, não fitness
  proporcional);
- a pressão seletiva é controlada diretamente por `k` (maior `k` = mais elitista);
- é simples e robusta — é também a estratégia do exemplo de aula (N-Rainhas).

---

## 6. Elitismo

> **Conceito.** *Elitismo* preserva os melhores indivíduos de uma geração para a
> seguinte, garantindo que a melhor solução **nunca piore** ao longo das gerações.

Mantemos os `elite = 2` melhores intactos a cada geração (início de
`nova_geracao`). Isso estabiliza a convergência e protege o melhor cromossomo de ser
destruído por crossover/mutação.

---

## 7. Cruzamento (crossover): Order Crossover (OX)

> **Conceito.** O *crossover* recombina dois pais para gerar filhos, herdando
> características de ambos — é o principal mecanismo de **exploração** do AG.

Usamos **Order Crossover (OX)** (`order_crossover`, controlado por `cross = 0.85`),
o operador **clássico para representação por permutação**:

1. Sorteia-se um **segmento** `[a, b)` e o filho **herda esse trecho do pai 1**.
2. As posições restantes são preenchidas com os genes do **pai 2**, na **ordem em
   que aparecem nele** (a partir de `b`, de forma cíclica), pulando os que já
   vieram do segmento.

Geramos dois filhos por casal (um herdando o segmento de cada pai).

**Exemplo (N=6).** Pais `p1 = [1 2 3 4 5 6]`, `p2 = [4 1 5 2 6 3]`, segmento `[2,5)`:
- filho herda `p1[2:5] = _ _ 3 4 5 _`;
- completa com a ordem de `p2` (sem 3,4,5): `4 1 2 6` → resultado `2 6 3 4 5 1`.

Por que OX (e não corte simples + reparo)?

- **Preserva a permutação por construção** — nunca gera ids repetidos, então
  **dispensa reparo e penalidade**.
- **Herda estrutura real dos pais**: mantém a *ordem relativa* dos genes do pai 2,
  diferente do reparo, que reembaralha aleatoriamente os "buracos" e descarta boa
  parte da informação herdada. Isso melhora a qualidade da busca.

> Versões anteriores usavam **corte simples + reparo + penalidade**. Trocamos pelo
> OX para herdar mais estrutura e simplificar a aptidão (sem penalidade).

---

## 8. Mutação

> **Conceito.** A *mutação* introduz pequenas alterações aleatórias, mantendo a
> **diversidade** e ajudando a escapar de ótimos locais (**exploração local**).

Usamos **mutação por troca (swap)**: com probabilidade `mut = 0.15`, trocam-se duas
posições da permutação (`mutacao`). A troca **preserva a validade** (continua sendo
uma permutação), então não exige reparo. Uma taxa moderada evita transformar a busca
em aleatória.

---

## 9. Busca local (algoritmo memético)

> **Conceito.** Um *algoritmo memético* combina um AG (busca global, exploração)
> com uma *busca local* (intensificação) aplicada aos indivíduos. A busca local
> "desce a ladeira" até um ótimo local, refinando o que o crossover/mutação
> produziram.

Após gerar cada filho, aplicamos **busca local 2-swap com *first-improvement***
(`busca_local`): testam-se trocas de duas posições e **aplica-se imediatamente
qualquer troca que reduza o custo**, repetindo até nenhum swap melhorar (um
**ótimo local** da vizinhança 2-swap).

O ponto-chave de eficiência é o **delta**: o ganho de trocar as posições `a` e `b`
é calculado em **O(1)** pela matriz de custo, sem recomputar o fitness inteiro:

```
delta = (custo[a][jb] + custo[b][ja]) - (custo[a][ja] + custo[b][jb])
```

Efeito prático: a busca local é o que **leva o AG ao ótimo de forma confiável** —
no `caso1.txt` ela atinge o custo **13** logo nas primeiras gerações. Ela é parte
fixa do ciclo (sempre ativa).

- **No código:** `busca_local()` (Seção 3); aplicada em `nova_geracao()` (Seção 4).

---

## 10. Critérios de parada

> **Conceito.** O AG precisa de uma condição de término — por tempo/gerações e/ou por
> convergência.

Usamos **parada dupla** (`executar_ag`):

1. **Máximo de gerações** (`geracoes = 500`).
2. **Estagnação**: sem melhora do melhor custo por `estagnacao = 50` gerações.
3. **Ótimo teórico atingido** (custo ≤ `2*N`): não há como melhorar, encerra.

Isso evita desperdício de processamento quando a população já convergiu.

---

## 11. Parâmetros e seu efeito

| Parâmetro     | Padrão  | Efeito de aumentar / observação                     |
|---------------|---------|-----------------------------------------------------|
| População     | 100     | Mais diversidade/exploração; mais custo por geração |
| Gerações máx. | 500     | Mais tempo para refinar; risco de desperdício       |
| Taxa crossover| 0.85    | Mais recombinação (OX, exploração)                  |
| Taxa mutação  | 0.15    | Mais diversidade; alta demais ≈ busca aleatória     |
| Torneio (k)   | 2       | Mais pressão seletiva (converge mais rápido)        |
| Elitismo      | 2       | Mais estabilidade; alto demais reduz diversidade    |
| Busca local   | ligada  | Refina cada filho (2-swap); sempre ativa            |

A **definição desses parâmetros é parte importante do trabalho**: foram escolhidos por
equilibrar exploração (crossover/mutação/população) e intensificação
(torneio/elitismo/**busca local**), e validados empiricamente nos arquivos de teste
(ver §12).

---

## 12. Validação empírica

- **`caso1.txt` (N=4):** o AG memético encontra custo **13**, **idêntico ao ótimo
  obtido por força bruta** (todas as 24 permutações) — solução `4 2 1 3`.
- **`caso2.txt` (N=10):** encontra uma solução válida de custo **30**
  (média 3,0 por dupla), aproveitando a estrutura cíclica das preferências.
- **Efeito da busca local:** sem o refinamento memético, o AG "puro" costuma estacionar
  em valores piores para o mesmo número de gerações — evidência de que o componente
  **memético** é decisivo para chegar ao ótimo de forma confiável.

Há ainda testes automatizados em [`../test_main.py`](../test_main.py) (rode
`pytest`) cobrindo leitura, aptidão, validade do OX, monotonicidade da busca local
e o ótimo de `caso1.txt`.

Esses testes confirmam que a **codificação**, a **heurística** e os **operadores**
estão coerentes e que o algoritmo converge para soluções ótimas/quase-ótimas.

---

## 13. Glossário rápido

- **Indivíduo/cromossomo:** uma solução candidata (aqui, uma permutação).
- **Gene:** uma posição do cromossomo (`perm[i]`).
- **População:** conjunto de indivíduos de uma geração.
- **Aptidão (fitness):** qualidade do indivíduo (aqui, **custo**, a minimizar).
- **Geração:** uma iteração completa do ciclo seleção→crossover→mutação→busca local.
- **Algoritmo memético:** AG combinado com busca local (intensificação).
- **Ótimo local/global:** melhor solução numa vizinhança / em todo o espaço.
