// Optional local QA. Uses installed Chrome and Node's native CDP WebSocket.
// No browser packages or project dependencies are installed.
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { setTimeout as delay } from 'node:timers/promises';
import assert from 'node:assert/strict';

const base = process.env.AFFINITY_PREVIEW_URL || 'http://127.0.0.1:8765/';
const chromePath = process.env.AFFINITY_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const artifacts = '/private/tmp/affinity-report-qa';
await mkdir(artifacts, { recursive: true });
let chromeLog = '';
const chrome = spawn(chromePath, ['--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--remote-debugging-port=9227', `--user-data-dir=${artifacts}/chrome-profile`, 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
chrome.stderr.on('data', chunk => { chromeLog += chunk.toString(); });
let ws;
try {
  let pages;
  const deadline = Date.now() + 45000;
  while (Date.now() < deadline) {
    try { const response = await fetch('http://127.0.0.1:9227/json/list', { signal: AbortSignal.timeout(1000) }); pages = await response.json(); if (pages.some(p => p.type === 'page')) break; } catch {}
    await delay(200);
  }
  assert(pages?.some(p => p.type === 'page'), `Chrome did not expose a page (exit ${chrome.exitCode}): ${chromeLog.slice(0, 2000)}`);
  const page = pages.find(p => p.type === 'page');
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { ws.addEventListener('open', resolve, { once: true }); ws.addEventListener('error', reject, { once: true }); });
  let id = 0;
  const pending = new Map(), errors = [];
  ws.addEventListener('message', event => {
    const message = JSON.parse(event.data);
    if (message.id) { const pair = pending.get(message.id); if (pair) { pending.delete(message.id); message.error ? pair.reject(Error(JSON.stringify(message.error))) : pair.resolve(message.result); } }
    if (message.method === 'Runtime.exceptionThrown') errors.push(message.params.exceptionDetails);
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => { const request = ++id; pending.set(request, { resolve, reject }); ws.send(JSON.stringify({ id: request, method, params })); });
  const evaluate = async expression => {
    const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (result.exceptionDetails) throw Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1100, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: base });
  let ready = false;
  for (let i = 0; i < 100; i++) { ready = await evaluate('document.body?.dataset.ready === "true"'); if (ready) break; await delay(100); }
  assert(ready, 'Report did not initialize');
  assert.equal(await evaluate('document.querySelector("[role=tab][aria-selected=true]").dataset.tab'), 'profiles');
  assert.equal(await evaluate('document.querySelectorAll("#color-results-table tbody tr").length'), 6);
  assert.equal(await evaluate('document.querySelectorAll("#color-profile-table tbody tr").length'), 5);
  assert((await evaluate('document.getElementById("color-sample-note").textContent')).includes('600.000'));
  assert.equal(await evaluate('document.querySelectorAll("#color-function-chart .chart-value-label").length'), 18);
  assert.equal(await evaluate('document.querySelectorAll("#color-early-chart .chart-value-label").length'), 24);
  assert((await evaluate('document.getElementById("weight-status").textContent')).includes('120.480'));
  const sourceBaseline=await evaluate('JSON.parse(document.getElementById("weight-result").dataset.sources)');
  for (const [i,color] of ['W','U','B','R'].entries()) {
    await evaluate(`document.getElementById('weight-reset').click(); document.getElementById('weight-${color}').value='0.5'; document.getElementById('weight-${color}').dispatchEvent(new Event('input'))`);
    const sources=await evaluate('JSON.parse(document.getElementById("weight-result").dataset.sources)');
    assert(sources[i]<sourceBaseline[i],`${color} must be independently reducible`);
  }
  await evaluate('document.getElementById("weight-W").value="0.5"; document.getElementById("weight-W").dispatchEvent(new Event("input"))');
  assert((await evaluate('location.search')).includes('weights=0.5%2C1%2C1%2C0.5'));
  await evaluate('document.querySelectorAll("[data-weight]").forEach(x=>{x.value="0";x.dispatchEvent(new Event("input"))})');
  assert.equal(await evaluate('document.getElementById("weight-status").dataset.state'),'invalid');
  assert.equal(await evaluate('document.getElementById("weight-result").hidden'),true);
  assert.equal(await evaluate('document.getElementById("weight-download").disabled'),true);
  await evaluate('document.getElementById("weight-reset").click()');
  assert.equal(await evaluate('document.getElementById("weight-status").dataset.state'),'ready');
  const balanced = await evaluate('document.getElementById("color-function-chart").dataset.values');
  for (const profile of ['blue','white','black','red']) {
    await evaluate(`document.getElementById('profile-select').value='${profile}'; document.getElementById('profile-select').dispatchEvent(new Event('change'))`);
    assert.notEqual(await evaluate('document.getElementById("color-function-chart").dataset.values'), balanced);
  }
  await evaluate('document.getElementById("profile-select").value="balanced"; document.getElementById("profile-select").dispatchEvent(new Event("change")); document.querySelector("[data-tab=parts]").click()');
  assert.equal(await evaluate('document.querySelectorAll("#part-one-table tbody tr").length'), 4);
  assert.equal(await evaluate('document.querySelectorAll("#part-two-table tbody tr").length'), 6);
  assert((await evaluate('document.getElementById("land-kpis").innerText')).includes('78,05'));
  assert.equal(await evaluate('document.querySelectorAll("#opening-chart .chart-value-label").length'), 16);
  assert.equal(await evaluate('document.querySelectorAll("#curve-chart .chart-value-label").length'), 12);
  assert.equal(await evaluate('document.querySelectorAll("#ratio-chart .chart-value-label").length'), 18);
  assert(await evaluate('Array.from(document.querySelectorAll(".chart-value-label")).every(x=>/^\\d+,\\d{2} %$/.test(x.textContent))'));
  assert.equal(await evaluate('document.querySelector("#curve-chart .chart-value-label[data-index=\\"2\\"][data-series=\\"0\\"]").textContent'), '78,05 %');
  assert((await evaluate('document.querySelector(".table-definition").textContent')).includes('1 + 2 + 3'));
  assert((await evaluate('document.querySelector("#part-two-table thead").textContent')).includes('Capacidad media · T3'));
  await evaluate('document.querySelector("[data-mode=OTD]").click()');
  assert((await evaluate('document.getElementById("land-kpis").innerText')).includes('85,15'));
  assert.equal(await evaluate('document.querySelector("#curve-chart .chart-value-label[data-index=\\"2\\"][data-series=\\"0\\"]").textContent'), '85,15 %');
  assert.equal(await evaluate('document.querySelector("[data-mode=OTD]").getAttribute("aria-pressed")'), 'true');
  await evaluate('document.querySelector("[data-lands=\\"20\\"]").click()');
  assert.equal(await evaluate('document.querySelector("#part-two-table tbody tr td:nth-child(2)").textContent'), '11');
  const before = await evaluate('document.getElementById("ratio-chart").dataset.values');
  await evaluate('document.getElementById("policy-select").value="bridge_t1_then_untapped"; document.getElementById("policy-select").dispatchEvent(new Event("change"))');
  const after = await evaluate('document.getElementById("ratio-chart").dataset.values');
  assert.notEqual(before, after, 'Policy must change actual chart values');
  for (const tab of ['overview', 'profiles', 'method', 'documents', 'parts']) {
    await evaluate(`document.querySelector('[data-tab="${tab}"]').click()`);
    assert.equal(await evaluate(`document.getElementById('panel-${tab}').hidden`), false);
    assert.equal(await evaluate('Array.from(document.querySelectorAll("[role=tabpanel]")).filter(x=>!x.hidden).length'), 1);
  }
  await evaluate('document.querySelector("[data-tab=documents]").click(); document.getElementById("document-select").value="doc-1"; document.getElementById("document-select").dispatchEvent(new Event("change"))');
  assert((await evaluate('document.getElementById("document-reader").innerText')).includes('Hypergeomancer'));
  const downloaded = await evaluate('fetch("downloads/structural-results.json").then(r=>r.json()).then(x=>x.cells.length)');
  assert.equal(downloaded, 52);
  assert.equal(await evaluate('fetch("downloads/color-results.json").then(r=>r.json()).then(x=>x.total_trials)'),600000);
  await evaluate('document.querySelector("[data-tab=profiles]").click(); window.scrollTo(0,0)');
  await delay(200);
  let colorShot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  await writeFile(`${artifacts}/colors-desktop.png`, Buffer.from(colorShot.data, 'base64'));
  await evaluate('document.querySelector("[data-tab=parts]").click(); document.querySelector("[data-mode=OTP]").click(); document.querySelector("[data-lands=\\"19\\"]").click(); document.getElementById("policy-select").value="untapped_first"; document.getElementById("policy-select").dispatchEvent(new Event("change")); window.scrollTo(0,0)');
  await delay(200);
  let shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  await writeFile(`${artifacts}/desktop.png`, Buffer.from(shot.data, 'base64'));
  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  await delay(250);
  const mobile = await evaluate('({width:innerWidth, body:document.body.scrollWidth, root:document.documentElement.scrollWidth})');
  assert(mobile.body <= mobile.width + 1 && mobile.root <= mobile.width + 1, `Mobile overflow: ${JSON.stringify(mobile)}`);
  for (const tab of ['overview', 'profiles', 'method', 'documents', 'parts']) {
    await evaluate(`document.querySelector('[data-tab="${tab}"]').click()`);
    const dimensions = await evaluate('({width:innerWidth, body:document.body.scrollWidth})');
    assert(dimensions.body <= dimensions.width + 1, `Overflow on ${tab}`);
  }
  await evaluate('document.querySelector("[data-tab=profiles]").click(); window.scrollTo(0,0)'); await delay(100);
  shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  await writeFile(`${artifacts}/mobile.png`, Buffer.from(shot.data, 'base64'));
  assert.equal(errors.length, 0, `Browser errors: ${JSON.stringify(errors)}`);
  console.log('Browser QA passed: tabs, OTP/OTD numbers, land ratios, policy graphs, documents, downloads and mobile layout.');
  console.log(`Screenshots: ${artifacts}/desktop.png and mobile.png`);
} finally {
  if (ws) ws.close();
  chrome.kill();
}
