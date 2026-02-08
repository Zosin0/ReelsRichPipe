import json
import os
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI")

ARQUIVO_ENTRADA = 'captions/caption_processed_1.json'
ARQUIVO_SAIDA = 'GUIA_DE_VIAGEM_TOKYO_1.md'

MODELO = "gemini-flash-latest" 

def configurar_gemini():
    genai.configure(api_key=API_KEY)
    
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    
    generation_config = {
        "temperature": 0.3,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    return genai.GenerativeModel(
        model_name=MODELO,
        generation_config=generation_config,
        safety_settings=safety_settings
    )

def criar_prompt(lote_videos):
    prompt = """
    Você é um especialista em viagens para o Japão e assistente pessoal.
    
    TAREFA:
    Eu tenho uma lista de dados extraídos de vídeos do Instagram (Reels) sobre Tóquio/Japão.
    Os dados contêm: 
    1. Legenda original (Caption) - pode estar em Inglês, Japonês ou Coreano.
    2. Transcrição do áudio (Transcription) - pode estar bagunçada ou ser música.
    3. URL original.

    Seu objetivo é analisar cada item e compilar um GUIA DE VIAGEM EM PORTUGUÊS (PT-BR).
    
    PARA CADA VÍDEO, GERE O SEGUINTE FORMATO MARKDOWN:

    ## [Nome do Local ou Atividade Identificada]
    * **Categoria:** (Ex: Comida, Compras, Passeio, Dica Prática, Curiosidade)
    * **O que é:** (Resumo de 1 ou 2 frases explicando o que é o local baseado na legenda e áudio).
    * **Dica Extraída:** (Qualquer dica específica mencionada, ex: "vá cedo", "peça o prato X", "custa 500 ienes").
    * **Link:** [Ver no Instagram]({url})
    
    REGRAS IMPORTANTES:
    - Se a transcription for "[Apenas Música/Instrumental]", ignore o áudio e use só a caption.
    - Se a caption estiver em Japonês/Coreano/Inglês, TRADUZA as informações essenciais para PT-BR.
    - Se não for um local específico (ex: vídeo de humor), classifique como "Outros".
    - Seja direto e prático.

    AQUI ESTÃO OS DADOS DOS VÍDEOS (Formato JSON):
    """
    
    prompt += json.dumps(lote_videos, ensure_ascii=False)
    return prompt

def main():
    if not API_KEY:
        print("ERRO: Variável de ambiente 'GEMINI' não configurada.")
        print("Configure com: $env:GEMINI = 'sua-chave-aqui' (PowerShell) ou set GEMINI=sua-chave-aqui (Cmd)")
        return

    print("Iniciando o Gerador de Guia de Viagem com Gemini...")
    model = configurar_gemini()
    
    with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8') as f:
        todos_videos = json.load(f)
    
    total = len(todos_videos)
    print(f"Total de vídeos para processar: {total}")

    TAMANHO_LOTE = 10
    
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f_saida:
        f_saida.write("# 🇯🇵 Guia de Viagem: Japão (Compilado do Instagram 01)\n\n")
        f_saida.write(f"*Gerado automaticamente base em {total}/360 vídeos.*\n\n---\n\n")
        
        for i in range(0, total, TAMANHO_LOTE):
            lote = todos_videos[i : i + TAMANHO_LOTE]
            print(f"Processando lote {i} a {i+len(lote)}...")
            
            try:
                prompt = criar_prompt(lote)
                response = model.generate_content(prompt)
                
                f_saida.write(response.text)
                f_saida.write("\n\n---\n\n")
                
                time.sleep(4) 
                
            except Exception as e:
                print(f"Erro no lote {i}: {e}")
                time.sleep(10)

    print(f"\nGuia finalizado!\n {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    main()