# Roteiro do Relatório (PPT) — T2 Olimpíada / Algoritmo Genético

> Conteúdo pronto para virar slides (PowerPoint/Google Slides). Cada `## Slide` é um
> slide; os tópicos são os bullets. A rubrica vale **2,0 pontos** para este relatório e
> exige: codificação, tamanho da população inicial, funções heurísticas, operadores
> escolhidos, taxa de mutação e cruzamento, problemas e considerações.

---

## Slide 1 — Capa
- **T2 – Algoritmos de Busca: Olimpíada**
- Disciplina: Inteligência Artificial — Profa. Silvia Moraes — PUCRS
- Integrantes do grupo: _(nomes)_
- Algoritmo escolhido: **Algoritmo Genético memético** (AG + busca local)

## Slide 2 — O problema
- Alunos de **duas escolas** (A e B) em **quartos duplos heterogêneos** (um de cada).
- Objetivo: melhor distribuição segundo as **preferências mútuas**.
- Entrada: arquivo-texto com listas ordenadas de preferência.
- Natureza: problema de **atribuição**, parente do **Casamento Estável**; espaço de
  busca = **N!** soluções → busca exaustiva inviável.

## Slide 3 — Por que Algoritmo Genético (memético)
- Meta-heurística populacional, guiada por função de aptidão.
- Boa para espaços combinatórios grandes (N!).
- Estrutura alinhada ao exemplo de aula (N-Rainhas).
- Reforçada com **busca local** (memético) para intensificar a convergência ao ótimo.

## Slide 4 — Codificação
- Indivíduo = **permutação** `perm`, onde `perm[i]` = aluno B do quarto do aluno A `i`.
- Toda permutação de `0..N-1` é um emparelhamento perfeito e heterogêneo.
- Ex.: `4 2 1 3` → A1–B4, A2–B2, A3–B1, A4–B3.
- _(figura: vetor + duplas correspondentes)_

## Slide 5 — Função heurística (aptidão)
- **Custo de insatisfação a minimizar**:
  `custo = Σ (rankA + rankB)` sobre as duplas (ranking base 1).
- 1ª escolha mútua → custo 2 (mínimo da dupla); ótimo teórico = **2·N**.
- Considera os **dois lados**; **independe da quantidade de duplas**.
- **Matriz de custo pré-computada** (`custo[i][j]`) → avaliação O(N) e *delta* O(1).
- **Sem penalidade:** todos os operadores preservam a permutação (nunca há inválido).

## Slide 6 — População inicial
- **100 indivíduos** (permutações aleatórias válidas).
- Equilíbrio entre diversidade (exploração) e custo computacional.

## Slide 7 — Operadores: Seleção e Elitismo
- **Seleção por torneio** (k=2): sorteia 2, vence o de menor custo.
- Não exige fitness normalizado; pressão seletiva ajustável por k.
- **Elitismo** (2 melhores preservados): a melhor solução nunca piora.

## Slide 8 — Operadores: Cruzamento e Mutação
- **Order Crossover (OX)** (taxa **0,85**): herda um segmento de um pai e completa
  com a ordem do outro. **Preserva a permutação por construção** — sem reparo nem
  penalidade, e herda mais estrutura que o corte simples.
- **Mutação por troca** (taxa **0,15**): troca duas posições; preserva validade.

## Slide 9 — Busca local (componente memético)
- Após cada filho: **busca local 2-swap** (*first-improvement*) — aplica trocas que
  **reduzem o custo** até um ótimo local.
- **Delta O(1)** via matriz de custo (não recalcula o fitness inteiro).
- É o que **leva o AG ao ótimo de forma confiável**; faz parte fixa do ciclo.

## Slide 10 — Ciclo e critérios de parada
- Ciclo: avaliar → (elitismo) → seleção → **OX** → mutação → **busca local** → repetir.
- Parada: **máx. de gerações (500)** OU **estagnação (50 sem melhora)** OU **ótimo
  teórico atingido**.

## Slide 11 — Parâmetros utilizados
| Parâmetro | Valor |
|-----------|-------|
| População | 100 |
| Gerações (máx.) | 500 |
| Taxa de crossover (OX) | 0,85 |
| Taxa de mutação | 0,15 |
| Torneio (k) | 2 |
| Elitismo | 2 |
| Estagnação | 50 |
| Busca local | sempre ligada |

> Parâmetros **fixos no código** (classe `Parametros`). A execução só recebe o
> arquivo e o `--modo`.

## Slide 12 — Modos de execução
- **Passo a passo:** pausa a cada geração (Enter), mostra o melhor indivíduo
  codificado e decodificado.
- **Final:** roda tudo e exibe a solução ao final.
- Ambos mostram a **evolução da heurística** (console + arquivo de saída).
- CLI enxuta: `python main.py <arquivo> --modo passo|final` (só esses dois argumentos).

## Slide 13 — Resultados
- **N=4 (caso1):** custo **13** = **ótimo** (confirmado por força bruta) — `4 2 1 3`.
- **N=10 (caso2):** solução válida, custo **30** (média 3,0/dupla).
- **Efeito do memético:** sem o refinamento, o AG "puro" estaciona em valores
  piores nas mesmas gerações → a busca local é decisiva.
- _(inserir trecho do log de evolução melhor/média/pior por geração)_

## Slide 14 — Problemas e considerações
- **Escolha do crossover:** corte simples quebra permutações (exigia reparo); migramos
  para **Order Crossover**, que preserva a permutação e herda mais estrutura.
- **Busca local (memético):** foi o que garantiu chegar ao ótimo de forma confiável.
- Calibração de taxas: mutação alta demais vira busca aleatória; torneio grande demais
  converge cedo (ótimo local).
- Heurística simétrica foi decisiva para soluções justas entre as duas escolas.
- Estagnação evita desperdício após convergência.

## Slide 15 — Como executar / Entregáveis
- `python main.py <arquivo> --modo final|passo` (ver `docs/DOCUMENTACAO_CODIGO.md`).
- Executável via PyInstaller (`pyinstaller --onefile main.py`).
- Testes: `pytest test_main.py`.
- Saídas: console + `<arquivo>_output.txt`.

## Slide 16 — Encerramento
- Domínio do problema e do AG memético.
- Perguntas.
