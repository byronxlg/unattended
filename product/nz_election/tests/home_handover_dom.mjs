import assert from 'node:assert/strict';
const scenario = process.argv[2];
const open = Date.parse('2026-11-07T06:00:00Z');
const stop = Date.parse('2026-11-08T06:00:00Z');
let now = open - 30000;
Date.now = () => now;
const intervals = [], listeners = {}, requests = [];
const waiting = '<section id="night-summary">Polls have closed and counting is under way.</section>';
const settled = '<section id="night-summary">New Zealand voted on 7 November. Live updates ended.</section>';
const seeded = scenario.startsWith('populated-');
const late = scenario.endsWith('after-stop') && !seeded;
if (seeded) now = Date.parse('2026-11-07T10:00:00Z');
if (late) now = stop + 60000;
// A markup-backed adapter for this fixture's elements, not a layout engine.
// Every query reads the current rendered markup; replaced elements cannot survive as mocks.
const visibleText = html => html.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
function element(selector) {
  const attribute = selector.startsWith('#') ? 'id' : 'class';
  const pattern = new RegExp('<([a-z]+)\\b[^>]*' + attribute + '="' + selector.slice(1) + '"[^>]*>([\\s\\S]*?)</\\1>');
  if (!pattern.test(target.innerHTML)) return null;
  return {
    get textContent() { return visibleText(pattern.exec(target.innerHTML)?.[2] || ''); },
    set textContent(value) {
      target.innerHTML = target.innerHTML.replace(pattern, (whole, tag) => whole.slice(0, whole.indexOf('>') + 1) + value + '</' + tag + '>');
    },
    get innerHTML() { return pattern.exec(target.innerHTML)?.[2] || ''; },
    set innerHTML(value) { this.textContent = value; },
    get dataset() {
      const markup = pattern.exec(target.innerHTML)?.[0] || '';
      return Object.fromEntries([...markup.matchAll(/data-([a-z-]+)="([^"]*)"/g)].map(([, key, value]) => [key.replace(/-([a-z])/g, (_, c) => c.toUpperCase()), value]));
    }
  };
}
const source = scenario === 'zero' ? {parties:{}, house:0, percent:'0.00'} :
  scenario === 'recovery' ? {parties:{National:51, Labour:49, Green:20}, house:120, percent:'67.25'} :
  {parties:{National:63, Labour:57}, house:120, percent:'98.50'};
const partyText = Object.entries(source.parties).map(([party, seats]) => party + ' ' + seats).join('; ') || '0 national seats reported.';
const home = '<section id="night-summary"><figure id="home-night"><p class="seat-answer">' + partyText + '</p><p>' + source.percent +
  '% of voting places reported. House: ' + source.house + ' seats.</p><p id="home-live-status" data-retrieved-at="' + new Date(open).toISOString() +
  '" data-mode="Live preliminary results">Live preliminary results.</p></figure></section>';
const target = {
  dataset: {loopEndsAt:new Date(stop).toISOString(), waiting, settled},
  innerHTML:seeded ? home : scenario === 'waiting-after-stop' ? waiting : 'poll hero',
  get textContent() { return visibleText(this.innerHTML); },
  querySelector: element
};
function counts() {
  const text = target.textContent;
  const parties = Object.fromEntries(Object.keys(source.parties).map(party => {
    const found = text.match(new RegExp('\\b' + party + ' (\\d+)\\b'));
    assert.ok(found, 'visible seats missing for ' + party);
    return [party, Number(found[1])];
  }));
  if (!Object.keys(source.parties).length) assert.match(text, /0 national seats reported\./);
  const house = text.match(/House: (\d+) seats/);
  const percent = text.match(/([\d.]+)% of voting places reported/);
  assert.ok(house, 'visible House total missing');
  assert.ok(percent, 'visible reporting percentage missing');
  const result = {parties, house:Number(house[1]), percent:percent[1]};
  assert.deepEqual(result, source, 'visible counts must match scenario input');
  return result;
}
function status() {
  const rendered = target.querySelector('#home-live-status');
  assert.ok(rendered, 'rendered status missing');
  return rendered.textContent;
}
function ended(before) {
  assert.deepEqual(counts(), before, 'cutoff must retain every visible result number');
  assert.match(status(), /Live updates ended/);
  assert.doesNotMatch(status(), /Live preliminary results/);
}
let timelinePresent = !seeded && scenario !== 'waiting-after-stop';
const timeline = {remove: () => { timelinePresent = false; }};
const dates = {innerHTML:'Enrolment closed on 25 October; advance voting from 26 October; election day 7 November.'};
globalThis.location = {href:'https://example.test/unattended/nz-election/'};
globalThis.document = {
  hidden:false,
  querySelector: selector => selector === '#home-live' ? target : selector === '#dates' ? dates : selector === '#night' && timelinePresent ? timeline : null,
  addEventListener: (name, fn) => { listeners[name] = fn; }
};
globalThis.setInterval = fn => intervals.push(fn);
globalThis.fetch = async url => {
  assert.equal(new URL(url).pathname.endsWith('/night-live.json'), true);
  requests.push(now);
  if (seeded) throw Error('offline');
  if (scenario === 'recovery' && requests.length === 1) throw Error('offline');
  return {ok:true, json:async()=>({available:scenario !== 'absent',
    loop_ended:false, loop_ends_at:new Date(stop).toISOString(),
    mode:'Live preliminary results', retrieved_at:new Date(open).toISOString(),
    reference_version:'a'.repeat(64), html:'night page', home_html:home})};
};
await import(process.argv[3] || '../web/home-live.mjs');
const flush = () => new Promise(resolve => setImmediate(resolve));
await flush();
if (seeded) {
  assert.match(status(), /Stale: last complete cycle retrieved 2026-11-07T06:00:00.000Z/);
  assert.doesNotMatch(status(), /Live preliminary results/);
  const before = counts();
  for (const clock of ['2026-11-08T06:00:00Z', '2026-11-08T06:01:00Z', '2026-11-14T00:00:00Z', '2026-11-27T00:00:00Z']) {
    now = Date.parse(clock); intervals.forEach(fn => fn()); await flush();
    ended(before);
  }
  assert.equal(requests.length, 1);
  console.log('PASS populated stale and ended clocks');
  process.exit(0);
}
if (late) {
  assert.equal(timelinePresent, false, 'obsolete timeline must retire on handover');
  assert.equal(target.innerHTML, settled);
  intervals.forEach(fn => fn()); await flush();
  assert.equal(requests.length, 0);
  console.log('PASS retirement: ' + scenario);
  process.exit(0);
}
assert.equal(target.innerHTML, 'poll hero');
assert.match(dates.innerHTML, /advance voting from 26 October/);
assert.equal(requests.length, 0);
now = open - 1; intervals.forEach(fn => fn()); await flush();
assert.equal(requests.length, 0);
now = open + 60000; intervals.forEach(fn => fn()); await flush();
assert.equal(requests.length, 1);
assert.equal(timelinePresent, false, 'obsolete timeline must retire on handover');
assert.equal(dates.innerHTML, '<p>Voting closed on 7 November at 7pm.</p>');
if (['absent', 'recovery'].includes(scenario)) assert.equal(target.innerHTML, waiting);
else counts();
if (scenario === 'recovery') {
  now += 125000; intervals.forEach(fn => fn()); await flush();
  counts();
  assert.equal(requests.length, 2);
}
const before = scenario === 'absent' ? null : counts();
now = stop;
const count = requests.length;
intervals.forEach(fn => fn()); await flush();
if (before) ended(before);
listeners.visibilitychange(); await flush();
now += 120000; intervals.forEach(fn => fn()); await flush();
assert.equal(requests.length, count);
if (scenario === 'absent') assert.equal(target.innerHTML, settled);
else ended(before);
assert.ok(requests.every(t => t >= open && t < stop));
console.log('PASS DOM handover: ' + scenario);
