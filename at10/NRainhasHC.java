
/**
 * Implementação do Hill Climbing para o problema das N Rainhas
 * 
 * @author Sílvia
 * @version 10/09/2013 - Atualizado em 08/04/2021
 */
import java.util.Random;
public class NRainhasHC
{
    private Character[][] tabuleiro, tabuleiroAux, tabuleiroMelhorVizinho;
    private int[] solucaoAtual, solucaoVizinha, solucaoMelhorVizinho;
    private int dimensao;
       
    public static void main(String args[]){
    	int N = 8;
    	NRainhasHC rainhas = new NRainhasHC(N);
    	rainhas.executaHillClimbing();
    }
    
    
    /*Cria o tabuleiro das NRainhas*/
    public NRainhasHC(int dimensao){
        this.dimensao = dimensao;
        tabuleiro = new Character[dimensao][dimensao];
        tabuleiroAux = new Character[dimensao][dimensao];
        tabuleiroMelhorVizinho = new Character[dimensao][dimensao];
        solucaoAtual = new int[dimensao];
        solucaoVizinha = new int[dimensao];
        solucaoMelhorVizinho = new int[dimensao];
        inicializa();
    }
    
    /*Posiciona aleatoriamente as rainhas*/
    private void inicializa(){
        limpaTabuleiro(tabuleiro);
        limpaTabuleiro(tabuleiroAux);
        geraSolucaoInicial();    
        incluiRainhas(tabuleiro,solucaoAtual);
    }
    
   private void limpaTabuleiro(Character [][]tab){
    	for(int i=0; i<dimensao; i++)
           for(int j=0; j<dimensao; j++){
                tab[i][j]='-';
            }
   }
   
   private void geraSolucaoInicial(){
   	Random geraPosicao = new Random();
        for(int i=0; i<dimensao; i++) {
        	solucaoAtual[i] = geraPosicao.nextInt(dimensao);
        }
   }
   
   private void incluiRainhas(Character [][] tab, int []solucao){
        
        for(int i=0; i<dimensao; i++){ 
            tab[solucao[i]][i]= '*';
        }
    }
    
    public String escreveTabuleiro(Character[][] tab){
        String msg="";
        for(int i=0; i<dimensao; i++){
            for(int j=0; j<dimensao; j++){
                msg = msg + tab[i][j]+" ";
            }
            msg = msg + "\n";
        }
        return msg;
    }
    
    /* Função heurística */
    public int h(Character[][] tabuleiro){
        int ataques = 0;
        for(int i=0; i<dimensao; i++)
            for(int j=0; j<dimensao; j++){
                if(tabuleiro[i][j]=='*'){
                    ataques = ataques + contaAtaquePorLinha(i,j,tabuleiro);
                  //  ataques = ataques + contaAtaquePorColuna(i,j,tabuleiro);
                    ataques = ataques + contaAtaqueDiagonais(i,j,tabuleiro);
                }
            }
        return ataques;
    }
    
    private int contaAtaquePorLinha(int linha, int coluna, Character [][]tabuleiro){
        int ataques = 0;
         for(int j=coluna+1; j<dimensao; j++)
             if(tabuleiro[linha][j]=='*') ataques++;
        return ataques;
    }
    
    private int contaAtaquePorColuna(int linha, int coluna,Character [][]tabuleiro){
        int ataques = 0;
        for(int i=linha+1; i<dimensao; i++)
             if(tabuleiro[i][coluna]=='*') ataques++;
        return ataques;
    }
    
    private int contaAtaqueDiagonais(int linha, int coluna,Character [][]tabuleiro){
        int ataques = 0;
        for(int i=linha+1,j=coluna+1; i<dimensao && j<dimensao; i++,j++){
            if(tabuleiro[i][j]=='*') ataques++;
        }
        for(int i=linha+1,j=coluna-1; i<dimensao && j>=0; i++,j--){
            if(tabuleiro[i][j]=='*') ataques++;
        }
        return ataques;
    }
    
    public void copiaTabuleiro(Character [][] tab1, Character [][] tab2){
    	 for(int i=0; i<dimensao; i++)
            for(int j=0; j<dimensao; j++){
            	tab1[i][j] = tab2[i][j];
            }
         
    }

    public void copiaSolucao(int v1[], int v2[]){
    	for(int i=0; i<dimensao; i++){
    		v1[i] = v2[i];
    	}
    }
    
    public void geraSolucaoVizinha(int ind){
        copiaSolucao(solucaoVizinha,solucaoAtual);
        
        Random gera = new Random();
        int novaLinha;
        do{
        	novaLinha = gera.nextInt(dimensao);
        } while(novaLinha == solucaoAtual[ind]);
        solucaoVizinha[ind] = novaLinha;
       
        limpaTabuleiro(tabuleiroAux);
        incluiRainhas(tabuleiroAux,solucaoVizinha);
        	
    }
    
    public void geraSolucaoVizinhaTodas(int linha,int coluna){
        copiaSolucao(solucaoVizinha,solucaoAtual);
        
        solucaoVizinha[linha] = coluna;
       
        limpaTabuleiro(tabuleiroAux);
        incluiRainhas(tabuleiroAux,solucaoVizinha);
        	
    }
    
    public void executaHillClimbing(){
        Random r = new Random();
        
        double valorSolucaoAtual, valorSolucaoVizinha,melhorVizinho;
        int iteracoes = 50000;
        
        
        System.out.println("Hill Climbing\nDimensão: " + dimensao+"\n");
        inicializa();
   
    	
        for(int t=1; t<=iteracoes; t++){  
            valorSolucaoAtual = h(tabuleiro);
            System.out.print( "Ciclo: " + t + " -") ;  
    	    System.out.println("Solução Atual - h=" + valorSolucaoAtual);
 //   	    System.out.println(escreveTabuleiro(tabuleiro));
            if(valorSolucaoAtual==0) break;
            
            melhorVizinho = 9999;
            
            for(int j=0; j<dimensao; j++)
            for(int i=0; i<dimensao; i++){
            	geraSolucaoVizinhaTodas(i,j);
  //          	geraSolucaoVizinha(i);   //coluna aleatoria
            	valorSolucaoVizinha = h(tabuleiroAux);
 //           System.out.println("Solução Vizinha - h=" + valorSolucaoVizinha + "\n" +escreveTabuleiro(tabuleiroAux));
 		if(valorSolucaoVizinha < melhorVizinho){
 			melhorVizinho = valorSolucaoVizinha;
 			copiaSolucao(solucaoMelhorVizinho,solucaoVizinha);
 			copiaTabuleiro(tabuleiroMelhorVizinho,tabuleiroAux);
 		}
            }
            if(melhorVizinho<valorSolucaoAtual){
            		System.out.println("Achou um vizinho melhor");
 			copiaSolucao(solucaoAtual, solucaoMelhorVizinho);
 			copiaTabuleiro(tabuleiro, tabuleiroMelhorVizinho);
            }
            else {
            	System.out.println("Não há vizinho melhor que o atual");
            	break;
            }
         }  
        
        System.out.println("Solução Atual - h=" + h(tabuleiro));
        System.out.println(escreveTabuleiro(tabuleiro));
        
    }
    
  
}
