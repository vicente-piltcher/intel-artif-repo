# -*- coding: utf-8 -*-
"""
T2 - Algoritmos de Busca: Olimpiada (PUCRS - Inteligencia Artificial)
=====================================================================

Problema
--------
Alunos de duas escolas (A e B) devem ser distribuidos em quartos duplos
HETEROGENEOS (um aluno de cada escola por quarto), respeitando ao maximo as
preferencias mutuas registradas em um arquivo-texto.

Solucao
-------
Algoritmo Genetico (AG). Cada individuo e uma PERMUTACAO que representa um
emparelhamento perfeito entre os alunos da escola A e os da escola B. A funcao
de aptidao (heuristica) e o CUSTO de insatisfacao: a soma, sobre todas as
duplas, do ranking que cada aluno deu ao seu par (rank comeca em 1). Quanto
MENOR o custo, melhor a solucao.

Execucao
--------
    python main.py <arquivo> --modo final
    python main.py <arquivo> --modo passo

Parametros opcionais: --pop, --geracoes, --cross, --mut, --torneio,
--elite, --estagnacao, --seed, --sem-grafico, --saida.

Autor: gerado para o trabalho T2.
"""

import argparse
import os
import random
import sys


# ---------------------------------------------------------------------------
# 1. LEITURA DO ARQUIVO DE ENTRADA
# ---------------------------------------------------------------------------
class Preferencias:
    """Armazena as preferencias lidas do arquivo e as tabelas de ranking.

    Formato do arquivo (ver quest.txt):
        - 1a linha: N  (numero de duplas / alunos por escola)
        - proximas N linhas: alunos da Escola A
        - proximas N linhas: alunos da Escola B
      Cada linha: <id> seguido de uma LISTA ORDENADA de ids do outro lado,
      do MAIS preferido (1a posicao) ao MENOS preferido (ultima posicao).

    Indexacao interna: todos os ids sao convertidos para base 0 (0..N-1).

    rank_a[i][j] = posicao (0..N-1) do aluno B 'j' na lista do aluno A 'i'.
                   0 = primeira escolha. Quanto menor, mais preferido.
    rank_b[j][i] = posicao do aluno A 'i' na lista do aluno B 'j'.
    """

    def __init__(self, n, rank_a, rank_b):
        self.n = n
        self.rank_a = rank_a
        self.rank_b = rank_b


def ler_arquivo(caminho):
    """Le o arquivo de preferencias e devolve um objeto Preferencias.

    Tolera linhas em branco e espacos extras. Valida que cada lista e uma
    permutacao de 1..N (cada aluno do outro lado aparece exatamente uma vez).
    """
    if not os.path.isfile(caminho):
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")

    with open(caminho, "r", encoding="utf-8") as f:
        linhas = [ln.strip() for ln in f if ln.strip() != ""]

    if not linhas:
        raise ValueError("Arquivo vazio.")

    n = int(linhas[0].split()[0])
    esperado = 1 + 2 * n
    if len(linhas) < esperado:
        raise ValueError(
            f"Arquivo incompleto: esperadas {esperado} linhas uteis "
            f"(1 + 2*{n}), encontradas {len(linhas)}."
        )

    def parse_bloco(inicio, nome):
        # rank[id_aluno][id_outro] = posicao na lista de preferencia
        rank = [[0] * n for _ in range(n)]
        for k in range(n):
            partes = linhas[inicio + k].split()
            ident = int(partes[0]) - 1          # id do aluno (base 0)
            lista = [int(x) - 1 for x in partes[1:]]  # lista ordenada (base 0)
            if ident < 0 or ident >= n:
                raise ValueError(f"Escola {nome}: id de aluno invalido na linha "
                                 f"'{linhas[inicio + k]}'.")
            if sorted(lista) != list(range(n)):
                raise ValueError(
                    f"Escola {nome}, aluno {ident + 1}: a lista de preferencias "
                    f"nao e uma permutacao de 1..{n}: {[x + 1 for x in lista]}"
                )
            for posicao, outro in enumerate(lista):
                rank[ident][outro] = posicao
        return rank

    rank_a = parse_bloco(1, "A")
    rank_b = parse_bloco(1 + n, "B")
    return Preferencias(n, rank_a, rank_b)


# ---------------------------------------------------------------------------
# 2. CODIFICACAO E FUNCAO DE APTIDAO (HEURISTICA)
# ---------------------------------------------------------------------------
# Individuo: lista 'perm' de tamanho N.
#   perm[i] = id (base 0) do aluno da Escola B alocado ao aluno A 'i'.
# Uma solucao valida e uma PERMUTACAO de 0..N-1 (cada B usado uma unica vez).

# Penalidade aplicada por id de B repetido/faltante (rede de seguranca, caso
# algum operador gere individuo invalido). O reparo deve evitar que isso ocorra.
PENALIDADE_POR_CONFLITO = 1000


def custo_dupla(prefs, i, j):
    """Custo de insatisfacao da dupla (A_i, B_j) = rank_A + rank_B (base 1)."""
    return (prefs.rank_a[i][j] + 1) + (prefs.rank_b[j][i] + 1)


def aptidao(prefs, perm):
    """Funcao heuristica: custo total da solucao (MENOR = melhor).

    custo = soma dos custos das duplas + penalidade por eventuais conflitos
    (B repetido). Para uma permutacao valida nao ha conflitos.
    """
    total = 0
    vistos = [0] * prefs.n
    conflitos = 0
    for i, j in enumerate(perm):
        total += custo_dupla(prefs, i, j)
        vistos[j] += 1
    for c in vistos:
        if c != 1:
            conflitos += abs(c - 1)
    return total + conflitos * PENALIDADE_POR_CONFLITO


def custo_minimo_possivel(prefs):
    """Limite inferior teorico (todos com sua 1a escolha mutua) = 2*N.
    Nem sempre e atingivel, mas serve de referencia para o grafico/log."""
    return 2 * prefs.n


# ---------------------------------------------------------------------------
# 3. OPERADORES DO ALGORITMO GENETICO
# ---------------------------------------------------------------------------
def individuo_aleatorio(n):
    """Gera um individuo valido: uma permutacao aleatoria de 0..N-1."""
    perm = list(range(n))
    random.shuffle(perm)
    return perm


def inicializa_populacao(n, tamanho):
    """Cria a populacao inicial com permutacoes aleatorias validas."""
    return [individuo_aleatorio(n) for _ in range(tamanho)]


def selecao_torneio(populacao, fits, k):
    """Selecao por torneio: sorteia k individuos e devolve o de menor custo."""
    melhor = random.randrange(len(populacao))
    for _ in range(k - 1):
        desafiante = random.randrange(len(populacao))
        if fits[desafiante] < fits[melhor]:
            melhor = desafiante
    return populacao[melhor]


def reparar(perm, n):
    """Restaura a validade de uma permutacao apos o crossover de corte simples.

    Troca valores duplicados pelos valores faltantes, preservando ao maximo a
    ordem original (estrategia classica de reparo para representacao por
    permutacao). Devolve uma permutacao valida de 0..N-1.
    """
    vistos = [False] * n
    faltantes = []
    # Marca a primeira ocorrencia de cada valor; duplicatas viram -1 (buraco).
    saida = []
    for v in perm:
        if 0 <= v < n and not vistos[v]:
            vistos[v] = True
            saida.append(v)
        else:
            saida.append(-1)  # duplicata ou valor fora da faixa
    faltantes = [v for v in range(n) if not vistos[v]]
    random.shuffle(faltantes)
    it = iter(faltantes)
    for idx in range(n):
        if saida[idx] == -1:
            saida[idx] = next(it)
    return saida


def crossover(pai1, pai2, n, taxa):
    """Crossover de CORTE SIMPLES seguido de REPARO.

    Com probabilidade 'taxa', escolhe um ponto de corte e combina o inicio de
    um pai com o fim do outro. Como isso pode gerar ids repetidos, aplica-se
    reparar() para garantir permutacoes validas. Sem crossover, os filhos sao
    copias dos pais.
    """
    if random.random() > taxa:
        return pai1[:], pai2[:]
    ponto = random.randint(1, n - 1) if n > 1 else 1
    filho1 = pai1[:ponto] + pai2[ponto:]
    filho2 = pai2[:ponto] + pai1[ponto:]
    return reparar(filho1, n), reparar(filho2, n)


def mutacao(perm, taxa):
    """Mutacao por TROCA: com probabilidade 'taxa', troca duas posicoes.

    A troca preserva a validade da permutacao (continua heterogenea e completa).
    """
    if random.random() < taxa and len(perm) > 1:
        a, b = random.sample(range(len(perm)), 2)
        perm[a], perm[b] = perm[b], perm[a]
    return perm


# ---------------------------------------------------------------------------
# 4. CICLO DO ALGORITMO GENETICO
# ---------------------------------------------------------------------------
class Estatistica:
    """Resumo de uma geracao para log e grafico."""

    def __init__(self, geracao, melhor, media, pior):
        self.geracao = geracao
        self.melhor = melhor
        self.media = media
        self.pior = pior


def avalia_populacao(prefs, populacao):
    """Devolve a lista de aptidoes (custos) da populacao, na mesma ordem."""
    return [aptidao(prefs, ind) for ind in populacao]


def ordena_por_aptidao(populacao, fits):
    """Devolve (populacao, fits) ordenados do MENOR custo para o MAIOR."""
    pares = sorted(zip(populacao, fits), key=lambda p: p[1])
    pop_ord = [p[0] for p in pares]
    fit_ord = [p[1] for p in pares]
    return pop_ord, fit_ord


def nova_geracao(prefs, populacao, fits, params):
    """Gera a proxima populacao: elitismo + (torneio -> crossover -> mutacao)."""
    n = prefs.n
    nova = []

    # Elitismo: mantem os 'elite' melhores individuos intactos.
    pop_ord, _ = ordena_por_aptidao(populacao, fits)
    for e in range(params.elite):
        nova.append(pop_ord[e][:])

    # Preenche o resto reproduzindo a partir de pais selecionados por torneio.
    while len(nova) < params.pop:
        pai1 = selecao_torneio(populacao, fits, params.torneio)
        pai2 = selecao_torneio(populacao, fits, params.torneio)
        filho1, filho2 = crossover(pai1, pai2, n, params.cross)
        filho1 = mutacao(filho1, params.mut)
        filho2 = mutacao(filho2, params.mut)
        nova.append(filho1)
        if len(nova) < params.pop:
            nova.append(filho2)
    return nova


class Parametros:
    """Agrupa os parametros do AG (com valores padrao sensatos)."""

    def __init__(self, pop=100, geracoes=500, cross=0.85, mut=0.15,
                 torneio=2, elite=2, estagnacao=50):
        self.pop = pop
        self.geracoes = geracoes
        self.cross = cross
        self.mut = mut
        self.torneio = torneio
        self.elite = max(1, elite)
        self.estagnacao = estagnacao


def executar_ag(prefs, params, modo, mostrar_callback=None):
    """Executa o ciclo completo do AG.

    Retorna (melhor_individuo, melhor_custo, historico).
    'historico' e uma lista de Estatistica (uma por geracao).
    'mostrar_callback(stat, melhor_ind)' e chamado a cada geracao (log/pausa).
    Criterios de parada: numero maximo de geracoes OU estagnacao (sem melhora
    por 'params.estagnacao' geracoes) OU custo otimo teorico atingido.
    """
    populacao = inicializa_populacao(prefs.n, params.pop)
    fits = avalia_populacao(prefs, populacao)
    populacao, fits = ordena_por_aptidao(populacao, fits)

    historico = []
    melhor_global = populacao[0][:]
    melhor_custo = fits[0]
    geracoes_sem_melhora = 0
    otimo = custo_minimo_possivel(prefs)

    geracao = 1
    while True:
        media = sum(fits) / len(fits)
        stat = Estatistica(geracao, fits[0], media, fits[-1])
        historico.append(stat)
        if mostrar_callback is not None:
            mostrar_callback(stat, populacao[0])

        # Atualiza melhor global e contador de estagnacao.
        if fits[0] < melhor_custo:
            melhor_custo = fits[0]
            melhor_global = populacao[0][:]
            geracoes_sem_melhora = 0
        else:
            geracoes_sem_melhora += 1

        # Criterios de parada.
        if melhor_custo <= otimo:
            break
        if geracao >= params.geracoes:
            break
        if geracoes_sem_melhora >= params.estagnacao:
            break

        # Evolui.
        geracao += 1
        populacao = nova_geracao(prefs, populacao, fits, params)
        fits = avalia_populacao(prefs, populacao)
        populacao, fits = ordena_por_aptidao(populacao, fits)

    return melhor_global, melhor_custo, historico


# ---------------------------------------------------------------------------
# 5. SAIDA: DECODIFICACAO, LOG, GRAFICO E ARQUIVO
# ---------------------------------------------------------------------------
def formata_estatistica(stat, otimo):
    return (f"Geracao {stat.geracao:>4} | "
            f"melhor={stat.melhor:>6} | "
            f"media={stat.media:>8.1f} | "
            f"pior={stat.pior:>6} | "
            f"otimo_teorico={otimo}")


def decodifica(prefs, perm):
    """Devolve uma lista de strings descrevendo cada quarto (dupla)."""
    linhas = []
    for i, j in enumerate(perm):
        ra = prefs.rank_a[i][j] + 1   # ranking que A_i deu a B_j (base 1)
        rb = prefs.rank_b[j][i] + 1   # ranking que B_j deu a A_i (base 1)
        c = custo_dupla(prefs, i, j)
        linhas.append(
            f"Quarto {i + 1:>3}: A{i + 1} <-> B{j + 1}  "
            f"(A escolheu B como {ra}a opcao; B escolheu A como {rb}a opcao; "
            f"custo={c})"
        )
    return linhas


def imprime_solucao(prefs, perm, custo, destino=print):
    """Mostra a solucao CODIFICADA e DECODIFICADA, alem do custo total."""
    n = prefs.n
    codificada = [j + 1 for j in perm]  # exibe em base 1
    destino("")
    destino("=" * 70)
    destino("SOLUCAO ENCONTRADA")
    destino("=" * 70)
    destino(f"Custo total (heuristica): {custo}")
    destino(f"Custo medio por dupla:    {custo / n:.3f}")
    destino(f"Custo otimo teorico (2*N): {custo_minimo_possivel(prefs)}")
    valida = sorted(perm) == list(range(n))
    destino(f"Solucao valida (emparelhamento perfeito): {'SIM' if valida else 'NAO'}")
    destino("")
    destino("Codificada (B alocado a cada A, na ordem A1..AN):")
    destino("  " + " ".join(str(x) for x in codificada))
    destino("")
    destino("Decodificada (duplas por quarto):")
    for ln in decodifica(prefs, perm):
        destino("  " + ln)
    destino("=" * 70)


def salva_saida(caminho, prefs, perm, custo, historico):
    """Salva a solucao e o log de evolucao em um arquivo-texto."""
    linhas = []
    imprime_solucao(prefs, perm, custo, destino=linhas.append)
    linhas.append("")
    linhas.append("EVOLUCAO DA HEURISTICA (por geracao):")
    otimo = custo_minimo_possivel(prefs)
    for stat in historico:
        linhas.append("  " + formata_estatistica(stat, otimo))
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")


def gera_grafico(historico, caminho_png, mostrar=True):
    """Plota a evolucao (melhor/media/pior) com matplotlib. Salva em PNG.

    Falha de forma graciosa caso matplotlib nao esteja instalado.
    """
    try:
        import matplotlib
        if not mostrar:
            matplotlib.use("Agg")  # backend sem janela
        import matplotlib.pyplot as plt
    except Exception as e:  # pragma: no cover
        print(f"[aviso] matplotlib indisponivel, grafico nao gerado ({e}).")
        return

    geracoes = [s.geracao for s in historico]
    melhor = [s.melhor for s in historico]
    media = [s.media for s in historico]
    pior = [s.pior for s in historico]

    plt.figure(figsize=(10, 6))
    plt.plot(geracoes, pior, label="Pior", color="#d62728", linewidth=1)
    plt.plot(geracoes, media, label="Media", color="#ff7f0e", linewidth=1.5)
    plt.plot(geracoes, melhor, label="Melhor", color="#2ca02c", linewidth=2)
    plt.title("Evolucao da funcao heuristica (custo) ao longo das geracoes")
    plt.xlabel("Geracao")
    plt.ylabel("Custo (menor = melhor)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    try:
        plt.savefig(caminho_png, dpi=120)
        print(f"[info] Grafico salvo em: {caminho_png}")
    except Exception as e:  # pragma: no cover
        print(f"[aviso] nao foi possivel salvar o grafico ({e}).")
    if mostrar:
        try:
            plt.show()
        except Exception:
            pass
    plt.close()


# ---------------------------------------------------------------------------
# 6. MODOS DE EXECUCAO E CLI
# ---------------------------------------------------------------------------
def callback_log(prefs):
    """Callback do modo FINAL: apenas imprime o resumo de cada geracao."""
    otimo = custo_minimo_possivel(prefs)

    def _cb(stat, melhor_ind):
        print(formata_estatistica(stat, otimo))

    return _cb


def callback_passo(prefs):
    """Callback do modo PASSO-A-PASSO: imprime a geracao e pausa (Enter)."""
    otimo = custo_minimo_possivel(prefs)

    def _cb(stat, melhor_ind):
        print(formata_estatistica(stat, otimo))
        codificada = " ".join(str(j + 1) for j in melhor_ind)
        print(f"   melhor individuo (codificado): {codificada}")
        for ln in decodifica(prefs, melhor_ind):
            print("      " + ln)
        try:
            input("   [Enter] proxima geracao... ")
        except EOFError:
            pass

    return _cb


def construir_parser():
    p = argparse.ArgumentParser(
        description="T2 - AG para distribuicao de alunos em quartos duplos "
                    "heterogeneos (Olimpiada).")
    p.add_argument("arquivo", help="Arquivo-texto com as preferencias.")
    p.add_argument("--modo", choices=["passo", "final"], default="final",
                   help="Modo de execucao: 'passo' (pausa por geracao) ou "
                        "'final' (roda tudo). Padrao: final.")
    p.add_argument("--pop", type=int, default=100, help="Tamanho da populacao.")
    p.add_argument("--geracoes", type=int, default=500,
                   help="Numero maximo de geracoes.")
    p.add_argument("--cross", type=float, default=0.85, help="Taxa de crossover.")
    p.add_argument("--mut", type=float, default=0.15, help="Taxa de mutacao.")
    p.add_argument("--torneio", type=int, default=2,
                   help="Tamanho do torneio de selecao.")
    p.add_argument("--elite", type=int, default=2,
                   help="Quantidade de individuos preservados por elitismo.")
    p.add_argument("--estagnacao", type=int, default=50,
                   help="Parada por estagnacao (geracoes sem melhora).")
    p.add_argument("--seed", type=int, default=None,
                   help="Semente aleatoria (reprodutibilidade).")
    p.add_argument("--sem-grafico", action="store_true",
                   help="Nao exibir/gerar o grafico matplotlib.")
    p.add_argument("--saida", default=None,
                   help="Arquivo-texto de saida (padrao: <arquivo>_saida.txt).")
    return p


def main(argv=None):
    args = construir_parser().parse_args(argv)

    if args.seed is not None:
        random.seed(args.seed)

    try:
        prefs = ler_arquivo(args.arquivo)
    except (FileNotFoundError, ValueError) as e:
        print(f"[erro] {e}")
        return 1

    params = Parametros(
        pop=args.pop, geracoes=args.geracoes, cross=args.cross, mut=args.mut,
        torneio=args.torneio, elite=args.elite, estagnacao=args.estagnacao,
    )

    print("=" * 70)
    print("T2 - ALGORITMO GENETICO - DISTRIBUICAO EM QUARTOS DUPLOS")
    print("=" * 70)
    print(f"Arquivo: {args.arquivo}")
    print(f"N (duplas): {prefs.n}")
    print(f"Modo: {args.modo}")
    print(f"Parametros: pop={params.pop}, geracoes={params.geracoes}, "
          f"cross={params.cross}, mut={params.mut}, torneio={params.torneio}, "
          f"elite={params.elite}, estagnacao={params.estagnacao}")
    print("-" * 70)
    print("Evolucao da heuristica:")

    callback = callback_passo(prefs) if args.modo == "passo" else callback_log(prefs)
    melhor, custo, historico = executar_ag(prefs, params, args.modo, callback)

    imprime_solucao(prefs, melhor, custo)

    # Arquivo de saida.
    saida = args.saida or (os.path.splitext(args.arquivo)[0] + "_saida.txt")
    salva_saida(saida, prefs, melhor, custo, historico)
    print(f"[info] Saida salva em: {saida}")

    # Grafico.
    if not args.sem_grafico:
        png = os.path.splitext(args.arquivo)[0] + "_evolucao.png"
        gera_grafico(historico, png, mostrar=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
