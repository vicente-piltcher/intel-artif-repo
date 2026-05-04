from collections import Counter

# ============================================================
# DADOS
# ============================================================

dados = [
    # (Atributo1, Atributo2, Atributo3, Atributo4, Classe)
    (0, 1, 3, 9, 'B'),
    (1, 0, 2, 7, 'A'),
    (4, 5, 6, 1, 'C'),
    (2, 2, 5, 7, 'B'),
    (7, 8, 5, 2, 'C'),
    (9, 6, 3, 3, 'C'),
    (0, 1, 2, 4, 'A'),
]

ponto = (5, 7, 2, 1)  # Amostra 8 a classificar
k = 4                 # Altere aqui


# ============================================================
# FUNÇÕES DE CÁLCULO
# ============================================================

def distancia_manhattan(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


def calcular_distancias(dados, ponto):
    resultado = []
    for i, (*atributos, classe) in enumerate(dados, start=1):
        atributos = tuple(atributos)
        parcelas = [abs(x - y) for x, y in zip(ponto, atributos)]
        dist = sum(parcelas)
        resultado.append({
            'id': i,
            'atributos': atributos,
            'classe': classe,
            'parcelas': parcelas,
            'distancia': dist,
        })
    return resultado


def selecionar_vizinhos(distancias, k):
    ordenado = sorted(distancias, key=lambda x: x['distancia'])
    return ordenado[:k]


def classificar(vizinhos):
    votos = Counter(v['classe'] for v in vizinhos)
    return votos.most_common(1)[0][0], dict(votos)


# ============================================================
# EXECUÇÃO
# ============================================================

distancias = calcular_distancias(dados, ponto)
vizinhos = selecionar_vizinhos(distancias, k)
classe_predita, votos = classificar(vizinhos)


# ============================================================
# EXIBIÇÃO DOS RESULTADOS
# ============================================================

print("=" * 75)
print(f"Ponto a classificar: {ponto}  |  k = {k}")
print("=" * 75)

print(f"\n{'#':<5} {'Atributos':<20} {'Classe':<8} {'Cálculo':<35} {'Dist.'}")
print("-" * 75)
for d in distancias:
    calculo = " + ".join(f"|{x}-{y}|" for x, y in zip(ponto, d['atributos']))
    calculo += " = " + " + ".join(map(str, d['parcelas']))
    calculo += f" = {d['distancia']}"
    print(f"{d['id']:<5} {str(d['atributos']):<20} {d['classe']:<8} {calculo}")

print(f"\n--- {k} vizinhos mais próximos ---")
print(f"{'#':<5} {'Classe':<8} {'Distância'}")
print("-" * 25)
for v in vizinhos:
    print(f"{v['id']:<5} {v['classe']:<8} {v['distancia']}")

print(f"\nVotos: {votos}")
print(f"Classe predita para {ponto}: {classe_predita}")
print("=" * 75)
