# Documentação do Código — `main.py`

Trabalho **T2 – Algoritmos de Busca: Olimpíada** (PUCRS – Inteligência Artificial).
Implementação de um **Algoritmo Genético (AG) memético** que distribui alunos de
duas escolas (A e B) em **quartos duplos heterogêneos** (um aluno de cada escola por
quarto), respeitando ao máximo as preferências mútuas. O código usa **dataclasses**
e **type hints** para legibilidade.

> Este documento explica **como o código funciona**. Os fundamentos teóricos
> (por que cada operador foi escolhido, conceitos de AG) estão em
> [`CONCEITOS.md`](CONCEITOS.md).

---

## 1. Como executar

Pré-requisito: **Python 3.8+** (sem dependências externas para executar).

```bash
# Modo final: roda tudo e mostra a solução ao final
python main.py caso1.txt --modo final

# Modo passo a passo: pausa a cada geração (pressione Enter para continuar)
python main.py caso1.txt --modo passo
```

### Argumentos da linha de comando

A execução tem apenas o necessário pelo enunciado: o **arquivo** e os **dois modos**.

| Argumento        | Padrão  | Descrição                                            |
|------------------|---------|------------------------------------------------------|
| `arquivo`        | —       | Arquivo-texto de preferências (obrigatório).         |
| `--modo`         | `final` | `passo` (pausado) ou `final` (corrido).              |

Os **parâmetros do AG** (população, gerações, taxas de crossover/mutação, torneio,
elitismo e estagnação) são **fixos no código**, na `@dataclass Parametros`. Para
ajustá-los, edite os valores padrão dessa classe em `main.py`.

### Saídas geradas
- **Console:** evolução da heurística por geração + solução codificada/decodificada.
- **`<arquivo>_output.txt`:** solução final + log completo de evolução.

---

## 2. Formato do arquivo de entrada

```
4                <- N = número de duplas (alunos por escola)
1 1 2 4 3        <- Escola A: id=1, lista ordenada de preferência sobre B: B1>B2>B4>B3
2 2 3 1 4        <- Escola A: id=2 ...
3 4 1 3 2
4 3 1 2 4
1 3 2 4 1        <- Escola B: id=1, lista ordenada de preferência sobre A: A3>A2>A4>A1
2 3 2 4 1        <- Escola B: id=2 ...
3 2 4 3 1
4 1 3 4 2
```

- 1ª linha: `N`.
- Próximas `N` linhas: alunos da **Escola A**.
- Próximas `N` linhas: alunos da **Escola B**.
- Cada linha: `id` seguido de uma **lista ordenada** de ids do outro lado, do
  **mais preferido** (1ª posição) ao **menos preferido**.

---

## 3. Estrutura do `main.py`

O arquivo é organizado em 6 seções comentadas:

```
1. Leitura do arquivo de entrada        -> dataclass Preferencias, ler_arquivo()
2. Codificação e função de aptidão       -> aptidao(), custo_dupla(), matriz custo
3. Operadores do AG                      -> seleção, Order Crossover, mutação, busca local
4. Ciclo do AG                           -> nova_geracao(), executar_ag()
5. Saída (decodificação/log/arquivo)     -> imprime_solucao(), salva_saida()...
6. Modos de execução e CLI               -> callbacks, argparse, main()
```

### 3.1. Leitura — `ler_arquivo(caminho)` → `Preferencias`

Lê o arquivo, ignora linhas em branco e **valida** que cada lista é uma permutação
de `1..N`. Converte tudo para **base 0** e monta duas **tabelas de ranking** e uma
**matriz de custo**:

- `rank_a[i][j]` = posição (0 = melhor) do aluno **B `j`** na lista do aluno **A `i`**.
- `rank_b[j][i]` = posição do aluno **A `i`** na lista do aluno **B `j`**.
- `custo[i][j]`  = `(rank_a[i][j] + 1) + (rank_b[j][i] + 1)` — custo da dupla `(A_i, B_j)`.

A **matriz de custo é pré-computada uma única vez** na leitura. Assim, calcular o
custo de qualquer dupla é **O(1)** e a busca local consegue avaliar o *delta* de uma
troca sem recomputar nada. `Preferencias` é uma `@dataclass`.

### 3.2. Codificação — permutação

Um **indivíduo** é uma lista `perm` de tamanho `N`:

```
perm[i] = id (base 0) do aluno da Escola B alocado ao aluno A 'i'
```

Uma solução **válida** é uma **permutação de `0..N-1`** (cada aluno B usado uma única
vez) — ou seja, um emparelhamento perfeito e heterogêneo. Exemplo (base 1): `4 2 1 3`
significa A1–B4, A2–B2, A3–B1, A4–B3.

### 3.3. Função de aptidão — `aptidao(prefs, perm)`

Heurística de **custo** (menor = melhor):

```
custo(perm) = Σ_i  prefs.custo[i][perm[i]]
            = Σ_i  [ rank_A(i, perm[i]) + 1 ] + [ rank_B(perm[i], i) + 1 ]
```

- `aptidao(prefs, perm)` apenas **soma a matriz de custo** ao longo das duplas.
- **Sem penalidade.** Como todos os operadores (Order Crossover, mutação por swap e
  busca local) **preservam a permutação**, nunca há id repetido/faltante — então a
  aptidão não precisa de termo de penalidade (`solucao_valida()` continua disponível
  apenas para o relatório de saída).
- `custo_dupla(prefs, i, j)` devolve `prefs.custo[i][j]` (usado na decodificação).
- `custo_minimo_possivel()` devolve `2*N` (todos com 1ª escolha mútua) — referência
  teórica usada no log (console e arquivo de saída).

### 3.4. Operadores genéticos (Seção 3 do código)

- **`individuo_aleatorio(n)`** e **`inicializa_populacao(n, tamanho)`**: criam
  permutações aleatórias válidas (`random.shuffle`).
- **`selecao_torneio(pop, fits, k)`**: sorteia `k` indivíduos e devolve o de **menor
  custo**. Pressão seletiva controlada por `k`.
- **`order_crossover(pai1, pai2, taxa)`**: **Order Crossover (OX)** — herda um
  segmento contíguo de um pai e completa as demais posições com os genes do outro pai
  na ordem em que aparecem. **Preserva a permutação por construção** (sem reparo).
  Auxiliar interno: `_ox_filho(...)`.
- **`mutacao(perm, taxa)`**: **troca** de duas posições (swap), que **preserva** a
  validade da permutação (altera no lugar).
- **`busca_local(prefs, perm)`**: **busca local 2-swap (first-improvement)** — o
  componente **memético**. Aplica trocas que reduzem o custo até atingir um ótimo
  local, avaliando cada troca por **delta O(1)** via matriz de custo. Devolve
  `(perm, custo)`.

### 3.5. Ciclo do AG (Seção 4)

- **`nova_geracao(...)`**: recebe a população **já ordenada**, aplica **elitismo**
  (copia os `elite` melhores diretamente) e preenche o restante por
  `seleção → Order Crossover → mutação → busca local`. Como o custo de cada filho já
  sai da busca local, a função **devolve `(nova_populacao, nova_fits)`**, evitando
  reavaliar a população depois.
- **`executar_ag(prefs, params, modo, callback)`**: laço principal.
  1. Inicializa e avalia a população, ordena por custo crescente.
  2. A cada geração: registra estatística (`Estatistica`: melhor/média/pior), chama o
     `callback` (log ou pausa), atualiza melhor global e contador de estagnação.
  3. **Critérios de parada** (qualquer um):
     - custo melhor ≤ ótimo teórico (`2*N`);
     - atingiu o máximo de gerações;
     - **estagnação**: `params.estagnacao` gerações sem melhora.
  4. Evolui para a próxima geração.

### 3.6. Saída (Seção 5)

- **`decodifica(prefs, perm)`**: gera as linhas legíveis dos quartos, com o ranking que
  cada lado deu ao par e o custo da dupla.
- **`imprime_solucao(...)`**: mostra a solução **codificada** (a permutação) e
  **decodificada** (os quartos), o custo total, o custo médio por dupla, o ótimo
  teórico e se a solução é válida.
- **`salva_saida(...)`**: grava tudo isso + o log de evolução em `<arquivo>_output.txt`.

### 3.7. Modos e CLI (Seção 6)

- **`callback_log`** (modo `final`): imprime só o resumo de cada geração.
- **`callback_passo`** (modo `passo`): imprime o resumo + o melhor indivíduo
  (codificado e decodificado) e **aguarda Enter**.
- **`construir_parser()` / `main()`**: leem o `arquivo` e o `--modo`, montam
  `Parametros` (valores fixos), rodam o AG e produzem as saídas. `main()` devolve
  código de saída (`0` ok, `1` erro de leitura), usado por `sys.exit`.

---

## 4. Parâmetros do AG (fixos no código)

Os parâmetros ficam na `@dataclass Parametros` (valores padrão) e **não** são passados
pela linha de comando. Para experimentar outros valores, edite-os em `main.py`.

| Parâmetro    | Valor | Significado                              |
|--------------|-------|------------------------------------------|
| `pop`        | 100   | tamanho da população                     |
| `geracoes`   | 500   | máximo de gerações                       |
| `cross`      | 0.85  | taxa de Order Crossover                  |
| `mut`        | 0.15  | taxa de mutação (swap)                   |
| `torneio`    | 2     | tamanho do torneio de seleção            |
| `elite`      | 2     | indivíduos preservados por elitismo      |
| `estagnacao` | 50    | gerações sem melhora até parar           |

---

## 5. Gerar o executável (.exe)

Com o **PyInstaller** (`pip install pyinstaller`):

```bash
pyinstaller --onefile main.py
```

O executável aparece em `dist/main.exe` e recebe o arquivo como argumento:

```bash
dist\main.exe caso2.txt --modo final
```

---

## 6. Mapa rápido funções → exigências da quest

| Exigência da quest                         | Onde está no código                         |
|--------------------------------------------|---------------------------------------------|
| Leitura do arquivo de entrada              | `ler_arquivo`, classe `Preferencias`        |
| Codificação                                | comentários §2; `perm` (permutação)         |
| Função heurística (aptidão)                | `aptidao`, `custo_dupla`, matriz `custo`     |
| Seleção                                    | `selecao_torneio`                            |
| Cruzamento (crossover)                     | `order_crossover` (Order Crossover, OX)      |
| Mutação                                    | `mutacao`                                    |
| Busca local (memético)                     | `busca_local`                                |
| Critérios de parada                        | `executar_ag` (§3.5)                         |
| Modo passo a passo / final                 | `callback_passo`, `callback_log`, `main`     |
| Evolução da heurística ao longo das iterações | `Estatistica`, log (console e arquivo)    |
| Solução codificada e decodificada          | `imprime_solucao`, `decodifica`              |
| Nome do arquivo via `args`                 | `construir_parser`                           |
