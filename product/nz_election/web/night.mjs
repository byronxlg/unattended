export class ReplayClock {
  constructor(times, now = () => performance.now()) {
    this.times = times; this.now = now; this.speed = 1; this.reset();
  }
  reset() { this.elapsed = 0; this.running = false; this.last = this.now(); }
  tick() {
    const now = this.now();
    if (this.running) this.elapsed = Math.min(this.times.at(-1), this.elapsed + (now - this.last) * this.speed / 1000);
    this.last = now;
    if (this.elapsed >= this.times.at(-1)) this.running = false;
    return this.times.reduce((index, t, i) => t <= this.elapsed ? i : index, 0);
  }
  play() { this.tick(); this.running = this.elapsed < this.times.at(-1); }
  pause() { this.tick(); this.running = false; }
  rate(speed) { if (![1, 10, 60].includes(speed)) throw Error('REPLAY_SPEED'); this.tick(); this.speed = speed; }
}

if (typeof document !== 'undefined') {
  const container = document.querySelector('#night-snapshot');
  if (container?.querySelector('[data-sequence]')) {
    const id = new URL(location.href).searchParams.get('sequence');
    const template = document.getElementById('sequence-' + (id === '2023-illustrative' ? 'illustrative-2023' : id));
    if (template instanceof HTMLTemplateElement) container.replaceChildren(template.content.cloneNode(true));
    const frames = [...container.querySelectorAll('[data-frame]')];
    const section = container.querySelector('[data-sequence]');
    const mode = section.querySelector('.night-mode');
    // Keep only the displayed frame in the accessibility tree and focus order.
    document.querySelectorAll('template[id^="sequence-"]').forEach(t => t.remove());
    let visible = -1;
    const clock = new ReplayClock(frames.map(f => Number(f.dataset.elapsed)));
    const controls = document.querySelector('#night-controls');
    const play = document.querySelector('#night-play');
    const output = document.querySelector('#night-clock');
    const announcement = document.querySelector('#night-announcement');
    controls.hidden = frames.length < 2;
    let timer;
    function draw() {
      clearTimeout(timer);
      const wasRunning = clock.running;
      const index = clock.tick();
      if (wasRunning && !clock.running) announcement.textContent = 'Replay ended.';
      if (visible !== index) { section.replaceChildren(frames[index], mode); visible = index; }
      play.textContent = clock.running ? 'Pause' : 'Play';
      const text = `${clock.running ? 'Playing' : 'Paused'}: ${Math.floor(clock.elapsed)} seconds`;
      if (frames.length > 1 && output.textContent !== text) output.textContent = text;
      // Re-anchor draws after each interaction and include the exact replay endpoint.
      if (clock.running) {
        const remaining = (clock.times.at(-1) - clock.elapsed) * 1000 / clock.speed;
        timer = setTimeout(draw, Math.min(100, remaining));
      }
    }
    play.addEventListener('click', () => {
      if (clock.running) clock.pause(); else clock.play();
      draw();
      announcement.textContent = clock.running ? `Replay playing at ${clock.speed}x.` : clock.elapsed === clock.times.at(-1) ? 'Replay ended.' : 'Replay paused.';
    });
    document.querySelector('#night-reset').addEventListener('click', () => { clock.reset(); draw(); announcement.textContent = 'Replay reset and paused.'; });
    document.querySelector('#night-speed').addEventListener('change', e => { clock.rate(Number(e.target.value)); draw(); announcement.textContent = `Replay speed ${clock.speed}x.`; });
    draw();
  }
}

if (typeof document !== 'undefined' && document.querySelector('#night-snapshot')) {
  const snapshot = document.querySelector('#night-snapshot');
  snapshot.addEventListener('input', event => {
    if (!event.target.matches('.night-search')) return;
    const query = event.target.value.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
    const electorates = event.target.closest('.night-electorates');
    // Keep the matching leader next to the search while preserving map-first browsing.
    electorates.querySelectorAll('.night-map, .night-map-key').forEach(map => { map.hidden = Boolean(query); });
    electorates.querySelectorAll('tbody tr').forEach(row => {
      row.hidden = !row.cells[0].textContent.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().includes(query);
    });
  });
}
