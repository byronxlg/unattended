// BigInt keeps quotient ordering independent of display rounding.
function integer(v) {
  if (typeof v === 'string' && /^(0|[1-9][0-9]*)$/.test(v)) return BigInt(v);
  if (typeof v === 'number' && Number.isSafeInteger(v) && v >= 0) return BigInt(v);
  throw Error('INVALID_INPUT: non-negative integer required');
}
function fail(message) { throw Error(`INVALID_INPUT: ${message}`); }
export function allocate(data) {
  const votes = Object.fromEntries(Object.entries(data.partyVotes).map(([p,v]) => [p,integer(v)]));
  const wins = Object.fromEntries(Object.entries(data.electorateWins).map(([p,v]) => [p,integer(v)]));
  const {lists, electorateWinners: winners, nonListWinners: nonlist} = data;
  const base = integer(data.baseSeats ?? 120), parties = Object.keys(votes).sort();
  const total = Object.values(votes).reduce((a,b) => a+b,0n);
  const same = obj => Object.keys(obj).length === parties.length && parties.every(p => p in obj);
  if (!base || !total || !same(wins)) fail('base, votes or party counts');
  if (Object.keys(lists).some(p => !(p in votes)) || !same(winners)) fail('unknown or missing party');
  const seen = new Map(); let elected = 0n;
  for (const p of parties) {
    const ls = lists[p] ?? [], ws = winners[p];
    if (!Array.isArray(ls) || !Array.isArray(ws)) fail('candidate arrays required');
    if (new Set(ls).size !== ls.length || new Set(ws).size !== ws.length || BigInt(ws.length) !== wins[p]) fail('candidate counts');
    if (wins[p] && !(p in lists)) fail('unlisted winners belong in nonListWinners');
    for (const c of [...ls,...ws]) {
      if (typeof c !== 'string' || !c || (seen.has(c) && seen.get(c) !== p)) fail('candidate identity');
      seen.set(c,p);
    }
    elected += BigInt(ws.length);
  }
  if (!Array.isArray(nonlist) || nonlist.some(c => typeof c !== 'string' || !c)) fail('non-list candidate identity');
  if (new Set(nonlist).size !== nonlist.length || nonlist.some(c => seen.has(c))) fail('duplicate candidate');
  if (elected + BigInt(nonlist.length) > base) fail('electorate capacity');
  const count = base - BigInt(nonlist.length);
  const eligible = parties.filter(p => lists[p]?.length && (100n*votes[p] >= 5n*total || wins[p]));
  if (count && !eligible.length) fail('no eligible parties');
  const qs = [];
  for (const p of eligible) for (let d=1n; d<2n*count+2n; d+=2n) qs.push({p,d});
  const cmp = (a,b) => { const v=votes[a.p]*b.d-votes[b.p]*a.d; return v>0n ? -1 : v<0n ? 1 : 0; };
  qs.sort(cmp);
  let selected = qs.slice(0,Number(count)), unresolved = [];
  if (count && qs.length > Number(count) && cmp(qs[Number(count)-1],qs[Number(count)])===0) {
    const boundary=qs[Number(count)], above=qs.filter(q=>cmp(q,boundary)<0), tied=qs.filter(q=>cmp(q,boundary)===0);
    const lot=data.tieOrder ?? {}, order=lot.order ?? [];
    const tiedParties=new Set(tied.map(q=>q.p));
    if (!lot.reference || new Set(order).size!==order.length || order.length!==tiedParties.size || order.some(p=>!tiedParties.has(p))) {
      unresolved=[{rank:above.length+1,places_remaining:Number(count)-above.length,candidates:tied.map(q=>q.p),tie_order_ref:null}];
    } else { tied.sort((a,b)=>order.indexOf(a.p)-order.indexOf(b.p)); selected=[...above,...tied.slice(0,Number(count)-above.length)]; }
  }
  if (unresolved.length) return {entitlements:null,listMembers:null,seats:null,overhang:null,vacancies:null,occupiedHouse:null,quotients:[],unresolvedTies:unresolved};
  const entitlements=Object.fromEntries(parties.map(p=>[p,0]));
  const quotients=selected.map((q,i)=>{entitlements[q.p]++;return {rank:i+1,party_id:q.p,numerator:String(votes[q.p]),divisor:String(q.d),selected:true};});
  const listMembers={},seats={}; let overhang=0,vacancies=0;
  for (const p of parties) {
    const w=Number(wins[p]), needed=Math.max(0,entitlements[p]-w);
    listMembers[p]=(lists[p]??[]).filter(c=>!winners[p].includes(c)).slice(0,needed);
    seats[p]=w+listMembers[p].length; vacancies+=needed-listMembers[p].length; overhang+=Math.max(0,w-entitlements[p]);
  }
  return {entitlements,listMembers,seats,overhang,vacancies,occupiedHouse:Number(base)+overhang-vacancies,quotients,unresolvedTies:[]};
}
