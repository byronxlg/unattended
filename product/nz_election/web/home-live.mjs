import {NightLive, OPEN} from './night-live.mjs';

const target = document.querySelector('#home-live');
if (target) {
  const stop = Date.parse(target.dataset.loopEndsAt);
  const url = new URL('night-live.json', import.meta.url);
  const live = new NightLive({
    loopEndsAt: target.dataset.loopEndsAt,
    visible: () => !document.hidden,
    fetcher: () => fetch(url, {cache: 'no-store', credentials: 'omit', mode: 'same-origin', redirect: 'error', signal: AbortSignal.timeout(20000)}),
    render: pack => {
      // Older packages can still serve night/ without replacing the home answer.
      if (typeof pack.home_html === 'string' && pack.home_html) target.innerHTML = pack.home_html;
    }
  });
  let handedOver = false;
  const tick = () => {
    if (Date.now() < OPEN) return;
    if (!handedOver) {
      const dates = document.querySelector('#dates');
      if (dates) dates.innerHTML = '<p>Voting closed on 7 November at 7pm.</p>';
      handedOver = true;
    }
    if (Date.now() >= stop) return;
    if (!target.querySelector('#night-summary')) target.innerHTML = target.dataset.waiting;
    return live.tick();
  };
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) live.invalidate(); else tick();
  });
  tick();
  setInterval(tick, 1000);
}
