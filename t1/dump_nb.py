import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('tic_tac_toe_classifier_32.ipynb', encoding='utf-8') as f:
    nb = json.load(f)
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell['source'])
    if src.strip():
        print(f"=== CELL {i} ({cell['cell_type']}) ===")
        print(src[:2500])
        print()
