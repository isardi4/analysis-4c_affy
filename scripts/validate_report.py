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
    assert page.tabs == page.panels and len(page.tabs) == 4, 'Broken tab navigation'
    for path in page.local_files:
        assert (SITE/path).is_file(), f'Missing local asset: {path}'
    prefix = 'window.AFFINITY_DATA = '
    raw = (SITE/'report-data.js').read_text()
    assert raw.startswith(prefix)
    data = json.loads(raw[len(prefix):].rstrip().removesuffix(';'))
    structural = json.loads((ROOT/'results/structural_stages/results.json').read_text())
    assert data['structural']['opening_distribution'] == structural['opening_distribution']
    assert data['structural']['control_trajectories'] == 104000
    assert data['structural']['checks_passed'] == data['structural']['checks_total'] == 2184
    assert len(data['structural']['cells']) == 52
    for source, packaged in zip(structural['cells'], data['structural']['cells']):
        assert source['exact'] == packaged['exact'], 'Dashboard changed analytical results'
    manifest = json.loads((SITE/'downloads/manifest.json').read_text())
    for name, item in manifest['files'].items():
        expected = hashlib.sha256((ROOT/item['source']).read_bytes()).hexdigest()
        actual = hashlib.sha256((SITE/'downloads'/name).read_bytes()).hexdigest()
        assert expected == actual == item['sha256'], f'Download differs: {name}'
    assert all(d['text'] == (ROOT/d['path']).read_text() for d in data['documents'])
    print('Publicación validada: cuatro pestañas, recursos locales, 52 celdas sin alterar y 10 descargas verificadas.')


if __name__ == '__main__':
    main()
