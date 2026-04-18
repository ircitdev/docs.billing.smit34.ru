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

  function render(found, q, results) {
    if (!found.length) {
      results.innerHTML = '<div class="docs-sr-empty">Ничего не найдено</div>';
      results.classList.add('show');
      return;
    }
    var re = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
    var html = '';
    for (var j = 0; j < found.length; j++) {
      var f = found[j];
      var item = f.item;
      var href = hrefBase + item.href;
      var ctxHtml = '';
      if (item.ctx) {
        var ci = item.ctx.toLowerCase().indexOf(q);
        var snippet;
        if (ci >= 0) {
          var start = Math.max(0, ci - 40);
          var end = Math.min(item.ctx.length, ci + q.length + 60);
          snippet = (start > 0 ? '…' : '') + item.ctx.substring(start, end) + (end < item.ctx.length ? '…' : '');
        } else {
          snippet = item.ctx.substring(0, 100) + (item.ctx.length > 100 ? '…' : '');
        }
        ctxHtml = '<div class="docs-sr-ctx">' + escH(snippet).replace(re, '<mark>$1</mark>') + '</div>';
      }
      var sectionLine = item.section;
      if (item.page && item.page !== item.section) {
        sectionLine = item.page + ' / ' + item.section;
      }
      html += '<a href="' + href + '" class="docs-sr-item">'
        + '<div class="docs-sr-section">' + escH(sectionLine) + '</div>'
        + '<div class="docs-sr-title">' + escH(item.title).replace(re, '<mark>$1</mark>') + '</div>'
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
      for (var i = 0; i < idx.length && found.length < 20; i++) {
        var item = idx[i];
        var score = 0;
        if (item.title && item.title.toLowerCase().indexOf(q) >= 0) score += 5;
        if (item.section && item.section.toLowerCase().indexOf(q) >= 0) score += 2;
        if (item.page && item.page.toLowerCase().indexOf(q) >= 0) score += 2;
        if (item.ctx && item.ctx.toLowerCase().indexOf(q) >= 0) score += 1;
        if (score > 0) found.push({ item: item, score: score });
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
