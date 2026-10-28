import {NightLive, OPEN} from './night-live.mjs';

const target = document.querySelector('#home-live');
if (target) {
  const stop = Date.parse(target.dataset.loopEndsAt);
  const url = new URL('night-live.json', import.meta.url);
  const live = new NightLive({
    loopEndsAt: target.dataset.loopEndsAt,
    resultNotice: target.dataset.resultNotice,
    status: text => {
      const notice = target.querySelector('#home-live-status');
      if (notice && notice.textContent !== text) notice.textContent = text;
    },
    visible: () => !document.hidden,
    fetcher: () => fetch(url, {cache: 'no-store', credentials: 'omit', mode: 'same-origin', redirect: 'error', signal: AbortSignal.timeout(20000)}),
    render: pack => {
      // Older packages can still serve night/ without replacing the home answer.
      if (Date.now() < stop && typeof pack.home_html === 'string' && pack.home_html) target.innerHTML = pack.home_html;
    }
  });
  const initial = target.querySelector('#home-live-status');
  if (initial && Number.isFinite(Date.parse(initial.dataset.retrievedAt)) && Date.parse(initial.dataset.retrievedAt) >= OPEN) {
    live.last = {retrieved_at: initial.dataset.retrievedAt, mode: initial.dataset.mode, state_sentence: initial.textContent};
  }
  let handedOver = false;
  const tick = () => {
    if (Date.now() < OPEN) return;
    if (!handedOver) {
      // The pre-election timeline shares the result figure and source IDs.
      document.querySelector('#night')?.remove();
      const dates = document.querySelector('#dates');
      if (dates) dates.innerHTML = '<p>Voting closed on 7 November at 7pm.</p>';
      handedOver = true;
    }
    if (Date.now() >= Date.parse(target.dataset.resultNoticeAt)) {
      live.resultNotice = target.dataset.postDateNotice;
      if (live.last) live.last.result_notice = live.resultNotice;
    }
    if (Date.now() >= stop) {
      if (!target.querySelector('#home-night') && target.innerHTML !== target.dataset.settled) target.innerHTML = target.dataset.settled;
      return live.tick();
    }
    if (!target.querySelector('#night-summary')) target.innerHTML = target.dataset.waiting;
    return live.tick();
  };
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) live.invalidate(); else tick();
  });
  tick();
  setInterval(tick, 1000);
}
