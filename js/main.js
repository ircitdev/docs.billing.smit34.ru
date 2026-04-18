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
  var theme = saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  html.setAttribute('data-theme', theme);

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
  }
  function openSidebar() {
    if (sidebar) sidebar.classList.add('open');
    if (backdrop) backdrop.classList.add('open');
  }
  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      if (sidebar.classList.contains('open')) closeSidebar(); else openSidebar();
    });
    if (backdrop) backdrop.addEventListener('click', closeSidebar);
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
    setTimeout(function(){ if (overlayInput) overlayInput.focus(); }, 50);
  }
  function closeOverlay() {
    if (!overlay) return;
    overlay.classList.remove('open');
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
          '<div class="protected-icon"><i class="bi bi-shield-lock"></i></div>' +
          '<h3>' + title + '</h3>' +
          '<p>' + hint + '</p>' +
          '<form class="protected-form" autocomplete="off">' +
            '<input type="password" placeholder="Пароль" autocomplete="new-password" required>' +
            '<button type="submit"><i class="bi bi-unlock"></i> Открыть</button>' +
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
  document.querySelectorAll('.content pre').forEach(function (pre) {
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
      '<button class="code-copy-btn" type="button" title="Скопировать в буфер"><i class="bi bi-clipboard"></i><span> Копировать</span></button>';
    wrap.insertBefore(bar, pre);

    bar.querySelector('.code-copy-btn').addEventListener('click', function () {
      var btn = this;
      copyToClipboard(text).then(function () {
        btn.classList.add('copied');
        btn.querySelector('i').className = 'bi bi-check2';
        btn.querySelector('span').textContent = ' Скопировано';
        setTimeout(function () {
          btn.classList.remove('copied');
          btn.querySelector('i').className = 'bi bi-clipboard';
          btn.querySelector('span').textContent = ' Копировать';
        }, 1600);
      });
    });
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
    btn.innerHTML = '<i class="bi bi-link-45deg"></i>';
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
});
