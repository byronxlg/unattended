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

const htmlEscape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#x27;'}[c]));
export function stripHTML(result, labels) {
  const ordered=Object.entries(result.seats).filter(([,n])=>n).sort((a,b)=>b[1]-a[1]||(a[0]<b[0]?-1:1));
  const fixed=n=>n.toFixed(6);
  const percent=n=>{
    const scaled=BigInt(n)*100000000n, house=BigInt(result.assumed_house);
    let units=scaled/house;
    const twice=2n*(scaled%house);
    if(twice>house || (twice===house && units%2n)) units++;
    return String(units/1000000n)+'.'+String(units%1000000n).padStart(6,'0');
  };
  let offset=0;
  const anchors=ordered.map(([p,n])=>{const anchor=offset*100/result.assumed_house; offset+=Math.min(n,result.entitlements[p]); return [p,anchor];});
  const positions=width=>{
    let cursor=0;
    const columns=width>=600?anchors.length:Math.max(1,Math.ceil(anchors.length/2));
    return Object.fromEntries(anchors.map(([p,anchor],index)=>{
      const row=Math.floor(index/columns);
      if(index%columns===0) cursor=0;
      const start=anchor*width/100, remaining=Math.min(columns-index%columns,anchors.length-index);
      const left=Math.min(Math.max(cursor,row===0?start:0),width-remaining*68+8);
      cursor=left+68; return [p,{row,left:left*100/width,anchor:start*100/width}];
    }));
  };
  const mobile=positions(328),desktop=positions(1072);
  let segments='',lanes='',rows='';
  for(const [p,n] of ordered) {
    const base=Math.min(n,result.entitlements[p]), name=htmlEscape(labels[p].name);
    segments+=`<div class="segment" data-party="${htmlEscape(p)}" style="width:${percent(base)}%;background:${htmlEscape(labels[p].colour)}"></div>`;
    for(const [mode,pos] of [['phone',mobile[p]],['wide',desktop[p]]]) {
      if(Math.abs(pos.left-pos.anchor)>.01 || pos.row) {
        const side=pos.anchor>pos.left?'right':'left';
        lanes+=`<span class="label-connector ${mode}" aria-hidden="true" style="left:${fixed(Math.min(pos.left,pos.anchor))}%;width:${fixed(Math.abs(pos.left-pos.anchor))}%;height:${6+pos.row*21}px;border-${side}:1px solid var(--ink)"></span>`;
      }
    }
    lanes+=`<div class="lane" role="group" data-party="${htmlEscape(p)}" style="--row:${mobile[p].row};--left:${fixed(mobile[p].left)}%;--large-left:${fixed(desktop[p].left)}%" aria-label="${name}: ${n} calculated seats"><span>${htmlEscape(p.toUpperCase())}</span> <strong>${n}</strong></div>`;
    rows+=`<tr><td>${name}</td><td>${base}</td><td>${n-base}</td><td>${n}</td></tr>`;
  }
  if(result.overhang) segments+=`<div class="segment overhang" style="width:${percent(result.overhang)}%"></div>`;
  return '<figure class="seat-figure" aria-describedby="source-seats"><div class="strip" role="img" '+
    'aria-describedby="source-seats" aria-label="Theoretical party seats, detailed in the following table">'+segments+
    `<span class="majority" style="left:${percent(result.assumed_majority)}%"></span></div>`+
    '<div class="lanes">'+lanes+'</div>'+`<p class="majority-label">${result.assumed_majority} for a majority</p>`+
    '<figcaption class="strip-note">Calculated seats; list capacity not checked.</figcaption></figure>'+
    '<details class="seat-data"><summary>Seat table and assumptions</summary>'+
    `<p aria-describedby="source-seats">Seats needed for a majority: <strong>${result.assumed_majority}</strong>, `+
    `assuming sufficient list candidates in a House of ${result.assumed_house}.</p>`+
    '<div class="scroll " tabindex="0" role="region" aria-label="Theoretical seats and overhang">'+
    '<table aria-describedby="source-seats"><caption>Theoretical seats and overhang</caption><thead><tr>'+
    ['Party','Base seats','Overhang','Seats'].map(h=>`<th scope="col">${h}</th>`).join('')+
    '</tr></thead><tbody>'+rows+'</tbody></table></div></details>';
}
function picture(root,result,labels) {
  root.innerHTML=stripHTML(result,labels);
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
      root.querySelector('[data-unassigned]').textContent=`${r.unassigned_electorates} electorate seats unassigned. 2023 electorate seats assumed; 2026 has different boundaries.`;
      if (!r.seats) { live.textContent='Seats are unavailable: no eligible party or an allocation tie needing a recorded lot result.'; output.replaceChildren(); return; }
      live.textContent=`Selected parties: ${r.selected_total} seats. Seats needed for a majority: ${r.assumed_majority}, assuming sufficient list candidates in a House of ${r.assumed_house}.`;
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
