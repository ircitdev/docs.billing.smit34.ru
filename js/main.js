// СмИТ Биллинг 1.0 Docs — navigation + theme toggle
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

  // --- Mark active nav link ---
  var path = location.pathname;
  var links = document.querySelectorAll('.sidebar nav a');
  links.forEach(function (a) {
    if (path.endsWith(a.getAttribute('href')) ||
        path.endsWith(a.getAttribute('href').replace('../', ''))) {
      a.classList.add('active');
    }
  });
});
