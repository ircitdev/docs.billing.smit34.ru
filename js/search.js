(function(){
  var input = document.getElementById('docsSearch');
  var results = document.getElementById('docsSearchResults');
  if (!input || !results) return;

  var index = [];
  document.querySelectorAll('h2[id], h3[id], h4').forEach(function(el) {
    var h2 = null;
    if (el.tagName === 'H2') { h2 = el; }
    else {
      var prev = el;
      while (prev = prev.previousElementSibling) {
        if (prev.tagName === 'H2') { h2 = prev; break; }
      }
    }
    var section = h2 ? h2.textContent.trim() : '';
    var next = el.nextElementSibling;
    var ctx = '';
    while (next && !['H2','H3','H4'].includes(next.tagName)) {
      ctx += ' ' + (next.textContent || '');
      if (ctx.length > 300) break;
      next = next.nextElementSibling;
    }
    index.push({
      title: el.textContent.trim(),
      id: el.id || '',
      section: section,
      ctx: ctx.trim().substring(0, 200)
    });
  });

  // Also index sidebar links for cross-page search
  document.querySelectorAll('.sidebar a[href]').forEach(function(a) {
    var href = a.getAttribute('href');
    if (href && href.indexOf('#') < 0 && href.indexOf('.html') >= 0) {
      index.push({
        title: a.textContent.trim(),
        id: '',
        section: 'Навигация',
        ctx: '',
        href: href
      });
    }
  });

  var timer = null;
  input.addEventListener('input', function() {
    clearTimeout(timer);
    timer = setTimeout(doSearch, 200);
  });
  input.addEventListener('focus', function() {
    if (input.value.trim().length >= 2) doSearch();
  });
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.docs-search-wrap')) results.classList.remove('show');
  });

  function doSearch() {
    var q = input.value.trim().toLowerCase();
    if (q.length < 2) { results.classList.remove('show'); return; }
    var found = [];
    for (var i = 0; i < index.length && found.length < 15; i++) {
      var item = index[i];
      var inTitle = item.title.toLowerCase().indexOf(q) >= 0;
      var inCtx = item.ctx.toLowerCase().indexOf(q) >= 0;
      if (inTitle || inCtx) {
        found.push({ item: item, inTitle: inTitle, inCtx: inCtx });
      }
    }
    if (!found.length) {
      results.innerHTML = '<div class="docs-sr-empty">Ничего не найдено</div>';
      results.classList.add('show');
      return;
    }
    var html = '';
    var re = new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
    for (var j = 0; j < found.length; j++) {
      var f = found[j];
      var href = f.item.href || (f.item.id ? '#' + f.item.id : '#');
      var ctxHtml = '';
      if (f.inCtx && f.item.ctx) {
        var ci = f.item.ctx.toLowerCase().indexOf(q);
        var start = Math.max(0, ci - 40);
        var end = Math.min(f.item.ctx.length, ci + q.length + 40);
        var snippet = (start > 0 ? '...' : '') + f.item.ctx.substring(start, end) + (end < f.item.ctx.length ? '...' : '');
        snippet = escH(snippet).replace(re, '<mark>$1</mark>');
        ctxHtml = '<div class="docs-sr-ctx">' + snippet + '</div>';
      }
      html += '<a href="' + href + '" class="docs-sr-item" onclick="document.getElementById(\'docsSearchResults\').classList.remove(\'show\')">'
        + '<div class="docs-sr-section">' + escH(f.item.section) + '</div>'
        + '<div class="docs-sr-title">' + escH(f.item.title) + '</div>'
        + ctxHtml + '</a>';
    }
    results.innerHTML = html;
    results.classList.add('show');
  }

  function escH(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }
})();
