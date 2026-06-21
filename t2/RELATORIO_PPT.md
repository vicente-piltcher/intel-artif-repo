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
- Algoritmo escolhido: **Algoritmo Genético**

## Slide 2 — O problema
- Alunos de **duas escolas** (A e B) em **quartos duplos heterogêneos** (um de cada).
- Objetivo: melhor distribuição segundo as **preferências mútuas**.
- Entrada: arquivo-texto com listas ordenadas de preferência.
- Natureza: problema de **atribuição**, parente do **Casamento Estável**; espaço de
  busca = **N!** soluções → busca exaustiva inviável.

## Slide 3 — Por que Algoritmo Genético
- Meta-heurística populacional, guiada por função de aptidão.
- Boa para espaços combinatórios grandes (N!).
- Estrutura alinhada ao exemplo de aula (N-Rainhas).

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
- Penalidade alta para soluções inválidas (rede de segurança).

## Slide 6 — População inicial
- **100 indivíduos** (permutações aleatórias válidas).
- Equilíbrio entre diversidade (exploração) e custo computacional.

## Slide 7 — Operadores: Seleção e Elitismo
- **Seleção por torneio** (k=2): sorteia 2, vence o de menor custo.
- Não exige fitness normalizado; pressão seletiva ajustável por k.
- **Elitismo** (2 melhores preservados): a melhor solução nunca piora.

## Slide 8 — Operadores: Cruzamento e Mutação
- **Crossover de corte simples** (taxa **0,85**).
- Problema: pode gerar permutação inválida → **reparo** (troca duplicatas por
  faltantes) **+ penalidade** como rede de segurança.
- **Mutação por troca** (taxa **0,15**): troca duas posições; preserva validade.

## Slide 9 — Ciclo e critérios de parada
- Ciclo: avaliar → (elitismo) → seleção → crossover+reparo → mutação → repetir.
- Parada: **máx. de gerações (500)** OU **estagnação (50 sem melhora)** OU **ótimo
  teórico atingido**.

## Slide 10 — Parâmetros utilizados
| Parâmetro | Valor |
|-----------|-------|
| População | 100 |
| Gerações (máx.) | 500 |
| Taxa de crossover | 0,85 |
| Taxa de mutação | 0,15 |
| Torneio (k) | 2 |
| Elitismo | 2 |
| Estagnação | 50 |

## Slide 11 — Modos de execução
- **Passo a passo:** pausa a cada geração (Enter), mostra o melhor indivíduo
  codificado e decodificado.
- **Final:** roda tudo e exibe a solução ao final.
- Ambos mostram a **evolução da heurística** (console + gráfico).
- CLI: `python main.py <arquivo> --modo passo|final`.

## Slide 12 — Resultados
- **N=4 (exemplo da quest):** custo **13** = **ótimo** (confirmado por força bruta).
- **N=10 (arquivoDeTeste1):** solução válida, custo **30** (média 3,0/dupla).
- _(inserir o gráfico `*_evolucao.png` mostrando melhor/média/pior)_

## Slide 13 — Problemas e considerações
- Corte simples quebra permutações → necessidade de **reparo** (decisão de projeto).
- Calibração de taxas: mutação alta demais vira busca aleatória; torneio grande demais
  converge cedo (ótimo local).
- Heurística simétrica foi decisiva para soluções justas entre as duas escolas.
- Estagnação evita desperdício após convergência.

## Slide 14 — Como executar / Entregáveis
- `python main.py <arquivo> --modo final|passo` (ver `DOCUMENTACAO_CODIGO.md`).
- Executável via PyInstaller (`pyinstaller --onefile --collect-all matplotlib main.py`).
- Saídas: console, `<arquivo>_saida.txt`, `<arquivo>_evolucao.png`.

## Slide 15 — Encerramento
- Domínio do problema e do AG.
- Perguntas.
