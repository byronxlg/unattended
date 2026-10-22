// Execute the real JS detail parser against an ElementTree-serialized DOM fixture.
import {detail} from '../web/night-parser.mjs';
let input = '';
for await (const chunk of process.stdin) input += chunk;
const cases = JSON.parse(input);
function element(tree) {
  const children = tree.children.map(element);
  return {
    tagName: tree.tag, nodeType: 1, children,
    attributes: Object.entries(tree.attrs).map(([name,value])=>({name,value})),
    getAttribute: name=>tree.attrs[name] ?? null,
    hasAttribute: name=>Object.hasOwn(tree.attrs,name),
    childNodes: [...(tree.text ? [{nodeType:3,data:tree.text}] : []), ...children]
  };
}
const results = cases.map(({xml,tree,refs})=>{
  globalThis.DOMParser = class {
    parseFromString(text, type) {
      if (text !== xml || type !== 'application/xml') throw Error('TEST_DOM_INPUT');
      return {documentElement:element(tree), querySelector:()=>null};
    }
  };
  return detail(new TextEncoder().encode(xml),refs);
});
console.log(JSON.stringify(results));
