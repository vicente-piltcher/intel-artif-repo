
/**
 * Implementação do Simulated Annealing para o problema das N Rainhas
 * 
 * @author Sílvia
 * @version 10/09/2013 - Atualizado em 08/04/2021
 */
import java.util.Random;
public class NRainhas
{
    private Character[][] tabuleiro, tabuleiroAux;
    private int[] solucaoAtual, solucaoVizinha;
    private int dimensao;
       
    public static void main(String args[]){
    	int N = 128;
    	NRainhas rainhas = new NRainhas(N);
    	rainhas.executaSimulatedAnnealing();
    }
    
    
    /*Cria o tabuleiro das NRainhas*/
    public NRainhas(int dimensao){
        this.dimensao = dimensao;
        tabuleiro = new Character[dimensao][dimensao];
        tabuleiroAux = new Character[dimensao][dimensao];
        solucaoAtual = new int[dimensao];
        solucaoVizinha = new int[dimensao];
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
    
    public void copiaTabuleiro(Character [][] tab){
    	 for(int i=0; i<dimensao; i++)
            for(int j=0; j<dimensao; j++){
            	tabuleiro[i][j] = tab[i][j];
            }
         
    }

    public void copiaSolucao(int v[]){
    	for(int i=0; i<dimensao; i++){
    		solucaoAtual[i] = v[i];
    	}
    }
    
    public void geraSolucaoVizinha(){
    	for(int i=0; i<dimensao; i++){
    		solucaoVizinha[i] = solucaoAtual[i];
        }
        
        Random gera = new Random();
        int novaLinha;
        int ind = gera.nextInt(dimensao);   //escolhe aa rainha
        do{
        	novaLinha = gera.nextInt(dimensao);
        } while(novaLinha == solucaoAtual[ind]);
        solucaoVizinha[ind] = novaLinha;
       
        limpaTabuleiro(tabuleiroAux);
        incluiRainhas(tabuleiroAux,solucaoVizinha);
        	
    }
    
    public void executaSimulatedAnnealing(){
        Random r = new Random();
        
        double valorSolucaoAtual, valorSolucaoVizinha;
        double energia,probabilidade,valor;
        double T = 1000000;
        int iteracoes = 200000;
        
        System.out.println("Simulated Annealing\nDimensão: " + dimensao+"\n");
        inicializa();
    	
        for(int t=1; t<=iteracoes; t++){  
            valorSolucaoAtual = h(tabuleiro);
            System.out.print( "Ciclo: " + t + "- Temperatura: " + T + " -") ;  
    	    System.out.println("Solução Atual - h=" + valorSolucaoAtual);
 //   	    System.out.println(escreveTabuleiro(tabuleiro));
            if(valorSolucaoAtual==0) break;
            
            geraSolucaoVizinha();
            valorSolucaoVizinha = h(tabuleiroAux);
 //           System.out.println("Solução Vizinha - h=" + valorSolucaoVizinha + "\n" +escreveTabuleiro(tabuleiroAux));
            
            energia = valorSolucaoVizinha - valorSolucaoAtual;
            if(energia<=0){
            	copiaSolucao(solucaoVizinha);
            	copiaTabuleiro(tabuleiroAux);
            }
            else {
            	 probabilidade = Math.exp(-energia/T);
            	 valor = r.nextDouble();
 //           	 System.out.println("Valor Gerado: " + valor + " Probabilidade: " + probabilidade);
            	 if(valor <probabilidade) {
            	 	System.out.println("Aceitou uma solução pior...");
            	 	copiaSolucao(solucaoVizinha);
            		copiaTabuleiro(tabuleiroAux);
            	 }
            }
              T = T * 0.6; 
            //T = T* 0.65;
            //T = T * 0.5;

        }  
        
        System.out.println("Solução Atual - h=" + h(tabuleiro));
        System.out.println(escreveTabuleiro(tabuleiro));
        
    }
    
  
}
