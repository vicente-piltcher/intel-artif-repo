# T1 — Jogo da Velha com Machine Learning
**PUCRS — Inteligência Artificial | Profa. Silvia Moraes | Grupo 32**

---

## Sumário

1. [Objetivo](#1-objetivo)
2. [Estrutura do Projeto](#2-estrutura-do-projeto)
3. [Dataset — Problemas e Engenharia](#3-dataset--problemas-e-engenharia)
4. [Divisão do Dataset](#4-divisão-do-dataset)
5. [Pré-processamento](#5-pré-processamento)
6. [Os 5 Algoritmos de Classificação](#6-os-5-algoritmos-de-classificação)
7. [Comparação e Escolha do Melhor Modelo](#7-comparação-e-escolha-do-melhor-modelo)
8. [Front End — Jogo Interativo](#8-front-end--jogo-interativo)
9. [Convenção de Nomenclatura `_32`](#9-convenção-de-nomenclatura-_32)
10. [Como Executar](#10-como-executar)

---

## 1. Objetivo

O sistema de IA **não joga** o jogo da velha — ele **classifica o estado atual do tabuleiro** 3×3 em uma de quatro categorias:

| Classe | Significado |
|---|---|
| `tem_jogo` | Partida em andamento (há casas livres e sem vencedor) |
| `x_venceu` | Jogador X completou uma linha, coluna ou diagonal |
| `o_venceu` | Jogador O completou uma linha, coluna ou diagonal |
| `empate` | Tabuleiro completo sem vencedor |

A IA recebe como entrada um vetor de 9 valores (representando as 9 casas do tabuleiro) e devolve uma dessas quatro predições.

---

## 2. Estrutura do Projeto

```
t1/
├── tic_tac_toe_classifier_32.ipynb   # Notebook principal (treino, avaliação)
├── tic_tac_toe_balanced_32.csv       # Dataset final balanceado (gerado pelo notebook)
├── tic+tac+toe+endgame/
│   └── tic-tac-toe.data              # Dataset original UCI
├── frontend/
│   ├── app.py                        # Servidor Flask
│   ├── requirements.txt
│   ├── models/                       # Modelos exportados pelo notebook
│   │   ├── melhor_modelo_32.pkl
│   │   ├── scaler_32.pkl
│   │   ├── le_32.pkl
│   │   └── model_info_32.txt
│   └── templates/
│       └── index.html                # Interface do jogo
└── DOCUMENTACAO.md                   # Este arquivo
```

---

## 3. Dataset — Problemas e Engenharia

### 3.1 Dataset original (UCI Tic-Tac-Toe Endgame)

O dataset da UCI (`tic-tac-toe.data`) contém **958 instâncias** de estados finais do jogo da velha com apenas **2 classes**:

| Classe original | Contagem |
|---|---|
| `positive` (X venceu) | 626 |
| `negative` (não-X)    | 332 |

### 3.2 Problemas identificados

| Problema | Impacto |
|---|---|
| Apenas 2 classes (`positive`/`negative`) | Não atende ao problema de 4 classes |
| `negative` mistura `o_venceu` + `empate` sem distinção | Impossível separar as classes sem relabeling |
| Nenhum estado `tem_jogo` (só estados finais) | Classe inteira ausente — modelo não aprenderia a detectar jogo em andamento |
| Dataset desbalanceado (626 vs 332) | Bias para a classe majoritária |

### 3.3 Soluções aplicadas

**Passo 1 — Relabeling determinístico**

Cada instância foi reclassificada usando lógica pura do jogo (função `classify_board_32`), que verifica as 8 linhas vencedoras possíveis:

```
Linhas:   (0,1,2), (3,4,5), (6,7,8)
Colunas:  (0,3,6), (1,4,7), (2,5,8)
Diagonais:(0,4,8), (2,4,6)
```

Resultado: `positive` → `x_venceu`, `negative` → `o_venceu` ou `empate` (conforme a verificação).

**Passo 2 — Geração sintética de estados `tem_jogo`**

Como o dataset UCI contém apenas estados finais, foi necessário gerar estados de "jogo em andamento" sinteticamente. A estratégia usada foi **Random Game Replay**:

1. Inicializar tabuleiro vazio
2. Simular entre 1 e 7 jogadas aleatórias, respeitando a ordem (X sempre começa)
3. Interromper a simulação se um vencedor for declarado durante o percurso (descartar)
4. Armazenar apenas tabuleiros únicos classificados como `tem_jogo`
5. Geração de ~250 estados únicos

**Passo 3 — Undersampling para balanceamento**

Com as 4 classes disponíveis, aplicou-se undersampling (máximo de **200 amostras por classe**):

| Classe | Disponível | Amostrado |
|---|---|---|
| `x_venceu`  | 626 | 200 |
| `o_venceu`  | ~70 | ~70 (todas) |
| `empate`    | ~262 | 200 |
| `tem_jogo`  | ~250 | 200 |

> **Justificativa do undersampling:** preserva a qualidade das amostras reais sem criar exemplos artificiais borderline que poderiam degradar o modelo (evita o ruído do SMOTE para este problema).

**Dataset final:** ~800 instâncias, ~200 por classe, balanceado.

### 3.4 Encoding

Cada casa do tabuleiro é codificada numericamente:

| Valor original | Codificação numérica |
|---|---|
| `x` | `+1` |
| `o` | `-1` |
| `b` (vazio) | `0` |

Isso cria um espaço de entrada em R⁹ com três valores possíveis por dimensão, capturando a assimetria entre X e O de forma natural.

---

## 4. Divisão do Dataset

O dataset foi dividido **fisicamente e de forma fixa** em três conjuntos, com `random_state=42` e estratificação por classe (garantindo proporção igual das 4 classes em cada split):

| Conjunto | Proporção | Finalidade |
|---|---|---|
| Treino (`X_treino_32`) | 70% (~560 amostras) | Ajustar os parâmetros dos modelos |
| Validação (`X_val_32`) | 15% (~120 amostras) | Selecionar hiperparâmetros (grid search) |
| Teste (`X_teste_32`) | 15% (~120 amostras) | Avaliação final — **não tocado durante o desenvolvimento** |

**Por que split físico e não validação cruzada?**

O enunciado exige que **os mesmos conjuntos** sejam usados para comparar os 5 algoritmos. Com splits físicos fixos, a comparação é garantidamente justa. A validação cruzada geraria partições diferentes por experimento, impossibilitando a comparação direta.

Após a seleção dos melhores hiperparâmetros via validação, o modelo final é retreinado no conjunto **treino + validação combinados** (`X_trainval_32`) antes da avaliação no teste.

---

## 5. Pré-processamento

**Normalização com `StandardScaler`** (média 0, desvio padrão 1):

- O scaler é ajustado **exclusivamente no conjunto de treino** (`fit_transform`)
- Aplicado via `transform` nos demais conjuntos
- **Por que normalizar?** k-NN, MLP e SVM são sensíveis à escala das features. Modelos baseados em árvore (DT, RF) são invariantes, mas o mesmo pipeline é aplicado a todos para consistência e comparação justa.

---

## 6. Os 5 Algoritmos de Classificação

Para cada algoritmo, o fluxo é:
1. Definir grade de hiperparâmetros
2. Grid search com conjunto de **validação fixo** (métrica: F1 Macro)
3. Refit do melhor modelo em **treino + validação**
4. Avaliação final no conjunto de **teste**

---

### 6.1 k-NN (k-Nearest Neighbors) — `knn_32`

**Como funciona:** Classifica uma nova instância com base nos `k` vizinhos mais próximos no espaço de features, usando votação (uniforme ou ponderada pela distância inversa).

**Hiperparâmetros tunados:**

| Parâmetro | Valores testados | Justificativa |
|---|---|---|
| `n_neighbors` | 1, 3, 5, 7, 9, 11, 15 | Valores ímpares evitam empates em problemas binários; faixa ampla para capturar melhor vizinhança |
| `metric` | euclidean, manhattan | Euclidiana é padrão; manhattan pode ser mais robusta com encoding {-1,0,1} |
| `weights` | uniform, distance | `distance` dá mais peso aos vizinhos mais próximos |

---

### 6.2 Árvore de Decisão — `dt_32`

**Como funciona:** Particiona recursivamente o espaço de features usando splits binários no atributo que maximiza a pureza dos subconjuntos resultantes (medida por Gini ou Entropia). A predição segue o caminho da raiz até uma folha.

**Hiperparâmetros tunados:**

| Parâmetro | Valores testados | Justificativa |
|---|---|---|
| `max_depth` | None, 3, 5, 7, 10 | Limitar profundidade é a principal forma de regularização — evita overfitting |
| `criterion` | gini, entropy | Gini é mais rápido; entropia pode gerar árvores mais balanceadas |
| `min_samples_split` | 2, 5, 10 | Mínimo de amostras para criar um split — valores maiores regularizam |
| `min_samples_leaf` | 1, 2, 4 | Mínimo por folha — evita folhas com 1 amostra (overfitting) |

---

### 6.3 MLP (Multilayer Perceptron) — `mlp_32`

**Como funciona:** Rede neural feedforward com camadas ocultas e propagação de erro por backpropagation. Aprende representações não-lineares dos dados.

**Topologia justificada:**

- **Entrada:** 9 neurônios (um por casa do tabuleiro)
- **Camadas ocultas:** 1 ou 2 camadas (testadas: `(50,)`, `(100,)`, `(50,50)`, `(100,50)`, `(64,32)`)
- **Saída:** 4 neurônios com softmax (uma por classe)

**Justificativa das topologias:** O problema tem baixa dimensionalidade (9 features, 3 valores possíveis). Redes com 1-2 camadas ocultas são suficientes. Camadas maiores que 100 neurônios teriam risco de overfitting neste dataset de ~800 amostras.

**Hiperparâmetros tunados:**

| Parâmetro | Valores testados | Justificativa |
|---|---|---|
| `hidden_layer_sizes` | (50,), (100,), (50,50), (100,50), (64,32) | Explorar 1 e 2 camadas ocultas |
| `activation` | relu, tanh | `tanh` pode se adaptar melhor ao encoding {-1,0,1} por ser simétrico em torno de 0 |
| `alpha` | 0.0001, 0.001, 0.01 | Regularização L2 — penaliza pesos grandes, evita overfitting |
| `max_iter` | 1000 | Fixo e alto para garantir convergência em todos os casos |

---

### 6.4 Random Forest — `rf_32` *(livre escolha #1)*

**Como funciona:** Ensemble de múltiplas árvores de decisão, onde cada árvore é treinada com uma amostra bootstrap do conjunto de treino (amostragem com reposição) e, em cada split, apenas um subconjunto aleatório de features é considerado. A predição final é por **votação majoritária** das árvores.

**Por que funciona melhor que uma única árvore?**

- **Redução de variância:** árvores individuais têm alta variância (overfitting). A média das predições de muitas árvores descorrelacionadas cancela boa parte da variância.
- **Decorrelação via aleatoriedade de features:** a seleção aleatória de features em cada split garante que as árvores sejam diferentes entre si, tornando a votação mais informativa.

**Por que escolhemos:** é extensão natural da Árvore de Decisão obrigatória e permite análise de importância de features (quais posições do tabuleiro são mais discriminativas), trazendo interpretabilidade extra.

**Hiperparâmetros tunados:**

| Parâmetro | Valores testados | Justificativa |
|---|---|---|
| `n_estimators` | 50, 100, 200 | Mais árvores = mais estável, mas custo computacional cresce |
| `max_depth` | None, 5, 10 | Regularização das árvores individuais do ensemble |
| `max_features` | sqrt, log2 | Controla o número de features sorteadas por split (`sqrt` = padrão sklearn) |

---

### 6.5 SVM (Support Vector Machine) — `svm_32` *(livre escolha #2)*

**Como funciona:** Encontra o **hiperplano de margem máxima** que separa as classes no espaço de features. Com o kernel RBF (Radial Basis Function), o espaço de entrada é mapeado implicitamente para alta dimensão, permitindo separações não-lineares. Para problemas multiclasse, usa estratégia **One-vs-Rest** (um classificador binário por classe).

O parâmetro `C` controla o trade-off entre:
- Maximizar a margem (menor `C`) → mais regularização, permite mais erros de treino
- Minimizar os erros de treino (maior `C`) → margem menor, mais sensível a ruído

**Por que escolhemos:** abordagem geometricamente diferente dos modelos baseados em árvores — enquanto DT e RF particionam o espaço recursivamente por impureza, o SVM encontra a separação ótima por margem. O espaço 9D com encoding {-1, 0, +1} tem estrutura geométrica regular que o SVM pode explorar bem.

**Hiperparâmetros tunados:**

| Parâmetro | Valores testados | Justificativa |
|---|---|---|
| `kernel` | rbf, linear, poly | RBF é o mais poderoso para dados não lineares; linear como baseline |
| `C` | 0.1, 1, 10, 100 | Faixa ampla para encontrar o ponto de equilíbrio margem/erros |
| `gamma` | scale, auto | `scale` = 1/(n_features × var(X)) — mais estável que `auto` |

---

## 7. Comparação e Escolha do Melhor Modelo

### 7.1 Métricas utilizadas

Todos os modelos são avaliados no **conjunto de teste** com quatro métricas:

| Métrica | Fórmula | O que mede |
|---|---|---|
| **Acurácia** | (acertos) / (total) | Proporção geral de predições corretas |
| **Precisão (macro)** | média de TP/(TP+FP) por classe | Evitar falsos positivos em cada classe |
| **Recall (macro)** | média de TP/(TP+FN) por classe | Evitar falsos negativos em cada classe |
| **F1 Macro** | média harmônica de precisão e recall por classe | Equilíbrio entre precisão e recall, igual peso para todas as classes |

**F1 Macro é a métrica de seleção** porque:
- Considera simultaneamente precisão e recall
- Dá peso igual a todas as 4 classes (não ponderado pelo tamanho)
- É mais discriminativa que acurácia para problemas multiclasse balanceados

### 7.2 Verificação de overfitting

Para o modelo selecionado, calcula-se o **gap de F1 entre treino e teste**. Um gap > 5% é considerado indicativo de overfitting.

### 7.3 Critério de desempate

Se a diferença de F1 entre o melhor e o segundo colocado for < 2%, considera-se o modelo mais simples (menor complexidade computacional).

---

## 8. Front End — Jogo Interativo

### 8.1 Arquitetura

```
Navegador (HTML/JS)  ←→  Flask (app.py)  ←→  Modelo .pkl (joblib)
```

- **Humano joga como X** (sempre o primeiro a mover)
- **CPU joga como O** (movimentos completamente aleatórios entre as casas livres)
- A cada turno, o modelo ML classifica o estado do tabuleiro

### 8.2 Fluxo de uma jogada (`POST /api/move`)

```
1. Humano escolhe posição → board[pos] = 'x'
2. Modelo classifica o estado atual
3. Se estado real ≠ 'tem_jogo' e modelo disse 'tem_jogo'
   → IA não detectou fim: ENCERRA o jogo (regra do enunciado)
4. Se estado real = 'tem_jogo' e modelo disse outra coisa
   → IA detectou fim incorretamente: LOG do erro, CONTINUA o jogo
5. CPU sorteia posição aleatória → board[cpu_pos] = 'o'
6. Modelo classifica novamente
7. Mesmas regras especiais aplicadas
8. Resposta JSON com board, predições, acertos, acurácia acumulada
```

### 8.3 Regras especiais (conforme enunciado)

> **Encerrar quando a IA não detectar fim de jogo:** se o estado real é `x_venceu`, `o_venceu` ou `empate`, mas o modelo prediz `tem_jogo`, o frontend encerra a partida imediatamente.
>
> **Continuar quando a IA detectar fim incorretamente:** se o estado real é `tem_jogo`, mas o modelo prediz outra coisa, um aviso é exibido e o jogo continua normalmente.

### 8.4 Contabilização de acertos

A cada predição (humano + CPU = até 2 predições por rodada), são contabilizados:
- `total_predicoes_32`: total de predições feitas no jogo
- `acertos_32`: predições onde `pred == true_label`
- `accuracy_32`: `acertos / total` em tempo real

### 8.5 Modo fallback

Se os arquivos `.pkl` não forem encontrados em `frontend/models/`, o servidor usa a função `classify_board_32` (lógica determinística pura). Isso garante que o frontend funcione sem os modelos treinados, com acurácia 100% — útil para testar a interface antes de exportar os modelos.

### 8.6 Logs no console do navegador

Ao abrir o DevTools (F12 → aba Console), cada jogada exibe:
- Modelo em uso e modo (ML ou Fallback)
- Visualização ASCII do tabuleiro após a jogada
- Array de entrada enviado ao modelo `[1, 0, -1, ...]`
- Predição do modelo e estado real
- Se a predição foi correta (✓) ou incorreta (✗)

### 8.7 Exportar modelos do notebook para o frontend

Após executar todas as seções do notebook, rode a célula de exportação (Seção EXPORT):

```python
# Salva em frontend/models/
joblib.dump(melhor_modelo_32, '.../melhor_modelo_32.pkl')
joblib.dump(scaler_32,        '.../scaler_32.pkl')
joblib.dump(le_32,            '.../le_32.pkl')
```

---

## 9. Convenção de Nomenclatura `_32`

Todas as variáveis criadas pelo grupo contêm o sufixo `_32` no nome, conforme exigência do enunciado. Exemplos por categoria:

| Categoria | Exemplos |
|---|---|
| Constantes | `RANDOM_STATE_32`, `CLASS_NAMES_32`, `WIN_LINES_32`, `ENCODE_MAP_32` |
| Dataset | `df_raw_32`, `df_32`, `df_synthetic_32`, `df_balanced_32`, `df_encoded_32` |
| Splits | `X_treino_32`, `X_val_32`, `X_teste_32`, `X_trainval_32` |
| Pré-processamento | `scaler_32`, `le_32` |
| Modelos | `knn_32`, `dt_32`, `mlp_32`, `rf_32`, `svm_32`, `melhor_modelo_32` |
| Métricas | `df_comparacao_32`, `resultados_32` |
| Front End | `total_predicoes_32`, `acertos_32`, `historico_32` |
| Funções | `classify_board_32`, `ia_predict_32`, `tune_model_32`, `avaliar_modelo_32` |

---

## 10. Como Executar

### Notebook (treino e avaliação)

```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter notebook
jupyter notebook tic_tac_toe_classifier_32.ipynb
# Execute: Kernel → Restart & Run All
```

### Front End (jogo interativo)

```bash
# 1. Exporte os modelos rodando a célula EXPORT no notebook
# 2. Inicie o servidor:
pip install flask joblib
python frontend/app.py
# Acesse: http://localhost:5000
```

---

*T1 — Inteligência Artificial | PUCRS | Grupo 32 | 2026/1*
