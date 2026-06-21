# T2 – Algoritmos de Busca: Olimpíada (Algoritmo Genético Memético)

Distribuição de alunos de duas escolas em **quartos duplos heterogêneos** (um aluno de
cada escola por quarto) usando um **Algoritmo Genético memético** (AG + **busca
local**), respeitando ao máximo as preferências mútuas. PUCRS – Inteligência Artificial.

## Conteúdo
- `main.py` — implementação do Algoritmo Genético memético (código-fonte).
- `test_main.py` — testes automatizados (`pytest`).
- `docs/DOCUMENTACAO_CODIGO.md` — explicação detalhada do código.
- `docs/CONCEITOS.md` — fundamentos teóricos do AG aplicados ao trabalho.
- `RELATORIO_PPT.md` — roteiro do relatório em formato PPT (rubrica).
- `caso1.txt` — instância de exemplo do enunciado (N=4).
- `caso2.txt` — instância de teste (N=10).

## Requisitos
- Python 3.8+
- (testes) pytest: `pip install pytest`

## Como executar
São **dois modos**, como pede o enunciado. O nome do arquivo é passado como argumento.

```bash
# Modo final (roda tudo e mostra a solução)
python main.py caso1.txt --modo final

# Modo passo a passo (pausa a cada geração, pressione Enter)
python main.py caso1.txt --modo passo
```

Os parâmetros do AG (população, gerações, taxas etc.) são **fixos no código**
(classe `Parametros` em `main.py`).

## Testes
```bash
pytest test_main.py
```

## Saídas
- **Console:** evolução da heurística por geração + solução codificada e decodificada.
- **`<arquivo>_output.txt`:** solução final + log completo de evolução.

## Gerar o executável (.exe)
```bash
pip install pyinstaller
pyinstaller --onefile main.py
# resultado em dist/main.exe
dist\main.exe caso2.txt --modo final
```
