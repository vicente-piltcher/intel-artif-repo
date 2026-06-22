# T2 - Algoritmos de Busca
# Vicente Piltcher, Michele Ughini e Ghabriel Girard

# Alunos de duas escolas (A e B) devem ser distribuidos em quartos duplos
# HETEROGENEOS (um aluno de cada escola por quarto), respeitando ao maximo as
# preferencias mutuas registradas em um arquivo-texto.

# Solucao:

# Algoritmo Genetico (AG). Cada individuo e uma PERMUTACAO que representa um emparelhamento perfeito entre os alunos da escola A e os da escola B.
#  A funcao de aptidao (heuristica) e o CUSTO de insatisfacao: a soma, sobre todas as duplas, do ranking que cada aluno deu ao seu par (rank comeca em 1).
# Quanto MENOR o CUSTO --> MELHOR a solucao.

# Operadores: selecao por torneio, ORDER CROSSOVER (OX) e mutacao por troca (swap).
# Apos cada filho aplica-se uma BUSCA LOCAL (2-swap, first-improvement) que refina
# a solucao -- e isso que torna o AG e o leva ao otimo de forma confiavel.
#
# Execucao (dois modos, como pede o enunciado):
#   python main.py <arquivo> --modo passo   (pausa a cada geracao)
#   python main.py <arquivo> --modo final   (roda tudo e mostra a solucao)
# Os parametros do AG sao fixos no codigo (classe Parametros).

from __future__ import annotations

import argparse
import os
import random
import sys
from dataclasses import dataclass


# 1. LEITURA DO ARQUIVO DE ENTRADA
@dataclass
class Preferencias:
    # Armazena as preferencias lidas do arquivo e as tabelas derivadas.

    # Formato do arquivo (ver quest.txt):
    #     - Linha 1: N  (numero de duplas / alunos por escola)
    #     - proximas N linhas: alunos da Escola A
    #     - proximas N linhas: alunos da Escola B
    # Cada linha: <id> seguido de uma LISTA ORDENADA de ids do outro lado,
    # do MAIS preferido (1° posicao) ao MENOS preferido (ultima posicao).

    # Indexacao interna: todos os ids sao convertidos para base 0 (0..N-1).

    # rank_a[i][j] = posicao (0..N-1) do aluno B 'j' na lista do aluno A 'i'.
    #                0 = primeira escolha. Quanto menor, mais preferido.
    # rank_b[j][i] = posicao do aluno A 'i' na lista do aluno B 'j'.
    # custo[i][j]  = custo de insatisfacao da dupla (A_i, B_j), em base 1:
    #                (rank_a[i][j] + 1) + (rank_b[j][i] + 1).
    #                Pre-computado uma unica vez para acelerar a aptidao e a
    #                busca local (acesso O(1), sem recalcular rankings).

    n: int
    rank_a: list[list[int]]
    rank_b: list[list[int]]
    custo: list[list[int]]


def ler_arquivo(caminho: str):
    # Le o arquivo de preferencias e devolve um objeto Preferencias.
    if not os.path.isfile(caminho):
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")

    with open(caminho, "r", encoding="utf-8") as f:
        linhas = [ln.strip() for ln in f if ln.strip() != ""]

    if not linhas:
        raise ValueError("Arquivo vazio.")

    n = int(linhas[0].split()[0])

    def parse_bloco(inicio: int, nome: str):
        # rank[id_aluno][id_outro] = posicao na lista de preferencia
        rank = [[0] * n for _ in range(n)]
        for k in range(n):
            partes = linhas[inicio + k].split()
            ident = int(partes[0]) - 1          # id do aluno
            lista = [int(x) - 1 for x in partes[1:]]  # lista ordenada
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

    # Matriz de custo pre-computada (base 1) para a dupla (A_i, B_j).
    custo = [[(rank_a[i][j] + 1) + (rank_b[j][i] + 1) for j in range(n)]
             for i in range(n)]
    return Preferencias(n, rank_a, rank_b, custo)


# 2. CODIFICACAO E FUNCAO DE APTIDAO (HEURISTICA)

# Individuo: lista 'perm' de tamanho N.
#   perm[i] = id do aluno da Escola B alocado ao aluno A 'i'.
# Uma solucao valida e uma PERMUTACAO de 0..N-1 (cada B usado uma unica vez).
# Todos os operadores (Order Crossover, mutacao por swap e busca local) PRESERVAM a permutacao, entao nao ha como gerar individuo 
# invalido e a aptidao nao precisa de penalidade.


def custo_dupla(prefs: Preferencias, i: int, j: int) -> int:
    # Custo de insatisfacao da dupla (A_i, B_j) = rank_A + rank_B.
    return prefs.custo[i][j]


def aptidao(prefs: Preferencias, perm: list[int]) -> int:
    # Funcao heuristica: custo total da solucao (MENOR = melhor).

    # Soma o custo de cada dupla usando a matriz pre-computada. 
    # Como a permutacao e sempre valida, o custo e simplesmente a soma das insatisfacoes das duplas.
    return sum(prefs.custo[i][j] for i, j in enumerate(perm))


def solucao_valida(perm: list[int], n: int) -> bool:
    # Verdadeiro se 'perm' é uma permutacao de 0..N-1 (emparelhamento perfeito).
    return sorted(perm) == list(range(n))


def custo_minimo_possivel(prefs: Preferencias) -> int:
    # Limite inferior teorico (todos com sua 1a escolha mutua) = 2*N.
    # Nem sempre e atingivel, mas serve de referencia para o grafico/log.
    return 2 * prefs.n


# 3. OPERADORES DO ALGORITMO GENETICO

def individuo_aleatorio(n: int):
    # Gera um individuo valido: uma permutacao aleatoria de 0..N-1.
    perm = list(range(n))
    random.shuffle(perm)
    return perm


def inicializa_populacao(n: int, tamanho: int):
    # Cria a populacao inicial com permutacoes aleatorias validas.
    return [individuo_aleatorio(n) for _ in range(tamanho)]


def selecao_torneio(populacao: list[list[int]], fits: list[int], k: int):
    """Selecao por torneio: sorteia k individuos e devolve o de menor custo."""
    melhor = random.randrange(len(populacao))
    for _ in range(k - 1):
        desafiante = random.randrange(len(populacao))
        if fits[desafiante] < fits[melhor]:
            melhor = desafiante
    return populacao[melhor]


def _ox_filho(p1: list[int], p2: list[int], a: int, b: int, n: int):
    # Gera um filho por Order Crossover (OX) a partir do segmento p1[a:b].

    # Copia o segmento [a, b) de p1 e preenche as demais posicoes com os genes de
    # p2 (na ordem em que aparecem em p2, a partir de b), pulando os ja herdados.
    # O resultado e sempre uma permutacao valida - sem necessidade de reparo.

    filho = [-1] * n
    filho[a:b] = p1[a:b]
    usados = set(p1[a:b])
    # Genes de p2 que ainda nao estao no filho, na ordem ciclica a partir de b.
    fila = []
    for k in range(n):
        g = p2[(b + k) % n]
        if g not in usados:
            fila.append(g)
    fi = 0
    for k in range(n):
        pos = (b + k) % n
        if filho[pos] == -1:
            filho[pos] = fila[fi]
            fi += 1
    return filho


def order_crossover(pai1: list[int], pai2: list[int], taxa: float) -> tuple[list[int], list[int]]:
    # Order Crossover (OX): recombina dois pais preservando a permutacao.

    # Com probabilidade 'taxa', escolhe um segmento aleatorio e gera dois filhos
    # (um herdando o segmento de cada pai). O OX preserva tanto a posicao relativa
    # quanto a ordem dos genes, herdando estrutura real dos pais -- diferente do
    # corte simples, ele nunca produz ids repetidos e dispensa reparo. Sem
    # crossover, os filhos sao copias dos pais.
     
    n = len(pai1)
    if n <= 1 or random.random() > taxa:
        return pai1[:], pai2[:]
    a, b = sorted(random.sample(range(n + 1), 2))  # 0 <= a < b <= n
    filho1 = _ox_filho(pai1, pai2, a, b, n)
    filho2 = _ox_filho(pai2, pai1, a, b, n)
    return filho1, filho2


def mutacao(perm: list[int], taxa: float):
    # Mutacao por TROCA: com probabilidade 'taxa', troca duas posicoes.

    # A troca preserva a validade da permutacao (continua heterogenea e completa).
    # Altera 'perm' no lugar e tambem o devolve por conveniencia.
    if random.random() < taxa and len(perm) > 1:
        a, b = random.sample(range(len(perm)), 2)
        perm[a], perm[b] = perm[b], perm[a]
    return perm


def busca_local(prefs: Preferencias, perm: list[int], custo_atual: int | None = None):
    # Busca local 2-swap (first-improvement)

    # Tenta trocar pares de posicoes e aplica imediatamente qualquer troca que
    # reduza o custo, repetindo ate nenhum swap melhorar (otimo local da vizinhanca
    # 2-swap). O ganho de cada troca e avaliado por DELTA usando a matriz de custo
    # (O(1) por troca), sem recalcular o fitness inteiro.

    # Altera 'perm' no lugar e devolve (perm, custo_final).
    n = prefs.n
    custo = prefs.custo
    if custo_atual is None:
        custo_atual = aptidao(prefs, perm)
    melhorou = True
    while melhorou:
        melhorou = False
        for a in range(n - 1):
            ja = perm[a]
            for b in range(a + 1, n):
                jb = perm[b]
                delta = (custo[a][jb] + custo[b][ja]) - (custo[a][ja] + custo[b][jb])
                if delta < 0:
                    perm[a], perm[b] = jb, ja
                    custo_atual += delta
                    ja = jb            # perm[a] agora vale jb
                    melhorou = True
    return perm, custo_atual


# 4. CICLO DO ALGORITMO GENETICO
@dataclass
class Estatistica:
    # Resumo de uma geracao para log e grafico.
    geracao: int
    melhor: int
    media: float
    pior: int


@dataclass
class Parametros:
    # Agrupa os parametros do AG (com valores padrao).
    pop: int = 100
    geracoes: int = 500
    cross: float = 0.85
    mut: float = 0.15
    torneio: int = 2
    elite: int = 2
    estagnacao: int = 50

    def __post_init__(self) -> None:
        self.elite = max(1, self.elite)


def avalia_populacao(prefs: Preferencias, populacao: list[list[int]]):
    # Devolve a lista de aptidoes (custos) da populacao, na mesma ordem.
    return [aptidao(prefs, ind) for ind in populacao]


def ordena_por_aptidao(populacao: list[list[int]], fits: list[int]):
    # Devolve (populacao, fits) ordenados do MENOR custo para o MAIOR.
    pares = sorted(zip(populacao, fits), key=lambda p: p[1])
    pop_ord = [p[0] for p in pares]
    fit_ord = [p[1] for p in pares]
    return pop_ord, fit_ord


def nova_geracao(prefs: Preferencias, populacao: list[list[int]], fits: list[int], params: Parametros):
    # Gera a proxima populacao e ja devolve os fits correspondentes.

    # Espera 'populacao'/'fits' ORDENADOS por custo crescente (a elite sai dos
    # primeiros). Estrutura: elitismo + (torneio -> Order Crossover -> mutacao -> busca local). 
    # Como o custo de cada filho e obtido durante a geracao (a busca local ja o devolve), 
    # nao é preciso reavaliar a populacao depois.
    nova = [populacao[e][:] for e in range(params.elite)]
    nova_fits = [fits[e] for e in range(params.elite)]

    while len(nova) < params.pop:
        pai1 = selecao_torneio(populacao, fits, params.torneio)
        pai2 = selecao_torneio(populacao, fits, params.torneio)
        filho1, filho2 = order_crossover(pai1, pai2, params.cross)
        for filho in (filho1, filho2):
            if len(nova) >= params.pop:
                break
            mutacao(filho, params.mut)
            filho, custo = busca_local(prefs, filho)
            nova.append(filho)
            nova_fits.append(custo)
    return nova, nova_fits


def executar_ag(prefs: Preferencias, params: Parametros, modo: str, mostrar_callback=None):
    # Executa o ciclo completo do AG.
    # Retorna (melhor_individuo, melhor_custo, historico).
    # 'historico' e uma lista de Estatistica (uma por geracao).
    # 'mostrar_callback(stat, melhor_ind)' e chamado a cada geracao (log/pausa).
    # Criterios de parada: numero maximo de geracoes OU estagnacao (sem melhora
    # por 'params.estagnacao' geracoes) OU custo otimo teorico atingido.
    populacao = inicializa_populacao(prefs.n, params.pop)
    fits = avalia_populacao(prefs, populacao)
    populacao, fits = ordena_por_aptidao(populacao, fits)

    historico: list[Estatistica] = []
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

        # Evolui (nova_geracao ja devolve os fits dos filhos).
        geracao += 1
        populacao, fits = nova_geracao(prefs, populacao, fits, params)
        populacao, fits = ordena_por_aptidao(populacao, fits)

    return melhor_global, melhor_custo, historico


# 5. OUTPUT: DECODIFICACAO, LOG E ARQUIVO
def formata_estatistica(stat: Estatistica, otimo: int) -> str:
    return (f"Geracao {stat.geracao:>4} | "
            f"melhor={stat.melhor:>6} | "
            f"media={stat.media:>8.1f} | "
            f"pior={stat.pior:>6} | "
            f"otimo_teorico={otimo}")


def decodifica(prefs: Preferencias, perm: list[int]) -> list[str]:
    # Devolve uma lista de strings descrevendo cada quarto (dupla).
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


def imprime_solucao(prefs: Preferencias, perm: list[int], custo: int, destino=print):
    # Mostra a solucao CODIFICADA e DECODIFICADA, alem do custo total.
    n = prefs.n
    codificada = [j + 1 for j in perm]  # exibe em base 1
    destino("")
    destino("=" * 70)
    destino("SOLUCAO ENCONTRADA")
    destino("=" * 70)
    destino(f"Custo total (heuristica): {custo}")
    destino(f"Custo medio por dupla:    {custo / n:.3f}")
    destino(f"Custo otimo teorico (2*N): {custo_minimo_possivel(prefs)}")
    valida = solucao_valida(perm, n)
    destino(f"Solucao valida (emparelhamento perfeito): {'SIM' if valida else 'NAO'}")
    destino("")
    destino("Codificada (B alocado a cada A, na ordem A1..AN):")
    destino("  " + " ".join(str(x) for x in codificada))
    destino("")
    destino("Decodificada (duplas por quarto):")
    for ln in decodifica(prefs, perm):
        destino("  " + ln)
    destino("=" * 70)


def salva_saida(caminho: str, prefs: Preferencias, perm: list[int], custo: int, historico: list[Estatistica]):
    # Salva a solucao e o log de evolucao em um arquivo-texto.
    linhas: list[str] = []
    imprime_solucao(prefs, perm, custo, destino=linhas.append)
    linhas.append("")
    linhas.append("EVOLUCAO DA HEURISTICA (por geracao):")
    otimo = custo_minimo_possivel(prefs)
    for stat in historico:
        linhas.append("  " + formata_estatistica(stat, otimo))
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")


# 6. MODOS DE EXECUCAO
def callback_log(prefs: Preferencias):
    # Callback do modo FINAL: apenas imprime o resumo de cada geracao.
    otimo = custo_minimo_possivel(prefs)

    def _cb(stat, melhor_ind):
        print(formata_estatistica(stat, otimo))

    return _cb


def callback_passo(prefs: Preferencias):
    # Callback do modo PASSO-A-PASSO: imprime a geracao e pausa (Enter).
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


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="AG para distribuicao de alunos em quartos duplos heterogeneos.")
    p.add_argument("arquivo", help="Arquivo-texto com as preferencias.")
    p.add_argument("--modo", choices=["passo", "final"], default="final",
                   help="Modo de execucao: 'passo' (pausa por geracao) ou "
                        "'final' (roda tudo). Padrao: final.")
    return p


def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)

    try:
        prefs = ler_arquivo(args.arquivo)
    except (FileNotFoundError, ValueError) as e:
        print(f"[erro] {e}")
        return 1

    params = Parametros()  # parametros do AG fixos no codigo

    print("ALGORITMO GENETICO - DISTRIBUICAO EM QUARTOS DUPLOS")
    print(f"Arquivo: {args.arquivo}")
    print(f"N (duplas): {prefs.n}")
    print(f"Modo: {args.modo}")
    print(f"Parametros: pop={params.pop}, geracoes={params.geracoes}, "
          f"cross={params.cross}, mut={params.mut}, torneio={params.torneio}, "
          f"elite={params.elite}, estagnacao={params.estagnacao}")
    print("Evolucao da heuristica:")

    callback = callback_passo(prefs) if args.modo == "passo" else callback_log(prefs)
    melhor, custo, historico = executar_ag(prefs, params, args.modo, callback)

    imprime_solucao(prefs, melhor, custo)

    # Arquivo de saida.
    saida = os.path.splitext(args.arquivo)[0] + "_output.txt"
    salva_saida(saida, prefs, melhor, custo, historico)
    print(f"[info] Saida salva em: {saida}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
