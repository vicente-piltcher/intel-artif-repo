# Roteiro do Relatório (PPT) — T2 Olimpíada / Algoritmo Genético Memético

> **Como usar.** Cada `## Slide N — Título` é **um slide**. Estrutura de cada slide:
> **bullets** = conteúdo visível; **🖼️ Sugestão visual** = figura/diagrama recomendado;
> **🎙️ Notas do apresentador** = narração (vai nas *notas* do slide).
>
> **Cobertura da rubrica (2,0 pts):** codificação (S4), população inicial (S6), função
> heurística (S5), operadores escolhidos (S6–S8), taxas de mutação/cruzamento (S7, S8,
> S10), problemas e considerações (S13). Identificação: **Algoritmo Genético Memético**
> (AG + busca local), em **Python**, com **dois modos** de execução.

---

## Slide 1 — Capa
- **T2 – Algoritmos de Busca: Olimpíada**
- Alocação de alunos em **quartos duplos heterogêneos** por **Algoritmo Genético Memético**
- Inteligência Artificial — Profa. Silvia Moraes — PUCRS
- Integrantes: **Vicente Piltcher, Michele Ughini e Ghabriel Girard**

🎙️ **Notas:** Resumo em uma frase: "alocar alunos de duas escolas em quartos de dois (um
de cada), respeitando ao máximo as preferências, com um AG reforçado por busca local".
Antecipe a estrutura: problema → modelagem → operadores → ciclo → resultados.

## Slide 2 — O problema e sua natureza
- Alunos de **duas escolas (A e B)**, mesmo tamanho **N**, em **quartos duplos
  heterogêneos** (exatamente um de cada escola por quarto).
- Cada aluno respondeu um questionário → **lista ordenada de preferência** sobre a outra
  escola (do mais ao menos preferido).
- **Objetivo:** emparelhamento que **maximiza a satisfação mútua**; **restrições:** todos
  alojados, nenhum quarto com dois da mesma escola.
- **Natureza:** problema de **atribuição (assignment)**, parente do **Casamento Estável**
  (Gale–Shapley); espaço de busca = **N!** (N=10 → **3.628.800**) → exaustivo inviável.

🖼️ **Sugestão visual:** duas colunas (A/B) ligadas por linhas formando duplas + curva de N!.

🎙️ **Notas:** Contextualize com a olimpíada do enunciado. "Satisfação" = posição que cada
um deu ao par. Como o nº de soluções explode fatorialmente, usamos uma busca *informada*
(heurística), não força bruta — exceto para validar instâncias pequenas.

## Slide 3 — Por que AG memético + visão geral (pipeline)
- **AG:** meta-heurística **populacional** inspirada na evolução (evolui um conjunto de
  soluções, combinando-as por gerações). Escolha permitida pelo enunciado (AG ou SA).
- **Memético = AG + busca local:** combina **exploração** (AG) com **intensificação**
  (busca local) → convergência **rápida e confiável** ao ótimo.
- **Pipeline:** ① ler arquivo → ② população inicial → ③ *ciclo por geração* (avaliar →
  elitismo → seleção → cruzamento → mutação → busca local → ordenar) → ④ parada → ⑤ saída.

🖼️ **Sugestão visual:** fluxograma do pipeline ①→⑤ (peça central da apresentação).

🎙️ **Notas:** Defina memético sem jargão: "o AG procura amplo; a busca local aprofunda".
Use este slide como mapa: os próximos abrem cada etapa do ciclo.

## Slide 4 — Entrada e Codificação  *(rubrica: leitura da entrada + codificação)*
- **Formato da entrada:** linha 1 = `N`; próximas **N** linhas = Escola A; próximas **N** =
  Escola B. Cada linha: `id` + lista ordenada de ids do outro lado (mais→menos preferido).
  A leitura **valida** que cada lista é uma permutação de `1..N` (e trata linhas em branco).
- **Codificação (cromossomo):** indivíduo = **permutação** `perm`, onde `perm[i]` = aluno
  **B** alocado ao aluno **A i**. Toda permutação de `0..N-1` é **automaticamente** um
  emparelhamento perfeito e heterogêneo (cada B usado exatamente uma vez).
- **Exemplo:** `4 2 1 3` → A1–B4, A2–B2, A3–B1, A4–B3.

🖼️ **Sugestão visual:** trecho real do arquivo (`caso1.txt`) + vetor `[4 2 1 3]` com setas.

🎙️ **Notas:** O programa recebe o arquivo por argumento (`args`), como exige o enunciado.
A permutação evita soluções inválidas (dois A no mesmo B / B sem par) — diferente de um
vetor livre, que exigiria reparo. Internamente os ids são base 0 (Python indexa do 0) e
exibidos em base 1; é só índice, não muda o modelo.

## Slide 5 — Função heurística / aptidão  *(rubrica: função heurística)*
- **Custo de insatisfação a MINIMIZAR:**
  `custo(perm) = Σ_i [ rankA(i, perm[i]) + 1 ] + [ rankB(perm[i], i) + 1 ]`
- `rankA`/`rankB` = posição do par na lista (0 = 1ª escolha; o `+1` deixa em base 1).
- **Mínimo por dupla = 2** (1ª escolha mútua); **ótimo teórico global = 2·N**.
- **Exemplo (`caso1`):** A1–B4 = 3+1 = **4**; A2–B2 = 1+2 = **3**; A3–B1 = 2+1 = **3**;
  A4–B3 = 1+2 = **3** → solução `4 2 1 3` custa **13** (média 3,25/dupla).
- **Propriedades:** **simétrica** (pondera A e B), **independe de N** (*scale-free*),
  **monotônica** (melhorar uma dupla nunca piora o total).

🖼️ **Sugestão visual:** tabela das 4 duplas (rankA, rankB, custo) somando 13.

🎙️ **Notas:** É a peça "fundamental" do AG (enunciado). Otimização: **matriz de custo
pré-computada** `custo[i][j] = (rankA+1)+(rankB+1)` calculada 1× na leitura → avaliação
**O(N)** e *delta* da busca local **O(1)**. Como todos os operadores preservam a
permutação, **não há termo de penalidade** — a aptidão é só a soma dos custos.

## Slide 6 — População, Seleção e Elitismo  *(rubrica: população + operadores)*
- **População inicial: 100** permutações **aleatórias válidas** (`random.shuffle`) —
  equilíbrio entre diversidade/exploração e custo computacional.
- **Seleção por torneio (k=2):** sorteia 2 indivíduos, vence o de **menor custo**. Define a
  **pressão seletiva** (k maior = mais elitista); não exige fitness normalizado.
- **Elitismo (2):** os 2 melhores passam **intactos** para a próxima geração → a melhor
  solução **nunca piora** ao longo das gerações.

🖼️ **Sugestão visual:** grade de cromossomos (diversidade) + 2 elites destacados + torneio.

🎙️ **Notas:** O AG evolui um *conjunto*, não uma única solução. Torneio dá vantagem aos
bons sem matar a diversidade cedo; elitismo é a rede de segurança. É a estratégia do
exemplo de aula (N-Rainhas).

## Slide 7 — Cruzamento: Order Crossover (OX)  *(rubrica: cruzamento, taxa)*
- **Taxa de cruzamento = 0,85** (com prob. 0,15 os filhos são cópias dos pais).
- **OX (operador clássico para permutações):** ① o filho **herda um segmento contíguo**
  `[a,b)` de um pai; ② completa as demais posições com os genes do **outro pai**, na
  **ordem em que aparecem** (ciclicamente, a partir de `b`), pulando os já herdados.
- **Preserva a permutação por construção** → nunca repete ids, **dispensa reparo**.
- **Exemplo:** `p1=[1 2 3 4 5 6]`, `p2=[4 1 5 2 6 3]`, segmento `[2,5)` → herda
  `_ _ 3 4 5 _`, completa com `1 2 6` → **`2 6 3 4 5 1`** (gera 2 filhos por casal).

🖼️ **Sugestão visual:** três linhas mostrando os passos ①→② do OX, com cor no segmento.

🎙️ **Notas:** Cruzamento é o principal mecanismo de **exploração** (combina dois pais). OX
herda a *ordem relativa* do segundo pai sem repetir ninguém — melhor que o "corte
simples", que quebrava a permutação e exigia reparo destrutivo.

## Slide 8 — Mutação e Busca local (memético)  *(rubrica: mutação, taxa)*
- **Mutação por troca (swap), taxa 0,15:** troca duas posições da permutação; **preserva a
  validade**; mantém **diversidade** e ajuda a escapar de ótimos locais.
- **Busca local 2-swap (first-improvement):** após cada filho, testa trocar pares de
  posições e **aplica imediatamente** qualquer troca que reduza o custo, até nenhum swap
  melhorar (**ótimo local** da vizinhança 2-swap).
- **Delta O(1)** (não recalcula o fitness inteiro):
  `delta = (custo[a][jb] + custo[b][ja]) − (custo[a][ja] + custo[b][jb])`.
- É o que **leva o AG ao ótimo de forma confiável** (componente memético).

🖼️ **Sugestão visual:** vetor com duas posições trocando + curva de custo "descendo a ladeira".

🎙️ **Notas:** Metáfora: cruzamento/mutação dão um "rascunho"; a busca local "lapida" esse
rascunho descendo a ladeira do custo. O delta torna isso barato — por isso é viável
aplicar a todos os filhos.

## Slide 9 — Ciclo do AG e critérios de parada
- **Ciclo (por geração):** avaliar população → **elitismo** → **seleção (torneio)** →
  **cruzamento (OX)** → **mutação (swap)** → **busca local** → ordenar por custo → repetir.
- **Critérios de parada (o que ocorrer primeiro):**
  ① **ótimo teórico** atingido (custo ≤ **2·N**); ② **máximo de gerações = 500**;
  ③ **estagnação = 50** gerações sem melhora do melhor custo.
- O **melhor global** é guardado a cada geração (nunca se perde).

🖼️ **Sugestão visual:** fluxograma do ciclo com os 3 critérios de parada destacados.

🎙️ **Notas:** Os critérios evitam desperdício: se já achamos o ótimo ou a busca estagnou,
encerramos. A cada geração registramos melhor/média/pior para acompanhar a evolução.

## Slide 10 — Parâmetros utilizados  *(rubrica: taxas)*
| Parâmetro | Valor | Efeito de aumentar / justificativa |
|-----------|-------|------------------------------------|
| População | 100 | mais diversidade/exploração; mais custo por geração |
| Gerações (máx.) | 500 | mais refino; risco de desperdício |
| Crossover (OX) | 0,85 | mais recombinação (exploração) |
| Mutação (swap) | 0,15 | mais diversidade; alta demais ≈ aleatório |
| Torneio (k) | 2 | mais pressão seletiva (converge mais rápido) |
| Elitismo | 2 | mais estabilidade; alto demais reduz diversidade |
| Estagnação | 50 | parar após convergir |
| Busca local | ligada | intensificação (memético) |

> Parâmetros **fixos no código** (classe `Parametros`). A execução só recebe o **arquivo**
> e o **`--modo`** — interface enxuta, focada nos dois modos exigidos.

🎙️ **Notas:** A definição dos parâmetros é parte importante da nota. Foram escolhidos para
equilibrar **exploração** (população/crossover/mutação) e **intensificação**
(torneio/elitismo/busca local), e validados empiricamente nos arquivos de teste.

## Slide 11 — Modos de execução e saída  *(rubrica: execução)*
- **Passo a passo (`--modo passo`):** pausa a cada geração (Enter) e mostra o melhor
  indivíduo **codificado** e **decodificado**.
- **Final (`--modo final`):** roda tudo e exibe a solução ao final.
- Ambos imprimem a **evolução da heurística** (melhor/média/pior por geração).
- **Saída decodificada (exemplo):**
  `Quarto 1: A1 <-> B4 (A escolheu B como 3a opcao; B escolheu A como 1a opcao; custo=4)`
- Persistência: console **+** arquivo **`<arquivo>_output.txt`** (solução + log completo).

🖼️ **Sugestão visual:** dois screenshots — modo passo (pausa) e modo final (corrido).

🎙️ **Notas:** Os dois modos atendem exatamente ao enunciado. Mostramos a solução
**codificada** (a permutação) e **decodificada** (quartos com rankings e custo), além de
custo total, custo médio, ótimo teórico e verificação de validade. Demo ao vivo, se der.

## Slide 12 — Resultados e impacto do memético
- **N=4 (`caso1.txt`):** custo **13** = **ótimo** (confirmado por força bruta nas 24
  permutações) → solução `4 2 1 3`.
- **N=10 (`caso2.txt`):** solução válida, custo **30** (média **3,0**/dupla); ótimo teórico
  20 **não atingível** (preferências conflitantes) — 30 é a melhor solução real.
- **AG puro × memético:** sem busca local, o AG "puro" **estaciona em custos piores** nas
  mesmas gerações → a busca local é **decisiva**.

🖼️ **Sugestão visual:** duas curvas de evolução sobrepostas (puro × memético) + tabela das
primeiras gerações mostrando a queda do custo.

🎙️ **Notas:** Atingimos o ótimo em N=4 e a melhor solução conhecida em N=10, com
convergência rápida. O slide demonstra *por que* a melhoria importa (decisão baseada em
evidência).

## Slide 13 — Problemas e considerações  *(rubrica: problemas e considerações)*
- **Cruzamento:** corte simples quebrava permutações (exigia reparo + penalidade) →
  migramos para **Order Crossover**, que preserva validade e herda mais estrutura.
- **Penalidade removida:** com OX + swap + busca local, soluções são **sempre válidas**.
- **Calibração de taxas:** mutação alta demais vira busca aleatória; torneio grande demais
  converge cedo (ótimo local).
- **Heurística simétrica** foi decisiva para soluções **justas** entre as duas escolas.
- **Estagnação** evita desperdício após a convergência; **matriz de custo** garante
  eficiência (avaliação O(N), delta O(1)).

🎙️ **Notas:** Houve iteração de projeto: começamos com uma abordagem mais simples e
evoluímos para uma melhor, justificando cada decisão. Esse é o tipo de reflexão que a
rubrica valoriza.

## Slide 14 — Conclusão e entregáveis
- Modelamos como **atribuição** e resolvemos com **AG memético**: **permutação** (sempre
  válida) + **heurística simétrica** + **operadores** (torneio, elitismo, OX, swap) +
  **busca local** → soluções **ótimas/quase-ótimas** com convergência rápida.
- **Como rodar:** `python main.py <arquivo> --modo final|passo`.
- **Executável (standalone, sem dependências):** `python -m PyInstaller --onefile main.py`
  → `dist/main.exe`.
- **Testes:** `pytest test_main.py` (6 testes: leitura, aptidão, validade do OX,
  monotonicidade da busca local, ótimo de `caso1`, erro de arquivo).
- **Saídas:** console + `<arquivo>_output.txt`.

🎙️ **Notas:** Feche reforçando o domínio do problema e do algoritmo: cada peça tem razão
de existir e os resultados comprovam a abordagem. Entregáveis: fonte, executável, arquivos
de saída e este relatório.

## Slide 15 — Encerramento
- **Obrigado!**
- Domínio do problema e do **AG memético**.
- **Perguntas?**

🎙️ **Notas:** Convide perguntas; esteja pronto para abrir o `main.py` (6 seções
comentadas) ou rodar uma demonstração ao vivo. **Glossário de apoio:**
indivíduo/cromossomo = solução (permutação); gene = `perm[i]`; população = conjunto de uma
geração; aptidão = custo (a minimizar); memético = AG + busca local; ótimo local/global =
melhor numa vizinhança / em todo o espaço.
