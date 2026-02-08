**Instagram Reels DM Pipeline**
Pipeline para extrair links de Reels (mensagens diretas), coletar legendas, transcrever áudio em várias línguas e agregar resultados em batches para processamento final com IA.

**Overview**
- **Objetivo**: Montar guias ou documentos a partir de legendas e transcrições de Reels coletados por DM.
- **Fluxo**: Extrair links → Capturar captions → Baixar áudio & transcrever → Agregar batches → Processar com IA.

**Scripts Principais**
- **DevTools Scraper**: [reelsLinkScrapper.js](reelsLinkScrapper.js) — extrai links únicos rodando no Console do DevTools do Instagram.
- **TamperMonkey Analyzer**: [reelsLinkAnalyzer.js](reelsLinkAnalyzer.js) — roda em TamperMonkey para visitar cada link e salvar a `caption` (legenda) no localStorage, depois exportar JSON.
- **Transcrição/Download**: [reelsAsMp3.py](reelsAsMp3.py) — baixa áudio via `yt_dlp` e usa `whisper` para transcrever em várias línguas.
- **Agregador de Batches**: [reelsBatches.py](reelsBatches.py) — junta arquivos JSON de batches em um arquivo final.


**Requisitos**
- Sistema: Windows / macOS / Linux com Python 3.8+
- Node/Browser: Console DevTools (Chrome/Chromium/Edge) + TamperMonkey para o Analyzer
- Python packages (exemplos):
	- `pip install yt-dlp openai-whisper torch` (para `reelsAsMp3.py` — ajuste `torch` conforme GPU/CPU)

**1) Extrair links (DevTools Console)**
- Abra o Instagram no navegador, no painel onde aparecem as miniaturas/DMs.
- Abra DevTools (F12) → Console e cole o conteúdo de [reelsLinkScrapper.js](reelsLinkScrapper.js).
- Execute. O script percorre imagens, abre, detecta `video` e registra links únicos. Ao final ele imprime e baixa um `.txt` com os links.

Dicas:
- Ajuste `TIME_TO_OPEN` / `TIME_TO_CLOSE` se a conexão for lenta.

**2) Capturar captions (TamperMonkey Analyzer)**
- Instale TamperMonkey e crie um novo script; cole o conteúdo de [reelsLinkAnalyzer.js](reelsLinkAnalyzer.js).
- Preencha a constante `LINK_LIST` com os links gerados pelo passo 1 (ou carregue via localStorage).
- Execute o script no Instagram: ele navegará por cada link, expandirá legendas (`mais`), extrairá texto e salvará no `localStorage`, então fará download do JSON final.

Dicas:
- Use intervalos entre requisições (as variáveis `MIN_DELAY` / `MAX_DELAY`) para evitar rate-limits.

**3) Baixar áudio e transcrever (reelsAsMp3.py)**
- Pré-requisitos: `cookies.txt` quando necessário para conteúdo privado/DMs. Configure `ARQUIVO_ENTRADA` com o JSON (cada item deve ter `url`).
- Rodar:

```bash
pip install -U yt-dlp openai-whisper torch
python reelsAsMp3.py
```

- O script processa por batches (configurável via `TAMANHO_BATCH`), baixa áudio com `yt_dlp`, converte para mp3 e executa transcrição com Whisper.
- Saída: arquivos JSON por batch em `batches/` contendo campo `transcription` para cada item.

Avisos:
- Configure `ARQUIVO_COOKIES` se necessário; permissões ou autenticação podem ser necessárias para conteúdo em DMs.

**4) Agregar batches (reelsBatches.py)**
- Quando os batches estiverem prontos, rode:

```bash
python reelsBatches.py
```

- Isso juntará todos os `batch_*.json` em `todos_videos_transcritos_final.json`.

**5) Processamento final com IA / Montagem de Guias**
- Use o arquivo final `todos_videos_transcritos_final.json` para gerar documentos, sumarizações ou guias.
- Exemplo rápido: envie cada `caption` + `transcription` para um LLM (OpenAI / local) solicitando:
	- Resumo
	- Tags/temas
	- Sugestões de roteiro/guia passo-a-passo baseado no conteúdo do vídeo

Recomendações práticas:
- Normalizar campos: garanta que cada item tenha `url`, `caption` e `transcription` antes de processar.
- Tratar duplicados: filtrar por `url` para evitar repetições.
- Taxas e limites: respeite os termos do Instagram e limites de acesso.

**Exemplo de pipeline (comandos)**
```bash
# 1) Extrair links: cole reelsLinkScrapper.js no Console do navegador
# 2) No TamperMonkey, configure LINK_LIST e execute reelsLinkAnalyzer.js para gerar batches de captions
# 3) Baixar áudio e transcrever
python reelsAsMp3.py
# 4) Agregar
python reelsBatches.py
# 5) Processar `todos_videos_transcritos_final.json` com seu script/IA

```

**Problemas comuns & Soluções**
- Captions vazias: aumente tempo de espera no Analyzer (`wait`), ou verifique seletores na página (podem mudar com updates do Instagram).
- Downloads falham: verifique `cookies.txt` e `yt_dlp` configurado corretamente.
- Transcrição ruim: escolha modelo Whisper maior (`small`, `medium`) e rode com GPU se disponível.

**Arquivos no repositório**
- [reelsLinkScrapper.js](reelsLinkScrapper.js)
- [reelsLinkAnalyzer.js](reelsLinkAnalyzer.js)
- [reelsAsMp3.py](reelsAsMp3.py)
- [reelsBatches.py](reelsBatches.py)

**Próximos passos sugeridos**
- Automatizar a conversão final com um script que chama a API do LLM para gerar guias a partir do JSON final.
- Adicionar validações e um pequeno CLI para facilitar reexecução de batches específicos.

**Licença & Uso**
- Uso pessoal / educacional. Respeite termos de serviço do Instagram e direitos autorais.
