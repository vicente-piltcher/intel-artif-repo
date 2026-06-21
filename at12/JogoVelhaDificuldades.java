
import java.util.Random;
import java.util.Scanner;

/**
 * Jogo da Velha: Humano (X) contra Computador (O).
 *
 * O computador joga em tres niveis de dificuldade, combinando o algoritmo
 * Minimax (Alfa-Beta) ja implementado com jogadas aleatorias:
 *
 *   Facil   -> 25% das jogadas com Minimax, 75% aleatorias
 *   Medio   -> 50% das jogadas com Minimax, 50% aleatorias
 *   Dificil -> 100% das jogadas com Minimax
 *
 * A cada jogada do computador e registrado se ele usou o Minimax ou foi
 * uma jogada aleatoria. O jogo e jogado pelo terminal, informando a
 * posicao (linha e coluna).
 *
 * Convencao do tabuleiro:  -1 = celula livre   1 = X (humano)   0 = O (computador)
 */
public class JogoVelhaDificuldades
{
    private int[][] tabuleiro;          // estado atual do jogo
    private double probMinimax;         // probabilidade de o computador usar o Minimax
    private String nomeDificuldade;     // rotulo da dificuldade escolhida

    private final Random rand = new Random();
    private final Scanner in = new Scanner(System.in);

    public JogoVelhaDificuldades(){
        tabuleiro = new int[][]{{-1,-1,-1},
                                {-1,-1,-1},
                                {-1,-1,-1}};
    }

    /**
     * Laco principal do jogo: escolhe a dificuldade e alterna as jogadas
     * entre o humano (X) e o computador (O) ate haver um vencedor ou empate.
     */
    public void iniciar(){
        System.out.println("\f===== JOGO DA VELHA =====");
        System.out.println("Voce e o X. O computador e o O.");
        escolheDificuldade();

        System.out.println("\nDificuldade escolhida: " + nomeDificuldade);
        System.out.println("Tabuleiro inicial: ");
        exibe();

        boolean vezDoHumano = true;     // o humano comeca jogando
        int resultado;
        while(true){
            if(vezDoHumano) jogadaHumano();
            else            jogadaComputador();

            exibe();

            resultado = verificaFim();
            if(resultado != EM_ANDAMENTO){
                anunciaResultado(resultado);
                break;
            }
            vezDoHumano = !vezDoHumano;
        }
    }

    // -------------------- ESCOLHA DE DIFICULDADE --------------------

    private void escolheDificuldade(){
        int opcao;
        do{
            System.out.println("\nEscolha a dificuldade:");
            System.out.println("  1 - Facil   (25% Minimax / 75% aleatorio)");
            System.out.println("  2 - Medio   (50% Minimax / 50% aleatorio)");
            System.out.println("  3 - Dificil (100% Minimax)");
            System.out.print("Opcao: ");
            opcao = lerInteiro();
            if(opcao < 1 || opcao > 3) System.out.println("Opcao invalida!");
        }while(opcao < 1 || opcao > 3);

        switch(opcao){
            case 1: probMinimax = 0.25; nomeDificuldade = "Facil";   break;
            case 2: probMinimax = 0.50; nomeDificuldade = "Medio";   break;
            default:probMinimax = 1.00; nomeDificuldade = "Dificil"; break;
        }
    }

    // -------------------- JOGADA DO HUMANO --------------------

    private void jogadaHumano(){
        int l, c;
        do{
            System.out.println("\nSua vez (X).");
            System.out.print("Informe a linha (0-2): ");
            l = lerInteiro();
            System.out.print("Informe a coluna (0-2): ");
            c = lerInteiro();
            if(l < 0 || c < 0 || l > 2 || c > 2 || tabuleiro[l][c] != -1)
                System.out.println("Coordenadas invalidas ou celula ocupada!");
        }while(l < 0 || c < 0 || l > 2 || c > 2 || tabuleiro[l][c] != -1);

        tabuleiro[l][c] = 1; // X
    }

    // -------------------- JOGADA DO COMPUTADOR --------------------

    private void jogadaComputador(){
        System.out.println("\nVez do computador (O)...");

        double sorteio = rand.nextDouble();
        int l, c;

        if(sorteio < probMinimax){
            // Jogada com Minimax (Alfa-Beta) reutilizando a implementacao existente
            TestaMinimax mini = new TestaMinimax(tabuleiro);
            Sucessor melhor = mini.joga();
            l = melhor.getLinha();
            c = melhor.getColuna();
            System.out.println(">>> [MINIMAX] O computador usou o Minimax e jogou em "
                               + "Linha " + l + ", Coluna " + c
                               + "  (utilidade = " + melhor.getValor() + ")");
        }else{
            // Jogada aleatoria entre as celulas livres
            int[] pos = jogadaAleatoria();
            l = pos[0];
            c = pos[1];
            System.out.println(">>> [ALEATORIO] O computador jogou aleatoriamente em "
                               + "Linha " + l + ", Coluna " + c);
        }

        tabuleiro[l][c] = 0; // O
    }

    /**
     * Sorteia uma celula livre do tabuleiro.
     * @return vetor {linha, coluna} de uma posicao livre.
     */
    private int[] jogadaAleatoria(){
        int[][] livres = new int[9][2];
        int n = 0;
        for(int i = 0; i < 3; i++)
            for(int j = 0; j < 3; j++)
                if(tabuleiro[i][j] == -1){
                    livres[n][0] = i;
                    livres[n][1] = j;
                    n++;
                }
        int escolha = rand.nextInt(n);
        return new int[]{ livres[escolha][0], livres[escolha][1] };
    }

    // -------------------- FIM DE JOGO --------------------

    private static final int X_VENCEU      = 1;  // humano
    private static final int O_VENCEU      = 0;  // computador
    private static final int EMPATE        = 3;
    private static final int EM_ANDAMENTO  = 2;

    /**
     * Verifica o estado do jogo.
     * @return X_VENCEU, O_VENCEU, EMPATE ou EM_ANDAMENTO.
     */
    private int verificaFim(){
        if(venceu(1)) return X_VENCEU;
        if(venceu(0)) return O_VENCEU;
        for(int i = 0; i < 3; i++)
            for(int j = 0; j < 3; j++)
                if(tabuleiro[i][j] == -1) return EM_ANDAMENTO;
        return EMPATE;
    }

    /**
     * Verifica se o jogador dado (1=X ou 0=O) venceu em linha, coluna ou diagonal.
     */
    private boolean venceu(int jogador){
        for(int i = 0; i < 3; i++){
            if(tabuleiro[i][0] == jogador && tabuleiro[i][1] == jogador && tabuleiro[i][2] == jogador) return true; // linha
            if(tabuleiro[0][i] == jogador && tabuleiro[1][i] == jogador && tabuleiro[2][i] == jogador) return true; // coluna
        }
        if(tabuleiro[0][0] == jogador && tabuleiro[1][1] == jogador && tabuleiro[2][2] == jogador) return true; // diagonal principal
        if(tabuleiro[0][2] == jogador && tabuleiro[1][1] == jogador && tabuleiro[2][0] == jogador) return true; // diagonal secundaria
        return false;
    }

    private void anunciaResultado(int resultado){
        System.out.println("\n========================");
        switch(resultado){
            case X_VENCEU: System.out.println(" Voce (X) venceu! Parabens!"); break;
            case O_VENCEU: System.out.println(" O computador (O) venceu!");   break;
            default:       System.out.println(" Deu velha! Empate.");         break;
        }
        System.out.println("========================");
    }

    // -------------------- UTILITARIOS --------------------

    private void exibe(){
        System.out.println();
        System.out.print("    0\t1\t2\n");
        for(int i = 0; i < 3; i++){
            System.out.print(i + "   ");
            for(int j = 0; j < 3; j++){
                if(tabuleiro[i][j] == -1)      System.out.print("#\t");
                else if(tabuleiro[i][j] == 1)  System.out.print("X\t");
                else                           System.out.print("O\t");
            }
            System.out.println();
        }
    }

    /**
     * Le um inteiro do terminal de forma segura (ignora entradas nao numericas).
     */
    private int lerInteiro(){
        while(!in.hasNextInt()){
            in.next();
            System.out.print("Digite um numero valido: ");
        }
        return in.nextInt();
    }

    public static void main(String[] args){
        new JogoVelhaDificuldades().iniciar();
    }
}
