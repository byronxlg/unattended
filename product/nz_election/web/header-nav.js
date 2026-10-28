(() => {
  const nav = document.querySelector('body > header nav');
  if (!nav) return;
  const links = [...nav.querySelectorAll('a')];
  const current = nav.querySelector('[aria-current="page"]');
  const paint = () => {
    const clip = nav.getBoundingClientRect();
    for (const link of links) {
      const box = link.getBoundingClientRect();
      const whole = box.left >= clip.left - 0.5 && box.right <= clip.right + 0.5;
      // Opacity preserves keyboard access and natural widths at the scroll edges.
      link.style.opacity = whole ? '1' : '0';
      link.style.pointerEvents = whole ? '' : 'none';
    }
  };
  const reveal = link => {
    if (link) {
      const clip = nav.getBoundingClientRect(), box = link.getBoundingClientRect();
      if (box.left < clip.left) nav.scrollLeft += box.left - clip.left;
      else if (box.right > clip.right) nav.scrollLeft += box.right - clip.right;
    }
    paint();
  };
  // Rotation must restore the route even when another tab retains keyboard focus.
  const refresh = () => reveal(current || (links.includes(document.activeElement) ? document.activeElement : null));
  nav.addEventListener('scroll', paint, {passive: true});
  nav.addEventListener('focusin', event => reveal(event.target.closest('a')));
  // Font loading and viewport changes can alter which complete labels fit.
  const observer = new ResizeObserver(refresh);
  observer.observe(nav);
  links.forEach(link => observer.observe(link));
  document.fonts.ready.then(refresh);
  window.addEventListener('pageshow', refresh);
  refresh();
})();
