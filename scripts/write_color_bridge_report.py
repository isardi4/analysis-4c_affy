"""Describe the actual results; no hand-edited probabilities in the website."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/color_bridges'


def main():
    d = json.loads((OUT/'results.json').read_text())
    pilot = json.loads((ROOT/'results/color_bridges_pilot/results.json').read_text())
    counts = d['config']['bridges']
    low, high = min(counts), max(counts)
    bases = len(d['candidates'])
    integer = lambda n: f'{n:,}'.replace(',', '.')
    def cell(p, b, m):
        return next(c for c in d['cells'] if (c['profile'], c['bridges'], c['mode']) == (p, b, m))
    def rate(p, b, m, key):
        return cell(p, b, m)['metrics'][key]['p']
    def average(p, b, key):
        return sum(rate(p, b, m, key) for m in ('OTP', 'OTD'))/2
    def winner(p, key):
        return max(counts, key=lambda b: (average(p, b, key), -b))
    def pc(p):
        return f'{100*p:.2f}%'
    recommended = winner('balanced', 'needed_t2_t3')
    neighbor = recommended + 1 if recommended < high else recommended - 1
    decision = {
        'bridges': recommended, 'untapped': 19-recommended, 'control_bridges': neighbor,
        'objective': 'Desarrollo T2 y T3: al menos un hechizo de motor/criatura cada turno; perfil equilibrado; media OTP/OTD.',
        'scope': f'Recomendación de trabajo entre las {bases} bases probadas ({low}–{high} bridges); no óptimo global ni tasa de victoria.',
        'title': f'Punto de partida: {recommended} bridges + {19-recommended} enderezadas.',
        'text': f'Es el mejor valor puntual del desarrollo T2–T3 en el perfil equilibrado, con igual peso para OTP y OTD. Mantener {neighbor} bridges como control cercano permite revisar el ratio al optimizar las cartas concretas. El fixing de cuatro colores se informa aparte: no se fuerza a gastar cuatro colores si la mano no los necesita.',
        'next_step': f'Optimizar qué bridges y tierras enderezadas forman la base de {recommended}/{19-recommended}; conservar {neighbor} bridges como sensibilidad. Cruzar con el piloto condicional de Citadel y hate y ampliar la validación. La cantidad elegida puede revisarse si una composición mejor o una política de juego distinta cambia el resultado.',
    }
    d['decision'] = decision
    d['profile_winners'] = [{'profile': p, 'development': winner(p, 'needed_t2_t3'),
                             'all4': winner(p, 'all4_t3')} for p in d['profiles']]
    (OUT/'results.json').write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n')
    lines = ['# Colores tempranos y cantidad de bridges', '', 'Fecha: 2026-10-29.', '',
             f'## {decision["title"]}', '', decision['text'], '', decision['scope'], '',
             f'Piloto: {integer(pilot["total_trials"])} partidas ({integer(pilot["n_per_cell"])} × {bases} bases × OTP/OTD). Confirmación con semilla independiente: {integer(d["total_trials"])} partidas ({integer(d["n_per_cell"])} por celda). No se suman ambas muestras. Horizonte T1–T5.', '',
             '## Qué significa cada prioridad', '',
             f'Para cada ratio {low}–{high} se busca una base representativa entre las seis parejas WUBR de bridges y las cuatro tierras artefacto monocolores. Siempre 19 tierras, cuatro Boulder, las mismas 41 cartas no tierra y máximo cuatro copias por nombre. Sin básicas ni Citadel en este experimento sin rival.', '',
             'La función de selección es Σ w(c) × [1 − C(60−fuentes(c),9)/C(60,9)]. Equilibrado: pesos 1/1/1/1. Cada perfil temprano da peso 3 al color elegido y 1 a los demás. Es una búsqueda exacta de un sustituto simple para generar hipótesis, no la probabilidad de jugar una curva ni una optimización completa de cada composición. Los desempates priorizan la menor fuente de color, luego enderezadas azules, negras y un orden estable de cartas. Equilibrado balancea fuentes totales, no tiempos de acceso idénticos; sus enderezadas favorecen el motor U/B. Estos desempates y cada composición están expuestos para revisar ese supuesto en la siguiente etapa.', '',
             'El mismo piloto juega todos los perfiles: no cambia sus prioridades para favorecer a un color. La recomendación usa desarrollo T2–T3 en equilibrado, promediando las dos posiciones por igual, sin asignar un área a un radar ni sumar indicadores correlacionados.', '',
             '## Resultados por perfil', '',
             '| Perfil | Mejor desarrollo T2–T3 (media OTP/OTD) | Mejor acceso 4 colores T3 |',
             '| --- | ---: | ---: |']
    for row in d['profile_winners']:
        p = row['profile']
        lines.append(f'| {d["profiles"][p]["label"]} | {row["development"]} bridges | {row["all4"]} bridges |')
    lines += ['', 'Ganadores por estimación puntual, sin afirmar que cada diferencia sea estadísticamente concluyente.', '',
              '## Equilibrado: velocidad y fixing', '',
              '| Modo | Bridges | Desarrollo T2–T3 | Amenaza hasta T3 | Cryogen hasta T2 | 4 colores hasta T3 | Operativo Boulder hasta T3 |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for mode in ('OTP', 'OTD'):
        for b in counts:
            values = [pc(rate('balanced', b, mode, key)) for key in ('needed_t2_t3', 'threat_t3', 'relic_t2', 'all4_t3', 'boulder_t3')]
            lines.append(f'| {mode} | {b} | ' + ' | '.join(values) + ' |')
    lines += ['', f'### Qué se gana y qué se pierde al subir de {low} a {high}', '']
    for mode in ('OTP', 'OTD'):
        delta = lambda key: 100*(rate('balanced', high, mode, key)-rate('balanced', low, mode, key))
        lines.append(f'- {mode}: 4 colores T3 cambia {delta("all4_t3"):+.2f} pp; desarrollo T2–T3, {delta("needed_t2_t3"):+.2f} pp; amenaza T3, {delta("threat_t3"):+.2f} pp; Cryogen T2, {delta("relic_t2"):+.2f} pp.')
    lines += ['', 'Para desarrollo sin rival, los puntos anteriores favorecen el extremo bajo del rango. La pequeña ganancia de cobertura de cuatro colores no recupera automáticamente las jugadas perdidas. Más bridges también implica más tierras indestructibles; falta simular el hate para ponerle un valor a esa ventaja. Al variar el ratio se vuelve a elegir la base representativa: estos cambios combinan entrada girada y la composición seleccionada, no aíslan causalmente el efecto de una carta concreta.', '']
    lines += ['', '## Diferencias pareadas frente al ratio de trabajo', '',
              'A−B usa los mismos índices aleatorios de barajado. El intervalo normal al 95% se calcula sobre diferencias por partida, no restando intervalos Wilson de dos porcentajes. Son intervalos puntuales, sin ajuste por comparaciones múltiples; no prueban un óptimo global. La confirmación usa una semilla distinta a la del piloto.', '',
              '| Modo | Comparación | Métrica | Diferencia | IC 95% (pp) |',
              '| --- | --- | --- | ---: | ---: |']
    for mode in ('OTP', 'OTD'):
        for other in counts:
            if other == recommended:
                continue
            for metric in ('needed_t2_t3', 'threat_t3', 'all4_t3'):
                a, b = sorted((recommended, other))
                row = next(x for x in d['paired_comparisons'] if (x['profile'], x['mode'], x['a'], x['b'], x['metric']) == ('balanced', mode, a, b, metric))
                sign = 1 if a == recommended else -1
                lo, hi = sorted(x*sign*100 for x in row['ci95'])
                lines.append(f'| {mode} | {recommended} − {other} | {metric} | {100*sign*row["difference"]:+.2f} pp | [{lo:+.2f}, {hi:+.2f}] |')
    lines += ['', '## Definiciones y denominadores', '',
              '- Desarrollo T2–T3: se lanza al menos un hechizo de motor o criatura en T2 y en T3. No cuenta una activación ni Galvanic Blast contra el jugador. La versión T1–T3 exige los tres turnos y penaliza cualquier apertura con bridge; por eso no se usa como único objetivo.',
              '- Amenaza T3: lanzar al menos un Refurbished Familiar, Utrom Monitor o Myr Enforcer hasta T3. No mide daño ni victoria.',
              '- 4 colores: en algún estado real hasta ese turno se puede producir W, U, B o R por separado. Un Boulder y una tierra disponibles alcanzan; no significa pagar WUBR simultáneamente. Siempre se descuentan los recursos ya gastados en ese turno.',
              '- Color T1 y pago 1C T2: capacidad en algún estado de ese turno, antes o entre acciones; no exige tener ese hechizo en mano. 1C exige dos manás en total, no dos activaciones de Boulder.',
              '- Boulder operativo: filtro enderezado y al menos una tierra enderezada. Lanzarlo no basta si ya se gastó todo el maná.',
              '- Curva T3/T4/T5: al menos esa cantidad de tierras en mesa al terminar el turno. Screw: dos o menos al terminar T4. Se incluye screw condicionado al keep en los datos.',
              '- color_block_t3 es diagnóstico: al menos un estado hasta T3 con algún hechizo coloreado pagable al ignorar color y ninguno pagable con los colores reales, respetando los otros requisitos. No equivale a perder un turno ni a perder la partida.',
              '- Proporciones de éxito sobre todos los intentos, incluidos fallos al piso de mulligan. Screw T4 se muestra entre keeps en el HTML. Intervalos Wilson 95% por proporción en CSV/JSON; diferencias pareadas por separado.', '',
              '## Reglas y política de juego', '',
              'London mulligan sobre siete, exigir ≥2 tierras siempre y piso de cuatro. Se conservan siete con dos o más, incluso manos cargadas de tierras: no se añadió un criterio de rechazo por flood. Al hacer fondo se buscan tres tierras si el tamaño lo permite (dos a cuatro cartas), cobertura de colores y al menos una enderezada; luego un Boulder, motor y desarrollo. No se mira la octava carta para decidir el keep en OTD.', '',
              'En cada turno se endereza y se roba si corresponde. Se elige tierra valorando el mejor hechizo legal, maná disponible y cobertura; si no hay acción inmediata se prepara un bridge. Tras robar durante el turno puede jugarse tierra si todavía no se hizo el land drop. Pagos preservan fuentes según la demanda visible en mano. Todos los costes soportados tienen como máximo un símbolo coloreado.', '',
              'Prioridad compartida: primer Boulder, Thoughtcast, Cryogen, amenazas con afinidad, Fountain, Hawk con rebote útil, Spellbomb y otros hechizos. Scry solo mira las dos cartas permitidas: busca tercera/cuarta tierra, primer filtro y motor. El piloto no vuelve a planificar usando robos futuros ni explora todas las secuencias legales. Los empates y las prioridades están fijados en el código.', '',
              'Se modelan afinidad (solo genérico), Blood de Fountain, robos ETB/LTB de Cryogen, Thoughtcast, Bargain y Spellbomb pagando B, y rebotes de Hawk a artefactos no tierra. Se protegen tierras, amenazas y el único Boulder frente a sacrificios. Con maná restante se usan habilidades de robo, Munitions con Cryogen y recuperación de criaturas de Fountain. Galvanic Blast puede lanzarse al rival, pero no puntúa como desarrollo. No se fuerza un Dispatch sin objetivo rival ni se sacrifica Hawk adrede cuando no hay rebote útil.', '',
              'Familiar supone que el rival tiene una carta para descartar: no se inventa robo por mano rival vacía. Sin combate, decisiones de matchup, respuestas, hate, banquillo ni efectos de Boulder a siete manás. Las restricciones del piloto son heurísticas explícitas, no prohibiciones de las reglas del juego.', '',
              '## Composiciones usadas', '']
    for p in d['profiles']:
        lines += [f'### {d["profiles"][p]["label"]}', '']
        for c in d['candidates']:
            if c['profile'] == p:
                lines.append(f'- {c["bridges"]} bridges: ' + '; '.join(f'{n} {name}' for name, n in c['lands'].items()) + '.')
        lines.append('')
    lines += ['## Alcance y próximo paso', '', decision['next_step'], '',
              'Las tasas de mulligan del modelo anterior no se pueden mezclar sin más con las curvas actuales: ahora existen scry, robos adicionales y una política de fondo con colores. La exigencia de dos tierras y la distinción OTP/OTD sí se mantienen.', '',
              'Esta simulación no termina de validar 19 frente a 20 con todo el motor, porque se fija 19 para aislar el ratio. Tampoco mide la resistencia de bridges/Citadel ante destrucción o exilio. La decisión es de desarrollo sin interacción. El resultado está condicionado a la lista candidata del mismo jugador y torneo; la exportación original de Goldfish sigue pendiente de contraste.', '',
              'Fuentes de reglas: [Boulder, reproducción del texto](https://mtg.wtf/card/hob/173/Giants-Boulder), [Cryogen, reproducción del texto](https://mtg.wtf/card/eoe/52/Cryogen-Relic), [Familiar, notas oficiales MH3](https://magic.wizards.com/en/news/feature/modern-horizons-3-release-notes), [Utrom, notas oficiales TMT](https://media.wizards.com/2026/downloads/TMT_Release_Notes_eM8Yplm3UV/u17aHk8iV1_EN_MTGTMT_ReleaseNotes_20251001.pdf).', '',
              '## Reproducir', '', '```sh',
              'python3 -m unittest discover -s tests -v',
              'python3 -m src.color_bridge_study --trials 2000',
              'python3 -m src.color_bridge_study --trials 10000 --seed 2026102902 --workers 4 --output results/color_bridges',
              'python3 scripts/write_color_bridge_report.py',
              'python3 scripts/build_report.py', '```', '',
              'Semillas, conteos, resultados por celda, trazas y hashes están en results.json. Aumentar --trials cambia la precisión, no elimina el sesgo de la política ni amplía el universo de bases probadas.']
    (OUT/'informe.md').write_text('\n'.join(lines)+'\n')
    print(decision['title'])


if __name__ == '__main__':
    main()
