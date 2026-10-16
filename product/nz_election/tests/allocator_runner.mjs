import {allocate} from '../web/allocator.mjs';
let input='';
for await (const chunk of process.stdin) input+=chunk;
const results=JSON.parse(input).map(data=>{try {return {result:allocate(data)};} catch(e) {return {error:e.message};}});
process.stdout.write(JSON.stringify(results));
