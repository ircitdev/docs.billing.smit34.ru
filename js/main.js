// СмИТ Биллинг 1.0 Docs — navigation + theme toggle + submenu
document.addEventListener('DOMContentLoaded', function () {
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
  }

  // --- Mobile sidebar toggle ---
  var toggle = document.querySelector('.menu-toggle');
  var sidebar = document.querySelector('.sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
    document.querySelector('.content').addEventListener('click', function () {
      sidebar.classList.remove('open');
    });
  }

  // --- Mark active nav link & auto-open submenu ---
  var path = location.pathname;
  var hash = location.hash;

  // Normalize: get just the filename part for matching
  function getFilename(href) {
    if (!href) return '';
    var h = href.split('#')[0];
    // Remove leading ../ or pages/
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

  // --- Submenu toggle on click ---
  document.querySelectorAll('.sidebar nav li.has-children > a').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var li = this.parentElement;
      var linkFile = getFilename(this.getAttribute('href'));

      // If we're already on this page, just toggle submenu
      if (linkFile === currentFile) {
        e.preventDefault();
        li.classList.toggle('open');
      }
      // Otherwise, navigate to the page (default behavior)
    });
  });
});
