/* СмИТ Биллинг Docs — Mermaid renderer (диаграммы, инфографика, mindmaps)
 *
 * Подключается во всех страницах docs. Рендерит две формы записи:
 *   1) <pre class="mermaid">flowchart TB ...</pre>           — чистый HTML
 *   2) <pre><code>```mermaid\nflowchart TB ...\n```</code></pre> — fenced-блок
 *      (удобно копировать схемы прямо из .md-отчётов dev_reports)
 *
 * Особенности:
 *   - mermaid.js грузится с CDN лениво, ТОЛЬКО если на странице есть диаграмма
 *     (на страницах без схем — ноль накладных расходов и сетевых запросов).
 *   - Тема (default/dark) берётся из <html data-theme="..."> docs-сайта
 *     и переключается на лету при смене темы.
 *   - Каждая отрисованная диаграмма оборачивается в zoom/pan-контейнер
 *     с кнопками увеличить / уменьшить / по ширине / сброс (как в dev_reports).
 *   - securityLevel:'strict' — пользовательский текст не исполняется.
 */
(function () {
  'use strict';

  var CDN = 'https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.1/mermaid.min.js';
  var _loading = null;       // Promise загрузки CDN
  var _initialized = false;  // mermaid.initialize() уже вызван
  var _seq = 0;              // счётчик для уникальных id диаграмм

  function isDark() {
    return document.documentElement.getAttribute('data-theme') === 'dark';
  }

  /* ── 1. Нормализация: fenced ```mermaid внутри <pre><code> → <pre class="mermaid"> ── */
  function normalizeFenced(root) {
    var codes = root.querySelectorAll('pre > code');
    for (var i = 0; i < codes.length; i++) {
      var code = codes[i];
      var pre = code.parentNode;
      if (pre.classList.contains('mermaid') || pre.dataset.mermaidDone) continue;

      var text = code.textContent || '';
      var m = text.match(/^\s*```+\s*mermaid\s*\n([\s\S]*?)\n?\s*```+\s*$/i);
      if (!m) continue;

      var fresh = document.createElement('pre');
      fresh.className = 'mermaid';
      fresh.textContent = m[1];
      pre.parentNode.replaceChild(fresh, pre);
    }
  }

  /* ── 2. Загрузка библиотеки с CDN (один раз) ── */
  function loadMermaid() {
    if (window.mermaid) return Promise.resolve(window.mermaid);
    if (_loading) return _loading;
    _loading = new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = CDN;
      s.async = true;
      s.onload = function () {
        if (window.mermaid) resolve(window.mermaid);
        else reject(new Error('mermaid не определён после загрузки'));
      };
      s.onerror = function () { reject(new Error('не удалось загрузить mermaid с CDN')); };
      document.head.appendChild(s);
    });
    return _loading;
  }

  function initMermaid() {
    if (!window.mermaid) return;
    window.mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      theme: isDark() ? 'dark' : 'default',
      flowchart: { useMaxWidth: true },
      themeVariables: { fontFamily: 'inherit' }
    });
    _initialized = true;
  }

  /* ── 3. Рендер всех необработанных диаграмм ── */
  function renderAll() {
    normalizeFenced(document);
    var nodes = document.querySelectorAll('pre.mermaid:not([data-processed]):not([data-mermaid-done])');
    if (!nodes.length) return;

    loadMermaid().then(function () {
      if (!_initialized) initMermaid();
      // mermaid.run читает textContent узла как исходник диаграммы
      window.mermaid.run({ nodes: nodes }).then(function () {
        for (var i = 0; i < nodes.length; i++) wrapZoom(nodes[i]);
      }).catch(function (e) {
        console.warn('[mermaid] ошибка рендера:', e);
      });
    }).catch(function (e) {
      // CDN недоступен — оставляем исходный текст диаграммы как есть, страница не падает
      console.warn('[mermaid] ' + e.message + ' — диаграммы показаны как текст');
    });
  }

  /* ── 4. Перерисовка при смене темы (default ↔ dark) ── */
  function rerenderForTheme() {
    if (!window.mermaid) return; // ещё не было ни одной диаграммы
    var pres = document.querySelectorAll('pre.mermaid[data-mermaid-done]');
    if (!pres.length) return;

    for (var i = 0; i < pres.length; i++) {
      var pre = pres[i];
      var src = pre.getAttribute('data-mermaid-src');
      if (src == null) continue;
      // вынимаем <pre> из zoom-обёртки, сбрасываем в исходное состояние
      var wrap = pre.closest('.mmd-zoom');
      pre.removeAttribute('data-processed');
      pre.removeAttribute('data-mermaid-done');
      delete pre.dataset.zoomWrapped;
      pre.textContent = src;
      if (wrap && wrap.parentNode) wrap.parentNode.replaceChild(pre, wrap);
    }
    _initialized = false; // переинициализировать с новой темой
    renderAll();
  }

  /* ── 5. zoom/pan-обёртка вокруг отрисованной диаграммы ──
   *
   * Принцип: ДЕФОЛТ — схема вписана по ширине и читается целиком, без действий.
   * mermaid c useMaxWidth:true сам ставит на SVG width:100%/max-width — поэтому
   * при scale=1 диаграмма занимает всю ширину контейнера, высота — авто (без обрезки,
   * без скролла). Зум (кнопки/Ctrl+колесо) увеличивает ОТ этой базы; скролл/pan нужны
   * только когда пользователь сам увеличил.
   */
  function wrapZoom(pre) {
    if (!pre || pre.dataset.zoomWrapped) return;
    pre.dataset.zoomWrapped = '1';
    pre.dataset.mermaidDone = '1';

    var wrap = document.createElement('div'); wrap.className = 'mmd-zoom';
    var viewport = document.createElement('div'); viewport.className = 'mmd-zoom-viewport';
    var stage = document.createElement('div'); stage.className = 'mmd-zoom-stage';

    var bar = document.createElement('div'); bar.className = 'mmd-zoom-bar';
    bar.innerHTML =
      '<button type="button" data-z="out" title="Уменьшить" aria-label="Уменьшить"><i class="bi bi-dash-lg" aria-hidden="true"></i></button>' +
      '<span class="mmd-zoom-pct" aria-live="polite">100%</span>' +
      '<button type="button" data-z="in" title="Увеличить" aria-label="Увеличить"><i class="bi bi-plus-lg" aria-hidden="true"></i></button>' +
      '<button type="button" data-z="reset" title="Сбросить" aria-label="Сбросить масштаб"><i class="bi bi-arrow-counterclockwise" aria-hidden="true"></i></button>';

    pre.parentNode.insertBefore(wrap, pre);
    stage.appendChild(pre);
    viewport.appendChild(stage);
    wrap.appendChild(bar);
    wrap.appendChild(viewport);

    // SVG растягиваем на всю ширину контейнера (mermaid useMaxWidth ставит max-width
    // в px по натуральному размеру — снимаем его, чтобы маленькие схемы тоже вписывались
    // читаемо, но не раздувались сверх натуральной ширины).
    var svg = pre.querySelector('svg');
    if (svg) {
      svg.style.width = '100%';
      svg.style.height = 'auto';
      svg.style.maxWidth = '100%';
      svg.removeAttribute('width');
      svg.removeAttribute('height');
    }

    var scale = 1, MIN = 0.5, MAX = 3, STEP = 0.25;
    var pct = bar.querySelector('.mmd-zoom-pct');
    function apply() {
      // scale=1 → база (вписано по ширине). >1 → крупнее, появляется скролл.
      stage.style.transform = scale === 1 ? '' : 'scale(' + scale + ')';
      stage.style.width = scale === 1 ? '100%' : (scale * 100) + '%';
      pct.textContent = Math.round(scale * 100) + '%';
      wrap.classList.toggle('is-zoomed', scale !== 1);
    }
    function zoom(delta) {
      scale = Math.min(MAX, Math.max(MIN, Math.round((scale + delta) * 100) / 100));
      apply();
    }
    bar.addEventListener('click', function (e) {
      var btn = e.target.closest('button'); if (!btn) return;
      var z = btn.dataset.z;
      if (z === 'in') zoom(STEP);
      else if (z === 'out') zoom(-STEP);
      else if (z === 'reset') { scale = 1; apply(); viewport.scrollTo({ left: 0, top: 0 }); }
    });

    // Ctrl/Cmd + колесо → зум; обычный скролл — прокрутка страницы
    viewport.addEventListener('wheel', function (e) {
      if (!(e.ctrlKey || e.metaKey)) return;
      e.preventDefault();
      zoom(e.deltaY < 0 ? STEP : -STEP);
    }, { passive: false });

    // drag-to-pan мышью (актуально только при увеличении)
    var panning = false, sx = 0, sy = 0, sl = 0, st = 0;
    viewport.addEventListener('mousedown', function (e) {
      if (e.button !== 0 || scale === 1) return;
      panning = true; viewport.classList.add('is-panning');
      sx = e.clientX; sy = e.clientY; sl = viewport.scrollLeft; st = viewport.scrollTop;
    });
    window.addEventListener('mousemove', function (e) {
      if (!panning) return;
      viewport.scrollLeft = sl - (e.clientX - sx);
      viewport.scrollTop = st - (e.clientY - sy);
    });
    window.addEventListener('mouseup', function () {
      if (panning) { panning = false; viewport.classList.remove('is-panning'); }
    });

    apply();
  }

  /* ── Сохраняем исходник диаграммы ДО рендера (для перерисовки при смене темы) ── */
  function stashSources() {
    var pres = document.querySelectorAll('pre.mermaid:not([data-mermaid-src])');
    for (var i = 0; i < pres.length; i++) {
      pres[i].setAttribute('data-mermaid-src', pres[i].textContent);
    }
  }

  function boot() {
    normalizeFenced(document);
    stashSources();
    renderAll();

    // Реакция на переключение темы: main.js меняет <html data-theme>
    var lastTheme = document.documentElement.getAttribute('data-theme');
    var mo = new MutationObserver(function () {
      var t = document.documentElement.getAttribute('data-theme');
      if (t !== lastTheme) { lastTheme = t; rerenderForTheme(); }
    });
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  // на случай ручного вызова (например, после AJAX-вставки контента)
  window.SmitMermaid = { render: function () { stashSources(); renderAll(); } };
})();
