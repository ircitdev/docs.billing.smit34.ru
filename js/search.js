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
  var MAX_RESULTS = 20;

  // Человеческие названия страниц: в выдаче «billing» ничего не говорит.
  // Индекс отдаёт имя в поле p; это запасной вариант для старого индекса.
  var PAGE_NAMES = {
    'index': 'Главная', 'billing': 'Биллинг', 'lk': 'Личный кабинет',
    'crm': 'CRM', 'helpdesk': 'Поддержка', 'sorm': 'СОРМ', 'stock': 'Склад',
    'api': 'API', 'equipment': 'Оборудование', 'server': 'Сервер',
    'installation': 'Установка', 'licensing': 'Лицензирование',
    'landing': 'Лендинги', 'video': 'Видеонаблюдение',
    'troubleshooting': 'Решение проблем', 'changelog': 'История изменений',
    'contacts': 'Контакты'
  };

  // Иконка раздела — та же, что у него в боковой навигации: подсказка и
  // навигация должны опознаваться одним и тем же значком.
  var PAGE_ICONS = {
    'index': 'ti-home', 'dashboard': 'ti-layout-dashboard', 'abonents': 'ti-users',
    'abonent-card': 'ti-id', 'tariffs': 'ti-receipt', 'dictionaries': 'ti-book',
    'equipment': 'ti-broadcast', 'nas-equipment': 'ti-server', 'reports': 'ti-chart-bar',
    'settings': 'ti-settings', 'settings-services': 'ti-plug', 'extras': 'ti-apps',
    'lk': 'ti-device-mobile', 'crm': 'ti-briefcase', 'helpdesk': 'ti-headset',
    'sorm': 'ti-shield-lock', 'stock': 'ti-packages', 'video': 'ti-device-cctv',
    'landing': 'ti-browser', 'api': 'ti-link', 'server': 'ti-server',
    'installation': 'ti-box', 'licensing': 'ti-file-description',
    'troubleshooting': 'ti-tool', 'changelog': 'ti-history', 'contacts': 'ti-phone',
    'billing': 'ti-file-text'
  };

  function loadIndex() {
    if (INDEX) return Promise.resolve(INDEX);
    if (loading) return loading;
    loading = fetch(indexUrl, { cache: 'default' })
      .then(function(r){ return r.json(); })
      .then(function(j){ INDEX = j.map(norm); return INDEX; })
      .catch(function(e){ console.error('search index load failed', e); return []; });
    return loading;
  }

  function escH(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  // Ё и е в запросе и в тексте должны совпадать: в документации встречается
  // и «учёт», и «учет», иначе половина разделов не находится.
  function fold(s) {
    return (s || '').toLowerCase().replace(/ё/g, 'е');
  }

  // Часть разделов названа латиницей, а ищут их русским словом.
  var SYNONYMS = {
    'радиус': 'radius', 'сорм': 'sorm', 'биллинг': 'billing',
    'апи': 'api', 'црм': 'crm', 'смс': 'sms', 'вайфай': 'wi-fi',
    'юкасса': 'yookassa', 'телеграм': 'telegram', 'айпи': 'ip',
    'вебхук': 'webhook', 'дашборд': 'dashboard', 'логин': 'login'
  };

  // Отсечение окончания: «блокировка» и «блокировки» — одно и то же слово.
  // Без этого поиск по фразе не находил разделы с другой формой слова.
  function stemOf(t) {
    if (t.length >= 7) return t.slice(0, t.length - 2);
    if (t.length >= 5) return t.slice(0, t.length - 1);
    return t;
  }

  // build 790+: индекс использует короткие ключи (t/id/f/c/p)
  // для экономии байт — нормализуем для удобства доступа.
  // t = title, id = anchor id, f = file path (pages/X.html), c = context,
  // p = человеческое имя страницы. Старые длинные ключи тоже поддерживаются.
  function norm(item) {
    var file = item.href || item.f || '';
    var slug = file.replace('pages/', '').replace('.html', '');
    var title = item.title || item.t || '';
    var ctx = item.ctx || item.c || '';
    return {
      title: title,
      ctx: ctx,
      file: file,
      anchor: item.anchor || item.id || '',
      page: item.p || PAGE_NAMES[slug] || slug,
      icon: PAGE_ICONS[slug] || 'ti-file-text',
      ftitle: fold(title),
      fctx: fold(ctx),
      fpage: fold(item.p || PAGE_NAMES[slug] || slug)
    };
  }

  function buildHref(n) {
    if (n.file && n.anchor) return hrefBase + n.file + '#' + n.anchor;
    if (n.file) return hrefBase + n.file;
    return '#';
  }

  /**
   * Оценка совпадения. Запрос делится на слова, и запись подходит, только если
   * найдено каждое слово — иначе «тариф юр лицо» выдавал бы всё про тарифы.
   * Точное вхождение всей фразы ценится выше суммы отдельных слов.
   */
  function scoreOf(n, terms, phrase) {
    var total = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i];
      var s = 0;
      var at = n.ftitle.indexOf(t);
      if (at === 0) s += 12;            // заголовок начинается с запроса
      else if (at > 0) s += 8;
      if (n.fpage.indexOf(t) >= 0) s += 3;
      if (n.fctx.indexOf(t) >= 0) s += 2;
      if (!s) {
        // слова в точной форме нет — пробуем основу и латинский синоним
        var alt = [stemOf(t)];
        if (SYNONYMS[t]) alt.push(SYNONYMS[t]);
        for (var k = 0; k < alt.length && !s; k++) {
          var a = alt[k];
          if (a === t || a.length < 3) continue;
          if (n.ftitle.indexOf(a) >= 0) s += 6;
          else if (n.fpage.indexOf(a) >= 0) s += 2;
          else if (n.fctx.indexOf(a) >= 0) s += 1;
        }
      }
      if (!s) return 0;                 // слово не найдено — запись не подходит
      total += s;
    }
    if (phrase.length > 2) {
      if (n.ftitle.indexOf(phrase) >= 0) total += 25;
      else if (n.fctx.indexOf(phrase) >= 0) total += 6;
    }
    // короткий заголовок точнее отвечает запросу, чем длинный
    total += Math.max(0, 6 - Math.floor(n.title.length / 12));
    return total;
  }

  // Экранирование спецсимволов регулярного выражения посимвольно:
  // так строка правила не зависит от того, чем её обрабатывали при правке файла.
  var RE_SPECIAL = '.*+?^${}()|[]/' + String.fromCharCode(92);
  function reEscape(s) {
    var out = '';
    for (var i = 0; i < s.length; i++) {
      var ch = s.charAt(i);
      if (RE_SPECIAL.indexOf(ch) >= 0) out += String.fromCharCode(92);
      out += ch;
    }
    return out;
  }

  function highlight(text, terms) {
    if (!terms.length) return escH(text);
    var pats = terms.map(function (t) {
      // в тексте может стоять и «е», и «ё» — подсвечиваем оба варианта
      return reEscape(t).replace(/е/g, '[её]');
    });
    var re = new RegExp('(' + pats.join('|') + ')', 'gi');
    // экранируем по кускам, чтобы теги <mark> не попали под экранирование
    var out = '', last = 0, m;
    while ((m = re.exec(text)) !== null) {
      if (!m[0].length) { re.lastIndex++; continue; }
      out += escH(text.slice(last, m.index)) + '<mark>' + escH(m[0]) + '</mark>';
      last = m.index + m[0].length;
    }
    return out + escH(text.slice(last));
  }

  function snippetOf(n, terms) {
    if (!n.ctx) return '';
    var at = -1;
    for (var i = 0; i < terms.length && at < 0; i++) at = n.fctx.indexOf(terms[i]);
    var text;
    // Ведущее многоточие убрано: строка и так начинается с обрыва, а лишний
    // символ шумит в каждом результате.
    if (at >= 0) {
      var start = Math.max(0, at - 30);
      var end = Math.min(n.ctx.length, at + 80);
      text = n.ctx.substring(start, end) + (end < n.ctx.length ? '…' : '');
    } else {
      text = n.ctx.substring(0, 90) + (n.ctx.length > 90 ? '…' : '');
    }
    return highlight(text, terms);
  }

  function render(found, terms, results, totalCount) {
    if (!found.length) {
      results.innerHTML = '<div class="docs-sr-empty">Ничего не найдено</div>';
      results.classList.add('show');
      return;
    }
    var html = '';
    for (var j = 0; j < found.length; j++) {
      var n = found[j];
      var ctx = snippetOf(n, terms);
      html += '<a href="' + buildHref(n) + '" class="docs-sr-item">'
        + '<span class="docs-sr-ico"><i class="ti ' + n.icon + '" aria-hidden="true"></i></span>'
        + '<span class="docs-sr-main">'
        + '<span class="docs-sr-title">' + highlight(n.title, terms) + '</span>'
        + '<span class="docs-sr-ctx"><b class="docs-sr-sec">' + escH(n.page) + '</b>'
        + (ctx ? ' · ' + ctx : '') + '</span>'
        + '</span></a>';
    }
    if (totalCount > found.length) {
      html += '<div class="docs-sr-more">Показано ' + found.length +
              ' из ' + totalCount + ' — уточните запрос</div>';
    }
    results.innerHTML = html;
    results.classList.add('show');
  }

  function doSearch(input, results) {
    var raw = input.value.trim();
    if (raw.length < 2) { results.classList.remove('show'); results.innerHTML = ''; return; }
    var phrase = fold(raw);
    var terms = phrase.split(/\s+/).filter(function(t){ return t.length > 1; });
    if (!terms.length) terms = [phrase];

    // для подсветки берём и основы: в тексте слово стоит в другой форме
    var marks = terms.slice();
    terms.forEach(function (t) {
      var st = stemOf(t);
      if (st !== t && st.length >= 3) marks.push(st);
      if (SYNONYMS[t]) marks.push(SYNONYMS[t]);
    });

    loadIndex().then(function(idx) {
      var found = [];
      // Индекс просматривается целиком: раньше цикл обрывался на 20-м
      // совпадении ДО сортировки, и наверх попадали не лучшие ответы,
      // а те, что раньше встретились в файле.
      for (var i = 0; i < idx.length; i++) {
        var s = scoreOf(idx[i], terms, phrase);
        if (s > 0) { idx[i]._s = s; found.push(idx[i]); }
      }
      // Ни одна запись не содержит всех слов — показываем те, где есть хотя бы
      // одно: пустая выдача по осмысленному запросу бесполезнее неточной.
      if (!found.length && terms.length > 1) {
        for (var j = 0; j < idx.length; j++) {
          var best = 0;
          for (var m = 0; m < terms.length; m++) {
            best = Math.max(best, scoreOf(idx[j], [terms[m]], terms[m]));
          }
          if (best > 0) { idx[j]._s = best; found.push(idx[j]); }
        }
      }
      found.sort(function(a, b){ return b._s - a._s; });
      render(found.slice(0, MAX_RESULTS), marks, results, found.length);
    });
  }

  // --- перемещение по результатам с клавиатуры ---
  function moveSelection(results, delta) {
    var items = results.querySelectorAll('.docs-sr-item');
    if (!items.length) return false;
    var cur = -1;
    for (var i = 0; i < items.length; i++) {
      if (items[i].classList.contains('sel')) { cur = i; break; }
    }
    if (cur >= 0) items[cur].classList.remove('sel');
    var next = cur < 0 ? (delta > 0 ? 0 : items.length - 1)
                       : (cur + delta + items.length) % items.length;
    items[next].classList.add('sel');
    items[next].scrollIntoView({ block: 'nearest' });
    return true;
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
    pair.input.addEventListener('keydown', function(e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        if (moveSelection(pair.results, e.key === 'ArrowDown' ? 1 : -1)) e.preventDefault();
      } else if (e.key === 'Enter') {
        var sel = pair.results.querySelector('.docs-sr-item.sel') ||
                  pair.results.querySelector('.docs-sr-item');
        if (sel) { e.preventDefault(); sel.click(); }
      } else if (e.key === 'Escape') {
        pair.results.classList.remove('show');
      }
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
