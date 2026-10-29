"""Package the existing, verified analysis as a buildless GitHub Pages site."""

from pathlib import Path
import hashlib
import json
import shutil
import unittest


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'


def main():
    structural = json.loads((ROOT/'results/structural_stages/results.json').read_text())
    pilot = json.loads((ROOT/'results/pilot_01/results.json').read_text())
    search = json.loads((ROOT/'results/search_space/manifest.json').read_text())
    color_study = json.loads((ROOT/'results/color_bridges/results.json').read_text())
    cells = [{k: v for k, v in c.items() if k != 'monte_carlo'} for c in structural['cells']]
    inputs = ['PLAN_ANALISIS.md', 'ANALISIS_VIDEO_HYPERGEOMANCER.md',
              'results/structural_stages/informe.md', 'results/pilot_01/informe_piloto.md',
              'results/search_space/universo_busqueda.md', 'README.md', 'results/color_bridges/informe.md']
    documents = [{'id': f'doc-{i}', 'path': p, 'title': title, 'text': (ROOT/p).read_text()}
                 for i, (p, title) in enumerate(zip(inputs, [
                     'Plan completo', 'Lectura del video y transcripción',
                     'Informe · partes 1 y 2', 'Piloto · aperturas y mulligans',
                     'Universo de composiciones', 'Guía reproducible', 'Colores tempranos y bridges']))]
    data = {
        'version': '1.1', 'date': '2026-10-29',
        'repository': 'https://github.com/isardi4/analysis-4c_affy',
        'structural': {'config': structural['config'], 'cells': cells,
                       'opening_distribution': structural['opening_distribution'],
                       'checks_passed': structural['checks_passed'],
                       'checks_total': structural['checks_total'],
                       'control_trajectories': len(cells)*structural['config']['trials_per_cell'],
                       'elapsed_seconds': structural['elapsed_seconds']},
        'pilot': {'trials': pilot['total_trials'], 'n_per_cell': pilot['n_per_cell'],
                  'cells': [{k: v for k, v in c.items() if k != 'traces'} for c in pilot['cells']],
                  'variants': pilot['variants']},
        'search': {'scope_totals': search['scope_totals'], 'counts': search['counts'],
                   'per_bridge_counts': search['per_bridge_counts']},
        'documents': documents,
        'color_study': {**color_study, 'cells': [{k:v for k,v in c.items() if k != 'traces'} for c in color_study['cells']]},
        'verification': {'test_count': unittest.TestLoader().discover(str(ROOT/'tests')).countTestCases(),
                         'command': 'python3 -m unittest discover -s tests -v',
                         'reference_status': 'Lista candidata del mismo jugador y torneo; exportación original de Goldfish pendiente de contraste.'},
    }
    OUT.mkdir(exist_ok=True)
    # Escaping angle brackets also makes the data safe if embedded in a script later.
    encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e')
    (OUT/'report-data.js').write_text('window.AFFINITY_DATA = '+encoded+';\n')
    downloads = OUT/'downloads'
    downloads.mkdir(exist_ok=True)
    copies = {
        'structural-results.json': 'results/structural_stages/results.json',
        'structural-metrics.csv': 'results/structural_stages/metrics.csv',
        'opening-pilot.json': 'results/pilot_01/results.json',
        'opening-metrics.csv': 'results/pilot_01/metrics.csv',
        'search-manifest.json': 'results/search_space/manifest.json',
        'search-profiles.csv': 'results/search_space/exact_opening_profiles.csv',
        'plan.md': 'PLAN_ANALISIS.md',
        'video-analysis.md': 'ANALISIS_VIDEO_HYPERGEOMANCER.md',
        'structural-report.md': 'results/structural_stages/informe.md',
        'message.txt': 'message.txt',
        'color-results.json': 'results/color_bridges/results.json',
        'color-metrics.csv': 'results/color_bridges/metrics.csv',
        'color-report.md': 'results/color_bridges/informe.md',
    }
    manifest = {'data_version': data['version'], 'files': {}}
    for target, source in copies.items():
        shutil.copyfile(ROOT/source, downloads/target)
        manifest['files'][target] = {'source': source,
                                    'sha256': hashlib.sha256((ROOT/source).read_bytes()).hexdigest()}
    (downloads/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    (OUT/'.nojekyll').touch()
    print(f'Informe empaquetado: {OUT}; {len(cells)} celdas, {len(documents)} documentos y {len(copies)} descargas.')


if __name__ == '__main__':
    main()
