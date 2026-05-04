# K-Means Clustering — Fundamentos e Análise

## Dataset: Online Shoppers Purchasing Intention

---

## 1. O que é Clustering?

Clustering (ou agrupamento) é uma técnica de **aprendizado não-supervisionado** cujo objetivo é organizar dados em grupos (clusters) de forma que:

- Elementos **dentro** do mesmo cluster sejam **semelhantes entre si**
- Elementos de clusters **diferentes** sejam **distintos** entre si

Diferentemente da classificação, não há rótulos de classe disponíveis durante o treinamento. O algoritmo descobre a estrutura dos dados por conta própria.

---

## 2. O Algoritmo K-Means

### 2.1 Ideia Central

O k-Means divide os dados em **k grupos** minimizando a variância intra-cluster, formalmente definida como:

$$J = \sum_{i=1}^{k} \sum_{x \in C_i} \| x - \mu_i \|^2$$

Onde:
- $k$ = número de clusters
- $C_i$ = conjunto de pontos no cluster $i$
- $\mu_i$ = centróide (média) do cluster $i$
- $\| x - \mu_i \|^2$ = distância euclidiana ao quadrado do ponto ao centróide

Essa soma é chamada de **WCSS** (Within-Cluster Sum of Squares) ou **Inertia**.

### 2.2 Passos do Algoritmo

```
1. Inicialização
   Escolher k centróides iniciais (aleatoriamente ou via k-means++)

2. Atribuição (E-step)
   Para cada ponto x, atribuir ao cluster do centróide mais próximo:
   c(x) = argmin_i ||x - μ_i||²

3. Atualização (M-step)
   Recalcular cada centróide como a média dos pontos atribuídos a ele:
   μ_i = (1/|C_i|) * Σ x, para x em C_i

4. Repetir passos 2 e 3 até convergência
   (centróides não mudam mais, ou mudança < threshold)
```

### 2.3 Inicialização K-Means++

A inicialização aleatória pode levar a soluções ruins. O **k-means++** melhora isso:

1. Escolhe o 1º centróide aleatoriamente
2. Cada centróide seguinte é escolhido com probabilidade proporcional à **distância ao centróide mais próximo já escolhido**
3. Isso garante que os centróides iniciais sejam bem distribuídos

Resultado: convergência mais rápida e soluções melhores.

### 2.4 Complexidade

| Aspecto | Valor |
|---|---|
| Tempo | O(n × k × d × i) |
| Espaço | O(n × d + k × d) |
| Convergência | Garantida (mas pode ser mínimo local) |

Onde n = amostras, k = clusters, d = features, i = iterações.

---

## 3. Estimando o Melhor k

O k-Means exige que o usuário defina k a priori. Dois métodos clássicos ajudam a encontrar o valor mais adequado:

### 3.1 Método do Cotovelo (Elbow Method)

Plota a **Inertia vs. k**. À medida que k aumenta, a inertia sempre diminui (mais clusters → pontos mais próximos dos centróides). O ponto de inflexão — onde o ganho começa a diminuir rapidamente — sugere o k ideal.

```
Inertia
  |
  |*
  | *
  |  *
  |   *___________  ← cotovelo aqui
  |________________ k
```

**Limitação:** O "cotovelo" nem sempre é óbvio em dados reais.

### 3.2 Silhouette Score

Mede quão bem cada ponto está em seu próprio cluster em comparação com o cluster vizinho mais próximo.

Para cada ponto $x_i$:

$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

Onde:
- $a(i)$ = distância média de $x_i$ a todos os outros pontos **no mesmo cluster** (coesão interna)
- $b(i)$ = distância média de $x_i$ ao cluster **vizinho mais próximo** (separação externa)

**Interpretação do coeficiente:**

| Valor | Significado |
|---|---|
| $s(i) \approx +1$ | Ponto bem posicionado em seu cluster |
| $s(i) \approx 0$ | Ponto na fronteira entre clusters |
| $s(i) \approx -1$ | Ponto provavelmente no cluster errado |

O **Silhouette Score médio** é calculado para todos os pontos. O k que maximiza esse valor é o k ótimo.

**Vantagem:** É um critério absoluto — não precisa de comparação visual, tem interpretação clara.

---

## 4. Pré-processamento para K-Means

### 4.1 Por que Escalar é Obrigatório?

O k-Means usa **distância euclidiana**. Se uma feature tem valores na faixa [0, 1000] e outra em [0, 1], a primeira domina completamente o cálculo de distância — independentemente de sua relevância real.

**StandardScaler** transforma cada feature para média 0 e desvio padrão 1:

$$x_{scaled} = \frac{x - \mu}{\sigma}$$

### 4.2 Variáveis Categóricas

O k-Means só trabalha com números. As variáveis categóricas foram codificadas com **LabelEncoder**, que converte categorias em inteiros:

- `Month`: Feb→0, Mar→1, ... Dec→9
- `VisitorType`: New_Visitor→0, Other→1, Returning_Visitor→2
- `Weekend`: False→0, True→1

> **Nota:** Para variáveis nominais sem ordem natural, o ideal seria One-Hot Encoding, mas aumentaria a dimensionalidade. LabelEncoder é uma simplificação prática adotada aqui.

### 4.3 Remoção do Rótulo

A coluna `Revenue` (comprou ou não) é o **alvo supervisionado** do dataset. Ela é **removida** antes do clustering para respeitar o paradigma não-supervisionado. Após o clustering, ela é usada apenas para **validação externa** — verificar se os clusters descobertos têm relação com o comportamento real de compra.

---

## 5. O Dataset: Online Shoppers Purchasing Intention

| Característica | Valor |
|---|---|
| Instâncias | 12.330 sessões de e-commerce |
| Features | 17 (removendo Revenue) |
| Rótulo ignorado | `Revenue` (True/False) |
| Desbalanceamento | 84,6% não comprou / 15,4% comprou |

### Features Principais

| Feature | Tipo | Descrição |
|---|---|---|
| Administrative | Int | Nº de páginas administrativas visitadas |
| Administrative_Duration | Float | Tempo total nessas páginas (s) |
| Informational | Int | Nº de páginas informativas visitadas |
| ProductRelated | Int | Nº de páginas de produto visitadas |
| ProductRelated_Duration | Float | Tempo em páginas de produto (s) |
| BounceRates | Float | Taxa de rejeição (% de visitantes que saem sem interagir) |
| ExitRates | Float | Taxa de saída de cada página |
| PageValues | Float | Valor médio da página antes de uma transação |
| SpecialDay | Float | Proximidade a datas especiais (0 a 1) |
| Month | Categórica | Mês da sessão |
| VisitorType | Categórica | Novo / Recorrente / Outro |
| Weekend | Boolean | Sessão ocorreu no fim de semana? |

---

## 6. Análise dos Resultados

### 6.1 Escolha do k

Os dois métodos foram aplicados para $k \in [2, 10]$:

| k | Inertia | Silhouette Score |
|---|---:|---:|
| **2** | 185.774 | **0,2570** ← máximo |
| 3 | 166.000 | 0,2478 |
| 4 | 153.942 | 0,1987 |
| 5 | 144.495 | 0,2059 |
| 6 | 136.759 | 0,1595 |
| 7 | 130.834 | 0,1812 |
| 8 | 124.232 | 0,1674 |
| 9 | 118.418 | 0,1724 |
| 10 | 114.341 | 0,1572 |

- **Elbow**: A curva de inertia apresenta inflexão clara em `k=2`, com ganhos decrescentes a partir daí.
- **Silhouette**: O score máximo é `0,2570` em `k=2`, confirmando como melhor partição.

**k* = 2** foi selecionado como valor ótimo por ambos os critérios.

> O Silhouette Score de 0,25 é considerado **fraco a moderado**, o que é esperado para dados reais de comportamento humano — as fronteiras entre grupos não são nítidas, mas o clustering ainda captura estrutura relevante.

### 6.2 Interpretação dos Clusters Encontrados

| | Cluster 0 | Cluster 1 |
|---|---|---|
| **Tamanho** | 10.378 (84,2%) | 1.952 (15,8%) |
| **Taxa de conversão** | 13,2% | 27,6% |
| **PageValues médio** | 5,12 | 9,97 |
| **ProductRelated_Duration** | 753 s | 3.546 s |
| **BounceRates** | 0,0252 | 0,0062 |

**Cluster 0 — Visitantes de Baixo Engajamento:**
- Maioria das sessões (84,2%)
- `PageValues` baixo: visitaram páginas com pouco valor transacional
- Tempo em produtos curto (~12 min)
- Taxa de bounce maior → saída mais rápida
- Apenas 13,2% converteram em compra

**Cluster 1 — Visitantes de Alta Intenção de Compra:**
- Minoria das sessões (15,8%), mas muito mais engajados
- Quase **5× mais tempo** em páginas de produto (~59 min)
- `PageValues` quase o dobro → navegaram por páginas mais próximas do checkout
- `BounceRates` 4× menor → raramente saíram sem interagir
- **27,6% converteram** — taxa 2,1× maior que o Cluster 0

O k-Means descobriu, **sem usar o rótulo `Revenue`**, a separação natural entre visitantes casuais e visitantes com alta intenção de compra.

### 6.3 Silhouette Plot

O gráfico de silhouette por amostra exibe a distribuição dos coeficientes dentro de cada cluster:

- Barras longas e uniformes → cluster bem definido
- Barras curtas ou com valores negativos → cluster com amostras mal alocadas
- A linha vermelha tracejada marca o score médio global (0,257)

---

## 7. Limitações do K-Means

| Limitação | Impacto | Alternativa |
|---|---|---|
| Assume clusters esféricos | Falha com formas irregulares | DBSCAN, Gaussian Mixture Models |
| k deve ser definido a priori | Requer análise prévia | DBSCAN (k automático) |
| Sensível a outliers | Centróides deslocados | K-Medoids (PAM) |
| Mínimos locais | Resultado varia com inicialização | n_init > 1, k-means++ |
| Distância euclidiana | Ruim com dados esparsos ou categoriais | K-Modes, K-Prototypes |

---

## 8. Fluxo Completo da Solução

```
Dataset Original (12.330 × 18)
         │
         ▼
  Remover Revenue (rótulo)
         │
         ▼
  Codificar Categóricas (LabelEncoder)
         │
         ▼
  Escalonar Features (StandardScaler)
         │
         ▼
  Avaliar k ∈ [2..10]
  ├── Elbow (Inertia)
  └── Silhouette Score
         │
         ▼
  Selecionar k* (melhor Silhouette)
         │
         ▼
  Treinar KMeans(k=k*, k-means++, n_init=20)
         │
         ▼
  Análise dos Clusters
  ├── Perfil dos centróides (heatmap)
  ├── Boxplots das features mais discriminantes
  ├── Visualização PCA 2D
  ├── Taxa de conversão por cluster
  └── Comparação com Revenue real
```

---

## 9. Referências

- MacQueen, J. (1967). *Some methods for classification and analysis of multivariate observations*. Proceedings of the 5th Berkeley Symposium.
- Arthur, D. & Vassilvitskii, S. (2007). *k-means++: The advantages of careful seeding*. SODA.
- Rousseeuw, P. J. (1987). *Silhouettes: A graphical aid to the interpretation and validation of cluster analysis*. Journal of Computational and Applied Mathematics.
- Sakar, C.O. et al. (2019). *Real-time prediction of online shoppers' purchasing intention using multilayer perceptron and LSTM recurrent neural networks*. Neural Computing and Applications. (Dataset original)
- Scikit-learn documentation: [sklearn.cluster.KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)
