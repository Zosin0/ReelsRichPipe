import json
import os
import yt_dlp
import whisper
import warnings
import torch
import math

warnings.filterwarnings("ignore")

ARQUIVO_ENTRADA = 'caption_1.json'
PASTA_SAIDA = 'batches'           
ARQUIVO_COOKIES = 'cookies.txt'
TAMANHO_BATCH = 3
MODELO_WHISPER = "base" 
THRESHOLD_NO_SPEECH = 0.6 

def carregar_json(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Arquivo {caminho} não encontrado.")
        return []

def salvar_json(dados, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    print(f"Batch salvo em: {caminho}")

def baixar_audio_temporario(url, id_unico):
    nome_arquivo = f"temp_{id_unico}"
    
    if not os.path.exists(ARQUIVO_COOKIES):
        print("ALERTA: cookies.txt não encontrado!")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': nome_arquivo,
        'cookiefile': ARQUIVO_COOKIES,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f"{nome_arquivo}.mp3"
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")
        return None

def filtrar_alucinacoes(texto):
    alucinacoes_comuns = [
        "Subtitles by", "Amara.org", "Translated by", "Music", 
        "[Music]", "(Music)", "♪", "MBC", "Copyright"
    ]
    if len(texto) < 5: return ""
    for aluc in alucinacoes_comuns:
        if aluc.lower() in texto.lower():
            return ""
    return texto

def transcrever_inteligente(modelo, caminho_audio):
    try:
        result = modelo.transcribe(
            caminho_audio, 
            condition_on_previous_text=False,
            no_speech_threshold=THRESHOLD_NO_SPEECH
        )
        
        probs_no_speech = [s['no_speech_prob'] for s in result['segments']]
        if probs_no_speech:
            media = sum(probs_no_speech) / len(probs_no_speech)
            if media > THRESHOLD_NO_SPEECH:
                return "[Apenas Música/Instrumental]"
        
        texto = filtrar_alucinacoes(result["text"].strip())
        if not texto: return "[Apenas Música/Instrumental]"
        
        return texto

    except Exception as e:
        print(f"Erro na transcrição: {e}")
        return ""

def main():
    if not os.path.exists(PASTA_SAIDA):
        os.makedirs(PASTA_SAIDA)

    dados_totais = carregar_json(ARQUIVO_ENTRADA)
    if not dados_totais: return

    total_items = len(dados_totais)
    total_batches = math.ceil(total_items / TAMANHO_BATCH)

    print(f"📂 Total de vídeos: {total_items}")
    print(f"📦 Tamanho do Batch: {TAMANHO_BATCH}")
    print(f"📑 Total de arquivos a gerar: {total_batches}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Carregando Whisper ({device.upper()})...")
    model = whisper.load_model(MODELO_WHISPER, device=device)

    for i in range(0, total_items, TAMANHO_BATCH):
        numero_batch = (i // TAMANHO_BATCH) + 1
        nome_arquivo_batch = os.path.join(PASTA_SAIDA, f"batch_{numero_batch:03d}.json")
        
        if os.path.exists(nome_arquivo_batch):
            print(f"⏭️  Pulando Batch {numero_batch} (Já existe)")
            continue

        print(f"\n🚀 Iniciando Batch {numero_batch}/{total_batches}")
        
        lote_atual = dados_totais[i : i + TAMANHO_BATCH]
        
        for idx, item in enumerate(lote_atual):
            url = item.get('url')
            print(f"   [{idx+1}/{len(lote_atual)}] Processando: {url}")
            
            arquivo_audio = baixar_audio_temporario(url, f"batch{numero_batch}_{idx}")
            
            if arquivo_audio and os.path.exists(arquivo_audio):
                transcricao = transcrever_inteligente(model, arquivo_audio)
                item['transcription'] = transcricao
                print(f"      📝 {transcricao[:50]}...")
                
                try: os.remove(arquivo_audio)
                except: pass
            else:
                item['transcription'] = "[Erro Download]"

        salvar_json(lote_atual, nome_arquivo_batch)

    print("\nProcessamento Completo!")

if __name__ == "__main__":
    main()