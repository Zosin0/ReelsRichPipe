(function() {
    'use strict';

    const MIN_DELAY = 4000;
    const MAX_DELAY = 7000;

    const LINK_LIST = [

    ];

    const STORAGE_KEY_QUEUE = 'ig_scraper_queue_v2';
    const STORAGE_KEY_RESULTS = 'ig_scraper_results_v2';
    const STORAGE_KEY_ACTIVE = 'ig_scraper_active_v2';

    const wait = ms => new Promise(r => setTimeout(r, ms));

    function getRobustCaption() {
        let caption = "";

        let h1 = document.querySelector('h1');
        if (h1 && h1.innerText.length > 5) {
            console.log("Legenda encontrada via H1");
            return h1.innerText;
        }

        let authorLink = document.querySelector('div[role="main"] ul li a[role="link"], div[role="main"] h2 a');

        if (authorLink) {
            let container = authorLink.closest('div') || authorLink.parentElement;

            let fullText = container.innerText;

            let username = authorLink.innerText;
            if (fullText.includes(username)) {
                caption = fullText.replace(username, '').trim();
                caption = caption.replace(/^\n+/, '');

                if (caption.length > 0) {
                    console.log("Legenda encontrada via Contexto do Usuário");
                    return caption;
                }
            }
        }

        let meta = document.querySelector('meta[property="og:description"]');
        if (meta) {
            let content = meta.content;

            let match = content.split(': "');
            if (match.length > 1) {
                let clean = match[1];
                if (clean.endsWith('"')) clean = clean.slice(0, -1);

                console.log("Legenda encontrada via Meta Tag (Limpa)");
                return clean;
            }
            console.log("Usando Meta Tag bruta (não conseguiu limpar)");
            return content;
        }

        return "LEGENDA NÃO ENCONTRADA";
    }

    function startScraping() {
        if (confirm(`Iniciar extração de ${LINK_LIST.length} links?`)) {
            localStorage.setItem(STORAGE_KEY_QUEUE, JSON.stringify(LINK_LIST));
            localStorage.setItem(STORAGE_KEY_RESULTS, JSON.stringify([]));
            localStorage.setItem(STORAGE_KEY_ACTIVE, 'true');
            processNext();
        }
    }

    function downloadResults() {
        const results = JSON.parse(localStorage.getItem(STORAGE_KEY_RESULTS) || '[]');
        const blob = new Blob([JSON.stringify(results, null, 2)], {type : 'application/json'});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `captions_FINAL_${new Date().getTime()}.json`;
        document.body.appendChild(a);
        a.click();

        localStorage.setItem(STORAGE_KEY_ACTIVE, 'false');
        alert('Concluído!');
    }

    async function processNext() {
        let queue = JSON.parse(localStorage.getItem(STORAGE_KEY_QUEUE) || '[]');
        if (queue.length === 0) {
            downloadResults();
            return;
        }
        let nextLink = queue.shift();
        localStorage.setItem(STORAGE_KEY_QUEUE, JSON.stringify(queue));
        window.location.href = nextLink;
    }

    async function captureCurrentPage() {
        console.log("Aguardando carregamento...");
        await wait(3500); 

        try {
            let spans = Array.from(document.querySelectorAll('span, div[role="button"]'));
            let moreBtn = spans.find(el => el.innerText.trim().toLowerCase() === 'mais' || el.innerText.trim().toLowerCase() === 'more');
            if (moreBtn) {
                console.log("Botão 'mais' encontrado, clicando...");
                moreBtn.click();
                await wait(1000);
            }
        } catch (e) {
            console.log("Erro ao tentar expandir legenda (pode já estar expandida)");
        }

        let text = getRobustCaption();
        let currentUrl = window.location.href;

        let results = JSON.parse(localStorage.getItem(STORAGE_KEY_RESULTS) || '[]');
        results.push({
            url: currentUrl,
            caption: text,
            date: new Date().toISOString()
        });
        localStorage.setItem(STORAGE_KEY_RESULTS, JSON.stringify(results));

        console.log(`Salvo (${text.substring(0, 30)}...)`);

        let delay = Math.floor(Math.random() * (MAX_DELAY - MIN_DELAY + 1) + MIN_DELAY);
        console.log(`Próximo em ${delay/1000}s...`);
        await wait(delay);
        processNext();
    }

    if (localStorage.getItem(STORAGE_KEY_ACTIVE) === 'true') {
        if (document.readyState === 'complete') captureCurrentPage();
        else window.onload = () => captureCurrentPage();
    } else {
        let btn = document.createElement('button');
        btn.innerText = "EXTRAIR";
        btn.style.position = "fixed";
        btn.style.top = "10px";
        btn.style.right = "10px";
        btn.style.zIndex = 9999;
        btn.style.padding = "15px";
        btn.style.background = "#28a745";
        btn.style.color = "white";
        btn.style.fontWeight = "bold";
        btn.style.border = "none";
        btn.style.borderRadius = "5px";
        btn.style.cursor = "pointer";
        btn.onclick = startScraping;
        document.body.appendChild(btn);
    }
})();