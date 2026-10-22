import {allocate} from './allocator.mjs';
export function waterfall(inputs, {complete = false, capacity_verified = false} = {}) {
  if (complete !== true) return {status:'incomplete', calculation:null};
  const result = allocate(inputs);
  if (result.unresolvedTies.length) return {status:'unresolved tie', calculation:null};
  if (capacity_verified !== true) for (const key of ['seats','listMembers','occupiedHouse','vacancies']) delete result[key];
  return {status:capacity_verified === true ? 'calculated' : 'unchecked list capacity', calculation:result};
}
