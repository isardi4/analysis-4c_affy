# Boulder y hate: rango 6–12 bridges

672.000 intentos; 336 celdas × 2.000. OTP/OTD separados, horizonte T1–T6. Piloto de escenarios condicionales; no tasa de victoria ni frecuencias observadas del metajuego.

## Qué incluía ya el estudio anterior

Perfiles predefinidos ya incluía cuatro Boulder, coste 1, scry 2, filtrado 1 + girar, afinidad, robos adicionales y rebotes. El control estructural y Composición a medida solo calculan tierras/fuentes naturales. Este nuevo estudio compara tres y cuatro Boulder y añade interacción.

## Composiciones comparadas

- Siempre 60 cartas y 19 tierras; 6–12 bridges, máximo cuatro copias por nombre.
- Cuatro Boulder: los otros 37 hechizos de la referencia permanecen iguales.
- Tres Boulder: se agrega una tercera Nihil Spellbomb. La sustitución mantiene artefactos y coste 1, pero cambia robos y habilidades; no es un reemplazo neutral.
- Las siete bases Equilibrado del experimento previo son las referencias. Se añade un control que cambia dos tierras monocolores por dos Citadel, eligiendo la sustitución con mejor cobertura natural. Cada lista exacta está en el JSON. No es una búsqueda exhaustiva con Citadel.
- Los cuatro pesos personalizados todavía no generan partidas simuladas: esta fase usa Equilibrado para aislar Boulder y hate.

## Reglas y tiempos del hate

| Escenario | Turno del rival | Efecto y condición |
| --- | --- | --- |
| Sin hate | — | Control con idénticos índices aleatorios |
| Vandalblast | T2 | Destruye un artefacto; evita objetivos indestructibles |
| Masked Vandal | T2 | Exilia uno; el rival tiene una criatura en el cementerio para pagar |
| Dust to Dust | T3 | Exilia dos artefactos distintos; requiere ambos objetivos |
| Gorilla Shaman | T2, T3 y T4 | Presente y sin remover; presupuestos totales 2/3/4 manás; activaciones cuestan 2×valor de maná+1, solo artefactos no criatura |
| Vandalblast sobrecargado | T5 | Destruye todos los artefactos vulnerables; conserva bridges/Citadel |

El Tn rival sucede antes de nuestro Tn en OTD, y entre nuestro Tn y T(n+1) en OTP. Por eso el barrido llega a T6: permite observar recuperación tras Vandalblast sobrecargado también en OTP. No se adelanta la sobrecarga a T3.

El rival dispone del hate y de sus requisitos en el turno declarado. La selección usa solo la mesa pública: negar tierras primero, luego Boulder y después amenazas/otros artefactos. Se preservan las zonas de cementerio/exilio y se resuelven disparos de Cryogen/Spellbomb correctamente. Destrucciones simultáneas retiran todo antes de pagar disparos con el maná sobreviviente.

No se modelan respuestas del jugador, maná flotado en respuesta, eliminación de Gorilla, counters ni interacción con el cementerio rival. Es una prueba de exposición y recuperación bajo esas condiciones. La habilidad de descarte de Familiar supone cartas en mano rival.

## Indicadores

- Boulder conservado: está en el keep después de London, exigiendo dos tierras desde las siete iniciales. El piso de cuatro sigue siendo una propuesta metodológica.
- Boulder por quinto robo: está en el keep o llega en uno de los primeros cinco robos reales, naturales o adicionales. Scry no cuenta como robo. El horizonte T6 permite llegar a cinco robos naturales incluso en OTP.
- Boulder operativo T3: hay un filtro enderezado y una tierra disponible en algún estado de ese turno, después de procesar el hate anterior.
- Cuatro colores Tn: acceso individual W/U/B/R en un estado real de ese turno, no haberlos tenido antes del ataque. No significa pagar WUBR simultáneamente.
- Motor y colores Tn: capacidad de pagar, por separado y sin exigir tenerlos en mano, 1U, 1B, W, R y el coste de Utrom con afinidad del estado actual. Se exige al menos un artefacto. Es un diagnóstico de pagos individuales, no una secuencia simultánea ni que se hayan lanzado esos hechizos.
- Desarrollo T2–T3: lanzar un hechizo de desarrollo en ambos turnos; conserva la definición del experimento previo.
- Tierras/artefactos/Boulder perdidos: media sobre todos los intentos, hasta T6. Amenaza Tn usa criaturas todavía en mesa.
- Tasas sobre todos los intentos, incluidos fallos al piso. CSV/JSON guardan intervalos Wilson 95%. Diferencias pareadas se calculan sobre los mismos índices aleatorios, con intervalos normales puntuales al 95%; no se ajustan por múltiples comparaciones.

## Boulder en las primeras siete, antes de mulligans

| Copias | Probabilidad exacta |
| ---: | ---: |
| 3 | 31.54% |
| 4 | 39.95% |

No confundir esta probabilidad exacta con Boulder conservado tras mulligans ni con filtro operativo.

## Acceso sin hate, sin Citadel

| Modo | Bridges | Boulder | Conservado | Hasta quinto robo | Operativo T3 | 4 colores T3 | Motor y colores T6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| OTP | 6 | 3 | 29.40% | 48.30% | 40.65% | 47.10% | 81.90% |
| OTP | 6 | 4 | 37.40% | 59.25% | 50.75% | 56.65% | 86.35% |
| OTP | 7 | 3 | 29.40% | 48.30% | 40.60% | 48.50% | 84.15% |
| OTP | 7 | 4 | 37.40% | 59.25% | 50.60% | 57.90% | 88.40% |
| OTP | 8 | 3 | 29.40% | 48.30% | 40.45% | 49.00% | 84.35% |
| OTP | 8 | 4 | 37.40% | 59.25% | 50.50% | 58.20% | 88.20% |
| OTP | 9 | 3 | 29.40% | 48.30% | 40.40% | 49.50% | 85.00% |
| OTP | 9 | 4 | 37.40% | 59.25% | 50.45% | 58.65% | 88.45% |
| OTP | 10 | 3 | 29.40% | 48.30% | 40.40% | 50.20% | 84.75% |
| OTP | 10 | 4 | 37.40% | 59.25% | 50.40% | 58.90% | 88.60% |
| OTP | 11 | 3 | 29.40% | 48.30% | 40.25% | 50.35% | 86.60% |
| OTP | 11 | 4 | 37.40% | 59.25% | 50.10% | 58.45% | 89.55% |
| OTP | 12 | 3 | 29.40% | 48.30% | 39.75% | 50.95% | 88.15% |
| OTP | 12 | 4 | 37.40% | 59.25% | 49.70% | 59.25% | 90.75% |
| OTD | 6 | 3 | 29.40% | 48.30% | 45.65% | 51.85% | 86.80% |
| OTD | 6 | 4 | 37.40% | 59.25% | 56.00% | 61.75% | 90.70% |
| OTD | 7 | 3 | 29.40% | 48.30% | 45.80% | 53.15% | 87.55% |
| OTD | 7 | 4 | 37.40% | 59.25% | 56.25% | 63.45% | 91.15% |
| OTD | 8 | 3 | 29.40% | 48.30% | 44.95% | 53.60% | 87.55% |
| OTD | 8 | 4 | 37.40% | 59.25% | 55.60% | 63.55% | 91.40% |
| OTD | 9 | 3 | 29.40% | 48.30% | 44.90% | 53.85% | 88.05% |
| OTD | 9 | 4 | 37.40% | 59.25% | 55.50% | 63.75% | 91.65% |
| OTD | 10 | 3 | 29.40% | 48.30% | 45.15% | 54.35% | 88.55% |
| OTD | 10 | 4 | 37.40% | 59.25% | 55.60% | 63.50% | 91.75% |
| OTD | 11 | 3 | 29.40% | 48.30% | 44.85% | 54.20% | 89.20% |
| OTD | 11 | 4 | 37.40% | 59.25% | 55.25% | 63.15% | 91.85% |
| OTD | 12 | 3 | 29.40% | 48.30% | 44.80% | 55.35% | 90.35% |
| OTD | 12 | 4 | 37.40% | 59.25% | 55.30% | 64.50% | 92.70% |

## Dos objetivos, sin sumarlos en una nota única

Desarrollar un hechizo en T2 y T3 mide velocidad real de las jugadas. Poder pagar el conjunto de costes por separado en T6 mide cobertura y capacidad posterior. Es esperable que el ganador cambie según el objetivo. El HTML muestra una frontera de opciones no dominadas por estimación puntual: una opción queda fuera si otra iguala o mejora ambas métricas y mejora al menos una. La frontera depende de q y no certifica dominancia estadística.

- 6 bridges / 4 Boulder / 0 Citadel, sin hate: desarrollo T2–T3 76.83%; diagnóstico de motor T6 88.53%. Media OTP/OTD con igual peso.
- 12 bridges / 4 Boulder / 0 Citadel, sin hate: desarrollo T2–T3 71.38%; diagnóstico de motor T6 91.72%. Media OTP/OTD con igual peso.

## Resistencia por escenario

La mejor estimación puntual del diagnóstico de motor T6 se muestra por escenario. Se da igual peso a OTP y OTD para esta tabla descriptiva; no se presupone frecuencia de cada tipo de hate.

| Escenario | Citadel | Mejor combinación puntual | Motor T6 · media OTP/OTD |
| --- | ---: | --- | ---: |
| Sin hate | 0 | 12 bridges / 4 Boulder | 91.72% |
| Sin hate | 2 | 12 bridges / 4 Boulder | 89.20% |
| Vandalblast · rival T2 | 0 | 12 bridges / 4 Boulder | 85.50% |
| Vandalblast · rival T2 | 2 | 11 bridges / 4 Boulder | 82.30% |
| Masked Vandal · rival T2 | 0 | 12 bridges / 4 Boulder | 77.45% |
| Masked Vandal · rival T2 | 2 | 12 bridges / 4 Boulder | 74.95% |
| Dust to Dust · rival T3 | 0 | 11 bridges / 4 Boulder | 61.15% |
| Dust to Dust · rival T3 | 2 | 10 bridges / 4 Boulder | 59.17% |
| Gorilla Shaman · rival T2–T4 | 0 | 12 bridges / 4 Boulder | 57.40% |
| Gorilla Shaman · rival T2–T4 | 2 | 12 bridges / 4 Boulder | 57.55% |
| Vandalblast sobrecargado · rival T5 | 0 | 12 bridges / 4 Boulder | 52.95% |
| Vandalblast sobrecargado · rival T5 | 2 | 12 bridges / 4 Boulder | 54.75% |

## Ponderar hate sin inventar frecuencias

El control interactivo usa q como frecuencia hipotética de UN escenario seleccionado: P(mixta)=(1−q)×P(sin hate)+q×P(con ese escenario). Empieza en q=0; el usuario decide el supuesto. Se muestran estimaciones puntuales y los intervalos de cada escenario por separado. No se presentan los intervalos individuales como intervalos de la mezcla.

Las otras formas de hate tienen frecuencia cero en esa mezcla. No hay independencia asumida entre múltiples ataques ni una tasa de victoria. El caso Gorilla ya incluye sus ataques sucesivos. La sobrecarga se evalúa mejor a T6; antes de su T5 rival aún no puede afectar los resultados.

La cantidad óptima no está certificada: solo se comparan estas bases representativas, dos cantidades de Boulder y dos controles de Citadel. Los resultados no obligan a que pocos bridges sean malos dentro del rango estudiado. La solidez depende del efecto concreto: indestructible protege frente a destrucción, no frente a exilio.

## Fuentes y reproducción

- [Masked Vandal](https://magic.wizards.com/en/news/feature/kaldheim-release-notes-2021-01-22)
- [Vandalblast](https://magic.wizards.com/en/news/feature/commander-masters-release-notes)
- [Gorilla Shaman](https://mtg.wtf/card?q=Gorilla+Shaman)
- [Dust to Dust](https://mtg.wtf/card?q=Dust+to+Dust)

```sh
python3 -m unittest discover -s tests -v
python3 -m src.boulder_hate --workers 4
python3 scripts/write_boulder_hate_report.py
python3 scripts/build_report.py
```

Los resultados completos incluyen semillas, hashes, listas de los 41 hechizos, tierras exactas, trazas y diferencias pareadas. Ampliar N reduce ruido, no elimina el sesgo de las decisiones heurísticas.
