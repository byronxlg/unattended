export const OPEN = Date.parse('2026-11-07T06:00:00Z');
export const FLOOR = 60000;
export const STALE = 15 * 60000;

export class NightLive {
  constructor({fetcher, loopEndsAt, resultNotice, now = Date.now, visible = () => true, render = () => {}, status = () => {}}) {
    Object.assign(this, {fetcher, loopEndsAt, resultNotice, now, visible, render, status});
    this.next = 0; this.failures = 0; this.pending = false; this.last = null; this.generation = 0;
  }
  ended() { return this.loopEnded || this.now() >= Date.parse(this.loopEndsAt); }
  invalidate() { this.generation++; }
  notice() {
    if (['Settled preliminary results', 'Official results'].includes(this.last?.mode)) {
      this.status(this.last.state_sentence); return;
    }
    if (this.ended()) {
      this.status('Preliminary; ' + (this.last?.result_notice || this.resultNotice || 'official results due 27 November.').replace(/^Official/, 'official') + ' Live updates ended.' +
        (this.last ? ' Last complete capture ' + this.last.retrieved_at + '.' : ' Check official results.')); return;
    }
    this.status(this.now() < OPEN ? 'Results start at 19:00 NZDT on 7 November.' : !this.last ?
      'Showing the dated packaged snapshot; check official results.' :
      this.now() - Date.parse(this.last.retrieved_at) >= STALE ?
      `Stale: last complete cycle retrieved ${this.last.retrieved_at}. Check official results.` :
      `Preliminary results. Packaged by the site at ${this.last.retrieved_at}.`);
  }
  async tick() {
    this.notice();
    if (this.ended() || ['Settled preliminary results', 'Official results'].includes(this.last?.mode) || this.now() < OPEN || !this.visible() || this.pending || this.now() < this.next) return;
    this.pending = true;
    this.next = this.now() + FLOOR;
    const generation = this.generation;
    try {
      const response = await this.fetcher();
      if (!response.ok) {
        const header = response.headers?.get('Retry-After');
        const retry = /^\d+$/.test(header || '') ? Number(header) : (Date.parse(header) - this.now()) / 1000;
        if (Number.isFinite(retry) && retry > 0) this.next = Math.max(this.next, this.now() + Math.min(retry, 3600) * 1000);
        throw Error('PACKAGE_UNAVAILABLE');
      }
      const pack = await response.json();
      if (generation !== this.generation || !this.visible()) return;
      const hasStop = typeof pack.loop_ended === 'boolean' && typeof pack.loop_ends_at === 'string' &&
        Number.isFinite(Date.parse(pack.loop_ends_at));
      if (pack.available === false && hasStop) {
        this.loopEnded = pack.loop_ended; this.loopEndsAt ??= pack.loop_ends_at; return;
      }
      if (!pack.available || !['Live preliminary results', 'Settled preliminary results', 'Official results'].includes(pack.mode) ||
          (pack.mode !== 'Live preliminary results' && (typeof pack.state_sentence !== 'string' || !pack.state_sentence.trim())) || !Number.isFinite(Date.parse(pack.retrieved_at)) ||
          Date.parse(pack.retrieved_at) < OPEN || Date.parse(pack.retrieved_at) > this.now() || typeof pack.html !== 'string' ||
          !/^[a-f0-9]{64}$/.test(pack.reference_version)) throw Error('PACKAGE_INVALID');
      if (generation !== this.generation || !this.visible()) return;
      if (this.last && Date.parse(pack.retrieved_at) < Date.parse(this.last.retrieved_at)) return;
      if (hasStop) { this.loopEnded = pack.loop_ended; this.loopEndsAt ??= pack.loop_ends_at; }
      this.last = pack; this.failures = 0;
      this.render(pack);
    } catch {
      this.failures++;
      this.next = Math.max(this.next, this.now() + Math.min(15 * FLOOR, FLOOR * 2 ** Math.min(this.failures, 4)));
    } finally { this.pending = false; this.notice(); }
  }
}

if (typeof document !== 'undefined' && [null, 'live'].includes(new URL(location.href).searchParams.get('sequence'))) {
  const target = document.querySelector('#night-snapshot');
  const notice = document.querySelector('#night-live-status');
  if (target && notice) {
    // import.meta.url is at the product root; requests never leave that origin.
    const url = new URL('night-live.json', import.meta.url);
    const live = new NightLive({
      loopEndsAt: target.dataset.loopEndsAt,
      resultNotice: target.dataset.resultNotice,
      visible: () => !document.hidden,
      fetcher: () => fetch(url, {cache: 'no-store', credentials: 'omit', mode: 'same-origin', redirect: 'error', signal: AbortSignal.timeout(20000)}),
      status: text => {
        if (notice.textContent !== text) notice.textContent = text;
        if (Date.now() >= OPEN) document.querySelectorAll('.night-page > .countdown, .night-page > p:has(a[href$="vote/"])').forEach(n => n.remove());
      },
      render: pack => {
        const query = target.querySelector('.night-search')?.value || '';
        const focused = target.querySelector('.night-search') === document.activeElement;
        target.innerHTML = pack.html;
        if (pack.mode !== 'Live preliminary results') document.querySelector('#night-result-status')?.remove();
        target.dataset.mode = pack.mode;
        target.dataset.retrievedAt = pack.retrieved_at;
        const search = target.querySelector('.night-search');
        if (search) { search.value = query; search.dispatchEvent(new Event('input', {bubbles:true})); if (focused) search.focus({preventScroll:true}); }
        document.querySelector('#night-controls').hidden = true;
        target.querySelectorAll('.source-actions a').forEach(link => {
          if (link.textContent === 'Snapshot JSON' || link.textContent === 'CSV') link.textContent += ' (Packaged by the site)';
        });
      }
    });
    const initial = target.dataset.retrievedAt;
    if (Number.isFinite(Date.parse(initial)) && Date.parse(initial) >= OPEN) live.last = {retrieved_at: initial, mode: target.dataset.mode, state_sentence: notice.textContent};
    document.addEventListener('visibilitychange', () => { if (document.hidden) live.invalidate(); else live.tick(); });
    live.tick();
    setInterval(() => live.tick(), 1000);
  }
}
