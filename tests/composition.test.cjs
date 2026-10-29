const {test}=require('node:test');
const assert=require('node:assert/strict');
const {choose,hit,bridges,monos}=require('../docs/composition.js');

test('equal weights balance natural and untapped coverage without a favored color',()=>{
  const c=choose([1,1,1,1]);
  assert.deepEqual([...c.sources].sort((a,b)=>a-b),[7,7,7,8]);
  assert.deepEqual([...c.untapped_sources].sort((a,b)=>a-b),[2,2,2,3]);
  assert.equal(c.bases_evaluated,120480);
});
test('each of the four colors can be reduced independently',()=>{
  const base=choose([1,1,1,1]);
  for(let color=0;color<4;color++) {
    const weights=[1,1,1,1];weights[color]=.5;
    const c=choose(weights);
    assert(c.sources[color]<base.sources[color]);
    assert(c.sources.filter((_,i)=>i!==color).every(n=>n>=8));
    weights[color]=0;
    assert.equal(choose(weights).sources[color],0);
  }
});
test('several weights can decrease and common scaling preserves the choice',()=>{
  const a=choose([1,.5,.25,.5]),b=choose([.5,.25,.125,.25]);
  assert.deepEqual(a.lands,b.lands);
  assert.deepEqual(a.weights,[1,.5,.25,.5]);
});
test('every ratio respects land totals, four-copy limit and reported sources',()=>{
  for(let n=8;n<=12;n++) {
    const c=choose([.5,1,.25,.75],n);
    assert.equal(Object.values(c.lands).reduce((s,x)=>s+x,0),19);
    assert(Object.values(c.lands).every(x=>x>=1 && x<=4));
    assert.equal(bridges.reduce((s,[name])=>s+(c.lands[name]||0),0),n);
    for(let color=0;color<4;color++) {
      const expected=bridges.reduce((s,[name,mask])=>s+(c.lands[name]||0)*mask[color],0)+(c.lands[monos[color]]||0);
      assert.equal(c.sources[color],expected);
    }
  }
});
test('probabilities are raw hypergeometric source hits, not turn availability',()=>{
  assert.equal(hit(0,7),0);
  assert(Math.abs(hit(1,7)-7/60)<1e-12);
  const c=choose([1,1,1,.5]);
  c.natural_in_9.forEach((p,i)=>assert(Math.abs(p-hit(c.sources[i],9))<1e-12));
  assert.match(c.scope,/sin mulligans/);
});
test('invalid settings and all-zero weights are rejected',()=>{
  for(const w of [[0,0,0,0],[1,NaN,1,1],[-1,1,1,1],[1,1,1]]) assert.throws(()=>choose(w));
  assert.throws(()=>choose([1,1,1,1],7));
  assert.throws(()=>choose([1,1,1,1],13));
});
