(function(){
  var inputs = [
    { input: document.getElementById('docsSearch'),       results: document.getElementById('docsSearchResults') },
    { input: document.getElementById('docsSearchMobile'), results: document.getElementById('docsSearchResultsMobile') }
  ].filter(function(p){ return p.input && p.results; });
  if (!inputs.length) return;

  // Determine base path to /search-index.json and for relative hrefs
  // Docs pages live at /pages/X.html or /index.html
  var path = location.pathname;
  var isPage = path.indexOf('/pages/') >= 0;
  var indexUrl = (isPage ? '../' : './') + 'search-index.json';
  var hrefBase = isPage ? '../' : './';

  var INDEX = null;
  var loading = null;

  function loadIndex() {
    if (INDEX) return Promise.resolve(INDEX);
    if (loading) return loading;
    loading = fetch(indexUrl, { cache: 'default' })
      .then(function(r){ return r.json(); })
      .then(function(j){ INDEX = j; return j; })
      .catch(function(e){ console.error('search index load failed', e); return []; });
    return loading;
  }

  function escH(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  // build 790+: индекс использует короткие ключи (t/id/f/c)
  // для экономии байт — нормализуем для удобства доступа.
  // t = title, id = anchor id, f = file path (pages/X.html), c = context.
  // Старые длинные ключи (title/section/page/href/ctx) тоже поддерживаются
  // на случай миграции.
  function norm(item) {
    return {
      title: item.title || item.t || '',
      ctx:   item.ctx   || item.c || '',
      file:  item.href  || item.f || '',
      anchor: item.anchor || item.id || '',
      // section/page deprecated — выводим page из file path
      page:  item.page  || (item.f ? item.f.replace('pages/', '').replace('.html', '') : ''),
      section: item.section || item.title || item.t || ''
    };
  }

  function buildHref(n) {
    if (n.file && n.anchor) return hrefBase + n.file + '#' + n.anchor;
    if (n.file) return hrefBase + n.file;
    return '#';
  }

  function render(found, q, results) {
    if (!found.length) {
      results.innerHTML = '<div class="docs-sr-empty">Ничего не найдено</div>';
      results.classList.add('show');
      return;
    }
    var re = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
    var html = '';
    for (var j = 0; j < found.length; j++) {
      var n = found[j].item; // уже нормализовано
      var href = buildHref(n);
      var ctxHtml = '';
      if (n.ctx) {
        var ci = n.ctx.toLowerCase().indexOf(q);
        var snippet;
        if (ci >= 0) {
          var start = Math.max(0, ci - 40);
          var end = Math.min(n.ctx.length, ci + q.length + 60);
          snippet = (start > 0 ? '…' : '') + n.ctx.substring(start, end) + (end < n.ctx.length ? '…' : '');
        } else {
          snippet = n.ctx.substring(0, 100) + (n.ctx.length > 100 ? '…' : '');
        }
        ctxHtml = '<div class="docs-sr-ctx">' + escH(snippet).replace(re, '<mark>$1</mark>') + '</div>';
      }
      var sectionLine = n.section;
      if (n.page && n.page !== n.section) {
        sectionLine = n.page + ' / ' + n.section;
      }
      html += '<a href="' + href + '" class="docs-sr-item">'
        + '<div class="docs-sr-section">' + escH(sectionLine) + '</div>'
        + '<div class="docs-sr-title">' + escH(n.title).replace(re, '<mark>$1</mark>') + '</div>'
        + ctxHtml + '</a>';
    }
    results.innerHTML = html;
    results.classList.add('show');
  }

  function doSearch(input, results) {
    var q = input.value.trim().toLowerCase();
    if (q.length < 2) { results.classList.remove('show'); results.innerHTML = ''; return; }
    loadIndex().then(function(idx) {
      var found = [];
      for (var i = 0; i < idx.length; i++) {
        var n = norm(idx[i]);
        var score = 0;
        if (n.title && n.title.toLowerCase().indexOf(q) >= 0) score += 5;
        if (n.section && n.section.toLowerCase().indexOf(q) >= 0) score += 2;
        if (n.page && n.page.toLowerCase().indexOf(q) >= 0) score += 2;
        if (n.ctx && n.ctx.toLowerCase().indexOf(q) >= 0) score += 1;
        if (score > 0) found.push({ item: n, score: score });
        if (found.length >= 20) break;
      }
      found.sort(function(a, b){ return b.score - a.score; });
      render(found, q, results);
    });
  }

  inputs.forEach(function(pair) {
    var timer = null;
    pair.input.addEventListener('input', function() {
      clearTimeout(timer);
      timer = setTimeout(function(){ doSearch(pair.input, pair.results); }, 150);
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

  // Pre-load index on first focus
  document.querySelector('#docsSearch, #docsSearchMobile')?.addEventListener('focus', loadIndex, { once: true });
})();
