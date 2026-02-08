import json
import os
import glob

PASTA_BATCHES = 'batches'
ARQUIVO_FINAL = 'todos_videos_transcritos_final.json'

def juntar():
    lista_completa = []
    arquivos = sorted(glob.glob(os.path.join(PASTA_BATCHES, "*.json")))
    
    print(f"Encontrados {len(arquivos)} arquivos de batch.")
    
    for arquivo in arquivos:
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            lista_completa.extend(dados)
            
    print(f"Total de itens combinados: {len(lista_completa)}")
    
    with open(ARQUIVO_FINAL, 'w', encoding='utf-8') as f:
        json.dump(lista_completa, f, ensure_ascii=False, indent=4)
        
    print(f"Arquivo final salvo: {ARQUIVO_FINAL}")

if __name__ == "__main__":
    juntar()