
/**
 * Escreva a descrição da classe TestaRede aqui.
 * 
 * @author Silvia
 * @version 12/11/2020
 */
import java.util.Random;
import java.util.Scanner;

public class JogoVelha
{
    private double[]tabuleiro;
    private int[][]tabuleiroVelha;
    
    public JogoVelha(){
        //------------------------ EXEMPLO DE TABULEIRO ------------------------------------------
        //tabuleiro do jogo da velha - Exemplo de teste
        tabuleiroVelha = new int[][]{{-1,-1,-1},            //-1: celula livre  1: X   0: O
                                     {-1,-1,-1},
                                     {-1,-1,-1}};
        
        System.out.println("\f\nTestando a interacao... ");
        System.out.println("\nSem validacao de fim ... ");   
        System.out.println("\nTabuleiro inicial: ");                             
        exibe();
        
        //tabuleiro de teste - conversao de matriz para vetor      
        tabuleiro = new double[tabuleiroVelha.length*tabuleiroVelha.length];
        int k=0;
        for(int i=0; i<tabuleiroVelha.length; i++){
            for(int j=0; j<tabuleiroVelha.length; j++){
                tabuleiro[k] = tabuleiroVelha[i][j];
                k++;
            }
        }
        
        for(int r=1; r<=4; r++){
             
            int l,c;
            Scanner in = new Scanner(System.in);
            do{
                System.out.print("Informe a linha: ");
                l = in.nextInt();
                System.out.print("Informe a coluna: ");
                c = in.nextInt();
                if(l<0||c<0||l>2||c>2||tabuleiroVelha[l][c]!=-1) System.out.println("Coordenadas invalidas ou celula ocupada");
            }while(l<0||c<0||l>2||c>2||tabuleiroVelha[l][c]!=-1);
        
            tabuleiroVelha[l][c] = 1;
            
            System.out.println("\nTabuleiro apos jogada: ");                             
            exibe();
                                
            //-----------------------------------------JOGA MINIMAX
            TestaMinimax mini = new TestaMinimax(tabuleiroVelha);
            Sucessor melhor = mini.joga();
            
            System.out.println(">>> MINIMAX escolheu - Linha: " + melhor.getLinha() + " Coluna: " + melhor.getColuna());
        
            if(tabuleiroVelha[melhor.getLinha()][melhor.getColuna()]!=-1) System.out.println("Posicao ocupada");
            else{
                tabuleiroVelha[melhor.getLinha()][melhor.getColuna()] = 0;
            
                System.out.println("\nTabuleiro apos jogada: ");                             
                exibe();
            }
            
            //tabuleiro de teste - conversao de matriz para vetor      
            k=0;
            for(int i=0; i<tabuleiroVelha.length; i++){
                for(int j=0; j<tabuleiroVelha.length; j++){
                    tabuleiro[k] = tabuleiroVelha[i][j];
                    k++;
                }
            }
        }
    }
    public void exibe(){
        for(int i=0; i<tabuleiroVelha.length; i++){
            for(int j=0; j<tabuleiroVelha.length; j++){
                if(tabuleiroVelha[i][j]==-1) System.out.print("#\t");
                else if(tabuleiroVelha[i][j]==1) System.out.print("X\t");
                     else System.out.print("O\t");
            }
            System.out.println();
        }
    }
    public static void main(String args[]){
        JogoVelha teste = new JogoVelha();
            
    }
    
    
}
