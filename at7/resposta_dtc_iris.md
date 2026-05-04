# Decision Tree Classifier — Gini vs Entropia no Dataset Iris

## Configuração do Experimento

- **Dataset:** Iris (150 amostras, 4 features, 3 classes)
- **Divisão:** 70% treino / 30% teste (`random_state=0`, `stratify=y`)
- **Modelo:** `DecisionTreeClassifier` (scikit-learn)
- **Parâmetros fixos:** `ccp_alpha=0.0`, `min_samples_split=2`, `min_samples_leaf=1`
- **Variável testada:** `criterion` → `'gini'` ou `'entropy'`

---

## Resultados de Acurácia

| Critério | Acurácia        |
|----------|-----------------|
| **Gini** | **97,78%**      |
| Entropia | 95,56%          |

> **Melhor critério: Gini** com acurácia de **0.9777... (≈ 97,78%)**

---

## Árvore Gerada — Critério Gini (melhor)

```
|--- petal width (cm) <= 0.80
|   |--- class: 0  (Iris-setosa)
|--- petal width (cm) >  0.80
|   |--- petal width (cm) <= 1.75
|   |   |--- petal length (cm) <= 4.95
|   |   |   |--- petal width (cm) <= 1.65
|   |   |   |   |--- class: 1  (Iris-versicolor)
|   |   |   |--- petal width (cm) >  1.65
|   |   |   |   |--- class: 2  (Iris-virginica)
|   |   |--- petal length (cm) >  4.95
|   |   |   |--- petal width (cm) <= 1.55
|   |   |   |   |--- class: 2  (Iris-virginica)
|   |   |   |--- petal width (cm) >  1.55
|   |   |   |   |--- class: 1  (Iris-versicolor)
|   |--- petal width (cm) >  1.75
|   |   |--- petal length (cm) <= 4.85
|   |   |   |--- sepal length (cm) <= 5.95
|   |   |   |   |--- class: 1  (Iris-versicolor)
|   |   |   |--- sepal length (cm) >  5.95
|   |   |   |   |--- class: 2  (Iris-virginica)
|   |   |--- petal length (cm) >  4.85
|   |   |   |--- class: 2  (Iris-virginica)
```

---

## Árvore Gerada — Critério Entropia

```
|--- petal width (cm) <= 0.80
|   |--- class: 0  (Iris-setosa)
|--- petal width (cm) >  0.80
|   |--- petal width (cm) <= 1.75
|   |   |--- petal width (cm) <= 1.45
|   |   |   |--- class: 1
|   |   |--- petal width (cm) >  1.45
|   |   |   |--- sepal width (cm) <= 2.85
|   |   |   |   |--- petal width (cm) <= 1.65
|   |   |   |   |   |--- petal width (cm) <= 1.55
|   |   |   |   |   |   |--- petal length (cm) <= 4.95
|   |   |   |   |   |   |   |--- class: 1
|   |   |   |   |   |   |--- petal length (cm) >  4.95
|   |   |   |   |   |   |   |--- class: 2
|   |   |   |   |   |--- petal width (cm) >  1.55
|   |   |   |   |   |   |--- class: 1
|   |   |   |   |--- petal width (cm) >  1.65
|   |   |   |   |   |--- class: 2
|   |   |   |--- sepal width (cm) >  2.85
|   |   |   |   |--- class: 1
|   |--- petal width (cm) >  1.75
|   |   |--- petal length (cm) <= 4.85
|   |   |   |--- sepal length (cm) <= 5.95
|   |   |   |   |--- class: 1
|   |   |   |--- sepal length (cm) >  5.95
|   |   |   |   |--- class: 2
|   |   |--- petal length (cm) >  4.85
|   |   |   |--- class: 2
```

---

## Análise Comparativa

### Por que o Gini foi melhor?

| Aspecto | Gini | Entropia |
|---|---|---|
| Acurácia no teste | **97,78%** | 95,56% |
| Complexidade da árvore | Menor (mais compacta) | Maior (mais profunda) |
| Features no nó raiz | petal width | petal width |
| Features usadas | petal width, petal length, sepal length | petal width, petal length, sepal width |

- O **Índice Gini** mede a impureza de um nó como a probabilidade de classificar incorretamente um elemento aleatório: `Gini = 1 - Σ pᵢ²`
- A **Entropia** mede a desordem informacional do nó: `H = -Σ pᵢ log₂(pᵢ)`

Ambos os critérios tendem a produzir árvores similares, mas a Entropia é computacionalmente mais custosa (usa logaritmo) e pode gerar árvores mais profundas quando os dados têm regiões de decisão complexas na fronteira entre classes.

### Feature mais discriminante

Em ambos os critérios, **`petal width (cm)`** é o atributo raiz (mais discriminante), confirmando que a largura da pétala é a feature com maior poder de separação entre as três espécies de Iris.

---

## Conclusão

> O critério **Gini** produziu a melhor acurácia: **97,78%** (44/45 amostras corretas no conjunto de teste), gerando uma árvore mais simples e com melhor generalização em comparação com o critério Entropia (95,56%).
