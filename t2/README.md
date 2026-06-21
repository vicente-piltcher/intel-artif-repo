# T2 – Algoritmos de Busca: Olimpíada (Algoritmo Genético)

Distribuição de alunos de duas escolas em **quartos duplos heterogêneos** (um aluno de
cada escola por quarto) usando um **Algoritmo Genético**, respeitando ao máximo as
preferências mútuas. PUCRS – Inteligência Artificial.

## Conteúdo
- `main.py` — implementação do Algoritmo Genético (código-fonte).
- `DOCUMENTACAO_CODIGO.md` — explicação detalhada do código.
- `CONCEITOS.md` — fundamentos teóricos do AG aplicados ao trabalho.
- `RELATORIO_PPT.md` — roteiro do relatório em formato PPT (rubrica).
- `exemplo_quest.txt` — instância de exemplo do enunciado (N=4).
- `arquivoDeTeste1.txt` — instância de teste (N=10).

## Requisitos
- Python 3.8+
- matplotlib: `pip install matplotlib`

## Como executar
```bash
# Modo final (roda tudo e mostra a solução)
python main.py exemplo_quest.txt --modo final

# Modo passo a passo (pausa a cada geração, pressione Enter)
python main.py exemplo_quest.txt --modo passo

# Sem o gráfico (apenas console + arquivo de saída)
python main.py arquivoDeTeste1.txt --sem-grafico

# Reprodutível (semente fixa)
python main.py exemplo_quest.txt --seed 42
```
O nome do arquivo é passado como argumento. Veja todos os parâmetros em
`DOCUMENTACAO_CODIGO.md`.

## Saídas
- **Console:** evolução da heurística por geração + solução codificada e decodificada.
- **`<arquivo>_saida.txt`:** solução final + log completo de evolução.
- **`<arquivo>_evolucao.png`:** gráfico melhor/média/pior por geração.

## Gerar o executável (.exe)
```bash
pip install pyinstaller
pyinstaller --onefile --collect-all matplotlib main.py
# resultado em dist/main.exe
dist\main.exe arquivoDeTeste1.txt --modo final
```
