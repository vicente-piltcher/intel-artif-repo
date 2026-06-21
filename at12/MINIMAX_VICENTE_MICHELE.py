import random

# Nomes: Vicente Piltcher e Michele Ughini

LIVRE = '#'
HUMANO = 'X'     
COMPUTADOR = 'O'  

class Minimax:

    def __init__(self, estado):
        self.estado = estado

    def get_melhor(self):
        return self._algoritmo_ab(self.estado, jogador=False,
                                  profundidade=self._livres(self.estado),
                                  alfa=-999, beta=999)

    @staticmethod
    def _livres(estado):
        return sum(linha.count(LIVRE) for linha in estado)

    @staticmethod
    def _posicoes_livres(estado):
        return [(i, j) for i in range(3) for j in range(3)
                if estado[i][j] == LIVRE]

    @staticmethod
    def _utilidade(estado):
        if Minimax._venceu(estado, HUMANO):
            return -1
        if Minimax._venceu(estado, COMPUTADOR):
            return 1
        if Minimax._livres(estado) == 0:
            return 0
        return None  # jogo ainda em andamento

    @staticmethod
    def _venceu(estado, c):
        for i in range(3):
            if all(estado[i][j] == c for j in range(3)):   # linha
                return True
            if all(estado[j][i] == c for j in range(3)):   # coluna
                return True
        if all(estado[i][i] == c for i in range(3)):       # diagonal principal
            return True
        if all(estado[i][2 - i] == c for i in range(3)):   # diagonal secundaria
            return True
        return False

    def _algoritmo_ab(self, estado, jogador, profundidade, alfa, beta):
        valor = self._utilidade(estado)
        if valor is not None:
            return (-1, -1, valor)

        melhor_lin = melhor_col = -1

        if jogador:  # MIN -> humano (X)
            menor = 999
            for (i, j) in self._posicoes_livres(estado):
                estado[i][j] = HUMANO
                _, _, v = self._algoritmo_ab(estado, False, profundidade - 1, alfa, beta)
                estado[i][j] = LIVRE
                if v < menor:
                    menor, melhor_lin, melhor_col = v, i, j
                if menor < alfa:
                    return (melhor_lin, melhor_col, menor)
                beta = min(beta, v)
            return (melhor_lin, melhor_col, menor)
        else:        # MAX -> computador (O)
            maior = -999
            for (i, j) in self._posicoes_livres(estado):
                estado[i][j] = COMPUTADOR
                _, _, v = self._algoritmo_ab(estado, True, profundidade - 1, alfa, beta)
                estado[i][j] = LIVRE
                if v > maior:
                    maior, melhor_lin, melhor_col = v, i, j
                if maior > beta:
                    return (melhor_lin, melhor_col, maior)
                alfa = max(alfa, v)
            return (melhor_lin, melhor_col, maior)


class JogoVelhaDificuldades:

    def __init__(self):
        self.tabuleiro = [[LIVRE] * 3 for _ in range(3)]
        self.prob_minimax = 1.0
        self.nome_dificuldade = ""

    def iniciar(self):
        print("JOGO DA VELHA")
        print("Voce e o X. O computador e o O.")
        self._escolhe_dificuldade()

        print(f"\nDificuldade escolhida: {self.nome_dificuldade}")
        print("Tabuleiro inicial:")
        self._exibe()

        vez_x = True  
        while True:
            if vez_x:
                self.jogada_x()
            else:
                self.jogada_O()

            self._exibe()

            resultado = self._verifica_fim()
            if resultado is not None:
                self._anuncia_resultado(resultado)
                break
            vez_x = not vez_x

    def _escolhe_dificuldade(self):
        opcoes = {1: (0.25, "Facil"), 2: (0.50, "Medio"), 3: (1.00, "Dificil")}
        while True:
            print("\nEscolha a dificuldade:")
            print("  1 - Facil")
            print("  2 - Medio")
            print("  3 - Dificil")
            opcao = self._ler_inteiro("Opcao: ")
            if opcao in opcoes:
                self.prob_minimax, self.nome_dificuldade = opcoes[opcao]
                return
            print("Opcao invalida")

    def jogada_x(self):
        while True:
            print("\nSua vez (X).")
            l = self._ler_inteiro("Informe a linha: ")
            c = self._ler_inteiro("Informe a coluna: ")
            if 0 <= l <= 2 and 0 <= c <= 2 and self.tabuleiro[l][c] == LIVRE:
                self.tabuleiro[l][c] = HUMANO
                return
            print("Coordenadas invalidas ou celula ocupada!")

    def jogada_O(self):
        print("\nVez do O")

        if random.random() < self.prob_minimax:
            l, c, valor = Minimax(self.tabuleiro).get_melhor()
            print(f"[MINIMAX] "
                  f"Linha {l}, Coluna {c}  (utilidade = {valor})")
        else:
            l, c = random.choice(Minimax._posicoes_livres(self.tabuleiro))
            print(f"[ALEATORIO] "
                  f"Linha {l}, Coluna {c}")

        self.tabuleiro[l][c] = COMPUTADOR

    def _verifica_fim(self):
        if Minimax._venceu(self.tabuleiro, HUMANO):
            return HUMANO
        if Minimax._venceu(self.tabuleiro, COMPUTADOR):
            return COMPUTADOR
        if Minimax._livres(self.tabuleiro) == 0:
            return "EMPATE"
        return None

    def _anuncia_resultado(self, resultado):
        if resultado == HUMANO:
            print(" X venceu!")
        elif resultado == COMPUTADOR:
            print(" O venceu!")
        else:
            print(" Deu velha")

    def _exibe(self):
        print()
        print("    0   1   2")
        for i in range(3):
            print(f"{i}   " + "   ".join(self.tabuleiro[i][j] for j in range(3)))

    @staticmethod
    def _ler_inteiro(prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Digite um numero valido")


if __name__ == "__main__":
    JogoVelhaDificuldades().iniciar()
