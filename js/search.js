(function(){
  var inputs = [
    { input: document.getElementById('docsSearch'),       results: document.getElementById('docsSearchResults') },
    { input: document.getElementById('docsSearchMobile'), results: document.getElementById('docsSearchResultsMobile') }
  ].filter(function(p){ return p.input && p.results; });
  if (!inputs.length) return;

  // Determine base path for index URL and result links
  // /index.html => '', /pages/foo.html => '../'
  var base = (location.pathname.indexOf('/pages/') >= 0) ? '../' : '';

  var index = [];
  var indexReady = false;
  var pendingQuery = null;

  fetch(base + 'js/search_index.json')
    .then(function(r){ return r.json(); })
    .then(function(data){
      index = data;
      indexReady = true;
      if (pendingQuery) {
        pendingQuery();
        pendingQuery = null;
      }
    })
    .catch(function(){ /* index load failed — silent */ });

  // Also index sidebar links (navigation shortcut)
  document.querySelectorAll('.sidebar a[href]').forEach(function(a) {
    var href = a.getAttribute('href');
    if (href && href.indexOf('#') < 0 && href.indexOf('.html') >= 0) {
      index.push({
        t: a.textContent.trim(),
        id: '',
        f: href,
        c: '',
        nav: true
      });
    }
  });

  function escH(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function buildHref(item) {
    if (item.nav) return item.f;
    // item.f is repo-relative ('index.html' or 'pages/foo.html')
    // need to prepend '../' when we're on a page under /pages/
    var target = base + item.f;
    if (item.id) target += '#' + item.id;
    return target;
  }

  function doSearch(input, results) {
    var q = input.value.trim().toLowerCase();
    if (q.length < 2) { results.classList.remove('show'); results.innerHTML=''; return; }
    if (!indexReady) {
      results.innerHTML = '<div class="docs-sr-empty">Загрузка индекса…</div>';
      results.classList.add('show');
      pendingQuery = function(){ doSearch(input, results); };
      return;
    }
    var found = [];
    for (var i = 0; i < index.length && found.length < 20; i++) {
      var item = index[i];
      var title = (item.t || '').toLowerCase();
      var ctx = (item.c || '').toLowerCase();
      var inTitle = title.indexOf(q) >= 0;
      var inCtx = ctx.indexOf(q) >= 0;
      if (inTitle || inCtx) found.push({ item: item, inTitle: inTitle, inCtx: inCtx });
    }
    // title matches first
    found.sort(function(a, b){ return (b.inTitle?1:0) - (a.inTitle?1:0); });
    if (!found.length) {
      results.innerHTML = '<div class="docs-sr-empty">Ничего не найдено</div>';
      results.classList.add('show');
      return;
    }
    var html = '';
    var re = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
    for (var j = 0; j < found.length; j++) {
      var f = found[j];
      var href = buildHref(f.item);
      var ctxHtml = '';
      if (f.inCtx && f.item.c) {
        var ci = f.item.c.toLowerCase().indexOf(q);
        var start = Math.max(0, ci - 40);
        var end = Math.min(f.item.c.length, ci + q.length + 40);
        var snippet = (start > 0 ? '…' : '') + f.item.c.substring(start, end) + (end < f.item.c.length ? '…' : '');
        snippet = escH(snippet).replace(re, '<mark>$1</mark>');
        ctxHtml = '<div class="docs-sr-ctx">' + snippet + '</div>';
      }
      var section = f.item.nav ? 'Навигация' : (f.item.f || '').replace(/^pages\//,'').replace(/\.html$/,'');
      html += '<a href="' + href + '" class="docs-sr-item">'
        + '<div class="docs-sr-section">' + escH(section) + '</div>'
        + '<div class="docs-sr-title">' + escH(f.item.t).replace(re, '<mark>$1</mark>') + '</div>'
        + ctxHtml + '</a>';
    }
    results.innerHTML = html;
    results.classList.add('show');
  }

  inputs.forEach(function(pair) {
    var timer = null;
    pair.input.addEventListener('input', function() {
      clearTimeout(timer);
      timer = setTimeout(function(){ doSearch(pair.input, pair.results); }, 180);
    });
    pair.input.addEventListener('focus', function() {
      if (pair.input.value.trim().length >= 2) doSearch(pair.input, pair.results);
    });
    if (pair.input.id === 'docsSearch') {
      document.addEventListener('click', function(e) {
        if (!e.target.closest('.docs-search-wrap')) pair.results.classList.remove('show');
      });
    }
    pair.results.addEventListener('click', function(e) {
      var link = e.target.closest('.docs-sr-item');
      if (!link) return;
      pair.results.classList.remove('show');
      var overlay = document.getElementById('searchOverlay');
      if (overlay) overlay.classList.remove('open');
    });
  });
})();
