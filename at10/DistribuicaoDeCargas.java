
/**
 * Implementação do Simulated Annealing 
 * Exemplo de distribuição de cargas
 * 
 * @author Sílvia
 * @version 13/04/2021
 */
import java.util.Random;
public class DistribuicaoDeCargas
{
    private static int[] cargas = {27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,50,24,26,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,27, 7, 6, 5, 4, 6, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,50,24,26,100,51,49};
    private static int[] distribuicao, distribuicaoVizinha;
   
   
       
    public static void main(String args[]){
    	DistribuicaoDeCargas c1 = new DistribuicaoDeCargas();
    	
        c1.executaSimulatedAnnealing();	
    	
    }

    public DistribuicaoDeCargas(){
        distribuicao = new int [cargas.length];
        distribuicaoVizinha = new int [cargas.length];
    	Random r = new Random();
    	for(int i=0; i<distribuicao.length; i++){
    		distribuicao[i] = r.nextInt(2);
    	}
    }    
    
    public static void print(int []v, int h){
    	for(int i=0; i<v.length; i++){
    		System.out.print(v[i] + " ");
    	}
    	System.out.println(" - h: " + h);
    }
    
    
   public static int heuristica(int []s){
   	int somaZero = 0;
   	int somaUm = 0;
    	for(int j = 0; j < cargas.length; j++){
      		if(s[j] == 0 ){
        		somaZero += cargas[j];
      		} 
      		else {
        		somaUm += cargas[j];
     		}
    	}
    	return Math.abs(somaZero - somaUm);
  }

  public static void geraVizinho(){
  	Random r = new Random();
  	for(int i=0; i<distribuicao.length; i++){
  		distribuicaoVizinha[i] = distribuicao[i];
  	}
  	int pos = r.nextInt(distribuicao.length);
  	if(distribuicaoVizinha[pos]==0) distribuicaoVizinha[pos]= 1;
  	else distribuicaoVizinha[pos]=0; 
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
        double T = 100;
        int iteracoes = 200;
        
        System.out.println("Simulated Annealing ");
        
    	
        for(int t=1; t<=iteracoes; t++){  
            valorSolucaoAtual = heuristica(distribuicao);
            System.out.print( "Ciclo: " + t + "- Temperatura: " + T + " -") ;  
    	    System.out.println("Solução Atual - h=" + valorSolucaoAtual);
 //   	    System.out.println(print(distribucao,h));
            if(valorSolucaoAtual==0) break;
            
            geraVizinho();
            valorSolucaoVizinha = heuristica(distribuicaoVizinha);
 //           System.out.println("Solução Vizinha - h=" + valorSolucaoVizinha + "\n" +print(distribuicaoVizinha,valorSolucaoVizinha));
            
            energia = valorSolucaoVizinha - valorSolucaoAtual;
            if(energia<0){
            	copiaSolucao(distribuicaoVizinha);
            }
            else {
            	 probabilidade = Math.exp(-energia/T);
            	 valor = r.nextDouble();
 //           	 System.out.println("Valor Gerado: " + valor + " Probabilidade: " + probabilidade);
            	 if(valor <probabilidade) {
            	 	System.out.println("Aceitou uma solução pior...");
            	 	copiaSolucao(distribuicaoVizinha);
            	 }
            }
              T = T * 0.6; 
            //T = T* 0.65;
            //T = T * 0.5;

        }  
        
        System.out.println("Solução Atual ");
        print(distribuicao,heuristica(distribuicao));
        int soma = 0;
  	
  	System.out.println("Solução Decodificada: ");
  	System.out.println("Pessoa 0: ");
  	for(int i=0; i<cargas.length; i++) 
  		if(distribuicao[i]==0) {
  				System.out.print(cargas[i]+ " ");
  				soma = soma + cargas[i];
  	        }
  		System.out.println(" - Total: " + soma);
  		
  		soma = 0;
  		System.out.println("Pessoa 1: ");
  		for(int i=0; i<cargas.length; i++) 
  			if(distribuicao[i]==1) {
  				System.out.print(cargas[i]+ " ");
  				soma = soma + cargas[i];
  		        }
  		System.out.println(" - Total: " + soma);
        
       }
     
}
