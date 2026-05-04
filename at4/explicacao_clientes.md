# 🏦 O Robozinho Bancário — Classificando Clientes
### Como o Perceptron decide se um cliente é bom ou mau pagador?

---

## O Problema 🤔

Um banco tem uma lista de 21 clientes com informações de **Renda** e **Dívida**, e sabe quais são bons e maus pagadores. Queremos ensinar um robozinho a tomar essa decisão sozinho para novos clientes!

---

## Passo 1 — Lendo os Dados 📋

O robozinho lê o arquivo `dados.csv`:

| Cliente | Renda | Dívida | Classe |
|:---:|:---:|:---:|:---:|
| 101 | 2800 | 550 | bom |
| 102 | 1300 | 500 | mau |
| 103 | 1400 | 80 | bom |
| ... | ... | ... | ... |

São 21 clientes no total.

---

## Passo 2 — Escolhendo os Atributos 🎯

O arquivo tem 4 colunas. Quais usar?

| Coluna | Usar? | Por quê? |
|---|:---:|---|
| Cliente | ❌ | É só um número de identificação, não diz nada sobre o pagamento |
| Renda | ✅ | Quem ganha mais tem mais condição de pagar |
| Dívida | ✅ | Quem deve muito tem mais risco de não pagar |
| Classe | 🎯 | É a **resposta certa** que queremos prever |

Ficamos com **Renda (x1)** e **Dívida (x2)** como entradas, e **Classe** como saída:
- `bom` → **1** ✅
- `mau` → **0** ❌

---

## Passo 3 — Pré-processamento: Normalização 🔧

### Por que normalizar?

Olha os números:
- Renda vai de **450** até **2800**
- Dívida vai de **70** até **800**

Se usarmos esses números direto, a Renda vai "gritar mais alto" que a Dívida por causa do tamanho — e o robozinho vai prestar mais atenção nela sem motivo!

### A fórmula mágica — Min-Max

$$x_{norm} = \frac{x - x_{min}}{x_{max} - x_{min}}$$

Isso transforma tudo para o intervalo **[0, 1]**:

| Antes | Depois |
|:---:|:---:|
| Renda: 450 | 0.000 |
| Renda: 2800 | 1.000 |
| Renda: 1625 | 0.500 |
| Dívida: 70 | 0.000 |
| Dívida: 800 | 1.000 |

Agora os dois estão no mesmo "volume"! 🔊🔊

---

## Passo 4 — Dividindo Treino e Teste ✂️

Temos 21 clientes. Dividimos assim:

```
70% → 14 clientes para TREINAR o robozinho
30% →  7 clientes para TESTAR se ele aprendeu
```

É como estudar com 14 questões de prova antiga e depois fazer um simulado com 7 questões novas! 📚

A divisão é feita de forma **aleatória** (mas sempre igual, usando `seed=42`).

---

## Passo 5 — Treinamento (mesma topologia de antes) 🏋️

O robozinho usa exatamente a mesma estrutura dos exemplos OR e AND:

```
Pesos: [w0, w1, w2]  →  bias, peso da Renda, peso da Dívida
```

A conta:
```
v = w0 + w1 × Renda_norm + w2 × Divida_norm
```

A porteira:
- Se `v >= 0` → **bom** ✅
- Se `v < 0`  → **mau** ❌

A diferença aqui: usamos **taxa de aprendizado `eta = 0.1`** (mais suave que 1) porque os dados reais são mais complexos que uma tabela lógica!

---

## Passo 6 — Gráfico de Convergência 📈

Depois do treinamento, desenhamos um gráfico mostrando como o erro foi caindo ao longo das épocas:

```
Erro
  |
8 | *
6 |   *
4 |     *  *
2 |           *  *
0 |                  * * * *  ← convergiu!
  +----------------------------→ Época
```

Quando a linha chega em zero, o robozinho aprendeu tudo que estava no conjunto de treino!

---

## Passo 7 — Testando com os 30% 🧪

Agora testamos com os 7 clientes que o robozinho **nunca viu antes**:

```
═══════════════════════════════════════════════════════
  Cliente     Renda    Dívida   Real   Pred    OK?
═══════════════════════════════════════════════════════
      105      1100       270    mau    mau     ✅
      110      2750       730    bom    bom     ✅
      116      1600       500    mau    mau     ✅
      ...
═══════════════════════════════════════════════════════
Acertos: 6/7
Acurácia: 85.7%
```

*(Os resultados exatos dependem da divisão aleatória)*

---

## Passo 8 — O Gráfico Final 🗺️

O gráfico mostra todos os 21 clientes no espaço Renda × Dívida:

- **Círculo verde** ⭘ → treino, cliente bom
- **Círculo vermelho** ⭘ → treino, cliente mau
- **Estrela verde** ★ → teste, cliente bom
- **Estrela vermelha** ★ → teste, cliente mau
- **Linha tracejada** → a fronteira que o robozinho aprendeu

Clientes acima ou abaixo da linha são classificados em grupos diferentes!

---

## Resumão — Atividade 2 🌟

| Etapa | O que fizemos |
|---|---|
| 1. Dados | Lemos o `dados.csv` com 21 clientes |
| 2. Atributos | Escolhemos Renda e Dívida (descartamos Cliente) |
| 3. Normalização | Transformamos tudo para [0, 1] com Min-Max |
| 4. Divisão | 70% treino (14) / 30% teste (7) |
| 5. Topologia | Mesma do OR/AND: bias + 2 pesos, função limiar |
| 6. Treinamento | Regra Delta com eta=0.1 |
| 7. Avaliação | Acurácia no conjunto de teste |
| 8. Gráfico | Fronteira de decisão no espaço normalizado |

---

## Por que o resultado não é 100%? 🤷

Porque o mundo real é mais bagunçado do que uma tabela lógica!

- No OR e AND os dados eram **perfeitamente separáveis** por uma reta
- Nos dados de clientes, pode haver **sobreposição** — um cliente com renda baixa e dívida baixa pode ser bom pagador, enquanto outro com renda alta e dívida alta pode ser mau

Isso é normal! Em problemas reais, o Perceptron simples dá uma boa primeira aproximação, mas redes mais complexas (como o MLP) conseguem fronteiras mais sofisticadas. 🚀
