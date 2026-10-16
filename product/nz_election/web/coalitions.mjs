import {entitlement} from './allocator.mjs';

const fail = () => { throw Error('INVALID_COALITION_STATE'); };
const record = x => x !== null && typeof x === 'object' && !Array.isArray(x)
  && [Object.prototype, null].includes(Object.getPrototypeOf(x));
const same = (a,b) => JSON.stringify([...a].sort()) === JSON.stringify([...b].sort());
export const canonical = x => JSON.stringify(sort(x));
function sort(x) {
  if (Array.isArray(x)) return x.map(sort);
  if (record(x)) return Object.fromEntries(Object.keys(x).sort().map(k => [k,sort(x[k])]));
  return x;
}
function count(v) {
  if (typeof v !== 'string' || v.length > 2 || !/^(0|[1-9][0-9]?)(?![\s\S])/.test(v) || BigInt(v)>71n) fail();
  return BigInt(v);
}
export function validate(state, parties) {
  if (!record(state) || !same(Object.keys(state), ['version','selected','counts','mode','fingerprint'])
      || state.version !== 1 || state.mode !== 'unchecked'
      || typeof state.fingerprint !== 'string' || !/^[0-9a-f]{64}(?![\s\S])/.test(state.fingerprint)
      || !Array.isArray(state.selected) || state.selected.some(p => !parties.includes(p))
      || new Set(state.selected).size !== state.selected.length
      || !record(state.counts) || !same(Object.keys(state.counts), parties)) fail();
  if (Object.values(state.counts).reduce((s,v)=>s+count(v),0n)>71n) fail();
  return state;
}
export function decode(value, parties) {
  try {
    if (typeof value !== 'string' || value.length > 8192 || !value.startsWith('#coalition=')) fail();
    const raw=decodeURIComponent(value.slice(11));
    const state=validate(JSON.parse(raw),parties);
    if (canonical(state)!==raw) fail();
    return state;
  } catch { fail(); }
}
export const encode = state => '#coalition='+encodeURIComponent(canonical(state));
export function inputs(average, seats, fingerprint) {
  try {
    const votes=average.shares, parties=Object.keys(votes).filter(p=>p!=='others').sort();
    if (!parties.length || Object.keys(votes).some(p=>! /^[a-z][a-z0-9-]{0,31}(?![\s\S])/.test(p)
        || ['constructor','prototype','__proto__'].includes(p))
        || average.coherent!==true || !Array.isArray(average.missing) || average.missing.length
        || seats.average_id!==average.id || seats.capacity_checked!==false
        || !Array.isArray(seats.assumptions.non_list_winners) || seats.assumptions.non_list_winners.length
        || seats.assumptions.base_seats!==120) fail();
    if (Object.values(votes).some(v=>!Number.isSafeInteger(v)||v<0)) fail();
    const total=Object.values(votes).reduce((s,v)=>s+BigInt(v),0n);
    if (!Number.isSafeInteger(average.denominator) || total!==BigInt(average.denominator) || total<=0n) fail();
    const ids=average.poll_ids;
    if (!Array.isArray(ids) || !ids.length || new Set(ids).size!==ids.length
        || !same(Object.keys(average.descriptive),Object.keys(votes))
        || Object.keys(votes).some(p=>!same(average.descriptive[p].poll_ids,ids))) fail();
    const wins=seats.assumptions.electorate_wins;
    if (Object.keys(wins).some(p=>!parties.includes(p))
        || Object.values(wins).some(v=>!Number.isSafeInteger(v)||v<0||v>71)) fail();
    const initial={version:1,selected:[],counts:Object.fromEntries(parties.map(p=>[p,String(wins[p]??0)])),mode:'unchecked',fingerprint};
    validate(initial,parties);
    return {parties,votes:Object.fromEntries(Object.entries(votes).map(([p,v])=>[p,String(v)])),initial};
  } catch { throw Error('INCOMPLETE_COALITION_INPUT'); }
}
export function scenario(data,state) {
  validate(state,data.parties);
  if (state.fingerprint!==data.initial.fingerprint) return {warning:'INPUT_FINGERPRINT_MISMATCH',applied:false};
  const votes=Object.fromEntries(Object.entries(data.votes).map(([p,v])=>[p,BigInt(v)]));
  const wins=Object.fromEntries(Object.entries(state.counts).map(([p,v])=>[p,count(v)]));
  const total=Object.values(votes).reduce((s,v)=>s+v,0n);
  const eligible=Object.keys(votes).sort().filter(p=>p!=='others'&&(votes[p]*100n>=total*5n||wins[p]));
  const result=entitlement(votes,eligible);
  const base={occupied_house:null,vacancies:null,majority:null,capacity_checked:false,
    unassigned_electorates:Number(71n-Object.values(wins).reduce((s,v)=>s+v,0n)),unresolved_ties:result.unresolvedTies};
  if (result.unresolvedTies.length || !eligible.length) return {...base,seats:null,entitlements:null,overhang:null,assumed_house:null,assumed_majority:null,selected_total:null};
  const ent=result.entitlements;
  const seats=Object.fromEntries(data.parties.map(p=>[p,Number(BigInt(ent[p])>wins[p]?BigInt(ent[p]):wins[p])]));
  const overhang=data.parties.reduce((s,p)=>s+BigInt(seats[p])-BigInt(ent[p]),0n), house=120n+overhang;
  return {...base,seats,entitlements:ent,overhang:Number(overhang),assumed_house:Number(house),assumed_majority:Number(house/2n+1n),
    selected_total:Number(state.selected.reduce((s,p)=>s+BigInt(seats[p]),0n))};
}

function element(tag, text, className) {
  const node=document.createElement(tag);
  if (text!==undefined) node.textContent=text;
  if (className) node.className=className;
  return node;
}
function picture(root,result,labels) {
  root.replaceChildren();
  const figure=element('figure',undefined,'seat-figure');
  const strip=element('div',undefined,'strip');
  strip.setAttribute('role','img');
  strip.setAttribute('aria-label','Assumed party seats, detailed in the following table');
  const lanes=element('div',undefined,'lanes');
  const table=element('table');
  table.append(element('caption','Assumed seats by party'));
  const body=element('tbody'); table.append(body);
  const house=BigInt(result.assumed_house);
  const percent=n=>String(n*10000n/house/100n)+'.'+String(n*10000n/house%100n).padStart(2,'0')+'%';
  let position=0n, mobile=0, desktop=0;
  for (const [p,n] of Object.entries(result.seats).filter(([,n])=>n).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))) {
    const base=BigInt(result.entitlements[p]), classes=(base<8n?' small':'')+(base<32n?' mobile-small':'');
    const segment=element('div',undefined,'segment'+classes);
    segment.style.width=percent(base); segment.style.background=labels[p].colour;
    const label=element('span',labels[p].name,'seat-label'); label.append(element('strong',String(n)));
    segment.append(label); strip.append(segment);
    if (base<32n) {
      const lane=element('div',undefined,'lane'+classes);
      lane.style.setProperty('--anchor',percent(position+base/2n));
      lane.style.setProperty('--mobile-row',String(mobile++));
      lane.style.setProperty('--desktop-row',String(base<8n?desktop++:0));
      const leader=element('span',undefined,'leader'), elbow=element('span',undefined,'elbow');
      leader.setAttribute('aria-hidden','true'); elbow.setAttribute('aria-hidden','true');
      const name=element('span',labels[p].name,'lane-label'); name.append(element('strong',String(n)));
      lane.append(leader,elbow,name); lanes.append(lane);
    }
    position+=base;
    const row=element('tr'); row.append(element('th',labels[p].name),element('td',String(n))); body.append(row);
  }
  if (result.overhang) {
    const extra=element('div',undefined,'segment overhang');
    extra.style.width=percent(BigInt(result.overhang)); extra.setAttribute('aria-label','Overhang'); strip.append(extra);
  }
  const marker=element('span',undefined,'majority'); marker.style.left=percent(BigInt(result.assumed_majority)); strip.append(marker);
  lanes.style.setProperty('--desktop-height',String(desktop?desktop*96+24:0)+'px');
  lanes.style.setProperty('--mobile-height',String(mobile?mobile*96+24:0)+'px');
  figure.append(strip,lanes,element('figcaption',`${result.overhang} overhang seats. Counts assume sufficient list candidates.`,'strip-note'));
  root.append(figure,table);
}
async function start(root) {
  const note=root.querySelector('[data-note]'), controls=root.querySelector('fieldset');
  try {
    const read=async (name,expected)=>{
      const response=await fetch(new URL('data/'+name,import.meta.url),{credentials:'same-origin'});
      if (!response.ok) throw Error('Data unavailable');
      const raw=await response.text();
      const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw))),v=>v.toString(16).padStart(2,'0')).join('');
      if (hash!==expected) throw Error('Data changed');
      return JSON.parse(raw);
    };
    const [averages,seats]=await Promise.all([read('averages.json',root.dataset.averages),read('seats.json',root.dataset.seats)]);
    if (seats.input_hashes['averages.json']!==root.dataset.averages) throw Error('Data mismatch');
    const data=inputs(averages.data.at(-1),seats.data,root.dataset.fingerprint);
    let state=structuredClone(data.initial);
    const labels=Object.fromEntries([...root.querySelectorAll('[data-party-row]')].map(row=>[row.dataset.partyRow,{name:row.dataset.name,colour:row.dataset.colour}]));
    if (!same(Object.keys(labels),data.parties)) throw Error('Party mismatch');
    const warning=root.querySelector('[data-warning]'), live=root.querySelector('[data-live]'), output=root.querySelector('[data-picture]');
    const sync=()=>{
      for (const p of data.parties) {
        root.querySelector(`[data-select="${p}"]`).checked=state.selected.includes(p);
        root.querySelector(`[data-count="${p}"]`).value=state.counts[p];
      }
    };
    const draw=()=>{
      const r=scenario(data,state);
      if (!r.seats) { live.textContent='Seats are unavailable: no eligible party or an allocation tie needing a recorded lot result.'; output.replaceChildren(); return; }
      live.textContent=`Selected parties: ${r.selected_total} seats. Seats needed for a majority: ${r.assumed_majority}, assuming sufficient list candidates in a House of ${r.assumed_house}.`;
      root.querySelector('[data-unassigned]').textContent=`${r.unassigned_electorates} electorate seats unassigned. 2023 electorate seats assumed; 2026 has different boundaries.`;
      picture(output,r,labels);
    };
    const restore=()=>{
      warning.textContent=''; state=structuredClone(data.initial);
      if (location.hash.startsWith('#coalition')) {
        try {
          const candidate=decode(location.hash,data.parties);
          if (candidate.fingerprint!==data.initial.fingerprint) warning.textContent='This link uses different poll inputs. It has not been applied. Reset to use these inputs.';
          else state=candidate;
        } catch { warning.textContent='This coalition link is invalid. It has not been applied. Reset to start again.'; }
      }
      sync(); draw();
    };
    controls.addEventListener('change',()=>{
      const candidate=structuredClone(state);
      candidate.selected=data.parties.filter(p=>root.querySelector(`[data-select="${p}"]`).checked);
      candidate.counts=Object.fromEntries(data.parties.map(p=>[p,root.querySelector(`[data-count="${p}"]`).value]));
      try {
        validate(candidate,data.parties); state=candidate; warning.textContent=''; draw();
        history.replaceState(null,'',encode(state));
      } catch { warning.textContent='Enter whole electorate counts from 0 to 71, totalling at most 71. The last valid result is shown.'; }
    });
    root.querySelector('[data-reset]').addEventListener('click',()=>{
      history.replaceState(null,'',location.pathname+location.search); restore();
    });
    root.querySelector('[data-share]').addEventListener('click',()=>{
      history.replaceState(null,'',encode(state));
      warning.textContent='The address now contains this scenario. Copy the address to share it.';
    });
    addEventListener('hashchange',restore);
    restore(); controls.hidden=false; controls.disabled=false;
    root.querySelector('[data-results]').hidden=false;
    note.textContent='Choose parties to compare their seats. This is not a prediction of who will form a government.';
  } catch {
    note.textContent='The explorer is unavailable because complete matching inputs could not be loaded. The published information above remains available.';
  }
}
if (typeof document!=='undefined') {
  const root=document.querySelector('#coalition-explorer');
  if (root && root.dataset.averages) start(root);
}
