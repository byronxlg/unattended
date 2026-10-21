import assert from 'node:assert/strict';
import test from 'node:test';

// Exercise the actual page wiring, including its timers, without a browser or dependencies.
class Element {
  constructor(dataset = {}) { this.dataset = dataset; this.listeners = new Map(); this.textContent = ''; }
  addEventListener(name, handler) { this.listeners.set(name, handler); }
  dispatch(name, value) { this.listeners.get(name)({target: {value}}); }
  replaceChildren(...children) { this.children = children; }
}

function fakeTime() {
  let now = 0, nextId = 0;
  const timers = new Map();
  function schedule(callback, delay, interval = false) {
    const id = ++nextId;
    timers.set(id, {callback, delay, interval, at: now + delay});
    return id;
  }
  return {
    now: () => now,
    setTimeout: (callback, delay) => schedule(callback, delay),
    setInterval: (callback, delay) => schedule(callback, delay, true),
    clear: id => timers.delete(id),
    pending: () => timers.size,
    advance(ms) {
      const end = now + ms;
      let calls = 0;
      while (true) {
        const next = [...timers.entries()].sort((a, b) => a[1].at - b[1].at || a[0] - b[0])[0];
        if (!next || next[1].at > end) break;
        assert.ok(++calls < 10000, 'scheduler must not spin');
        const [id, timer] = next;
        now = timer.at;
        if (timer.interval) timer.at += timer.delay;
        else timers.delete(id);
        timer.callback();
      }
      now = end;
    },
  };
}

test('60x replay renders the final frame within 10,000 ms of Play and stops', async t => {
  const time = fakeTime();
  const frames = [0, 300, 600].map((elapsed, frame) => new Element({elapsed: String(elapsed), frame: String(frame)}));
  const mode = new Element();
  mode.textContent = 'Illustrative replay based on 2023 final results';
  const section = new Element();
  section.querySelector = () => mode;
  const container = new Element();
  container.querySelectorAll = () => frames;
  container.querySelector = () => section;
  const controls = Object.fromEntries(['play', 'reset', 'speed', 'clock', 'controls'].map(id => ['#night-' + id, new Element()]));
  const document = {
    querySelector: selector => selector === '#night-snapshot' ? container : controls[selector],
    getElementById: () => null,
    querySelectorAll: () => [],
  };
  const globals = {
    document, location: {href: 'https://example.invalid/night/'}, HTMLTemplateElement: class {},
    performance: {now: time.now}, setTimeout: time.setTimeout, setInterval: time.setInterval,
    clearTimeout: time.clear, clearInterval: time.clear,
  };
  for (const [key, value] of Object.entries(globals)) {
    const original = Object.getOwnPropertyDescriptor(globalThis, key);
    Object.defineProperty(globalThis, key, {configurable: true, writable: true, value});
    t.after(() => original ? Object.defineProperty(globalThis, key, original) : delete globalThis[key]);
  }
  await import(process.env.NIGHT_MODULE_URL || '../web/night.mjs');
  const frame = () => Number(section.children[1].dataset.frame);
  assert.equal(frame(), 0);
  // Play is an interaction, not necessarily aligned to the page-load timer phase.
  time.advance(37);
  controls['#night-speed'].dispatch('change', '60');
  controls['#night-play'].dispatch('click');
  time.advance(10000);
  assert.equal(frame(), 2, 'at 10,000 ms the rendered frame must be the endpoint');
  assert.equal(controls['#night-play'].textContent, 'Play');
  assert.equal(controls['#night-clock'].textContent, 'Paused: 600 seconds');
  assert.equal(time.pending(), 0, 'completed replay must stop scheduling draws');
  time.advance(10000);
  assert.equal(frame(), 2);
  assert.equal(section.children[0], mode);

  controls['#night-reset'].dispatch('click');
  assert.equal(frame(), 0);
  controls['#night-play'].dispatch('click');
  time.advance(2500);
  controls['#night-play'].dispatch('click');
  assert.equal(time.pending(), 0, 'pause cancels the pending draw');
  time.advance(1000);
  controls['#night-speed'].dispatch('change', '10');
  controls['#night-play'].dispatch('click');
  time.advance(15000);
  assert.equal(frame(), 1);
  controls['#night-reset'].dispatch('click');
  assert.equal(frame(), 0);
  assert.equal(time.pending(), 0, 'reset cancels the pending draw');
});
