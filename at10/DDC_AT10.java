
/**
 * Implementação do Simulated Annealing
 * Distribuição de cargas entre 3 pessoas (adaptação de DistribuicaoDeCargas.java)
 *
 * Alterações em relação ao original:
 *  - Codificação ternária: distribuicao[i] ∈ {0, 1, 2}
 *  - Heurística: range (max − min) das 3 somas
 *  - Vizinho: realoca uma carga para uma das outras 2 pessoas
 *  - Saída: laço sobre as 3 pessoas
 *  - Parâmetros SA reajustados para o espaço de busca 3^156
 */
import java.util.Random;
public class DDC_AT10
{
    private static final int NUM_PESSOAS = 3;
    private static int[] cargas = {27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,50,24,26,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,50,24,26,100,51,49};
    private static int[] distribuicao, distribuicaoVizinha;


    public static void main(String args[]){
        DDC_AT10 c1 = new DDC_AT10();
        c1.executaSimulatedAnnealing();
    }

    public DDC_AT10(){
        distribuicao = new int [cargas.length];
        distribuicaoVizinha = new int [cargas.length];
        Random r = new Random();
        for(int i=0; i<distribuicao.length; i++){
            distribuicao[i] = r.nextInt(NUM_PESSOAS);
        }
    }

    public static void print(int []v, int h){
        for(int i=0; i<v.length; i++){
            System.out.print(v[i] + " ");
        }
        System.out.println(" - h: " + h);
    }


   public static int heuristica(int []s){
        int[] somas = new int[NUM_PESSOAS];
        for(int j = 0; j < cargas.length; j++){
            somas[s[j]] += cargas[j];
        }
        int max = somas[0];
        int min = somas[0];
        for(int k = 1; k < NUM_PESSOAS; k++){
            if(somas[k] > max) max = somas[k];
            if(somas[k] < min) min = somas[k];
        }
        return max - min;
  }

  public static void geraVizinho(){
        Random r = new Random();
        for(int i=0; i<distribuicao.length; i++){
            distribuicaoVizinha[i] = distribuicao[i];
        }
        int pos = r.nextInt(distribuicao.length);
        int atual = distribuicaoVizinha[pos];
        int novo;
        do {
            novo = r.nextInt(NUM_PESSOAS);
        } while (novo == atual);
        distribuicaoVizinha[pos] = novo;
  }

  public void copiaSolucao(int v[]){
        for(int i=0; i<distribuicao.length; i++){
            distribuicao[i] = v[i];
        }
    }

  public void executaSimulatedAnnealing(){
        Random r = new Random();

        double valorSolucaoAtual, valorSolucaoVizinha;
        double energia,probabilidade,valor;
        double T = 1000;
        int iteracoes = 1000;

        System.out.println("Simulated Annealing - Distribuição entre " + NUM_PESSOAS + " pessoas");


        for(int t=1; t<=iteracoes; t++){
            valorSolucaoAtual = heuristica(distribuicao);
            System.out.print( "Ciclo: " + t + "- Temperatura: " + T + " -") ;
            System.out.println("Solução Atual - h=" + valorSolucaoAtual);
            if(valorSolucaoAtual==0) break;

            geraVizinho();
            valorSolucaoVizinha = heuristica(distribuicaoVizinha);

            energia = valorSolucaoVizinha - valorSolucaoAtual;
            if(energia<0){
                copiaSolucao(distribuicaoVizinha);
            }
            else {
                 probabilidade = Math.exp(-energia/T);
                 valor = r.nextDouble();
                 if(valor <probabilidade) {
                    System.out.println("Aceitou uma solução pior...");
                    copiaSolucao(distribuicaoVizinha);
                 }
            }
              T = T * 0.95;

        }

        System.out.println("Solução Atual ");
        print(distribuicao,heuristica(distribuicao));

        System.out.println("Solução Decodificada: ");
        for(int pessoa = 0; pessoa < NUM_PESSOAS; pessoa++){
            int soma = 0;
            System.out.println("Pessoa " + pessoa + ": ");
            for(int i=0; i<cargas.length; i++){
                if(distribuicao[i] == pessoa){
                    System.out.print(cargas[i] + " ");
                    soma += cargas[i];
                }
            }
            System.out.println(" - Total: " + soma);
        }

       }

}
