(async function() {
    console.clear();
    console.log("%c EXTRATOR DE REELS (DM)", "color: #00ff00; font-size: 16px; font-weight: bold;");

    let collectedLinks = new Set();
    
    const TIME_TO_OPEN = 2500; 
    const TIME_TO_CLOSE = 1000;  
    const AUTO_CONVERT = true;  

    let allImages = Array.from(document.querySelectorAll('img'));
    let candidateThumbnails = allImages.filter(img => img.clientWidth > 100 && img.clientHeight > 100);

    console.log(`%c📸 Encontradas ${candidateThumbnails.length} miniaturas. Verificando quais são vídeos...`, "color: cyan");

    for (let i = 0; i < candidateThumbnails.length; i++) {
        let img = candidateThumbnails[i];
        
        img.scrollIntoView({behavior: "auto", block: "center"});
        await new Promise(r => setTimeout(r, 300)); 

        console.log(`➡️ [${i+1}/${candidateThumbnails.length}] Abrindo mídia...`);
        try {
            img.click();
        } catch (e) {
            console.log("Erro ao clicar, pulando...");
            continue;
        }

        await new Promise(r => setTimeout(r, TIME_TO_OPEN));

        let currentUrl = window.location.href;
        let isVideoTagPresent = document.querySelector('video') !== null;
        
        if (currentUrl.includes('/reel/') || (currentUrl.includes('/p/') && isVideoTagPresent)) {
            
            let cleanUrl = currentUrl.split('?')[0];

            if (AUTO_CONVERT && cleanUrl.includes('/p/')) {
                cleanUrl = cleanUrl.replace('/p/', '/reel/');
            }
            
            if (!collectedLinks.has(cleanUrl)) {
                collectedLinks.add(cleanUrl);
                console.log(`%c REEL CAPTURADO: ${cleanUrl}`, "color: #0f0; font-weight: bold;");
            } else {
                console.log(`Duplicado.`);
            }
        } else {
            console.log(`Ignorado (É foto ou não carregou). URL: ${currentUrl}`);
        }

        let closeButton = document.querySelector('svg[aria-label="Fechar"]');
        if (closeButton) {
            closeButton.closest('div[role="button"]').click();
        } else {
            document.body.dispatchEvent(new KeyboardEvent('keydown', {'key': 'Escape', 'code': 'Escape', 'keyCode': 27, 'which': 27, 'bubbles': true}));
        }

        await new Promise(r => setTimeout(r, TIME_TO_CLOSE));
    }

    console.log("%cFIM DO PROCESSO", "color: yellow; font-size: 16px;");
    console.log(`Total de Reels únicos: ${collectedLinks.size}`);
    
    let finalText = Array.from(collectedLinks).join('\n');
    console.log(finalText);

    if (collectedLinks.size > 0) {
        let blob = new Blob([finalText], { type: 'text/plain' });
        let a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `reels_dm_extracao_${new Date().getTime()}.txt`;
        document.body.appendChild(a);
        a.click();
        console.log("Arquivo TXT baixado.");
    }
})();