// Run the actual startup modules against the server tree without network or a browser.
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
class Element {
  constructor(node) {
    this.tag = node.tag; this.attrs = node.attrs;
    this.children = node.children.map(c => typeof c === 'string' ? c : new Element(c));
    for (const child of this.children) if (typeof child !== 'string') child.parent = this;
    this.dataset = Object.fromEntries(Object.entries(this.attrs).filter(([k]) => k.startsWith('data-'))
      .map(([k, v]) => [k.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase()), v]));
  }
  get textContent() { return this.tag === 'template' ? '' : this.children.map(c => typeof c === 'string' ? c : c.textContent).join(''); }
  set textContent(value) { this.children = [value]; }
  matches(selector) {
    if (selector.startsWith('#')) return this.attrs.id === selector.slice(1);
    if (selector.startsWith('.')) return (this.attrs.class || '').split(' ').includes(selector.slice(1));
    if (selector === 'template[id^="sequence-"]') return this.tag === 'template' && this.attrs.id.startsWith('sequence-');
    if (/^\[[\w-]+\]$/.test(selector)) return selector.slice(1, -1) in this.attrs;
    throw Error('Unsupported selector: ' + selector);
  }
  querySelectorAll(selector) {
    return this.children.flatMap(c => typeof c === 'string' ? [] :
      [...(c.matches(selector) ? [c] : []), ...(c.tag === 'template' ? [] : c.querySelectorAll(selector))]);
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  replaceChildren(...children) { this.children = children; }
  remove() { this.parent.children = this.parent.children.filter(c => c !== this); }
  addEventListener() {}
}
const root = new Element(input.tree);
const document = {
  querySelector: s => root.querySelector(s), querySelectorAll: s => root.querySelectorAll(s),
  getElementById: id => root.querySelector('#' + id), addEventListener() {}, hidden: false,
};
Object.assign(globalThis, {document, location: {href: 'https://example.invalid/night/'},
  HTMLTemplateElement: class {}, setInterval() {}, setTimeout() {}, clearTimeout() {},
  fetch() { throw Error('Unexpected startup fetch before polling opens'); }});
Date.now = () => Date.parse(input.built);
const before = root.textContent;
for (const module of ['night.mjs', 'night-live.mjs']) {
  await import(pathToFileURL(path.join(process.argv[2], module)));
}
process.stdout.write(JSON.stringify({before, after: root.textContent}));
