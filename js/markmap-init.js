/* СмИТ Биллинг Docs — Markmap майндмапы (интерактивные, вертикальные)
 *
 * Рендерит майндмап из markdown-списка (плавные ветви-кривые, разворачивание,
 * зум/пан). Панель кнопок в правом верхнем углу: зум +/−, 100% (fit), на весь экран.
 *
 * Формы записи:
 *   1) <pre class="markmap"> markdown-список </pre>
 *   2) fenced ```markmap ... ``` внутри <pre><code>
 *
 * Библиотеки (d3 + markmap-view + markmap-lib) грузятся с CDN ЛЕНИВО.
 * Фирменная зелёная палитра СмИТ, тема из <html data-theme>.
 */
(function () {
  'use strict';

  var LIBS = [
    'https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js',
    'https://cdn.jsdelivr.net/npm/markmap-view@0.18/dist/browser/index.js',
    'https://cdn.jsdelivr.net/npm/markmap-lib@0.18.11/dist/browser/index.iife.js'
  ];
  var _loading = null, _seq = 0;

  function isDark() {
    return document.documentElement.getAttribute('data-theme') === 'dark';
  }

  function normalizeFenced(root) {
    var codes = root.querySelectorAll('pre > code');
    for (var i = 0; i < codes.length; i++) {
      var code = codes[i], pre = code.parentNode;
      if (pre.classList.contains('markmap') || pre.dataset.markmapDone) continue;
      var m = (code.textContent || '').match(/^\s*```+\s*markmap\s*\n([\s\S]*?)\n?\s*```+\s*$/i);
      if (!m) continue;
      var fresh = document.createElement('pre');
      fresh.className = 'markmap';
      fresh.textContent = m[1];
      pre.parentNode.replaceChild(fresh, pre);
    }
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = src; s.async = false;
      s.onload = resolve;
      s.onerror = function () { reject(new Error('не загрузился ' + src)); };
      document.head.appendChild(s);
    });
  }
  function loadLibs() {
    if (window.markmap && window.markmap.Markmap && window.markmap.Transformer) return Promise.resolve();
    if (_loading) return _loading;
    _loading = LIBS.reduce(function (p, src) {
      return p.then(function () { return loadScript(src); });
    }, Promise.resolve()).then(function () {
      if (!(window.markmap && window.markmap.Markmap && window.markmap.Transformer))
        throw new Error('markmap не инициализирован');
    });
    return _loading;
  }

  // фирменная зелёная палитра ветвей (по глубине)
  var PALETTE = ['#2d9a5f', '#43b77a', '#5cc48d', '#38a86e', '#6bcf9a', '#2f8f59'];

  function makeBtn(html, title) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'mmap-btn'; b.innerHTML = html;
    b.setAttribute('aria-label', title); b.title = title;
    return b;
  }

  function renderOne(pre) {
    if (pre.dataset.markmapDone) return;
    pre.dataset.markmapDone = '1';
    var md = pre.textContent || '';
    var id = 'mm-' + (++_seq);

    var wrap = document.createElement('div');
    wrap.className = 'mmap-wrap';
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('id', id); svg.setAttribute('class', 'mmap-svg');
    wrap.appendChild(svg);

    // панель кнопок (правый верхний угол)
    var bar = document.createElement('div');
    bar.className = 'mmap-toolbar';
    var bIn = makeBtn('+', 'Увеличить'),
        bOut = makeBtn('&minus;', 'Уменьшить'),
        bFit = makeBtn('100%', 'Вписать / сброс'),
        bFull = makeBtn('&#9974;', 'На весь экран');
    bar.appendChild(bIn); bar.appendChild(bOut); bar.appendChild(bFit); bar.appendChild(bFull);
    wrap.appendChild(bar);

    pre.parentNode.replaceChild(wrap, pre);

    var dark = isDark();
    var mm = window.markmap.Markmap.create(svg, {
      autoFit: true, duration: 350, spacingVertical: 10, spacingHorizontal: 88,
      paddingX: 16, initialExpandLevel: -1, maxWidth: 260,
      color: function (node) { return PALETTE[(node.state.depth || 0) % PALETTE.length]; },
      style: function (sid) {
        var tc = dark ? '#e6edea' : '#1c2b23';
        return '#' + sid + ' { font: 15px inherit; }' +
          '#' + sid + ' div { color:' + tc + '; }' +
          '#' + sid + ' a { color:#43b77a; }';
      }
    }, window.markmap.Transformer ? new window.markmap.Transformer().transform(md).root : null);

    // Пост-обработка узлов: капсулы 1-2 уровня + FA-иконки на ветвях.
    // Не зависим от внутренней структуры markmap — идём от текста узла.
    var ROOT = 'Лендинги';
    var BRANCH_ICONS = {
      'Конструктор': 'fa-cubes', 'Hero и медиа': 'fa-photo-film',
      'Эффекты': 'fa-wand-magic-sparkles', 'AI': 'fa-robot',
      'Публикация': 'fa-globe', 'Заявки': 'fa-inbox', 'Аналитика': 'fa-chart-line'
    };
    function decorate() {
      var divs = svg.querySelectorAll('foreignObject > div');
      divs.forEach(function (d) {
        if (d.dataset.smitDone) return;
        var txt = (d.textContent || '').trim();
        var fo = d.parentNode;
        if (txt === ROOT) {
          fo.setAttribute('data-mmdepth', '0'); d.dataset.smitDone = '1';
        } else if (BRANCH_ICONS[txt]) {
          fo.setAttribute('data-mmdepth', '1');
          if (!d.querySelector('i')) {
            d.innerHTML = '<i class="fas ' + BRANCH_ICONS[txt] + '"></i> ' + d.innerHTML;
          }
          d.dataset.smitDone = '1';
        }
      });
    }
    decorate();
    // после добавления капсул размеры узлов изменились — пересчитать раскладку и вписать
    setTimeout(function () { try { mm.setData(mm.state.data); mm.fit(); } catch (e) { try { mm.fit(); } catch (e2) {} } }, 60);
    // markmap перерисовывает узлы при разворачивании/зуме — повторяем decorate
    var mo = new MutationObserver(function () { decorate(); });
    mo.observe(svg, { childList: true, subtree: true });

    // кнопки
    bIn.addEventListener('click', function () { mm.rescale(1.25); });
    bOut.addEventListener('click', function () { mm.rescale(0.8); });
    bFit.addEventListener('click', function () { mm.fit(); });
    bFull.addEventListener('click', function () {
      if (!document.fullscreenElement) {
        (wrap.requestFullscreen ? wrap.requestFullscreen() : Promise.resolve())
          .then(function () { setTimeout(function () { mm.fit(); }, 120); });
      } else if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    });
    wrap.addEventListener('fullscreenchange', function () { setTimeout(function () { mm.fit(); }, 120); });
    // перерисовка палитры/текста при смене темы страницы
    wrap._mm = mm; wrap._md = md;
  }

  function renderAll() {
    normalizeFenced(document);
    var pres = Array.prototype.slice.call(document.querySelectorAll('pre.markmap:not([data-markmap-done])'));
    if (!pres.length) return;
    loadLibs().then(function () { pres.forEach(renderOne); })
      .catch(function (e) { console.warn('[markmap] ' + e.message + ' — майндмап показан как текст'); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderAll);
  } else {
    renderAll();
  }
})();
