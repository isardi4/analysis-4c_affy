/* Exact source-based candidate generator. No game simulation or hidden draws. */
globalThis.AffinityComposition = (() => {
  'use strict';
  const colors = ['W', 'U', 'B', 'R'];
  const bridges = [
    ['Razortide Bridge', [1,1,0,0]], ['Mistvault Bridge', [0,1,1,0]],
    ['Drossforge Bridge', [0,0,1,1]], ['Rustvale Bridge', [1,0,0,1]],
    ['Goldmire Bridge', [1,0,1,0]], ['Silverbluff Bridge', [0,1,0,1]],
  ];
  const monos = ['Ancient Den', 'Seat of the Synod', 'Vault of Whispers', 'Great Furnace'];
  const cache = new Map();
  function bounded(total, size) {
    if (size === 1) return total >= 0 && total <= 4 ? [[total]] : [];
    const result = [];
    for (let n = Math.max(0,total-4*(size-1)); n <= Math.min(4,total); n++) {
      for (const rest of bounded(total-n,size-1)) result.push([n,...rest]);
    }
    return result;
  }
  function hit(sources, cards) {
    let miss = 1;
    for (let i=0;i<cards;i++) miss *= (60-sources-i)/(60-i);
    return 1-miss;
  }
  const hit7 = Array.from({length:20},(_,s)=>hit(s,7));
  const hit9 = Array.from({length:20},(_,s)=>hit(s,9));
  function universe(count) {
    if (!cache.has(count)) {
      cache.set(count, {
        bv: bounded(count,6).map(v=>({v,s:colors.map((_,c)=>v.reduce((sum,n,i)=>sum+n*bridges[i][1][c],0))})),
        uv: bounded(19-count,4),
      });
    }
    return cache.get(count);
  }
  function choose(weights, count=10) {
    if (!Number.isInteger(count) || count < 9 || count > 14) throw Error('Bridges debe estar entre 9 y 14.');
    if (!Array.isArray(weights) || weights.length!==4 || weights.some(w=>!Number.isFinite(w)||w<0) || !weights.some(w=>w>0)) throw Error('Asigná al menos un peso mayor que cero.');
    const scale = Math.max(...weights), w = weights.map(x=>x/scale);
    const {bv,uv} = universe(count);
    const early = uv.map(v=>v.reduce((s,n,c)=>s+w[c]*hit7[n],0));
    const eps=1e-12;
    let best, score=-Infinity, secondary=-Infinity, ties=0;
    for (const bridge of bv) for (let j=0;j<uv.length;j++) {
      const u=uv[j], s=bridge.s.map((n,c)=>n+u[c]);
      const objective=s.reduce((sum,n,c)=>sum+w[c]*hit9[n],0);
      const better=objective>score+eps, equal=Math.abs(objective-score)<=eps;
      if (better) { score=objective; ties=1; secondary=-Infinity; }
      else if (equal) ties++;
      if (better || (equal && early[j]>secondary+eps)) {
        secondary=early[j]; best={bv:bridge.v,uv:u,sources:s};
      }
    }
    const lands=Object.fromEntries([...bridges.map(([name],i)=>[name,best.bv[i]]),...monos.map((name,i)=>[name,best.uv[i]])].filter(([,n])=>n));
    return {model:'natural-sources-v1',weights:[...weights],bridges:count,untapped:19-count,
      lands,sources:best.sources,untapped_sources:best.uv,
      natural_in_7:best.sources.map(s=>hit7[s]),natural_in_9:best.sources.map(s=>hit9[s]),
      untapped_in_7:best.uv.map(s=>hit7[s]),score,secondary_score:secondary,
      bases_evaluated:bv.length*uv.length,primary_ties:ties,
      scope:'Fuentes naturales; sin mulligans, Boulder, entrada girada ni simulación de partidas.',
      tie_break:'Mayor cobertura ponderada de fuentes enderezadas en siete; luego orden estable de cartas.'};
  }
  return {choose,hit,colors,bridges,monos};
})();
if (typeof module !== 'undefined') module.exports=globalThis.AffinityComposition;
