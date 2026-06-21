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
`--pop = 100` indivíduos por padrão. Uma população maior aumenta a diversidade (melhor
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

- **No código:** `custo_dupla()` e `aptidao()` (Seção 2).

### Penalidade
A `aptidao` ainda soma uma **penalidade** alta por id repetido/faltante. Numa
permutação válida o termo é zero; ele só existe como **rede de segurança** caso um
operador gere algo inválido (ver §7).

---

## 5. Seleção

> **Conceito.** A *seleção* decide quais indivíduos se reproduzem, dando mais chances
> aos melhores (pressão seletiva), sem eliminar a diversidade cedo demais.

Usamos **seleção por torneio** (`selecao_torneio`): sorteiam-se `k` indivíduos
(`--torneio = 2`) e o de **menor custo** vence. Vantagens sobre a roleta:

- não exige aptidões normalizadas nem positivas (lidamos com **custo**, não fitness
  proporcional);
- a pressão seletiva é controlada diretamente por `k` (maior `k` = mais elitista);
- é simples e robusta — é também a estratégia do exemplo de aula (N-Rainhas).

---

## 6. Elitismo

> **Conceito.** *Elitismo* preserva os melhores indivíduos de uma geração para a
> seguinte, garantindo que a melhor solução **nunca piore** ao longo das gerações.

Mantemos os `--elite = 2` melhores intactos a cada geração (início de
`nova_geracao`). Isso estabiliza a convergência e protege o melhor cromossomo de ser
destruído por crossover/mutação.

---

## 7. Cruzamento (crossover) e reparo

> **Conceito.** O *crossover* recombina dois pais para gerar filhos, herdando
> características de ambos — é o principal mecanismo de **exploração** do AG.

Usamos **crossover de corte simples**: escolhe-se um ponto e combina-se o início de um
pai com o fim do outro (`crossover`, controlado por `--cross = 0.85`).

**Problema:** em representação por permutação, o corte simples pode gerar **ids
repetidos** (filho inválido: dois A no mesmo B). Tratamos isso com a estratégia
**"corte simples + reparo E penalidade"**:

1. **Reparo** (`reparar`): valores duplicados viram "buracos" e são preenchidos com os
   ids faltantes → o filho volta a ser uma permutação válida. É a defesa **principal**.
2. **Penalidade** (na `aptidao`): rede de segurança adicional, caso qualquer indivíduo
   inválido escape ao reparo, ele é fortemente penalizado e some da população.

> Alternativas clássicas seriam PMX ou OX (crossovers que já preservam permutação).
> Optamos por **corte simples + reparo** por ser mais próximo do exemplo de aula e
> didaticamente mais simples de explicar, mantendo a validade garantida pelo reparo.

---

## 8. Mutação

> **Conceito.** A *mutação* introduz pequenas alterações aleatórias, mantendo a
> **diversidade** e ajudando a escapar de ótimos locais (**exploração local**).

Usamos **mutação por troca (swap)**: com probabilidade `--mut = 0.15`, trocam-se duas
posições da permutação (`mutacao`). A troca **preserva a validade** (continua sendo
uma permutação), então não exige reparo. Uma taxa moderada evita transformar a busca
em aleatória.

---

## 9. Critérios de parada

> **Conceito.** O AG precisa de uma condição de término — por tempo/gerações e/ou por
> convergência.

Usamos **parada dupla** (`executar_ag`):

1. **Máximo de gerações** (`--geracoes = 500`).
2. **Estagnação**: sem melhora do melhor custo por `--estagnacao = 50` gerações.
3. **Ótimo teórico atingido** (custo ≤ `2*N`): não há como melhorar, encerra.

Isso evita desperdício de processamento quando a população já convergiu.

---

## 10. Parâmetros e seu efeito

| Parâmetro     | Padrão | Efeito de aumentar                                  |
|---------------|--------|-----------------------------------------------------|
| População     | 100    | Mais diversidade/exploração; mais custo por geração |
| Gerações máx. | 500    | Mais tempo para refinar; risco de desperdício       |
| Taxa crossover| 0.85   | Mais recombinação (exploração)                      |
| Taxa mutação  | 0.15   | Mais diversidade; alta demais ≈ busca aleatória     |
| Torneio (k)   | 2      | Mais pressão seletiva (converge mais rápido)        |
| Elitismo      | 2      | Mais estabilidade; alto demais reduz diversidade    |

A **definição desses parâmetros é parte importante do trabalho**: foram escolhidos por
equilibrar exploração (crossover/mutação/população) e intensificação
(torneio/elitismo), e validados empiricamente nos arquivos de teste (ver §11).

---

## 11. Validação empírica

- **`exemplo_quest.txt` (N=4):** o AG encontra custo **13**, **idêntico ao ótimo obtido
  por força bruta** (todas as 24 permutações) — solução `4 2 1 3`.
- **`arquivoDeTeste1.txt` (N=10):** o AG encontra uma solução válida de custo **30**
  (média 3,0 por dupla), aproveitando a estrutura cíclica das preferências.

Esses testes confirmam que a **codificação**, a **heurística** e os **operadores**
estão coerentes e que o algoritmo converge para soluções ótimas/quase-ótimas.

---

## 12. Glossário rápido

- **Indivíduo/cromossomo:** uma solução candidata (aqui, uma permutação).
- **Gene:** uma posição do cromossomo (`perm[i]`).
- **População:** conjunto de indivíduos de uma geração.
- **Aptidão (fitness):** qualidade do indivíduo (aqui, **custo**, a minimizar).
- **Geração:** uma iteração completa do ciclo seleção→crossover→mutação.
- **Ótimo local/global:** melhor solução numa vizinhança / em todo o espaço.
