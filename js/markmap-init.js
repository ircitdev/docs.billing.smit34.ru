/* СмИТ Биллинг Docs — Markmap renderer (майндмапы)
 *
 * Рендерит красивые интерактивные майндмапы (плавные ветви-кривые, аккуратная
 * типографика, разворачивание узлов) из markdown-списка. Замена mermaid mindmap.
 *
 * Формы записи:
 *   1) <pre class="markmap"> markdown-список </pre>
 *   2) fenced ```markmap ... ``` внутри <pre><code> (удобно копировать из .md)
 *
 * Особенности:
 *   - библиотеки (d3 + markmap-view + markmap-lib) грузятся с CDN ЛЕНИВО,
 *     только если на странице есть майндмап;
 *   - фирменная палитра + шрифт inherit; тёмная тема из <html data-theme>;
 *   - каждый майндмап вписан по ширине, высота фиксируется аккуратно;
 *   - securityLevel: markdown парсится в текст, без исполнения скриптов.
 */
(function () {
  'use strict';

  var LIBS = [
    'https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js',
    'https://cdn.jsdelivr.net/npm/markmap-view@0.18/dist/browser/index.js',
    'https://cdn.jsdelivr.net/npm/markmap-lib@0.18.11/dist/browser/index.iife.js'
  ];
  var _loading = null;
  var _seq = 0;

  function isDark() {
    return document.documentElement.getAttribute('data-theme') === 'dark';
  }

  /* fenced ```markmap → <pre class="markmap"> */
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

  /* последовательная загрузка CDN-скриптов (d3 → view → lib) */
  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = src; s.async = false;
      s.onload = resolve;
      s.onerror = function () { reject(new Error('не удалось загрузить ' + src)); };
      document.head.appendChild(s);
    });
  }
  function loadLibs() {
    if (window.markmap && window.markmap.Markmap && window.markmap.Transformer) return Promise.resolve();
    if (_loading) return _loading;
    _loading = LIBS.reduce(function (p, src) {
      return p.then(function () {
        // markmap-lib и markmap-view кладутся в один namespace window.markmap
        if (src.indexOf('d3') > -1 && window.d3) return;
        return loadScript(src);
      });
    }, loadScript(LIBS[0])).then(function () {
      // подчистка: гарантируем наличие нужных классов
      if (!(window.markmap && window.markmap.Markmap)) throw new Error('markmap не инициализирован');
    });
    return _loading;
  }

  function brandColors() {
    // фирменная спокойная палитра ветвей (уровни)
    return ['#43b77a', '#2d9a5f', '#5aa9d6', '#8a7fd6', '#d69a5a', '#4a5a52'];
  }

  function renderOne(pre) {
    if (pre.dataset.markmapDone) return;
    pre.dataset.markmapDone = '1';
    var md = pre.textContent || '';
    var id = 'mm-' + (++_seq);

    // обёртка + svg
    var wrap = document.createElement('div');
    wrap.className = 'mmap-wrap';
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('id', id);
    svg.setAttribute('class', 'mmap-svg');
    wrap.appendChild(svg);
    pre.parentNode.replaceChild(wrap, pre);

    var Transformer = window.markmap.Transformer;
    var Markmap = window.markmap.Markmap;
    var tf = new Transformer();
    var res = tf.transform(md);

    var dark = isDark();
    Markmap.create(svg, {
      autoFit: true,
      duration: 350,
      spacingVertical: 12,
      spacingHorizontal: 100,
      paddingX: 18,
      initialExpandLevel: -1,
      maxWidth: 260,
      color: (function () {
        var pal = brandColors();
        return function (node) { return pal[(node.state.depth || 0) % pal.length]; };
      })(),
      style: function (id2) {
        return '#' + id2 + ' { font: 15px inherit; }' +
          '#' + id2 + ' .markmap-node > text { fill: ' + (dark ? '#e6edea' : '#1c2b23') + '; }' +
          '#' + id2 + ' .markmap-link { stroke-width: 1.6; opacity: .85; }';
      }
    }, res.root);
  }

  function renderAll() {
    normalizeFenced(document);
    var pres = Array.prototype.slice.call(document.querySelectorAll('pre.markmap:not([data-markmap-done])'));
    if (!pres.length) return;
    loadLibs().then(function () {
      pres.forEach(renderOne);
    }).catch(function (e) {
      console.warn('[markmap] ' + e.message + ' — майндмапы показаны как текст');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderAll);
  } else {
    renderAll();
  }
})();
