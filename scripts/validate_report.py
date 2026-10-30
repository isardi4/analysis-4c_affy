"""Check publication assets and numerical provenance without a browser."""

from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT/'docs'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.local_files, self.panels, self.tabs = [], [], set(), set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.append(a['id'])
        if a.get('role') == 'tab':
            self.tabs.add(a['aria-controls'])
        if a.get('role') == 'tabpanel':
            self.panels.add(a['id'])
        for key in ('src', 'href'):
            value = a.get(key, '')
            if value and not re.match(r'^(https?:|#|mailto:)', value):
                self.local_files.append(value.split('#')[0].split('?')[0])


def main():
    page = Page()
    page.feed((SITE/'index.html').read_text())
    assert len(page.ids) == len(set(page.ids)), 'Duplicate HTML ids'
    assert page.tabs == page.panels and len(page.tabs) == 8, 'Broken tab navigation'
    for path in page.local_files:
        assert (SITE/path).is_file(), f'Missing local asset: {path}'
    prefix = 'window.AFFINITY_DATA = '
    raw = (SITE/'report-data.js').read_text()
    assert raw.startswith(prefix)
    data = json.loads(raw[len(prefix):].rstrip().removesuffix(';'))
    structural = json.loads((ROOT/'results/structural_stages/results.json').read_text())
    assert data['structural']['opening_distribution'] == structural['opening_distribution']
    counts = structural['config']['part_2']['bridge_counts']
    assert counts == [6,7,8,9,10,11,12]
    expected_structural = len(structural['config']['land_totals'])*len(structural['config']['modes'])*(1+len(counts)*len(structural['config']['part_2']['policies']))
    assert data['structural']['control_trajectories'] == expected_structural*structural['config']['trials_per_cell']
    assert data['structural']['checks_passed'] == data['structural']['checks_total'] == structural['checks_total'] > 0
    assert len(data['structural']['cells']) == expected_structural
    for source, packaged in zip(structural['cells'], data['structural']['cells']):
        assert source['exact'] == packaged['exact'], 'Dashboard changed analytical results'
    color = json.loads((ROOT/'results/color_bridges/results.json').read_text())
    assert color['config']['bridges'] == counts
    expected_color = len(counts)*len(color['profiles'])*2
    assert len(color['cells']) == expected_color
    assert {(c['bridges'],c['profile'],c['mode']) for c in color['cells']} == {(b,p,m) for b in counts for p in color['profiles'] for m in ('OTP','OTD')}
    assert color['total_trials'] == expected_color*color['n_per_cell']
    assert data['search']['scope_totals'] == json.loads((ROOT/'results/search_space/manifest.json').read_text())['scope_totals']
    assert data['color_study']['candidates'] == color['candidates']
    assert data['color_study']['decision'] == color['decision']
    for source, packaged in zip(color['cells'], data['color_study']['cells']):
        assert source['metrics'] == packaged['metrics']
    for path, digest in color['source_hashes'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, f'Engine input changed: {path}'
    stress = json.loads((ROOT/'results/boulder_hate/results.json').read_text())
    assert stress['bridges'] == counts and stress['config']['boulders'] == [3,4]
    expected_stress=len(counts)*2*2*2*len(stress['config']['scenarios'])
    assert len(stress['cells']) == expected_stress
    assert stress['total_trials'] == expected_stress*stress['config']['trials_per_cell']
    assert data['boulder_hate']['paired_comparisons'] == stress['paired_comparisons']
    for source,packaged in zip(stress['cells'],data['boulder_hate']['cells']):
        assert source['metrics'] == packaged['metrics'] and source['means'] == packaged['means']
    for path,digest in stress['source_hashes'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, f'Hate model changed: {path}'
    manifest = json.loads((SITE/'downloads/manifest.json').read_text())
    for name, item in manifest['files'].items():
        expected = hashlib.sha256((ROOT/item['source']).read_bytes()).hexdigest()
        actual = hashlib.sha256((SITE/'downloads'/name).read_bytes()).hexdigest()
        assert expected == actual == item['sha256'], f'Download differs: {name}'
    assert all(d['text'] == (ROOT/d['path']).read_text() for d in data['documents'])
    print(f'Publicación validada: ocho pestañas, {expected_structural} celdas estructurales, {expected_color} de colores, {expected_stress} de Boulder/hate y {len(manifest["files"])} descargas verificadas.')


if __name__ == '__main__':
    main()
