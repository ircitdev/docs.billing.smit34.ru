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
});
