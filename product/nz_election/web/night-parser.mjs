// Bounded archive XML contract. This module performs no network requests.
const fail = code => { throw Error(code); };
export function count(value) {
  if (typeof value !== 'string' || /^(0|[1-9][0-9]{0,8})$/.exec(value)?.[0] !== value) fail('XML_COUNT');
  return Number(BigInt(value));
}
export function percent(value) {
  if (typeof value !== 'string' || /^[0-9]{1,3}(\.[0-9]{1,2})?$/.exec(value)?.[0] !== value || Number(value) > 100) fail('XML_PERCENT');
  return value;
}
const counts = new Set(['total_voting_places','total_party_informals','total_candidate_informals','total_candidates','votes','party_seats','candidate_seats','total_seats','list_no','total_voting_places_counted','total_votes_cast','total_electorates_final','total_minimal_votes','total_special_votes','total_registered_parties']);
export function documentXML(raw, tag) {
  if (!(raw instanceof Uint8Array) || !raw.length || raw.length > 2000000) fail('XML_DOCUMENT');
  let text;
  try { text = new TextDecoder('utf-8', {fatal:true}).decode(raw); } catch { fail('XML_DOCUMENT'); }
  if (/<!DOCTYPE|<!ENTITY/i.test(text)) fail('XML_DOCUMENT');
  const doc = new DOMParser().parseFromString(text, 'application/xml');
  if (doc.querySelector('parsererror') || doc.documentElement.tagName !== tag) fail('XML_DOCUMENT');
  return doc.documentElement;
}
function fields(node, required) {
  const children = [...node.children];
  if (children.length !== required.length || new Set(children.map(c=>c.tagName)).size !== required.length || children.some(c=>!required.includes(c.tagName))) fail('XML_FIELDS');
  const result = {};
  for (const child of children) {
    // ElementTree's .text stops before the first nested element.
    let leading = '';
    for (const node of child.childNodes) {
      if (node.nodeType === 1) break;
      if (node.nodeType === 3 || node.nodeType === 4) leading += node.data;
    }
    const text = leading || null;
    if (counts.has(child.tagName)) count(text);
    if (child.children.length || child.attributes.length || !text?.trim()) fail('XML_FIELDS');
    result[child.tagName] = text;
  }
  return result;
}
function records(root, tag, attr, required) {
  const result = {};
  for (const node of root.children) {
    if (node.tagName !== tag || node.attributes.length !== 1 || !node.hasAttribute(attr)) fail('XML_REFERENCE');
    const id = node.getAttribute(attr); count(id);
    if (Object.hasOwn(result,id)) fail('XML_REFERENCE');
    result[id] = fields(node,required);
  }
  if (!Object.keys(result).length) fail('XML_REFERENCE');
  return result;
}
const canonical = v => v && typeof v === 'object' ? (Array.isArray(v) ? '[' + v.map(canonical).join(',') + ']' : '{' + Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',') + '}') : JSON.stringify(v);
export async function references(parties, electorates, candidates) {
  const refs = {
    parties:records(documentXML(parties,'parties'),'party','p_no',['abbrev','short_name','party_name','registered']),
    electorates:records(documentXML(electorates,'electorates'),'electorate','e_no',['electorate_name']),
    candidates:records(documentXML(candidates,'candidates'),'candidate','c_no',['candidate_name','electorate','party','list_no'])
  };
  const ranks = new Set();
  for (const c of Object.values(refs.candidates)) {
    const rank = count(c.list_no), key = c.party+':'+rank;
    if ((!Object.hasOwn(refs.parties,c.party) && c.party !== '0') || (c.electorate !== '0' && !Object.hasOwn(refs.electorates,c.electorate)) || (rank && ranks.has(key))) fail('XML_REFERENCE');
    if (rank) ranks.add(key);
  }
  if (Object.values(refs.parties).some(p=>!['yes','no'].includes(p.registered))) fail('XML_REFERENCE');
  const digest = await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(refs)));
  return {...refs,reference_version:[...new Uint8Array(digest)].map(b=>b.toString(16).padStart(2,'0')).join('')};
}
export function election(raw, refs) {
  const root = documentXML(raw,'election'), local = root.getAttribute('updated');
  if (root.attributes.length !== 1 || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$/.test(local || '') || local.startsWith('0000') || !Number.isFinite(Date.parse(local+'Z')) || new Date(local+'Z').toISOString().slice(0,19) !== local) fail('XML_TIMESTAMP');
  if ([...root.children].map(c=>c.tagName).join(',') !== 'statistics,partystatus') fail('XML_FIELDS');
  let stats = fields(root.children[0],['total_voting_places_counted','percent_voting_places_counted','total_votes_cast','percent_votes_cast','total_electorates_final','percent_electorates_final','total_minimal_votes','total_special_votes','total_registered_parties']);
  stats = Object.fromEntries(Object.entries(stats).map(([k,v])=>[k,k.startsWith('percent_')?percent(v):count(v)]));
  let parties = records(root.children[1],'party','p_no',['votes','percent_votes','party_seats','candidate_seats','total_seats']);
  parties = Object.fromEntries(Object.entries(parties).map(([p,r])=>[p,Object.fromEntries(Object.entries(r).map(([k,v])=>[k,k==='percent_votes'?percent(v):count(v)]))]));
  if (Object.keys(parties).some(p=>!Object.hasOwn(refs.parties,p))) fail('XML_REFERENCE');
  const rows = Object.values(parties), sum = key => rows.reduce((s,r)=>s+BigInt(r[key]),0n);
  const valid = sum('votes'), electorateCount = Object.keys(refs.electorates).length;
  if (valid > BigInt(stats.total_votes_cast) || stats.total_electorates_final > electorateCount || sum('candidate_seats') > BigInt(electorateCount)) fail('XML_TOTAL');
  for (const r of rows) {
    if (r.total_seats !== r.party_seats+r.candidate_seats || (!valid && (Number(r.percent_votes) || r.total_seats))) fail('XML_TOTAL');
    const precision = 10n ** BigInt((r.percent_votes.split('.')[1]||'').length);
    const delta = BigInt(r.percent_votes.replace('.',''))*valid - 100n*BigInt(r.votes)*precision;
    if (valid && (delta < 0n ? -delta : delta) > valid) fail('XML_TOTAL');
  }
  return {reference_version:refs.reference_version,source_updated_local:local,statistics:stats,party_results:parties,valid_party_votes:Number(valid),reported_house:Number(sum('total_seats'))};
}
export function detail(raw, refs) {
  const root = documentXML(raw, 'electorate'), id = root.getAttribute('e_no'), local = root.getAttribute('updated');
  if (root.attributes.length !== 3 || [...root.attributes].some(a=>!['e_no','final','updated'].includes(a.name)) || !Object.hasOwn(refs.electorates,id) || !['true','false'].includes(root.getAttribute('final'))) fail('XML_REFERENCE');
  if (!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$/.test(local || '') || local.startsWith('0000') || !Number.isFinite(Date.parse(local+'Z')) || new Date(local+'Z').toISOString().slice(0,19) !== local) fail('XML_TIMESTAMP');
  if ([...root.children].map(c=>c.tagName).join(',') !== 'statistics,partyvotes,candidatevotes') fail('XML_FIELDS');
  const stats = Object.fromEntries(Object.entries(fields(root.children[0], ['total_voting_places','total_voting_places_counted','percent_voting_places_counted','total_votes_cast','percent_votes_cast','total_party_informals','total_candidate_informals','total_registered_parties','total_candidates'])).map(([k,v])=>[k,k.startsWith('percent_')?percent(v):count(v)]));
  const parties = Object.fromEntries(Object.entries(records(root.children[1],'party','p_no',['votes'])).map(([k,v])=>[k,count(v.votes)]));
  const candidates = Object.fromEntries(Object.entries(records(root.children[2],'candidate','c_no',['votes'])).map(([k,v])=>[k,count(v.votes)]));
  if (Object.keys(parties).some(p=>!Object.hasOwn(refs.parties,p)) || Object.keys(candidates).some(c=>!Object.hasOwn(refs.candidates,c) || refs.candidates[c].electorate !== id)) fail('XML_REFERENCE');
  const sum = obj=>Object.values(obj).reduce((a,b)=>a+b,0);
  if (stats.total_voting_places_counted > stats.total_voting_places || Object.keys(candidates).length !== stats.total_candidates || sum(parties)+stats.total_party_informals > stats.total_votes_cast || sum(candidates)+stats.total_candidate_informals > stats.total_votes_cast) fail('XML_TOTAL');
  const ordered=Object.keys(candidates).sort((a,b)=>candidates[b]-candidates[a] || (a<b?-1:1));
  const margin=candidates[ordered[0]]-(ordered.length>1?candidates[ordered[1]]:0);
  const reported=stats.total_voting_places_counted>0 && sum(candidates)>0;
  const leader=reported && margin>0 ? ordered[0] : null;
  return {electorate_id:id,source_updated_local:local,statistics:stats,party_votes:parties,candidate_votes:candidates,leader,margin:reported?margin:null,...(reported && margin===0?{tied_candidates:ordered.filter(c=>candidates[c]===candidates[ordered[0]])}:{}),status:reported && stats.total_voting_places>0 && stats.total_voting_places_counted===stats.total_voting_places && root.getAttribute('final')==='true'?'final':reported?'provisional':'not yet reported'};
}
