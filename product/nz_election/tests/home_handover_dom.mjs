import assert from 'node:assert/strict';
const scenario = process.argv[2];
const open = Date.parse('2026-11-07T06:00:00Z');
const stop = Date.parse('2026-11-08T06:00:00Z');
let now = open - 30000;
Date.now = () => now;
const intervals = [], listeners = {}, requests = [];
const waiting = '<section id="night-summary">Polls have closed and counting is under way.</section>';
const target = {
  dataset: {loopEndsAt:new Date(stop).toISOString(), waiting},
  innerHTML:'poll hero',
  querySelector: () => target.innerHTML.includes('night-summary') ? {} : null
};
const dates = {innerHTML:'Enrolment closed on 25 October; advance voting from 26 October; election day 7 November.'};
globalThis.location = {href:'https://example.test/unattended/nz-election/'};
globalThis.document = {
  hidden:false,
  querySelector: selector => selector === '#home-live' ? target : selector === '#dates' ? dates : null,
  addEventListener: (name, fn) => { listeners[name] = fn; }
};
globalThis.setInterval = fn => intervals.push(fn);
const home = '<section id="night-summary">' + (scenario === 'complete' ? 'House: 120 seats.' : '0 national seats reported.') + '</section>';
globalThis.fetch = async url => {
  assert.equal(new URL(url).pathname.endsWith('/night-live.json'), true);
  requests.push(now);
  if (scenario === 'recovery' && requests.length === 1) throw Error('offline');
  return {ok:true, json:async()=>({available:scenario !== 'absent',
    loop_ended:false, loop_ends_at:new Date(stop).toISOString(),
    mode:'Live preliminary results', retrieved_at:new Date(open).toISOString(),
    reference_version:'a'.repeat(64), html:'night page', home_html:home})};
};
await import(process.argv[3] || '../web/home-live.mjs');
const flush = () => new Promise(resolve => setImmediate(resolve));
await flush();
assert.equal(target.innerHTML, 'poll hero');
assert.match(dates.innerHTML, /advance voting from 26 October/);
assert.equal(requests.length, 0);
now = open - 1; intervals.forEach(fn => fn()); await flush();
assert.equal(requests.length, 0);
now = open + 60000; intervals.forEach(fn => fn()); await flush();
assert.equal(requests.length, 1);
assert.equal(dates.innerHTML, '<p>Voting closed on 7 November at 7pm.</p>');
assert.equal(target.innerHTML, ['absent', 'recovery'].includes(scenario) ? waiting : home);
if (scenario === 'recovery') {
  now += 125000; intervals.forEach(fn => fn()); await flush();
  assert.equal(target.innerHTML, home);
  assert.equal(requests.length, 2);
}
now = stop;
const count = requests.length;
intervals.forEach(fn => fn()); await flush();
listeners.visibilitychange(); await flush();
now += 120000; intervals.forEach(fn => fn()); await flush();
assert.equal(requests.length, count);
assert.ok(requests.every(t => t >= open && t < stop));
console.log('PASS DOM handover: ' + scenario);
