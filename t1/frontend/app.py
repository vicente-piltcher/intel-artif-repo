"""
app.py — Frontend Flask para o Jogo da Velha x IA
T1 - Inteligência Artificial | PUCRS |

Para rodar:
    pip install -r requirements.txt
    python app.py
Acesse: http://localhost:5000
"""

import os
import random
import numpy as np
from flask import Flask, render_template, request, jsonify

# ── Carrega modelos treinados ───────────────────────────────────────────────
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

model        = None
scaler       = None
le           = None
model_name   = 'Desconhecido'
model_loaded = False

try:
    import joblib
    model  = joblib.load(os.path.join(MODELS_DIR, 'melhor_modelo.pkl'))
    scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler.pkl'))
    le     = joblib.load(os.path.join(MODELS_DIR, 'le.pkl'))
    info_path = os.path.join(MODELS_DIR, 'model_info.txt')
    if os.path.exists(info_path):
        with open(info_path, 'r') as f:
            model_name = f.read().strip()
    model_loaded = True
    print(f'[OK] Modelo carregado: {model_name}')
except Exception as e:
    print(f'[ERRO] Modelos nao encontrados ({e}). Execute a celula EXPORT do notebook primeiro.')

# ── Predição via modelo ─────────────────────────────────────────────────────
ENCODE_MAP = {'x': 1, 'o': -1, 'b': 0}


def ia_predict(board):
    encoded  = np.array([ENCODE_MAP[v] for v in board], dtype=float).reshape(1, -1)
    scaled   = scaler.transform(encoded)
    pred_int = model.predict(scaled)[0]
    return le.inverse_transform([int(pred_int)])[0]


# ── App Flask ───────────────────────────────────────────────────────────────
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    return jsonify({
        'model_loaded': model_loaded,
        'model_name':   model_name
    })


@app.route('/api/new_game')
def api_new_game():
    return jsonify({
        'board':        ['b'] * 9,
        'model_loaded': model_loaded,
        'model_name':   model_name
    })


@app.route('/api/move', methods=['POST'])
def api_move():
    if not model_loaded:
        return jsonify({'error': 'Modelo nao carregado. Execute a celula EXPORT do notebook e reinicie o servidor.'}), 503

    data     = request.get_json()
    board    = list(data['board'])
    position = int(data['position'])

    if position < 0 or position > 8 or board[position] != 'b':
        return jsonify({'error': 'Posicao invalida'}), 400

    # ── Jogada do Humano (X) ────────────────────────────────────────────────
    board[position] = 'x'
    pred_x    = ia_predict(board)
    game_over = (pred_x != 'tem_jogo')

    cpu_position = None
    pred_o       = None

    if not game_over:
        empty = [i for i, v in enumerate(board) if v == 'b']

        if not empty:
            game_over = True
        else:
            # ── Jogada do CPU (O) ───────────────────────────────────────────
            cpu_position = random.choice(empty)
            board[cpu_position] = 'o'
            pred_o    = ia_predict(board)
            game_over = (pred_o != 'tem_jogo')

            # Tabuleiro cheio: força fim de jogo mesmo que modelo diga tem_jogo
            if not game_over and not any(v == 'b' for v in board):
                game_over = True

    return jsonify({
        'board':        board,
        'cpu_position': cpu_position,
        'pred_x':       pred_x,
        'pred_o':       pred_o,
        'game_over':    game_over,
        'model_name':   model_name
    })


if __name__ == '__main__':
    print('=== Jogo da Velha × IA — T1 PUCRS Grupo 32 ===')
    if model_loaded:
        print(f'Modelo: {model_name}')
    else:
        print('AVISO: Execute a celula EXPORT do notebook e reinicie.')
    print('Acesse: http://localhost:5000')
    app.run(debug=True, port=5000)
