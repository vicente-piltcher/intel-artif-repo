# Implementação do Simulated Annealing
# Distribuição de cargas entre 3 pessoas (porte em Python de DDC_AT10.java)

# Codificação: distribuicao[i] in {0, 1, 2}
# Heurística : range (max − min) das somas das 3 pessoas
# Vizinho    : realoca uma carga para uma das outras 2 pessoas

# Grupo: Vicente Piltcher Diehl, Ghabriel Molina Girard e Michele Ughini Trindade;

import math
import random

NUM_PESSOAS = 3

cargas = [
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    50, 24, 26,
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
    50, 24, 26, 100, 51, 49,
]


def print_solucao(v, h):
    print(" ".join(str(x) for x in v) + " - h: " + str(h))


def heuristica(s):
    somas = [0] * NUM_PESSOAS
    for j in range(len(cargas)):
        somas[s[j]] += cargas[j]
    return max(somas) - min(somas)


def gera_vizinho(distribuicao):
    vizinha = distribuicao[:]
    pos = random.randint(0, len(vizinha) - 1)
    atual = vizinha[pos]
    novo = random.randint(0, NUM_PESSOAS - 1)
    while novo == atual:
        novo = random.randint(0, NUM_PESSOAS - 1)
    vizinha[pos] = novo
    return vizinha


def executa_simulated_annealing():
    distribuicao = [random.randint(0, NUM_PESSOAS - 1) for _ in range(len(cargas))]

    T = 1000.0
    iteracoes = 1000

    print("Simulated Annealing - Distribuição entre " + str(NUM_PESSOAS) + " pessoas")

    for t in range(1, iteracoes + 1):
        valor_atual = heuristica(distribuicao)
        print("Ciclo: " + str(t) + "- Temperatura: " + str(T) + " -" +
              "Solução Atual - h=" + str(valor_atual))
        if valor_atual == 0:
            break

        vizinha = gera_vizinho(distribuicao)
        valor_vizinha = heuristica(vizinha)

        energia = valor_vizinha - valor_atual
        if energia < 0:
            distribuicao = vizinha
        else:
            probabilidade = math.exp(-energia / T)
            valor = random.random()
            if valor < probabilidade:
                print("Aceitou uma solução pior...")
                distribuicao = vizinha

        T = T * 0.95

    print("Solução Atual ")
    print_solucao(distribuicao, heuristica(distribuicao))

    print("Solução Decodificada: ")
    for pessoa in range(NUM_PESSOAS):
        soma = 0
        print("Pessoa " + str(pessoa) + ": ")
        for i in range(len(cargas)):
            if distribuicao[i] == pessoa:
                print(cargas[i], end=" ")
                soma += cargas[i]
        print(" - Total: " + str(soma))


if __name__ == "__main__":
    executa_simulated_annealing()
