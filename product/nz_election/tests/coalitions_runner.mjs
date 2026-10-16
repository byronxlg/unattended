import {canonical, decode, inputs, scenario} from '../web/coalitions.mjs';
let raw='';
for await (const chunk of process.stdin) raw+=chunk;
const results=JSON.parse(raw).map(request=>{
  try {
    if (request.op==='decode') return {result:decode(request.hash,request.parties)};
    const data=inputs(request.average,request.seats,request.fingerprint);
    return {result:request.op==='inputs'?data:scenario(data,Object.hasOwn(request,'state')?request.state:data.initial)};
  } catch (e) { return {error:e.message}; }
});
process.stdout.write(canonical(results));
