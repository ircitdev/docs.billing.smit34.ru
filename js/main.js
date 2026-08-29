// СмИТ Биллинг 1.0 Docs — navigation + theme toggle + submenu
document.addEventListener('DOMContentLoaded', function () {

  // --- Header logo click → smooth scroll to top ---
  var headerLogo = document.querySelector('header.header .logo');
  if (headerLogo) {
    headerLogo.classList.add('logo-scroll-top');
    headerLogo.style.cursor = 'pointer';
    headerLogo.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // --- Theme toggle ---
  var html = document.documentElement;
  var saved = localStorage.getItem('smit-docs-theme');
  var mq = window.matchMedia('(prefers-color-scheme: dark)');
  var theme = saved || (mq.matches ? 'dark' : 'light');
  html.setAttribute('data-theme', theme);

  // Пока пользователь не выбрал тему сам, документация следует за системой —
  // в том числе если та переключается на ходу (по расписанию дня и ночи).
  var onSystemTheme = function (e) {
    if (localStorage.getItem('smit-docs-theme')) return;
    html.setAttribute('data-theme', e.matches ? 'dark' : 'light');
  };
  if (mq.addEventListener) mq.addEventListener('change', onSystemTheme);
  else if (mq.addListener) mq.addListener(onSystemTheme);

  var toggleBtn = document.querySelector('.theme-toggle');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      var current = html.getAttribute('data-theme');
      var next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('smit-docs-theme', next);
    });

  // Sidebar theme toggle (mobile)
  var sidebarTheme = document.querySelector('.sidebar-theme-toggle');
  if (sidebarTheme) {
    sidebarTheme.addEventListener('click', function () {
      var current = html.getAttribute('data-theme');
      var next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('smit-docs-theme', next);
    });
  }

  }

  // --- Mobile sidebar toggle ---
  var toggle = document.querySelector('.menu-toggle');
  var sidebar = document.querySelector('.sidebar');
  var backdrop = document.getElementById('sidebarBackdrop');
  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('open');
    document.body.classList.remove('sidebar-open');
  }
  function openSidebar() {
    if (sidebar) sidebar.classList.add('open');
    if (backdrop) backdrop.classList.add('open');
    // меню перекрывает страницу целиком — фон под ним не прокручиваем
    document.body.classList.add('sidebar-open');
  }
  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      if (sidebar.classList.contains('open')) closeSidebar(); else openSidebar();
    });
    if (backdrop) backdrop.addEventListener('click', closeSidebar);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidebar.classList.contains('open')) closeSidebar();
    });
    // переход по ссылке-якорю страницу не перезагружает — закрываем меню сами
    sidebar.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a') : null;
      if (a && a.getAttribute('href') && !a.querySelector('.arrow')) closeSidebar();
    });
    var contentEl = document.querySelector('.content');
    if (contentEl) contentEl.addEventListener('click', closeSidebar);
  }

  // --- Mobile search overlay ---
  var searchBtn = document.querySelector('.mobile-search-btn');
  var overlay = document.getElementById('searchOverlay');
  var overlayClose = document.getElementById('searchOverlayClose');
  var overlayInput = document.getElementById('docsSearchMobile');
  function openOverlay() {
    if (!overlay) return;
    overlay.classList.add('open');
    // страница под поиском не должна уезжать вместе с пальцем
    document.body.classList.add('search-open');
    setTimeout(function(){ if (overlayInput) overlayInput.focus(); }, 50);
  }
  function closeOverlay() {
    if (!overlay) return;
    overlay.classList.remove('open');
    document.body.classList.remove('search-open');
    if (overlayInput) { overlayInput.value = ''; overlayInput.dispatchEvent(new Event('input')); }
  }
  if (searchBtn) searchBtn.addEventListener('click', openOverlay);
  if (overlayClose) overlayClose.addEventListener('click', closeOverlay);
  if (overlay) {
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) closeOverlay();
    });
  }
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && overlay && overlay.classList.contains('open')) closeOverlay();
  });

  // --- Mark active nav link & auto-open submenu ---
  var path = location.pathname;
  var hash = location.hash;

  function getFilename(href) {
    if (!href) return '';
    var h = href.split('#')[0];
    h = h.replace(/^\.\.\//, '').replace(/^pages\//, '');
    return h;
  }

  var currentFile = path.split('/').pop() || 'index.html';

  // Mark top-level page links active and open their submenu
  document.querySelectorAll('.sidebar nav > ul > li').forEach(function (li) {
    var mainLink = li.querySelector(':scope > a');
    if (!mainLink) return;
    var linkFile = getFilename(mainLink.getAttribute('href'));

    if (linkFile === currentFile) {
      mainLink.classList.add('active');
      if (li.classList.contains('has-children')) {
        li.classList.add('open');
      }
    }
  });

  // Mark submenu links active if hash matches
  if (hash) {
    document.querySelectorAll('.sidebar .submenu a').forEach(function (a) {
      var href = a.getAttribute('href');
      if (!href) return;
      var linkFile = getFilename(href);
      var linkHash = href.indexOf('#') !== -1 ? '#' + href.split('#')[1] : '';
      if (linkFile === currentFile && linkHash === hash) {
        a.classList.add('active');
      }
    });
  }

  // --- Sub-item toggle: show sub-items only for the active/clicked section ---
  function showSubItemsFor(sectionLi) {
    // Hide all sub-items in same submenu
    var submenu = sectionLi.closest('ul.submenu');
    if (!submenu) return;
    submenu.querySelectorAll('li.sub-item').forEach(function (si) {
      si.classList.remove('visible');
    });
    // Show sub-items that follow this section li until next non-sub-item
    var next = sectionLi.nextElementSibling;
    while (next && next.classList.contains('sub-item')) {
      next.classList.add('visible');
      next = next.nextElementSibling;
    }
  }

  // On page load: determine which section is active (by hash or first section)
  var activeSectionLi = null;
  document.querySelectorAll('.sidebar ul.submenu > li:not(.sub-item)').forEach(function (li) {
    var a = li.querySelector('a');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var linkFile = getFilename(href);
    var linkHash = href.indexOf('#') !== -1 ? '#' + href.split('#')[1] : '';

    if (linkFile === currentFile && hash && linkHash === hash) {
      activeSectionLi = li;
    }
  });

  // Also check if hash matches a sub-item — activate its parent section
  if (!activeSectionLi && hash) {
    document.querySelectorAll('.sidebar ul.submenu > li.sub-item').forEach(function (si) {
      var a = si.querySelector('a');
      if (!a) return;
      var href = a.getAttribute('href') || '';
      var linkHash = href.indexOf('#') !== -1 ? '#' + href.split('#')[1] : '';
      if (linkHash === hash) {
        // Find parent section (previous non-sub-item sibling)
        var prev = si.previousElementSibling;
        while (prev && prev.classList.contains('sub-item')) {
          prev = prev.previousElementSibling;
        }
        if (prev) activeSectionLi = prev;
      }
    });
  }

  if (activeSectionLi) {
    showSubItemsFor(activeSectionLi);
  }

  // Click handler: toggle sub-items when clicking a section header in submenu
  document.querySelectorAll('.sidebar ul.submenu > li:not(.sub-item) > a').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var li = this.parentElement;
      var href = this.getAttribute('href') || '';
      var linkFile = getFilename(href);

      // If same page, toggle sub-items without navigation
      if (linkFile === currentFile) {
        // Check if sub-items are already visible
        var nextSib = li.nextElementSibling;
        var hasVisible = nextSib && nextSib.classList.contains('sub-item') && nextSib.classList.contains('visible');

        if (hasVisible) {
          // Hide them (collapse)
          var n = li.nextElementSibling;
          while (n && n.classList.contains('sub-item')) {
            n.classList.remove('visible');
            n = n.nextElementSibling;
          }
        } else {
          showSubItemsFor(li);
        }
        // Don't prevent default — let browser scroll to hash
      }
    });
  });

  // --- Top-level submenu toggle on click ---
  document.querySelectorAll('.sidebar nav > ul > li.has-children > a').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var li = this.parentElement;
      var linkFile = getFilename(this.getAttribute('href'));

      if (linkFile === currentFile) {
        e.preventDefault();
        li.classList.toggle('open');
      }
    });
  });

  // --- Password gate for protected-section blocks (client-side veneer) ---
  // data-gate="staff" requires password "smit888billing"; unlock cached in sessionStorage.
  (function initProtected() {
    var GATES = {
      // SHA-256("smit888billing")
      staff: 'e634c311c9418f8f1dad40b33e99718f94a15ac68aff46777af331318f1f5659'
    };
    var sections = document.querySelectorAll('.protected-section[data-gate]');
    if (!sections.length) return;

    async function sha256(s) {
      if (!crypto || !crypto.subtle) return '';
      var buf = new TextEncoder().encode(s);
      var hashBuf = await crypto.subtle.digest('SHA-256', buf);
      return Array.from(new Uint8Array(hashBuf)).map(function(b){ return b.toString(16).padStart(2,'0'); }).join('');
    }

    function unlock(section) {
      section.classList.add('unlocked');
      var cover = section.querySelector('.protected-cover');
      if (cover) cover.remove();
    }

    // Also flag body if staff gate is unlocked (enables visible "staff-only" sidebar items)
    if (sessionStorage.getItem('docs-gate-staff') === '1') {
      document.body.classList.add('docs-staff-unlocked');
    }

    sections.forEach(function(section) {
      var gate = section.dataset.gate;
      var expected = GATES[gate];
      if (!expected) return;
      // Already unlocked in this session?
      if (sessionStorage.getItem('docs-gate-' + gate) === '1') {
        unlock(section);
        return;
      }
      // Build cover UI
      var title = section.dataset.gateTitle || 'Закрытый раздел';
      var hint  = section.dataset.gateHint  || 'Введите пароль для продолжения.';
      var cover = document.createElement('div');
      cover.className = 'protected-cover';
      cover.innerHTML =
        '<div class="protected-cover-inner">' +
          '<div class="protected-icon"><i class="ti ti-shield-lock"></i></div>' +
          '<h3>' + title + '</h3>' +
          '<p>' + hint + '</p>' +
          '<form class="protected-form" autocomplete="off">' +
            '<input type="password" placeholder="Пароль" autocomplete="new-password" required>' +
            '<button type="submit"><i class="ti ti-lock-open"></i> Открыть</button>' +
          '</form>' +
          '<div class="protected-error" hidden>Неверный пароль</div>' +
        '</div>';
      section.appendChild(cover);
      var form = cover.querySelector('form');
      var input = form.querySelector('input');
      var err   = cover.querySelector('.protected-error');
      form.addEventListener('submit', async function(e) {
        e.preventDefault();
        var hex = await sha256(input.value);
        if (hex === expected) {
          sessionStorage.setItem('docs-gate-' + gate, '1');
          if (gate === 'staff') document.body.classList.add('docs-staff-unlocked');
          unlock(section);
        } else {
          err.hidden = false;
          input.value = '';
          input.focus();
          setTimeout(function(){ err.hidden = true; }, 2500);
        }
      });
    });
  })();

  // --- Copy-to-clipboard helper with toast ---
  function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); resolve(); } catch (e) { reject(e); }
      document.body.removeChild(ta);
    });
  }

  function showToast(message) {
    var t = document.createElement('div');
    t.className = 'docs-toast';
    t.textContent = message;
    document.body.appendChild(t);
    setTimeout(function () { t.classList.add('show'); }, 10);
    setTimeout(function () {
      t.classList.remove('show');
      setTimeout(function () { t.remove(); }, 250);
    }, 1600);
  }

  // --- Copy button on code blocks ---
  // Схемы и карты мыслей тоже лежат в <pre>, но кодом не являются: панель
  // «CODE · Копировать» над диаграммой выглядит ошибкой вёрстки.
  document.querySelectorAll('.content pre:not(.mermaid):not(.markmap)').forEach(function (pre) {
    // Wrap pre in .code-block if not already
    if (pre.parentElement.classList.contains('code-block')) return;
    var wrap = document.createElement('div');
    wrap.className = 'code-block';
    pre.parentNode.insertBefore(wrap, pre);
    wrap.appendChild(pre);

    // Detect language hint from first comment line (bash/python/sql)
    var codeEl = pre.querySelector('code');
    var text = codeEl ? codeEl.textContent : pre.textContent;
    var lang = '';
    if (/^\s*#!?\//.test(text) || /\bgit\s|\bdocker\s|\bcp\s|\bcd\s/.test(text.slice(0, 200))) lang = 'bash';
    else if (/^\s*SELECT\s|^\s*INSERT\s|^\s*UPDATE\s/im.test(text)) lang = 'sql';
    else if (/\bdef\s|\bimport\s|print\(/.test(text.slice(0, 300))) lang = 'python';

    var bar = document.createElement('div');
    bar.className = 'code-block-bar';
    bar.innerHTML = '<span class="code-block-lang">' + (lang || 'code') + '</span>' +
      '<button class="code-copy-btn" type="button" title="Скопировать в буфер"><i class="ti ti-clipboard"></i><span> Копировать</span></button>';
    wrap.insertBefore(bar, pre);

    bar.querySelector('.code-copy-btn').addEventListener('click', function () {
      var btn = this;
      copyToClipboard(text).then(function () {
        btn.classList.add('copied');
        btn.querySelector('i').className = 'ti ti-check';
        btn.querySelector('span').textContent = ' Скопировано';
        setTimeout(function () {
          btn.classList.remove('copied');
          btn.querySelector('i').className = 'ti ti-clipboard';
          btn.querySelector('span').textContent = ' Копировать';
        }, 1600);
      });
    });
  });

  // --- Широкие таблицы листаются внутри своей рамки ---
  // Без обёртки таблица шире колонки выталкивала вбок всю страницу.
  document.querySelectorAll('.content table').forEach(function (table) {
    if (table.parentElement.classList.contains('table-scroll')) return;
    var box = document.createElement('div');
    box.className = 'table-scroll';
    table.parentNode.insertBefore(box, table);
    box.appendChild(table);

    // тень у правого края — только пока есть что листать
    function hint() {
      var more = box.scrollWidth - box.clientWidth - box.scrollLeft > 4;
      box.classList.toggle('has-overflow', more);
    }
    box.addEventListener('scroll', hint, { passive: true });
    window.addEventListener('resize', hint);
    hint();
  });

  // --- Numeric badge before section H2/H3 headings ---
  // Heading text like "1. Принцип работы" or "9.7. Адреса" -> show badge with "1" / "9.7"
  document.querySelectorAll('.content h2[id], .content h3[id]').forEach(function (h) {
    // Skip if already has a badge
    if (h.querySelector('.heading-badge')) return;
    var text = h.textContent.trim();
    var m = text.match(/^(\d+(?:[.А]\d*)*)\.\s+(.+)$/);
    if (!m) return;
    var num = m[1];
    var label = m[2];
    var badge = document.createElement('span');
    badge.className = 'heading-badge';
    badge.textContent = num;
    // Rebuild the heading: badge + label, preserve existing share button if present
    var share = h.querySelector('.heading-share');
    // Clear text nodes only, keep share btn
    while (h.firstChild) h.removeChild(h.firstChild);
    h.appendChild(badge);
    h.appendChild(document.createTextNode(' ' + label));
    if (share) h.appendChild(share);
  });

  // --- Share button on headings with id ---
  document.querySelectorAll('.content h1[id], .content h2[id], .content h3[id], .content h4[id]').forEach(function (h) {
    var btn = document.createElement('button');
    btn.className = 'heading-share';
    btn.type = 'button';
    btn.title = 'Скопировать ссылку на раздел';
    btn.setAttribute('aria-label', 'Поделиться ссылкой на раздел');
    btn.innerHTML = '<i class="ti ti-link"></i>';
    h.appendChild(btn);
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var url = location.origin + location.pathname + '#' + h.id;
      copyToClipboard(url).then(function () {
        showToast('Ссылка скопирована');
        btn.classList.add('copied');
        setTimeout(function () { btn.classList.remove('copied'); }, 1500);
        // Update URL hash without scrolling
        if (history.replaceState) history.replaceState(null, '', '#' + h.id);
      });
    });
  });

  // ═══════════ Dynamic Island TOC — мобильная навигация по разделам ═══════════
  // Капсула внизу по центру (только ≤768px): свёрнута — активный раздел + кольцо
  // прогресса чтения; развёрнута — список h2-разделов страницы. Строится из DOM.
  (function initDocsIsland() {
    // Остров нужен там, где страница длинная. Раньше здесь стоял список из
    // четырёх файлов; после разбиения раздела биллинга на десять страниц он
    // перестал совпадать с реальностью. Решает сама страница: мало разделов —
    // острова не будет (проверка headings.length ниже).

    // Чистый текст заголовка: без badge-числа и без share-кнопки
    function headingText(h) {
      var clone = h.cloneNode(true);
      clone.querySelectorAll('.heading-badge, .heading-share').forEach(function (el) {
        el.remove();
      });
      return clone.textContent.trim().replace(/\s+/g, ' ');
    }
    function esc(s) {
      return s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
    }

    // Собрать разделы ВЕРХНЕГО УРОВНЯ страницы. Структура различается:
    //   • api/sorm/crm/stock — разделы это h2, h3 внутри них подразделы;
    //   • dashboard/settings/abonents и прочие после разбиения биллинга —
    //     один h2 (заголовок страницы) и 12–18 h3-разделов.
    // Отсюда правило: h2 достаточно много — идём по ним; иначе разделы
    // страницы это h3, и берём h2 и h3 в порядке документа.
    var h2list = Array.prototype.slice.call(
      document.querySelectorAll('.content h2[id]')
    );
    var headings = h2list.length >= 3 ? h2list : Array.prototype.slice.call(
      document.querySelectorAll('.content h2[id], .content h3[id]')
    );
    if (headings.length < 3) return;  // слишком мало разделов — остров не нужен

    // entries: { id, el, label } — пункты навигации (для scrollspy/прогресса)
    var entries = headings.map(function (h) {
      return { id: h.id, el: h, label: headingText(h) };
    });
    var listHtml = entries.map(function (it) {
      return '<li><a href="#' + it.id + '">' + esc(it.label) + '</a></li>';
    }).join('');

    // --- Разметка острова (создаётся скриптом, HTML-страницы не трогаем) ---
    var backdrop = document.createElement('div');
    backdrop.className = 'docs-island-backdrop';

    var island = document.createElement('nav');
    island.className = 'docs-island';
    island.setAttribute('aria-label', 'Навигация по разделам страницы');

    island.innerHTML =
      '<div class="docs-island-pill" role="button" tabindex="0" ' +
        'aria-expanded="false" aria-controls="docsIslandPanel" ' +
        'aria-label="Оглавление страницы">' +
        '<span class="docs-island-ring">' +
          '<span class="docs-island-num">01</span></span>' +
        '<span class="docs-island-label"></span>' +
        '<span class="docs-island-caret" aria-hidden="true">▲</span>' +
      '</div>' +
      '<div class="docs-island-panel" id="docsIslandPanel">' +
        '<div class="docs-island-progress" aria-hidden="true">' +
          '<div class="docs-island-progress-bar"></div></div>' +
        '<ol class="docs-island-list">' + listHtml + '</ol>' +
      '</div>';

    document.body.appendChild(backdrop);
    document.body.appendChild(island);

    var pill = island.querySelector('.docs-island-pill');
    var ring = island.querySelector('.docs-island-ring');
    var numEl = island.querySelector('.docs-island-num');
    var labelEl = island.querySelector('.docs-island-label');
    var barEl = island.querySelector('.docs-island-progress-bar');
    var links = Array.prototype.slice.call(
      island.querySelectorAll('.docs-island-list a')
    );

    // --- Открыть / закрыть ---
    function openIsland() {
      island.classList.add('open');
      pill.setAttribute('aria-expanded', 'true');
      backdrop.classList.add('show');
    }
    function closeIsland() {
      island.classList.remove('open');
      pill.setAttribute('aria-expanded', 'false');
      backdrop.classList.remove('show');
    }
    function toggleIsland() {
      island.classList.contains('open') ? closeIsland() : openIsland();
    }
    pill.addEventListener('click', toggleIsland);
    pill.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleIsland(); }
    });
    backdrop.addEventListener('click', closeIsland);
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && island.classList.contains('open')) closeIsland();
    });

    // --- Клик по разделу: плавный скролл + закрыть остров ---
    links.forEach(function (link) {
      link.addEventListener('click', function (e) {
        var id = this.getAttribute('href').slice(1);
        var target = document.getElementById(id);
        if (!target) return;
        e.preventDefault();
        var headerH = 56;  // --header-height
        var top = target.getBoundingClientRect().top + window.pageYOffset - headerH - 8;
        window.scrollTo({ top: top, behavior: 'smooth' });
        closeIsland();
        if (history.replaceState) history.replaceState(null, '', '#' + id);
      });
    });

    // --- Прогресс чтения страницы → кольцо в пилюле + полоса в панели ---
    function updateProgress() {
      var docH = document.documentElement.scrollHeight - window.innerHeight;
      var pct = docH > 0
        ? Math.min(100, Math.max(0, (window.pageYOffset / docH) * 100))
        : 0;
      ring.style.setProperty('--di-progress', pct.toFixed(1));
      barEl.style.width = pct.toFixed(1) + '%';
    }
    window.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress);
    updateProgress();

    // --- Scrollspy: подсветка активного раздела ---
    function setActive(id) {
      var activeLink = null;
      links.forEach(function (l) {
        var on = l.getAttribute('href') === '#' + id;
        l.classList.toggle('active', on);
        if (on) activeLink = l;
      });
      if (!activeLink) return;
      var idx = links.indexOf(activeLink) + 1;
      numEl.textContent = idx < 10 ? '0' + idx : String(idx);
      labelEl.textContent = activeLink.textContent;
      if (island.classList.contains('open')) {
        activeLink.scrollIntoView({ block: 'nearest' });
      }
    }
    // Стартовое значение — первый раздел
    setActive(entries[0].id);

    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function (obsEntries) {
        var topMost = null;
        obsEntries.forEach(function (entry) {
          if (entry.isIntersecting &&
              (!topMost || entry.boundingClientRect.top < topMost.boundingClientRect.top)) {
            topMost = entry;
          }
        });
        if (topMost) setActive(topMost.target.id);
      }, { rootMargin: '-64px 0px -55% 0px', threshold: 0 });
      entries.forEach(function (it) { obs.observe(it.el); });
    }
  })();
  /* ── Правый рельс «На этой странице» ──────────────────────────────────
   * На длинной странице оглавление в начале уезжает после первой прокрутки,
   * и понять, где находишься, нечем. Рельс держит подразделы перед глазами
   * и подсвечивает текущий. Подпункты показываются только у активного
   * раздела: в справочнике их полторы сотни, все сразу — стена ссылок.
   */
  (function pageRail() {
    var content = document.querySelector('.content');
    if (!content) return;
    var heads = content.querySelectorAll('h2[id], h3[id]');
    if (heads.length < 4) return;

    var rail = document.createElement('nav');
    rail.className = 'page-rail';
    rail.setAttribute('aria-label', 'На этой странице');
    var html = '<div class="pr-head">На этой странице</div><ul class="pr-list">';
    var items = [];
    for (var i = 0; i < heads.length; i++) {
      var h = heads[i];
      // значки из заголовка в навигацию не переносим
      var txt = (h.textContent || '')
        .replace(/[\u{1F000}-\u{1FAFF}\u2600-\u27BF\uFE0F]/gu, '')
        .replace(/\s+/g, ' ').trim();
      if (!txt) continue;
      var lvl = h.tagName === 'H2' ? 2 : 3;
      html += '<li class="pr-i pr-l' + lvl + '" data-for="' + h.id + '">' +
              '<a href="#' + h.id + '">' + txt + '</a></li>';
      items.push({ id: h.id, el: h, lvl: lvl });
    }
    html += '</ul>';
    rail.innerHTML = html;
    content.parentNode.insertBefore(rail, content.nextSibling);

    var links = rail.querySelectorAll('.pr-i');

    function activate(id) {
      var idx = -1;
      for (var i = 0; i < items.length; i++) if (items[i].id === id) idx = i;
      if (idx < 0) return;
      // корневой раздел активного пункта — от него зависит, что раскрыто
      var rootIdx = idx;
      while (rootIdx > 0 && items[rootIdx].lvl > 2) rootIdx--;
      var rootId = items[rootIdx].id;
      for (var j = 0; j < links.length; j++) {
        var li = links[j];
        var own = items[j];
        li.classList.toggle('is-active', own.id === id);
        if (own.lvl === 3) {
          var myRoot = j;
          while (myRoot > 0 && items[myRoot].lvl > 2) myRoot--;
          li.classList.toggle('is-shown', items[myRoot].id === rootId);
        }
      }
      var act = rail.querySelector('.pr-i.is-active');
      if (act) act.scrollIntoView({ block: 'nearest' });
    }

    activate(items[0].id);
    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function (entries) {
        var top = null;
        entries.forEach(function (e) {
          if (e.isIntersecting &&
              (!top || e.boundingClientRect.top < top.boundingClientRect.top)) top = e;
        });
        if (top) activate(top.target.id);
      }, { rootMargin: '-70px 0px -60% 0px', threshold: 0 });
      items.forEach(function (it) { obs.observe(it.el); });
    }
  })();

  /* ── Соседние разделы внизу страницы ──────────────────────────────────
   * Порядок берём из бокового меню — оно и так описывает всю структуру,
   * отдельный список вести не нужно.
   */
  (function pagePager() {
    var content = document.querySelector('.content');
    var nav = document.querySelector('.sidebar nav');
    if (!content || !nav) return;

    var seen = {}, pages = [];
    nav.querySelectorAll('a[href]').forEach(function (a) {
      var href = a.getAttribute('href') || '';
      if (/^(https?:|mailto:|#)/.test(href)) return;
      var file = href.split('#')[0];
      if (!file || !/\.html$/.test(file) || file.indexOf('graphify') >= 0) return;
      if (seen[file]) return;
      seen[file] = 1;
      pages.push({ href: file, title: (a.textContent || '').replace(/\s+/g, ' ').trim() });
    });

    var here = location.pathname.split('/').pop() || 'index.html';
    var at = -1;
    for (var i = 0; i < pages.length; i++) {
      if (pages[i].href.split('/').pop() === here) at = i;
    }
    if (at < 0) return;

    var prev = at > 0 ? pages[at - 1] : null;
    var next = at < pages.length - 1 ? pages[at + 1] : null;
    if (!prev && !next) return;

    function side(item, kind) {
      if (!item) return '<span class="pg-empty"></span>';
      var label = kind === 'prev' ? 'Предыдущий раздел' : 'Следующий раздел';
      return '<a class="pg-link pg-' + kind + '" href="' + item.href + '">' +
             '<span class="pg-kind">' + label + '</span>' +
             '<span class="pg-title">' + item.title + '</span></a>';
    }

    var pager = document.createElement('nav');
    pager.className = 'page-pager';
    pager.setAttribute('aria-label', 'Соседние разделы');
    pager.innerHTML = side(prev, 'prev') + side(next, 'next');
    content.appendChild(pager);
  })();

  /* ── Кнопка «наверх» ──────────────────────────────────────────────────
   * Страница справочника — сотни экранов; возвращаться прокруткой долго.
   */
  (function toTop() {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'to-top';
    btn.setAttribute('aria-label', 'Наверх страницы');
    btn.innerHTML = '<i class="ti ti-arrow-up" aria-hidden="true"></i>';
    document.body.appendChild(btn);
    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    function toggle() {
      btn.classList.toggle('is-shown', window.pageYOffset > 900);
    }
    window.addEventListener('scroll', toggle, { passive: true });
    toggle();
  })();
});
