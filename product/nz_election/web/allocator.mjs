// BigInt keeps quotient ordering independent of display rounding.
// All numeric fields accept non-negative safe integers, regardless of JSON spelling.
function integer(v) {
  if (typeof v === 'string' && /^(0|[1-9][0-9]*)$/.test(v)) return BigInt(v);
  if (typeof v === 'number' && Number.isSafeInteger(v) && v >= 0) return BigInt(v);
  throw Error('INVALID_INPUT');
}
// Python compares Unicode code points; JS's default sort compares UTF-16 units.
function comparePartyIds(left, right) {
  const a = Array.from(left, c => c.codePointAt(0));
  const b = Array.from(right, c => c.codePointAt(0));
  for (let i = 0; i < Math.min(a.length, b.length); i++) {
    if (a[i] !== b[i]) return a[i] - b[i];
  }
  return a.length - b.length;
}
function fail() { throw Error('INVALID_INPUT'); }
const own = (obj, key) => Object.hasOwn(obj, key);
const record = obj => obj !== null && typeof obj === 'object' && !Array.isArray(obj)
  && (Object.getPrototypeOf(obj) === Object.prototype || Object.getPrototypeOf(obj) === null);
function validateShape(data) {
  const required = ['partyVotes', 'electorateWins', 'lists', 'electorateWinners', 'nonListWinners'];
  if (!record(data) || required.some(k => !own(data,k))
      || Object.keys(data).some(k => ![...required,'baseSeats','tieOrder'].includes(k))) fail();
  for (const key of ['partyVotes','electorateWins','lists','electorateWinners']) {
    if (!record(data[key])) fail();
  }
  const candidates = value => Array.isArray(value)
    && Array.from(value).every(c => typeof c === 'string' && c.length > 0);
  for (const key of ['lists','electorateWinners']) {
    if (!Object.values(data[key]).every(candidates)) fail();
  }
  if (!candidates(data.nonListWinners)) fail();
  if (own(data,'tieOrder')) {
    const lot=data.tieOrder;
    if (!record(lot) || Object.keys(lot).some(k => !['order','reference'].includes(k))) fail();
    if (own(lot,'order') && (!Array.isArray(lot.order)
        || !Array.from(lot.order).every(p => typeof p === 'string'))) fail();
    if (own(lot,'reference') && typeof lot.reference !== 'string') fail();
  }
}
export function allocate(data) {
  validateShape(data);
  const votes = Object.fromEntries(Object.entries(data.partyVotes).map(([p,v]) => [p,integer(v)]));
  const wins = Object.fromEntries(Object.entries(data.electorateWins).map(([p,v]) => [p,integer(v)]));
  const {lists, electorateWinners: winners, nonListWinners: nonlist} = data;
  const base = integer(own(data,'baseSeats') ? data.baseSeats : 120), parties = Object.keys(votes).sort(comparePartyIds);
  const total = Object.values(votes).reduce((a,b) => a+b,0n);
  const same = obj => Object.keys(obj).length === parties.length && parties.every(p => own(obj,p));
  if (!base || !total || !same(wins)) fail();
  if (Object.keys(lists).some(p => !own(votes,p)) || !same(winners)) fail();
  const seen = new Map(); let elected = 0n;
  for (const p of parties) {
    const ls = own(lists,p) ? lists[p] : [], ws = winners[p];
    if (!Array.isArray(ls) || !Array.isArray(ws)) fail();
    if (new Set(ls).size !== ls.length || new Set(ws).size !== ws.length || BigInt(ws.length) !== wins[p]) fail();
    if (wins[p] && !own(lists,p)) fail();
    for (const c of [...ls,...ws]) {
      if (typeof c !== 'string' || !c || (seen.has(c) && seen.get(c) !== p)) fail();
      seen.set(c,p);
    }
    elected += BigInt(ws.length);
  }
  if (!Array.isArray(nonlist) || nonlist.some(c => typeof c !== 'string' || !c)) fail();
  if (new Set(nonlist).size !== nonlist.length || nonlist.some(c => seen.has(c))) fail();
  if (elected + BigInt(nonlist.length) > base) fail();
  const count = base - BigInt(nonlist.length);
  const eligible = parties.filter(p => (own(lists,p) && lists[p].length) && (100n*votes[p] >= 5n*total || wins[p]));
  if (count && !eligible.length) fail();
  const allocation=entitlement(votes,eligible,count,data.tieOrder);
  if (allocation.unresolvedTies.length) return {...allocation,listMembers:null,seats:null,overhang:null,vacancies:null,occupiedHouse:null};
  const {entitlements,quotients}=allocation;
  const listMembers=Object.create(null),seats=Object.create(null); let overhang=0,vacancies=0;
  for (const p of parties) {
    const w=Number(wins[p]), needed=Math.max(0,entitlements[p]-w);
    listMembers[p]=(own(lists,p) ? lists[p] : []).filter(c=>!winners[p].includes(c)).slice(0,needed);
    seats[p]=w+listMembers[p].length; vacancies+=needed-listMembers[p].length; overhang+=Math.max(0,w-entitlements[p]);
  }
  return {entitlements,listMembers,seats,overhang,vacancies,occupiedHouse:Number(base)+overhang-vacancies,quotients,unresolvedTies:[]};
}

// Shared primitive also supports theoretical seats without fabricated list candidates.
export function entitlement(votes, eligible, count=120n, tieOrder=null) {
  const parties=Object.keys(votes).sort(comparePartyIds);
  const qs = [];
  for (const p of eligible) for (let d=1n; d<2n*count+2n; d+=2n) qs.push({p,d});
  const cmp = (a,b) => { const v=votes[a.p]*b.d-votes[b.p]*a.d; return v>0n ? -1 : v<0n ? 1 : 0; };
  qs.sort(cmp);
  let selected = qs.slice(0,Number(count)), unresolved = [];
  if (count && qs.length > Number(count) && cmp(qs[Number(count)-1],qs[Number(count)])===0) {
    const boundary=qs[Number(count)], above=qs.filter(q=>cmp(q,boundary)<0), tied=qs.filter(q=>cmp(q,boundary)===0);
    const lot=tieOrder ?? {}, order=lot.order ?? [];
    const tiedParties=new Set(tied.map(q=>q.p));
    if (!lot.reference || new Set(order).size!==order.length || order.length!==tiedParties.size || order.some(p=>!tiedParties.has(p))) {
      unresolved=[{rank:above.length+1,places_remaining:Number(count)-above.length,candidates:tied.map(q=>q.p),tie_order_ref:null}];
    } else { tied.sort((a,b)=>order.indexOf(a.p)-order.indexOf(b.p)); selected=[...above,...tied.slice(0,Number(count)-above.length)]; }
  }
  if (unresolved.length) return {entitlements:null,quotients:[],unresolvedTies:unresolved};
  const entitlements=Object.fromEntries(parties.map(p=>[p,0]));
  const quotients=selected.map((q,i)=>{entitlements[q.p]++;return {rank:i+1,party_id:q.p,numerator:String(votes[q.p]),divisor:String(q.d),selected:true};});
  return {entitlements,quotients,unresolvedTies:[]};
}
