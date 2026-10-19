// Exercise the real startup and drawing path with local data and a minimal DOM adapter.
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import path from 'node:path';

const {site, explorer, parties} = JSON.parse(fs.readFileSync(0, 'utf8'));
const nodes = new Map();
const node = selector => {
  if (!nodes.has(selector)) nodes.set(selector, {
    hidden:true, innerHTML:'', textContent:'', addEventListener(){},
    replaceChildren(){this.innerHTML='';}
  });
  return nodes.get(selector);
};
let finished;
const ready = new Promise(resolve => {finished=resolve;});
Object.defineProperty(node('[data-note]'), 'textContent', {
  set(value){this.message=value; finished();}
});
const root = {
  dataset:explorer,
  querySelector:node,
  querySelectorAll(selector){
    if (selector !== '[data-party-row]') throw Error('Unexpected selector: '+selector);
    return parties.map(dataset => ({dataset}));
  }
};
globalThis.document = {querySelector(selector){
  if (selector !== '#coalition-explorer') throw Error('Unexpected selector: '+selector);
  return root;
}};
globalThis.location = {hash:'', pathname:'', search:''};
globalThis.addEventListener = () => {};
globalThis.fetch = async url => {
  const name=path.basename(new URL(url).pathname);
  if (!['averages.json','seats.json'].includes(name)) throw Error('Unexpected input: '+name);
  return {ok:true, text:async()=>fs.readFileSync(path.join(site,'data',name),'utf8')};
};
await import(pathToFileURL(path.join(site,'coalitions.mjs')));
await ready;
if (node('[data-results]').hidden) throw Error(node('[data-note]').message);
process.stdout.write(node('[data-picture]').innerHTML);
