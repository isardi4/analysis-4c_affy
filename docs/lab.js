/* Buildless report: every chart reads existing analytical results. */
(() => {
  'use strict';
  const D = window.AFFINITY_DATA;
  if (!D) { document.body.dataset.error = 'missing-data'; return; }
  const $ = (id) => document.getElementById(id);
  const colors = { nineteen: '#267c72', twenty: '#cb714f', blue: '#6685b1' };
  const fmt = (x, digits = 2) => Number(x).toLocaleString('es-AR', { minimumFractionDigits: digits, maximumFractionDigits: digits });
  const pct = (x, digits = 2) => `${fmt(100 * x, digits)} %`;
  const integer = (x) => Number(x).toLocaleString('es-AR');
  const points = (x) => `${x > 0 ? '+' : x < 0 ? '−' : ''}${fmt(Math.abs(x), 2)} pp`;
  const params = new URLSearchParams(location.search);
  const state = {
    mode: params.get('mode') === 'OTD' ? 'OTD' : 'OTP',
    lands: params.get('lands') === '20' ? 20 : 19,
    policy: params.get('policy') === 'bridge_t1_then_untapped' ? 'bridge_t1_then_untapped' : 'untapped_first',
    tab: ['overview', 'parts', 'method', 'documents'].includes(location.hash.slice(1)) ? location.hash.slice(1) : 'parts',
  };
  let chartId = 0;
  const cell = (part, lands, mode, bridges = 0, policy = 'untapped_first') => {
    const result = D.structural.cells.find(c => c.part === part && c.lands === lands && c.mode === mode && c.bridges === bridges && c.policy === policy);
    if (!result) throw new Error(`Missing analytical cell: ${[part, lands, mode, bridges, policy].join('/')}`);
    return result;
  };
  const probability = (c, turn, key) => c.exact.turns[turn - 1].probabilities_unconditional[key] || 0;
  const svgNS = 'http://www.w3.org/2000/svg';
  function node(tag, className, text) {
    const n = document.createElement(tag);
    if (className) n.className = className;
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function svgNode(tag, attrs = {}, text) {
    const n = document.createElementNS(svgNS, tag);
    for (const [key, val] of Object.entries(attrs)) n.setAttribute(key, String(val));
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function chart(host, { title, labels, series, type = 'line', max = 100 }) {
    host.replaceChildren();
    const width = 720, height = 286, padding = { l: 48, r: 19, t: 15, b: 40 };
    const plotW = width - padding.l - padding.r, plotH = height - padding.t - padding.b;
    const uid = `chart-title-${++chartId}`;
    const root = svgNode('svg', { viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-labelledby': uid });
    root.append(svgNode('title', { id: uid }, title));
    root.append(svgNode('desc', {}, 'Gráfico de probabilidades. Los valores completos están disponibles en las tablas y en el CSV descargable.'));
    const y = value => padding.t + plotH * (1 - value / max);
    for (let i = 0; i <= 4; i++) {
      const value = max * i / 4;
      root.append(svgNode('line', { x1: padding.l, x2: width - padding.r, y1: y(value), y2: y(value), class: i ? 'grid-line' : 'baseline' }));
      root.append(svgNode('text', { x: padding.l - 11, y: y(value) + 4, 'text-anchor': 'end', class: 'axis-label' }, `${fmt(value, 0)} %`));
    }
    const step = plotW / (type === 'bar' ? labels.length : Math.max(1, labels.length - 1));
    const x = i => padding.l + (type === 'bar' ? i + .5 : i) * step;
    labels.forEach((label, i) => root.append(svgNode('text', { x: x(i), y: height - 13, 'text-anchor': 'middle', class: 'axis-label' }, label)));
    series.forEach((s, si) => {
      if (type === 'line') {
        root.append(svgNode('polyline', { points: s.values.map((v, i) => `${x(i)},${y(v)}`).join(' '), fill: 'none', stroke: s.color, 'stroke-width': 2.7, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
        s.values.forEach((v, i) => {
          const description = `${labels[i]} · ${s.name}: ${fmt(v, 2)} %`;
          const point = svgNode('circle', { cx: x(i), cy: y(v), r: 4.4, fill: '#fffefb', stroke: s.color, 'stroke-width': 2.5, tabindex: 0, class: 'chart-point', 'aria-label': description });
          point.append(svgNode('title', {}, description)); root.append(point);
        });
      } else {
        const groupW = step * .69, barW = groupW / series.length;
        s.values.forEach((v, i) => {
          const description = `${labels[i]} · ${s.name}: ${fmt(v, 2)} %`;
          const bar = svgNode('rect', { x: x(i) - groupW / 2 + si * barW, y: y(v), width: Math.max(1, barW - 3), height: Math.max(0, plotH * v / max), rx: 2, fill: s.color, tabindex: 0, 'aria-label': description });
          bar.append(svgNode('title', {}, description)); root.append(bar);
        });
      }
    });
    host.append(root);
    const legend = node('div', 'chart-legend');
    series.forEach(s => { const item = node('span'); const swatch = node('i', 'legend-swatch'); swatch.style.background = s.color; item.append(swatch, document.createTextNode(s.name)); legend.append(item); });
    host.append(legend);
    host.dataset.values = JSON.stringify(series.map(s => s.values));
  }
  function makeTable(host, headers, rows, options = {}) {
    host.replaceChildren();
    const table = node('table');
    if (options.caption) { const cap = node('caption', 'sr-only', options.caption); table.append(cap); }
    const head = node('thead'), hr = node('tr');
    headers.forEach(h => { const th = node('th', '', h); th.scope = 'col'; hr.append(th); }); head.append(hr);
    const body = node('tbody');
    rows.forEach(row => {
      const tr = node('tr', row.active ? 'active-row' : '');
      row.values.forEach((value, i) => {
        const td = node('td');
        if (i === 0 && row.color) { const label = node('span', 'table-series', value); label.style.setProperty('--series-color', row.color); td.append(label); }
        else td.textContent = value;
        tr.append(td);
      });
      body.append(tr);
    });
    table.append(head, body); host.append(table);
  }
  function metrics(host, items) {
    host.replaceChildren();
    items.forEach(item => {
      const card = node('div', 'metric-item');
      const value = node('strong', `metric-number ${item.color || ''}`, item.value);
      if (item.suffix) value.append(node('span', '', item.suffix));
      card.append(node('span', 'label', item.label), value, node('span', 'metric-caption', item.caption)); host.append(card);
    });
  }
  function updateURL() {
    const p = new URLSearchParams();
    p.set('mode', state.mode); p.set('lands', state.lands); p.set('policy', state.policy);
    history.replaceState(null, '', `${location.pathname}?${p}#${state.tab}`);
  }
  function activateTab(name, focus = false) {
    state.tab = name;
    document.querySelectorAll('[data-tab]').forEach(button => {
      const active = button.dataset.tab === name;
      button.setAttribute('aria-selected', String(active)); button.tabIndex = active ? 0 : -1;
      $(`panel-${button.dataset.tab}`).hidden = !active;
      if (active && focus) button.focus();
    });
    updateURL();
  }
  function renderPartOne() {
    const a = cell(1, 19, state.mode), b = cell(1, 20, state.mode);
    const screwA = a.exact.turns[3].screw_le2_conditional_on_kept;
    const screwB = b.exact.turns[3].screw_le2_conditional_on_kept;
    metrics($('land-kpis'), [
      { label: 'Tercera tierra · 19', value: pct(probability(a, 3, 'lands_on_curve')), caption: `${state.mode} · todos los intentos`, color: 'green' },
      { label: 'Tercera tierra · 20', value: pct(probability(b, 3, 'lands_on_curve')), caption: `${state.mode} · todos los intentos`, color: 'orange' },
      { label: 'Menos screw con 20', value: fmt(100 * (screwA - screwB)), suffix: 'pp', caption: 'T4 · entre manos conservadas' },
      { label: 'Robos naturales a T3', value: state.mode === 'OTP' ? '2' : '3', suffix: 'cartas', caption: 'Sin contar las siete iniciales' },
    ]);
    chart($('curve-chart'), { title: `Land drops a tiempo, ${state.mode}`, labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6'], series: [
      { name: '19 tierras', color: colors.nineteen, values: a.exact.turns.map(t => 100 * (t.probabilities_unconditional.lands_on_curve || 0)) },
      { name: '20 tierras', color: colors.twenty, values: b.exact.turns.map(t => 100 * (t.probabilities_unconditional.lands_on_curve || 0)) },
    ] });
    const deltas = [3, 4, 5].map(t => ({ label: `Land drop a T${t}`, value: points(100 * (probability(b, t, 'lands_on_curve') - probability(a, t, 'lands_on_curve'))) }));
    deltas.push({ label: 'Screw al T4', value: points(100 * (screwB - screwA)) });
    deltas.push({ label: 'Fallo de mulligan', value: points(100 * (b.exact.opening.failed - a.exact.opening.failed)) });
    const dl = $('delta-list'); dl.replaceChildren();
    deltas.forEach(d => { const row = node('div', 'delta-row'); row.append(node('span', '', d.label), node('strong', '', d.value)); dl.append(row); });
    const rows = [];
    for (const mode of ['OTP', 'OTD']) for (const lands of [19, 20]) {
      const c = cell(1, lands, mode), ts = c.exact.turns;
      rows.push({ active: mode === state.mode, color: lands === 19 ? colors.nineteen : colors.twenty,
        values: [`${lands} tierras`, mode, ...[3, 4, 5].map(t => pct(probability(c, t, 'lands_on_curve'))), pct(ts[3].screw_le2_conditional_on_kept), pct(c.exact.opening.failed), fmt(c.exact.opening.mean_cards_unconditional, 3)] });
    }
    makeTable($('part-one-table'), ['Base', 'Modo', 'Curve T3', 'Curve T4', 'Curve T5', 'Screw T4 · keeps', 'Fallo mulligan', 'Cartas medias*'], rows);
  }
  function renderFixedCharts() {
    chart($('opening-chart'), { title: 'Distribución de tierras en las siete originales', type: 'bar', max: 40,
      labels: ['0', '1', '2', '3', '4', '5', '6', '7'], series: [
        { name: '19 tierras', color: colors.nineteen, values: D.structural.opening_distribution['19'].map(p => 100 * p) },
        { name: '20 tierras', color: colors.twenty, values: D.structural.opening_distribution['20'].map(p => 100 * p) },
      ] });
    chart($('screw-chart'), { title: 'Screw al T4 entre manos conservadas', type: 'bar', max: 20, labels: ['OTP', 'OTD'], series: [
      { name: '19 tierras', color: colors.nineteen, values: ['OTP', 'OTD'].map(m => 100 * cell(1, 19, m).exact.turns[3].screw_le2_conditional_on_kept) },
      { name: '20 tierras', color: colors.twenty, values: ['OTP', 'OTD'].map(m => 100 * cell(1, 20, m).exact.turns[3].screw_le2_conditional_on_kept) },
    ] });
  }
  function renderPartTwo() {
    const counts = [9, 10, 11, 12, 13, 14];
    const cs = counts.map(b => cell(2, state.lands, state.mode, b, state.policy));
    const definitions = [
      { turn: 1, key: 'capacity_ge1', name: 'T1 · ≥1 maná', color: colors.nineteen },
      { turn: 2, key: 'capacity_ge2', name: 'T2 · ≥2 manás', color: colors.twenty },
      { turn: 3, key: 'capacity_ge3', name: 'T3 · ≥3 manás', color: colors.blue },
    ];
    chart($('ratio-chart'), { title: `Capacidad de maná según bridges, ${state.lands} tierras, ${state.mode}`, labels: counts.map(String), series: definitions.map(d => ({ name: d.name, color: d.color, values: cs.map(c => 100 * probability(c, d.turn, d.key)) })) });
    const difference = 100 * (probability(cs[5], 2, 'capacity_ge2') - probability(cs[0], 2, 'capacity_ge2'));
    const delta = $('ratio-delta'); delta.replaceChildren(node('strong', 'ratio-delta-number', points(difference)), node('span', 'ratio-delta-label', `en la probabilidad de tener ≥2 manás en T2 · ${state.mode} · ${state.lands} tierras`));
    $('policy-explainer').textContent = state.policy === 'untapped_first'
      ? 'Si hay una tierra enderezada en mano, se juega antes que un bridge.'
      : 'Se abre con bridge si hay uno; desde T2 se priorizan enderezadas.';
    $('ratio-table-badge').textContent = `${state.lands} tierras · ${state.mode}`;
    makeTable($('part-two-table'), ['Bridges', 'Enderezadas', '≥1 maná T1', '≥2 manás T2', '≥3 manás T3', 'Capacidad acumulada T1–T3'], cs.map(c => ({ values: [String(c.bridges), String(c.lands - c.bridges), ...definitions.map(d => pct(probability(c, d.turn, d.key))), fmt(c.exact.turns.slice(0, 3).reduce((s, t) => s + t.mean_capacity_unconditional, 0), 3)] })));
    const heatmap = node('table', 'heatmap'), head = node('thead'), hr = node('tr');
    ['Bridges', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6'].forEach(name => { const th = node('th', '', name); th.scope = 'col'; hr.append(th); }); head.append(hr);
    const body = node('tbody');
    cs.forEach(c => {
      const row = node('tr'); const label = node('td', '', String(c.bridges)); label.append(node('small', '', `${c.lands - c.bridges} ender.`)); row.append(label);
      c.exact.turns.forEach(t => {
        const value = t.mean_capacity_unconditional, p = Math.min(1, value / 6);
        const td = node('td', '', fmt(value, 2));
        const from = [238, 243, 232], to = [34, 107, 94];
        const rgb = from.map((a, i) => Math.round(a + (to[i] - a) * p));
        td.style.background = `rgb(${rgb.join(',')})`;
        const linear = rgb.map(v => { const x = v / 255; return x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4; });
        const luminance = .2126 * linear[0] + .7152 * linear[1] + .0722 * linear[2];
        td.style.color = luminance <= .18 ? '#ffffff' : '#000000'; td.title = `${c.bridges} bridges, T${t.turn}: ${fmt(value)} manás de capacidad media`;
        row.append(td);
      }); body.append(row);
    });
    heatmap.append(head, body); $('capacity-heatmap').replaceChildren(heatmap);
  }
  function syncControls() {
    document.querySelectorAll('[data-mode]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.mode === state.mode)));
    document.querySelectorAll('[data-lands]').forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.lands) === state.lands)));
    $('policy-select').value = state.policy;
    $('mode-explainer').textContent = state.mode === 'OTP'
      ? 'OTP decide el mulligan sobre siete cartas y no roba en T1.'
      : 'OTD decide el mulligan sobre siete cartas y roba una al comenzar T1.';
    renderPartOne(); renderPartTwo(); updateURL();
  }
  function renderMethod() {
    metrics($('method-kpis'), [
      { label: 'Celdas estructurales', value: integer(D.structural.cells.length), caption: 'Dos modos y controles de secuenciación' },
      { label: 'Trayectorias de control', value: integer(D.structural.control_trajectories), caption: '2.000 por celda · azar compartido' },
      { label: 'Controles exactos', value: `${integer(D.structural.checks_passed)}/${integer(D.structural.checks_total)}`, caption: 'Tolerancia amplia de depuración', color: 'green' },
      { label: 'Pruebas automatizadas', value: String(D.verification.test_count), caption: 'Reglas, probabilidad y conservación' },
    ]);
    $('reference-status').textContent = D.verification.reference_status;
    const ps = D.pilot.cells.filter(c => c.variant === 'original19_b4' && c.floor === 4);
    makeTable($('pilot-table'), ['Política', 'N', 'Boulder conservado', 'Boulder + enderezada', 'Cartas medias*', 'Fallo'], ps.map(c => ({ values: [c.policy === 'min_two' ? 'Mínimo dos tierras' : 'Buscar Boulder una vez', integer(c.n), pct(c.events.kept_boulder.rate), pct(c.events.kept_boulder_untapped.rate), fmt(c.mean_cards_unconditional, 3), pct(c.events.failed.rate)] })));
    $('universe-count').textContent = integer(D.search.scope_totals.wubr_core);
  }
  function safeSourceURL(href, documentPath) {
    if (/^https?:\/\//i.test(href)) return href;
    if (/^(javascript|data|vbscript):/i.test(href)) return null;
    if (href.startsWith('#')) return `${D.repository}/blob/main/${documentPath}${href}`;
    const root = '/Users/isardi4/Documents/GitHub/analysis-4c_affy/';
    let source = href.startsWith(root) ? href.slice(root.length) : href;
    const base = documentPath.split('/').slice(0, -1);
    if (!href.startsWith(root)) source = [...base, source].join('/');
    const resolved = [];
    for (const bit of source.split('/')) { if (bit === '..') resolved.pop(); else if (bit !== '.' && bit) resolved.push(bit); }
    return `${D.repository}/blob/main/${resolved.join('/')}`;
  }
  function inline(parent, text, documentPath) {
    const pattern = /(`[^`]+`|\*\*[^*]+\*\*|\[([^\]]+)\]\(([^)]+)\))/g;
    let offset = 0, m;
    while ((m = pattern.exec(text))) {
      parent.append(document.createTextNode(text.slice(offset, m.index)));
      if (m[0].startsWith('`')) parent.append(node('code', '', m[0].slice(1, -1)));
      else if (m[0].startsWith('**')) parent.append(node('strong', '', m[0].slice(2, -2)));
      else {
        const url = safeSourceURL(m[3], documentPath);
        if (url) { const link = node('a', '', m[2]); link.href = url; link.target = '_blank'; link.rel = 'noopener'; parent.append(link); }
        else parent.append(document.createTextNode(m[2]));
      }
      offset = pattern.lastIndex;
    }
    parent.append(document.createTextNode(text.slice(offset)));
  }
  function markdown(text, path) {
    const fragment = document.createDocumentFragment(), lines = text.replace(/\r/g, '').split('\n');
    let i = 0;
    const special = line => !line.trim() || /^(#{1,6})\s|^```|^\s*\||^\s*[-*]\s|^\s*\d+\.\s/.test(line);
    while (i < lines.length) {
      const line = lines[i];
      if (!line.trim()) { i++; continue; }
      if (line.startsWith('```')) {
        const code = []; i++; while (i < lines.length && !lines[i].startsWith('```')) code.push(lines[i++]); i++;
        const pre = node('pre'); pre.append(node('code', '', code.join('\n'))); fragment.append(pre); continue;
      }
      const heading = line.match(/^(#{1,6})\s+(.+)/);
      if (heading) { const h = node(`h${Math.min(heading[1].length, 3)}`); inline(h, heading[2], path); fragment.append(h); i++; continue; }
      if (/^\s*\|/.test(line)) {
        const table = node('table'), thead = node('thead'), tbody = node('tbody'); let first = true;
        while (i < lines.length && /^\s*\|/.test(lines[i])) {
          const values = lines[i++].trim().replace(/^\||\|$/g, '').split('|').map(v => v.trim());
          if (values.every(v => /^:?-+:?$/.test(v))) continue;
          const row = node('tr');
          values.forEach(v => { const td = node(first ? 'th' : 'td'); if (first) td.scope = 'col'; inline(td, v, path); row.append(td); });
          (first ? thead : tbody).append(row); first = false;
        }
        table.append(thead, tbody); const wrap = node('div', 'table-scroll'); wrap.append(table); fragment.append(wrap); continue;
      }
      if (/^\s*([-*]|\d+\.)\s/.test(line)) {
        const ordered = /^\s*\d+\./.test(line), list = node(ordered ? 'ol' : 'ul');
        const pattern = ordered ? /^\s*\d+\.\s/ : /^\s*[-*]\s/;
        while (i < lines.length && pattern.test(lines[i])) { const li = node('li'); inline(li, lines[i++].replace(pattern, ''), path); list.append(li); }
        fragment.append(list); continue;
      }
      const paragraph = [lines[i++]];
      while (i < lines.length && !special(lines[i])) paragraph.push(lines[i++]);
      const p = node('p'); inline(p, paragraph.join(' '), path); fragment.append(p);
    }
    return fragment;
  }
  function renderDocument() {
    const doc = D.documents.find(d => d.id === $('document-select').value) || D.documents[0];
    $('document-reader').replaceChildren(markdown(doc.text, doc.path));
    $('document-reader').dataset.document = doc.id;
    $('document-source').href = `${D.repository}/blob/main/${doc.path}`;
  }
  D.documents.forEach(doc => { const option = node('option', '', doc.title); option.value = doc.id; $('document-select').append(option); });
  $('document-select').addEventListener('change', renderDocument);
  document.querySelectorAll('[data-tab]').forEach(button => {
    button.addEventListener('click', () => activateTab(button.dataset.tab));
    button.addEventListener('keydown', event => {
      const tabs = [...document.querySelectorAll('[data-tab]')], i = tabs.indexOf(button);
      let next;
      if (event.key === 'ArrowRight') next = (i + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (i - 1 + tabs.length) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next !== undefined) { event.preventDefault(); activateTab(tabs[next].dataset.tab, true); }
    });
  });
  document.querySelectorAll('[data-open-tab]').forEach(button => button.addEventListener('click', () => {
    activateTab(button.dataset.openTab);
    if (button.dataset.scroll) $(button.dataset.scroll).scrollIntoView({ behavior: 'smooth' });
  }));
  document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => { state.mode = button.dataset.mode; syncControls(); }));
  document.querySelectorAll('[data-lands]').forEach(button => button.addEventListener('click', () => { state.lands = Number(button.dataset.lands); syncControls(); }));
  $('policy-select').addEventListener('change', () => { state.policy = $('policy-select').value; syncControls(); });
  document.querySelectorAll('a[href="#overview"]').forEach(link => link.addEventListener('click', event => { event.preventDefault(); activateTab('overview'); window.scrollTo({ top: 0, behavior: 'smooth' }); }));
  addEventListener('hashchange', () => { const tab = location.hash.slice(1); if (['overview', 'parts', 'method', 'documents'].includes(tab)) activateTab(tab); });
  renderFixedCharts(); renderMethod(); renderDocument(); syncControls(); activateTab(state.tab);
  document.body.dataset.ready = 'true';
})();
