# Documentação do Código — `main.py`

Trabalho **T2 – Algoritmos de Busca: Olimpíada** (PUCRS – Inteligência Artificial).
Implementação de um **Algoritmo Genético (AG)** que distribui alunos de duas escolas
(A e B) em **quartos duplos heterogêneos** (um aluno de cada escola por quarto),
respeitando ao máximo as preferências mútuas.

> Este documento explica **como o código funciona**. Os fundamentos teóricos
> (por que cada operador foi escolhido, conceitos de AG) estão em
> [`CONCEITOS.md`](CONCEITOS.md).

---

## 1. Como executar

Pré-requisito: **Python 3.8+** e **matplotlib** (`pip install matplotlib`).

```bash
# Modo final: roda tudo e mostra a solução ao final
python main.py exemplo_quest.txt --modo final

# Modo passo a passo: pausa a cada geração (pressione Enter para continuar)
python main.py exemplo_quest.txt --modo passo

# O nome do arquivo é passado como argumento (args), conforme exigido
python main.py arquivoDeTeste1.txt
```

### Argumentos da linha de comando

| Argumento        | Padrão  | Descrição                                            |
|------------------|---------|------------------------------------------------------|
| `arquivo`        | —       | Arquivo-texto de preferências (obrigatório).         |
| `--modo`         | `final` | `passo` (pausado) ou `final` (corrido).              |
| `--pop`          | `100`   | Tamanho da população.                                |
| `--geracoes`     | `500`   | Número máximo de gerações.                           |
| `--cross`        | `0.85`  | Taxa de crossover.                                   |
| `--mut`          | `0.15`  | Taxa de mutação.                                     |
| `--torneio`      | `2`     | Tamanho do torneio de seleção.                       |
| `--elite`        | `2`     | Indivíduos preservados por elitismo.                 |
| `--estagnacao`   | `50`    | Para se não houver melhora por N gerações.           |
| `--seed`         | —       | Semente aleatória (reprodutibilidade).               |
| `--sem-grafico`  | —       | Não gera/exibe o gráfico matplotlib.                 |
| `--saida`        | auto    | Arquivo-texto de saída (padrão `<arquivo>_saida.txt`). |

### Saídas geradas
- **Console:** evolução da heurística por geração + solução codificada/decodificada.
- **`<arquivo>_saida.txt`:** solução final + log completo de evolução.
- **`<arquivo>_evolucao.png`:** gráfico melhor/média/pior por geração.

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
1. Leitura do arquivo de entrada        -> classe Preferencias, ler_arquivo()
2. Codificação e função de aptidão       -> custo_dupla(), aptidao()
3. Operadores do AG                      -> seleção, crossover+reparo, mutação
4. Ciclo do AG                           -> nova_geracao(), executar_ag()
5. Saída (decodificação/log/gráfico)     -> imprime_solucao(), gera_grafico()...
6. Modos de execução e CLI               -> callbacks, argparse, main()
```

### 3.1. Leitura — `ler_arquivo(caminho)` → `Preferencias`

Lê o arquivo, ignora linhas em branco e **valida** que cada lista é uma permutação
de `1..N`. Converte tudo para **base 0** e monta duas **tabelas de ranking**:

- `rank_a[i][j]` = posição (0 = melhor) do aluno **B `j`** na lista do aluno **A `i`**.
- `rank_b[j][i]` = posição do aluno **A `i`** na lista do aluno **B `j`**.

Guardar o *ranking* (e não a lista) permite calcular o custo de qualquer dupla em
tempo **O(1)**.

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
custo(perm) = Σ_i [ rank_A(i, perm[i]) + 1 ]  +  [ rank_B(perm[i], i) + 1 ]
              + PENALIDADE * (conflitos de validade)
```

- `custo_dupla(prefs, i, j)` soma os dois rankings (base 1) → insatisfação da dupla.
- A **penalidade** (`PENALIDADE_POR_CONFLITO = 1000`) é somada caso algum id de B
  apareça repetido/faltante. Numa permutação válida não há conflito; a penalidade é
  apenas uma **rede de segurança** (ver §3.4).
- `custo_minimo_possivel()` devolve `2*N` (todos com 1ª escolha mútua) — referência
  teórica usada no log e no gráfico.

### 3.4. Operadores genéticos (Seção 3 do código)

- **`individuo_aleatorio(n)`** e **`inicializa_populacao(n, tamanho)`**: criam
  permutações aleatórias válidas (`random.shuffle`).
- **`selecao_torneio(pop, fits, k)`**: sorteia `k` indivíduos e devolve o de **menor
  custo**. Pressão seletiva controlada por `k`.
- **`crossover(pai1, pai2, n, taxa)`**: **corte simples** — combina o início de um pai
  com o fim do outro. Como isso pode gerar ids repetidos, aplica **`reparar()`**.
- **`reparar(perm, n)`**: restaura a permutação — marca duplicatas como "buracos" e os
  preenche com os ids faltantes, devolvendo sempre uma permutação válida. É a parte
  **"reparo"** da estratégia "corte simples + reparo **e** penalidade".
- **`mutacao(perm, taxa)`**: **troca** de duas posições (swap), que **preserva** a
  validade da permutação.

### 3.5. Ciclo do AG (Seção 4)

- **`nova_geracao(...)`**: aplica **elitismo** (copia os `elite` melhores) e preenche o
  restante por `seleção → crossover → mutação`.
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
- **`salva_saida(...)`**: grava tudo isso + o log de evolução em `<arquivo>_saida.txt`.
- **`gera_grafico(...)`**: plota melhor/média/pior por geração com matplotlib e salva
  em PNG. Se o matplotlib não estiver instalado, apenas avisa e segue (degradação
  graciosa).

### 3.7. Modos e CLI (Seção 6)

- **`callback_log`** (modo `final`): imprime só o resumo de cada geração.
- **`callback_passo`** (modo `passo`): imprime o resumo + o melhor indivíduo
  (codificado e decodificado) e **aguarda Enter**.
- **`construir_parser()` / `main()`**: leem os argumentos, montam `Parametros`, rodam o
  AG e produzem todas as saídas. `main()` devolve código de saída (`0` ok, `1` erro de
  leitura), usado por `sys.exit`.

---

## 4. Reprodutibilidade

Use `--seed` para fixar a aleatoriedade e reproduzir exatamente a mesma execução:

```bash
python main.py exemplo_quest.txt --seed 42
```

---

## 5. Gerar o executável (.exe)

Com o **PyInstaller** (`pip install pyinstaller`):

```bash
pyinstaller --onefile --collect-all matplotlib main.py
```

O executável aparece em `dist/main.exe` e recebe o arquivo como argumento:

```bash
dist\main.exe arquivoDeTeste1.txt --modo final
```

> `--collect-all matplotlib` garante que os dados/back-ends do matplotlib sejam
> empacotados. Para um `.exe` menor, rode com `--sem-grafico` e omita essa flag.

---

## 6. Mapa rápido funções → exigências da quest

| Exigência da quest                         | Onde está no código                         |
|--------------------------------------------|---------------------------------------------|
| Leitura do arquivo de entrada              | `ler_arquivo`, classe `Preferencias`        |
| Codificação                                | comentários §2; `perm` (permutação)         |
| Função heurística (aptidão)                | `aptidao`, `custo_dupla`                     |
| Seleção                                    | `selecao_torneio`                            |
| Cruzamento (crossover)                     | `crossover` + `reparar`                      |
| Mutação                                    | `mutacao`                                    |
| Critérios de parada                        | `executar_ag` (§3.5)                         |
| Modo passo a passo / final                 | `callback_passo`, `callback_log`, `main`     |
| Evolução da heurística ao longo das iterações | `Estatistica`, log e `gera_grafico`       |
| Solução codificada e decodificada          | `imprime_solucao`, `decodifica`              |
| Nome do arquivo via `args`                 | `construir_parser`                           |
