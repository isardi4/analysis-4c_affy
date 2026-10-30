# Colores tempranos y cantidad de bridges

Fecha: 2026-10-29.

## Punto de partida: 6 bridges + 13 enderezadas.

Es el mejor valor puntual del desarrollo T2–T3 en el perfil equilibrado, con igual peso para OTP y OTD. Mantener 7 bridges como control cercano permite revisar el ratio al optimizar las cartas concretas. El fixing de cuatro colores se informa aparte: no se fuerza a gastar cuatro colores si la mano no los necesita.

Recomendación de trabajo entre las 35 bases probadas (6–12 bridges); no óptimo global ni tasa de victoria.

Piloto: 140.000 partidas (2.000 × 35 bases × OTP/OTD). Confirmación con semilla independiente: 700.000 partidas (10.000 por celda). No se suman ambas muestras. Horizonte T1–T5.

## Qué significa cada prioridad

Para cada ratio 6–12 se busca una base representativa entre las seis parejas WUBR de bridges y las cuatro tierras artefacto monocolores. Siempre 19 tierras, cuatro Boulder, las mismas 41 cartas no tierra y máximo cuatro copias por nombre. Sin básicas ni Citadel en este experimento sin rival.

La función de selección es Σ w(c) × [1 − C(60−fuentes(c),9)/C(60,9)]. Equilibrado: pesos 1/1/1/1. Cada perfil temprano da peso 3 al color elegido y 1 a los demás. Es una búsqueda exacta de un sustituto simple para generar hipótesis, no la probabilidad de jugar una curva ni una optimización completa de cada composición. Los desempates priorizan la menor fuente de color, luego enderezadas azules, negras y un orden estable de cartas. Equilibrado balancea fuentes totales, no tiempos de acceso idénticos; sus enderezadas favorecen el motor U/B. Estos desempates y cada composición están expuestos para revisar ese supuesto en la siguiente etapa.

El mismo piloto juega todos los perfiles: no cambia sus prioridades para favorecer a un color. La recomendación usa desarrollo T2–T3 en equilibrado, promediando las dos posiciones por igual, sin asignar un área a un radar ni sumar indicadores correlacionados.

## Resultados por perfil

| Perfil | Mejor desarrollo T2–T3 (media OTP/OTD) | Mejor acceso 4 colores T3 |
| --- | ---: | ---: |
| Equilibrado | 6 bridges | 12 bridges |
| Azul temprano | 7 bridges | 6 bridges |
| Blanco temprano | 6 bridges | 6 bridges |
| Negro temprano | 6 bridges | 6 bridges |
| Rojo temprano | 6 bridges | 6 bridges |

Ganadores por estimación puntual, sin afirmar que cada diferencia sea estadísticamente concluyente.

## Equilibrado: velocidad y fixing

| Modo | Bridges | Desarrollo T2–T3 | Amenaza hasta T3 | Cryogen hasta T2 | 4 colores hasta T3 | Operativo Boulder hasta T3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OTP | 6 | 71.49% | 58.36% | 22.53% | 55.99% | 49.07% |
| OTP | 7 | 71.54% | 58.69% | 21.82% | 56.71% | 49.01% |
| OTP | 8 | 71.10% | 58.23% | 20.85% | 57.07% | 48.89% |
| OTP | 9 | 70.35% | 57.18% | 19.85% | 57.33% | 48.75% |
| OTP | 10 | 69.99% | 55.92% | 19.26% | 57.25% | 48.58% |
| OTP | 11 | 69.47% | 55.20% | 17.84% | 57.53% | 48.42% |
| OTP | 12 | 67.54% | 52.26% | 16.48% | 57.99% | 48.02% |
| OTD | 6 | 79.29% | 63.34% | 24.73% | 60.37% | 53.77% |
| OTD | 7 | 79.23% | 63.65% | 24.14% | 61.10% | 53.74% |
| OTD | 8 | 78.77% | 63.13% | 22.98% | 61.52% | 53.59% |
| OTD | 9 | 77.88% | 61.79% | 21.92% | 61.75% | 53.43% |
| OTD | 10 | 77.12% | 60.60% | 21.28% | 61.49% | 53.31% |
| OTD | 11 | 76.80% | 59.67% | 19.69% | 61.31% | 53.01% |
| OTD | 12 | 75.02% | 56.69% | 18.41% | 61.68% | 52.71% |

### Qué se gana y qué se pierde al subir de 6 a 12

- OTP: 4 colores T3 cambia +2.00 pp; desarrollo T2–T3, -3.95 pp; amenaza T3, -6.10 pp; Cryogen T2, -6.05 pp.
- OTD: 4 colores T3 cambia +1.31 pp; desarrollo T2–T3, -4.27 pp; amenaza T3, -6.65 pp; Cryogen T2, -6.32 pp.

Para desarrollo sin rival, los puntos anteriores favorecen el extremo bajo del rango. La pequeña ganancia de cobertura de cuatro colores no recupera automáticamente las jugadas perdidas. Más bridges también implica más tierras indestructibles; falta simular el hate para ponerle un valor a esa ventaja. Al variar el ratio se vuelve a elegir la base representativa: estos cambios combinan entrada girada y la composición seleccionada, no aíslan causalmente el efecto de una carta concreta.


## Diferencias pareadas frente al ratio de trabajo

A−B usa los mismos índices aleatorios de barajado. El intervalo normal al 95% se calcula sobre diferencias por partida, no restando intervalos Wilson de dos porcentajes. Son intervalos puntuales, sin ajuste por comparaciones múltiples; no prueban un óptimo global. La confirmación usa una semilla distinta a la del piloto.

| Modo | Comparación | Métrica | Diferencia | IC 95% (pp) |
| --- | --- | --- | ---: | ---: |
| OTP | 6 − 7 | needed_t2_t3 | -0.05 pp | [-0.60, +0.50] |
| OTP | 6 − 7 | threat_t3 | -0.33 pp | [-0.90, +0.24] |
| OTP | 6 − 7 | all4_t3 | -0.72 pp | [-1.21, -0.23] |
| OTP | 6 − 8 | needed_t2_t3 | +0.39 pp | [-0.35, +1.13] |
| OTP | 6 − 8 | threat_t3 | +0.13 pp | [-0.61, +0.87] |
| OTP | 6 − 8 | all4_t3 | -1.08 pp | [-1.70, -0.46] |
| OTP | 6 − 9 | needed_t2_t3 | +1.14 pp | [+0.37, +1.91] |
| OTP | 6 − 9 | threat_t3 | +1.18 pp | [+0.40, +1.96] |
| OTP | 6 − 9 | all4_t3 | -1.34 pp | [-1.98, -0.70] |
| OTP | 6 − 10 | needed_t2_t3 | +1.50 pp | [+0.68, +2.32] |
| OTP | 6 − 10 | threat_t3 | +2.44 pp | [+1.61, +3.27] |
| OTP | 6 − 10 | all4_t3 | -1.26 pp | [-1.94, -0.58] |
| OTP | 6 − 11 | needed_t2_t3 | +2.02 pp | [+1.11, +2.93] |
| OTP | 6 − 11 | threat_t3 | +3.16 pp | [+2.24, +4.08] |
| OTP | 6 − 11 | all4_t3 | -1.54 pp | [-2.25, -0.83] |
| OTP | 6 − 12 | needed_t2_t3 | +3.95 pp | [+2.98, +4.92] |
| OTP | 6 − 12 | threat_t3 | +6.10 pp | [+5.11, +7.09] |
| OTP | 6 − 12 | all4_t3 | -2.00 pp | [-2.72, -1.28] |
| OTD | 6 − 7 | needed_t2_t3 | +0.06 pp | [-0.45, +0.57] |
| OTD | 6 − 7 | threat_t3 | -0.31 pp | [-0.89, +0.27] |
| OTD | 6 − 7 | all4_t3 | -0.73 pp | [-1.22, -0.24] |
| OTD | 6 − 8 | needed_t2_t3 | +0.52 pp | [-0.17, +1.21] |
| OTD | 6 − 8 | threat_t3 | +0.21 pp | [-0.53, +0.95] |
| OTD | 6 − 8 | all4_t3 | -1.15 pp | [-1.76, -0.54] |
| OTD | 6 − 9 | needed_t2_t3 | +1.41 pp | [+0.69, +2.13] |
| OTD | 6 − 9 | threat_t3 | +1.55 pp | [+0.77, +2.33] |
| OTD | 6 − 9 | all4_t3 | -1.38 pp | [-2.01, -0.75] |
| OTD | 6 − 10 | needed_t2_t3 | +2.17 pp | [+1.40, +2.94] |
| OTD | 6 − 10 | threat_t3 | +2.74 pp | [+1.91, +3.57] |
| OTD | 6 − 10 | all4_t3 | -1.12 pp | [-1.78, -0.46] |
| OTD | 6 − 11 | needed_t2_t3 | +2.49 pp | [+1.64, +3.34] |
| OTD | 6 − 11 | threat_t3 | +3.67 pp | [+2.74, +4.60] |
| OTD | 6 − 11 | all4_t3 | -0.94 pp | [-1.64, -0.24] |
| OTD | 6 − 12 | needed_t2_t3 | +4.27 pp | [+3.36, +5.18] |
| OTD | 6 − 12 | threat_t3 | +6.65 pp | [+5.66, +7.64] |
| OTD | 6 − 12 | all4_t3 | -1.31 pp | [-2.03, -0.59] |

## Definiciones y denominadores

- Desarrollo T2–T3: se lanza al menos un hechizo de motor o criatura en T2 y en T3. No cuenta una activación ni Galvanic Blast contra el jugador. La versión T1–T3 exige los tres turnos y penaliza cualquier apertura con bridge; por eso no se usa como único objetivo.
- Amenaza T3: lanzar al menos un Refurbished Familiar, Utrom Monitor o Myr Enforcer hasta T3. No mide daño ni victoria.
- 4 colores: en algún estado real hasta ese turno se puede producir W, U, B o R por separado. Un Boulder y una tierra disponibles alcanzan; no significa pagar WUBR simultáneamente. Siempre se descuentan los recursos ya gastados en ese turno.
- Color T1 y pago 1C T2: capacidad en algún estado de ese turno, antes o entre acciones; no exige tener ese hechizo en mano. 1C exige dos manás en total, no dos activaciones de Boulder.
- Boulder operativo: filtro enderezado y al menos una tierra enderezada. Lanzarlo no basta si ya se gastó todo el maná.
- Curva T3/T4/T5: al menos esa cantidad de tierras en mesa al terminar el turno. Screw: dos o menos al terminar T4. Se incluye screw condicionado al keep en los datos.
- color_block_t3 es diagnóstico: al menos un estado hasta T3 con algún hechizo coloreado pagable al ignorar color y ninguno pagable con los colores reales, respetando los otros requisitos. No equivale a perder un turno ni a perder la partida.
- Proporciones de éxito sobre todos los intentos, incluidos fallos al piso de mulligan. Screw T4 se muestra entre keeps en el HTML. Intervalos Wilson 95% por proporción en CSV/JSON; diferencias pareadas por separado.

## Reglas y política de juego

London mulligan sobre siete, exigir ≥2 tierras siempre y piso de cuatro. Se conservan siete con dos o más, incluso manos cargadas de tierras: no se añadió un criterio de rechazo por flood. Al hacer fondo se buscan tres tierras si el tamaño lo permite (dos a cuatro cartas), cobertura de colores y al menos una enderezada; luego un Boulder, motor y desarrollo. No se mira la octava carta para decidir el keep en OTD.

En cada turno se endereza y se roba si corresponde. Se elige tierra valorando el mejor hechizo legal, maná disponible y cobertura; si no hay acción inmediata se prepara un bridge. Tras robar durante el turno puede jugarse tierra si todavía no se hizo el land drop. Pagos preservan fuentes según la demanda visible en mano. Todos los costes soportados tienen como máximo un símbolo coloreado.

Prioridad compartida: primer Boulder, Thoughtcast, Cryogen, amenazas con afinidad, Fountain, Hawk con rebote útil, Spellbomb y otros hechizos. Scry solo mira las dos cartas permitidas: busca tercera/cuarta tierra, primer filtro y motor. El piloto no vuelve a planificar usando robos futuros ni explora todas las secuencias legales. Los empates y las prioridades están fijados en el código.

Se modelan afinidad (solo genérico), Blood de Fountain, robos ETB/LTB de Cryogen, Thoughtcast, Bargain y Spellbomb pagando B, y rebotes de Hawk a artefactos no tierra. Se protegen tierras, amenazas y el único Boulder frente a sacrificios. Con maná restante se usan habilidades de robo, Munitions con Cryogen y recuperación de criaturas de Fountain. Galvanic Blast puede lanzarse al rival, pero no puntúa como desarrollo. No se fuerza un Dispatch sin objetivo rival ni se sacrifica Hawk adrede cuando no hay rebote útil.

Familiar supone que el rival tiene una carta para descartar: no se inventa robo por mano rival vacía. Sin combate, decisiones de matchup, respuestas, hate, banquillo ni efectos de Boulder a siete manás. Las restricciones del piloto son heurísticas explícitas, no prohibiciones de las reglas del juego.

## Composiciones usadas

### Equilibrado

- 6 bridges: 3 Razortide Bridge; 2 Drossforge Bridge; 1 Rustvale Bridge; 2 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 3 Great Furnace.
- 7 bridges: 3 Razortide Bridge; 3 Drossforge Bridge; 1 Rustvale Bridge; 2 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 2 Great Furnace.
- 8 bridges: 3 Razortide Bridge; 3 Drossforge Bridge; 2 Rustvale Bridge; 2 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 1 Great Furnace.
- 9 bridges: 3 Razortide Bridge; 3 Drossforge Bridge; 3 Rustvale Bridge; 1 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 1 Great Furnace.
- 10 bridges: 4 Razortide Bridge; 3 Drossforge Bridge; 3 Rustvale Bridge; 4 Seat of the Synod; 4 Vault of Whispers; 1 Great Furnace.
- 11 bridges: 4 Razortide Bridge; 4 Drossforge Bridge; 3 Rustvale Bridge; 4 Seat of the Synod; 4 Vault of Whispers.
- 12 bridges: 4 Razortide Bridge; 4 Drossforge Bridge; 4 Rustvale Bridge; 4 Seat of the Synod; 3 Vault of Whispers.

### Azul temprano

- 6 bridges: 4 Razortide Bridge; 1 Mistvault Bridge; 1 Silverbluff Bridge; 1 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 4 Great Furnace.
- 7 bridges: 4 Razortide Bridge; 1 Mistvault Bridge; 2 Silverbluff Bridge; 1 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 3 Great Furnace.
- 8 bridges: 4 Razortide Bridge; 1 Mistvault Bridge; 3 Silverbluff Bridge; 1 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 2 Great Furnace.
- 9 bridges: 4 Razortide Bridge; 2 Mistvault Bridge; 1 Rustvale Bridge; 2 Silverbluff Bridge; 4 Seat of the Synod; 4 Vault of Whispers; 2 Great Furnace.
- 10 bridges: 4 Razortide Bridge; 2 Mistvault Bridge; 2 Rustvale Bridge; 2 Silverbluff Bridge; 4 Seat of the Synod; 4 Vault of Whispers; 1 Great Furnace.
- 11 bridges: 4 Razortide Bridge; 1 Mistvault Bridge; 1 Drossforge Bridge; 2 Rustvale Bridge; 3 Silverbluff Bridge; 4 Seat of the Synod; 4 Vault of Whispers.
- 12 bridges: 4 Razortide Bridge; 2 Mistvault Bridge; 1 Drossforge Bridge; 2 Rustvale Bridge; 3 Silverbluff Bridge; 4 Seat of the Synod; 3 Vault of Whispers.

### Blanco temprano

- 6 bridges: 1 Razortide Bridge; 4 Rustvale Bridge; 1 Goldmire Bridge; 4 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 1 Great Furnace.
- 7 bridges: 1 Razortide Bridge; 4 Rustvale Bridge; 2 Goldmire Bridge; 4 Ancient Den; 4 Seat of the Synod; 3 Vault of Whispers; 1 Great Furnace.
- 8 bridges: 1 Razortide Bridge; 4 Rustvale Bridge; 3 Goldmire Bridge; 4 Ancient Den; 4 Seat of the Synod; 2 Vault of Whispers; 1 Great Furnace.
- 9 bridges: 2 Razortide Bridge; 1 Drossforge Bridge; 4 Rustvale Bridge; 2 Goldmire Bridge; 4 Ancient Den; 4 Seat of the Synod; 2 Vault of Whispers.
- 10 bridges: 2 Razortide Bridge; 1 Drossforge Bridge; 4 Rustvale Bridge; 3 Goldmire Bridge; 3 Ancient Den; 4 Seat of the Synod; 2 Vault of Whispers.
- 11 bridges: 2 Razortide Bridge; 2 Drossforge Bridge; 4 Rustvale Bridge; 3 Goldmire Bridge; 3 Ancient Den; 4 Seat of the Synod; 1 Vault of Whispers.
- 12 bridges: 2 Razortide Bridge; 2 Drossforge Bridge; 4 Rustvale Bridge; 4 Goldmire Bridge; 3 Ancient Den; 4 Seat of the Synod.

### Negro temprano

- 6 bridges: 1 Mistvault Bridge; 4 Drossforge Bridge; 1 Goldmire Bridge; 4 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 1 Great Furnace.
- 7 bridges: 1 Mistvault Bridge; 4 Drossforge Bridge; 2 Goldmire Bridge; 3 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 1 Great Furnace.
- 8 bridges: 1 Mistvault Bridge; 4 Drossforge Bridge; 3 Goldmire Bridge; 2 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 1 Great Furnace.
- 9 bridges: 1 Razortide Bridge; 1 Mistvault Bridge; 4 Drossforge Bridge; 3 Goldmire Bridge; 1 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 1 Great Furnace.
- 10 bridges: 2 Razortide Bridge; 4 Drossforge Bridge; 4 Goldmire Bridge; 4 Seat of the Synod; 4 Vault of Whispers; 1 Great Furnace.
- 11 bridges: 1 Razortide Bridge; 1 Mistvault Bridge; 4 Drossforge Bridge; 2 Rustvale Bridge; 3 Goldmire Bridge; 4 Seat of the Synod; 4 Vault of Whispers.
- 12 bridges: 2 Mistvault Bridge; 4 Drossforge Bridge; 2 Rustvale Bridge; 4 Goldmire Bridge; 4 Seat of the Synod; 3 Vault of Whispers.

### Rojo temprano

- 6 bridges: 1 Drossforge Bridge; 4 Rustvale Bridge; 1 Silverbluff Bridge; 1 Ancient Den; 4 Seat of the Synod; 4 Vault of Whispers; 4 Great Furnace.
- 7 bridges: 2 Drossforge Bridge; 4 Rustvale Bridge; 1 Silverbluff Bridge; 1 Ancient Den; 4 Seat of the Synod; 3 Vault of Whispers; 4 Great Furnace.
- 8 bridges: 3 Drossforge Bridge; 4 Rustvale Bridge; 1 Silverbluff Bridge; 1 Ancient Den; 4 Seat of the Synod; 2 Vault of Whispers; 4 Great Furnace.
- 9 bridges: 1 Razortide Bridge; 4 Drossforge Bridge; 4 Rustvale Bridge; 4 Seat of the Synod; 2 Vault of Whispers; 4 Great Furnace.
- 10 bridges: 1 Razortide Bridge; 4 Drossforge Bridge; 4 Rustvale Bridge; 1 Silverbluff Bridge; 4 Seat of the Synod; 2 Vault of Whispers; 3 Great Furnace.
- 11 bridges: 1 Razortide Bridge; 4 Drossforge Bridge; 4 Rustvale Bridge; 1 Goldmire Bridge; 1 Silverbluff Bridge; 4 Seat of the Synod; 1 Vault of Whispers; 3 Great Furnace.
- 12 bridges: 4 Drossforge Bridge; 4 Rustvale Bridge; 2 Goldmire Bridge; 2 Silverbluff Bridge; 4 Seat of the Synod; 3 Great Furnace.

## Alcance y próximo paso

Optimizar qué bridges y tierras enderezadas forman la base de 6/13; conservar 7 bridges como sensibilidad. Cruzar con el piloto condicional de Citadel y hate y ampliar la validación. La cantidad elegida puede revisarse si una composición mejor o una política de juego distinta cambia el resultado.

Las tasas de mulligan del modelo anterior no se pueden mezclar sin más con las curvas actuales: ahora existen scry, robos adicionales y una política de fondo con colores. La exigencia de dos tierras y la distinción OTP/OTD sí se mantienen.

Esta simulación no termina de validar 19 frente a 20 con todo el motor, porque se fija 19 para aislar el ratio. Tampoco mide la resistencia de bridges/Citadel ante destrucción o exilio. La decisión es de desarrollo sin interacción. El resultado está condicionado a la lista candidata del mismo jugador y torneo; la exportación original de Goldfish sigue pendiente de contraste.

Fuentes de reglas: [Boulder, reproducción del texto](https://mtg.wtf/card/hob/173/Giants-Boulder), [Cryogen, reproducción del texto](https://mtg.wtf/card/eoe/52/Cryogen-Relic), [Familiar, notas oficiales MH3](https://magic.wizards.com/en/news/feature/modern-horizons-3-release-notes), [Utrom, notas oficiales TMT](https://media.wizards.com/2026/downloads/TMT_Release_Notes_eM8Yplm3UV/u17aHk8iV1_EN_MTGTMT_ReleaseNotes_20251001.pdf).

## Reproducir

```sh
python3 -m unittest discover -s tests -v
python3 -m src.color_bridge_study --trials 2000
python3 -m src.color_bridge_study --trials 10000 --seed 2026102902 --workers 4 --output results/color_bridges
python3 scripts/write_color_bridge_report.py
python3 scripts/build_report.py
```

Semillas, conteos, resultados por celda, trazas y hashes están en results.json. Aumentar --trials cambia la precisión, no elimina el sesgo de la política ni amplía el universo de bases probadas.
