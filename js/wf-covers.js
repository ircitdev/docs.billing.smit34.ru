/* Видео-обложки карточек со схемами.

   Ролик весит больше картинки, поэтому грузится только тогда, когда его
   собираются смотреть: под курсором на десктопе и у карточки, оказавшейся
   в центре экрана на телефоне. */
(function () {
  var cards = [].slice.call(document.querySelectorAll('.wf-link.has-clip'));
  if (!cards.length) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  function visibleClip(card) {
    var clips = [].slice.call(card.querySelectorAll('.clip'));
    for (var i = 0; i < clips.length; i++) {
      if (clips[i].offsetParent !== null) return clips[i];
    }
    return null;
  }

  function play(card) {
    var clip = visibleClip(card);
    if (!clip) return;
    if (!clip.src) clip.src = clip.dataset.src;
    clip.classList.add('ready');
    var started = clip.play();
    if (started && started.catch) started.catch(function () {});
  }

  function stop(card) {
    [].forEach.call(card.querySelectorAll('.clip'), function (clip) {
      clip.classList.remove('ready');
      if (!clip.paused) clip.pause();
    });
  }

  // Наведение и фокус вешаем всегда: на тач-устройстве эти события просто не
  // приходят, а на десктопе это основной способ посмотреть ролик.
  cards.forEach(function (card) {
    card.addEventListener('mouseenter', function () { play(card); });
    card.addEventListener('mouseleave', function () { stop(card); });
    card.addEventListener('focus', function () { play(card); });
    card.addEventListener('blur', function () { stop(card); });
  });

  // Узкий экран или отсутствие курсора: играет карточка в середине экрана.
  // Проверяем и ширину — эмуляция телефона в браузере оставляет hover: hover,
  // и по одному только hover поведение на разработке не воспроизвести.
  var touch = window.matchMedia('(hover: none)').matches ||
              window.matchMedia('(max-width: 700px)').matches;
  if (!touch || !('IntersectionObserver' in window)) return;
  var active = null;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting && e.intersectionRatio > 0.6) {
        if (active && active !== e.target) stop(active);
        active = e.target;
        play(active);
      } else if (e.target === active && e.intersectionRatio < 0.3) {
        stop(active);
        active = null;
      }
    });
  }, { threshold: [0.3, 0.6, 0.9], rootMargin: '-20% 0px -20% 0px' });

  cards.forEach(function (card) { io.observe(card); });
})();
