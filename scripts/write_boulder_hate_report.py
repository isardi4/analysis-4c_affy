"""Publish data-derived comparisons, keeping stress assumptions explicit."""
from math import comb
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/boulder_hate'


def main():
    d=json.loads((OUT/'results.json').read_text())
    cfg=d['config'];counts=d['bridges']
    def cell(bridge,boulder,mode,scenario,citadel=0):
        return next(c for c in d['cells'] if (c['bridges'],c['boulders'],c['mode'],c['scenario'],c['citadels'])==(bridge,boulder,mode,scenario,citadel))
    def p(c,key):return c['metrics'][key]['p']
    def pc(x):return f'{100*x:.2f}%'
    def integer(x):return f'{x:,}'.replace(',','.')
    lines=['# Boulder y hate: rango 6–12 bridges','',
           f'{integer(d["total_trials"])} intentos; {len(d["cells"])} celdas × {integer(cfg["trials_per_cell"])}. OTP/OTD separados, horizonte T1–T6. Piloto de escenarios condicionales; no tasa de victoria ni frecuencias observadas del metajuego.','',
           '## Qué incluía ya el estudio anterior','',
           'Perfiles predefinidos ya incluía cuatro Boulder, coste 1, scry 2, filtrado 1 + girar, afinidad, robos adicionales y rebotes. El control estructural y Composición a medida solo calculan tierras/fuentes naturales. Este nuevo estudio compara tres y cuatro Boulder y añade interacción.','',
           '## Composiciones comparadas','',
           '- Siempre 60 cartas y 19 tierras; 6–12 bridges, máximo cuatro copias por nombre.',
           '- Cuatro Boulder: los otros 37 hechizos de la referencia permanecen iguales.',
           '- Tres Boulder: se agrega una tercera Nihil Spellbomb. La sustitución mantiene artefactos y coste 1, pero cambia robos y habilidades; no es un reemplazo neutral.',
           '- Las siete bases Equilibrado del experimento previo son las referencias. Se añade un control que cambia dos tierras monocolores por dos Citadel, eligiendo la sustitución con mejor cobertura natural. Cada lista exacta está en el JSON. No es una búsqueda exhaustiva con Citadel.',
           '- Los cuatro pesos personalizados todavía no generan partidas simuladas: esta fase usa Equilibrado para aislar Boulder y hate.','',
           '## Reglas y tiempos del hate','',
           '| Escenario | Turno del rival | Efecto y condición |','| --- | --- | --- |',
           '| Sin hate | — | Control con idénticos índices aleatorios |',
           '| Vandalblast | T2 | Destruye un artefacto; evita objetivos indestructibles |',
           '| Masked Vandal | T2 | Exilia uno; el rival tiene una criatura en el cementerio para pagar |',
           '| Dust to Dust | T3 | Exilia dos artefactos distintos; requiere ambos objetivos |',
           '| Gorilla Shaman | T2, T3 y T4 | Presente y sin remover; presupuestos totales 2/3/4 manás; activaciones cuestan 2×valor de maná+1, solo artefactos no criatura |',
           '| Vandalblast sobrecargado | T5 | Destruye todos los artefactos vulnerables; conserva bridges/Citadel |','',
           'El Tn rival sucede antes de nuestro Tn en OTD, y entre nuestro Tn y T(n+1) en OTP. Por eso el barrido llega a T6: permite observar recuperación tras Vandalblast sobrecargado también en OTP. No se adelanta la sobrecarga a T3.','',
           'El rival dispone del hate y de sus requisitos en el turno declarado. La selección usa solo la mesa pública: negar tierras primero, luego Boulder y después amenazas/otros artefactos. Se preservan las zonas de cementerio/exilio y se resuelven disparos de Cryogen/Spellbomb correctamente. Destrucciones simultáneas retiran todo antes de pagar disparos con el maná sobreviviente.','',
           'No se modelan respuestas del jugador, maná flotado en respuesta, eliminación de Gorilla, counters ni interacción con el cementerio rival. Es una prueba de exposición y recuperación bajo esas condiciones. La habilidad de descarte de Familiar supone cartas en mano rival.','',
           '## Indicadores','',
           '- Boulder conservado: está en el keep después de London, exigiendo dos tierras desde las siete iniciales. El piso de cuatro sigue siendo una propuesta metodológica.',
           '- Boulder por quinto robo: está en el keep o llega en uno de los primeros cinco robos reales, naturales o adicionales. Scry no cuenta como robo. El horizonte T6 permite llegar a cinco robos naturales incluso en OTP.',
           '- Boulder operativo T3: hay un filtro enderezado y una tierra disponible en algún estado de ese turno, después de procesar el hate anterior.',
           '- Cuatro colores Tn: acceso individual W/U/B/R en un estado real de ese turno, no haberlos tenido antes del ataque. No significa pagar WUBR simultáneamente.',
           '- Motor y colores Tn: capacidad de pagar, por separado y sin exigir tenerlos en mano, 1U, 1B, W, R y el coste de Utrom con afinidad del estado actual. Se exige al menos un artefacto. Es un diagnóstico de pagos individuales, no una secuencia simultánea ni que se hayan lanzado esos hechizos.',
           '- Desarrollo T2–T3: lanzar un hechizo de desarrollo en ambos turnos; conserva la definición del experimento previo.',
           '- Tierras/artefactos/Boulder perdidos: media sobre todos los intentos, hasta T6. Amenaza Tn usa criaturas todavía en mesa.',
           '- Tasas sobre todos los intentos, incluidos fallos al piso. CSV/JSON guardan intervalos Wilson 95%. Diferencias pareadas se calculan sobre los mismos índices aleatorios, con intervalos normales puntuales al 95%; no se ajustan por múltiples comparaciones.','',
           '## Boulder en las primeras siete, antes de mulligans','',
           '| Copias | Probabilidad exacta |','| ---: | ---: |']
    for b in cfg['boulders']:
        lines.append(f'| {b} | {pc(1-comb(60-b,7)/comb(60,7))} |')
    lines+=['','No confundir esta probabilidad exacta con Boulder conservado tras mulligans ni con filtro operativo.','',
            '## Acceso sin hate, sin Citadel','',
            '| Modo | Bridges | Boulder | Conservado | Hasta quinto robo | Operativo T3 | 4 colores T3 | Motor y colores T6 |','| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for mode in ('OTP','OTD'):
        for bridge in counts:
            for b in cfg['boulders']:
                c=cell(bridge,b,mode,'none')
                lines.append(f'| {mode} | {bridge} | {b} | '+' | '.join(pc(p(c,k)) for k in ('boulder_kept','boulder_by_fifth_draw','boulder_t3','all4_t3','suite_t6'))+' |')
    lines+=['','## Dos objetivos, sin sumarlos en una nota única','',
            'Desarrollar un hechizo en T2 y T3 mide velocidad real de las jugadas. Poder pagar el conjunto de costes por separado en T6 mide cobertura y capacidad posterior. Es esperable que el ganador cambie según el objetivo. El HTML muestra una frontera de opciones no dominadas por estimación puntual: una opción queda fuera si otra iguala o mejora ambas métricas y mejora al menos una. La frontera depende de q y no certifica dominancia estadística.','']
    for bridge in (min(counts),max(counts)):
        early=sum(p(cell(bridge,4,m,'none'),'development_t2_t3') for m in ('OTP','OTD'))/2
        late=sum(p(cell(bridge,4,m,'none'),'suite_t6') for m in ('OTP','OTD'))/2
        lines.append(f'- {bridge} bridges / 4 Boulder / 0 Citadel, sin hate: desarrollo T2–T3 {pc(early)}; diagnóstico de motor T6 {pc(late)}. Media OTP/OTD con igual peso.')
    lines+=['','## Resistencia por escenario','',
            'La mejor estimación puntual del diagnóstico de motor T6 se muestra por escenario. Se da igual peso a OTP y OTD para esta tabla descriptiva; no se presupone frecuencia de cada tipo de hate.','',
            '| Escenario | Citadel | Mejor combinación puntual | Motor T6 · media OTP/OTD |','| --- | ---: | --- | ---: |']
    for s,info in cfg['scenarios'].items():
        for cit in cfg['citadels']:
            def mean(b,k):return sum(p(cell(b,k,m,s,cit),'suite_t6') for m in ('OTP','OTD'))/2
            b,k=max(((b,k) for b in counts for k in cfg['boulders']),key=lambda x:(mean(*x),-x[0],x[1]))
            lines.append(f'| {info["label"]} | {cit} | {b} bridges / {k} Boulder | {pc(mean(b,k))} |')
    lines+=['','## Ponderar hate sin inventar frecuencias','',
            'El control interactivo usa q como frecuencia hipotética de UN escenario seleccionado: P(mixta)=(1−q)×P(sin hate)+q×P(con ese escenario). Empieza en q=0; el usuario decide el supuesto. Se muestran estimaciones puntuales y los intervalos de cada escenario por separado. No se presentan los intervalos individuales como intervalos de la mezcla.','',
            'Las otras formas de hate tienen frecuencia cero en esa mezcla. No hay independencia asumida entre múltiples ataques ni una tasa de victoria. El caso Gorilla ya incluye sus ataques sucesivos. La sobrecarga se evalúa mejor a T6; antes de su T5 rival aún no puede afectar los resultados.','',
            'La cantidad óptima no está certificada: solo se comparan estas bases representativas, dos cantidades de Boulder y dos controles de Citadel. Los resultados no obligan a que pocos bridges sean malos dentro del rango estudiado. La solidez depende del efecto concreto: indestructible protege frente a destrucción, no frente a exilio.','',
            '## Fuentes y reproducción','']
    for name,url in cfg['sources'].items():lines.append(f'- [{name}]({url})')
    lines+=['','```sh','python3 -m unittest discover -s tests -v','python3 -m src.boulder_hate --workers 4','python3 scripts/write_boulder_hate_report.py','python3 scripts/build_report.py','```','',
            'Los resultados completos incluyen semillas, hashes, listas de los 41 hechizos, tierras exactas, trazas y diferencias pareadas. Ampliar N reduce ruido, no elimina el sesgo de las decisiones heurísticas.']
    (OUT/'informe.md').write_text('\n'.join(lines)+'\n')
    print(f'Informe Boulder/hate: {len(d["cells"])} celdas, {integer(d["total_trials"])} intentos.')


if __name__=='__main__':main()
