(function(){
  function isExternal(url){
    try { const u = new URL(url, location.href); return u.hostname !== location.hostname; }
    catch(e){ return false; }
  }

  function flashCopied(btn){
    const original = btn.innerHTML;
    btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg> Copied!';
    btn.classList.add('copied');
    setTimeout(function(){ btn.innerHTML = original; btn.classList.remove('copied'); }, 2000);
  }

  function copyText(text, btn){
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function(){ flashCopied(btn); }).catch(function(){ fallbackCopy(text, btn); });
    } else {
      fallbackCopy(text, btn);
    }
  }

  function fallbackCopy(text, btn){
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.top = '0'; ta.style.left = '0';
    document.body.appendChild(ta); ta.focus(); ta.select();
    try { if (document.execCommand('copy')) flashCopied(btn); } catch(e){}
    document.body.removeChild(ta);
  }

  document.addEventListener('DOMContentLoaded', function(){
    // Outbound click tracking (rel attributes are set server-side at build time).
    document.querySelectorAll('a[href]').forEach(function(a){
      const href = a.getAttribute('href');
      a.addEventListener('click', function(){
        if (window.gtag && isExternal(href)) {
          gtag('event','click', { 'event_category':'outbound', 'event_label': href });
        }
      });
    });

    // Copy-link buttons (data-copy holds the absolute URL).
    document.addEventListener('click', function(e){
      const btn = e.target.closest && e.target.closest('.copy-link');
      if (btn && btn.dataset.copy) { copyText(btn.dataset.copy, btn); }
    });
  });
})();
