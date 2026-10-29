# Piloto 01: manos iniciales y mulligans

Este piloto valida aperturas y mulligans. No simula turnos, scry, robos de hechizos, filtrado operativo ni hate; no determina todavía la mejor base de maná.

Semilla: 20261029. 28 celdas de 2,000 intentos: 56,000 aperturas completas. Tiempo de cálculo: 5.80 s. No se duplica play/draw porque todavía no hay turnos.

Lista de referencia candidata del mismo jugador/torneo; la exportación original de Goldfish sigue sin contrastar. Ver procedencia en `data/reference_deck.json`.

## Regla del jugador y políticas de control

Toda mano conservada, incluida la primera de siete y la mano final después de poner cartas al fondo, debe tener al menos dos tierras. Boulder no cuenta como tierra.

- `min_two`: conservar cualquier mano con al menos dos tierras; control sencillo, no recomendación de keep para todo matchup.
- `seek_boulder_once`: con siete exigir también Boulder; desde seis, exigir únicamente las dos tierras. Como máximo un mulligan voluntario por falta de Boulder.
- Piso principal propuesto: cuatro cartas. Si no se logra una mano admisible al llegar al piso, se registra fallo de política; nunca se remuestrea gratis ni se excluye ese intento del denominador. También se prueba el piso de tres y dos sobre la lista original.
- Al elegir el fondo se preservan al menos dos tierras y se favorece Boulder + tierra enderezada. Es una política explícita de control; todavía no optimiza secuencias de juego.

## Controles exactos de las primeras siete

Los porcentajes siguientes son analíticos y no están condicionados a conservar la mano. «Boulder + enderezada» solo indica posibilidad de lanzarlo T1 sin interacción: no significa poder filtrar T1, ni siquiera que la mano cumpla las dos tierras mínimas.

| Composición | Tierras | Enderezadas | Bridges | Boulder | <2 tierras | Boulder | Boulder + enderezada | ≥2 tierras + Boulder + enderezada |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| original19_b4 | 19 | 9 | 10 | 4 | 27.94% | 39.95% | 26.26% | 21.20% |
| original19_b3 | 19 | 9 | 10 | 3 | 27.94% | 31.54% | 20.63% | 16.59% |
| original19_b2 | 19 | 9 | 10 | 2 | 27.94% | 22.15% | 14.41% | 11.54% |
| citadel_for_vault19_b4 | 19 | 9 | 10 | 4 | 27.94% | 39.95% | 26.26% | 21.20% |
| citadel_for_vault19_b3 | 19 | 9 | 10 | 3 | 27.94% | 31.54% | 20.63% | 16.59% |
| citadel_for_vault19_b2 | 19 | 9 | 10 | 2 | 27.94% | 22.15% | 14.41% | 11.54% |
| citadel_for_bridge19_b4 | 19 | 10 | 9 | 4 | 27.94% | 39.95% | 27.95% | 22.32% |
| citadel_for_bridge19_b3 | 19 | 10 | 9 | 3 | 27.94% | 31.54% | 21.96% | 17.47% |
| citadel_for_bridge19_b2 | 19 | 10 | 9 | 2 | 27.94% | 22.15% | 15.35% | 12.15% |
| add_citadel20_b4 | 20 | 10 | 10 | 4 | 24.70% | 39.95% | 27.95% | 23.05% |
| add_citadel20_b3 | 20 | 10 | 10 | 3 | 24.70% | 31.54% | 21.96% | 18.05% |
| add_citadel20_b2 | 20 | 10 | 10 | 2 | 24.70% | 22.15% | 15.35% | 12.56% |

## Piloto Monte Carlo

Todos los porcentajes de esta tabla usan todos los intentos de la celda, incluidos los fallos. Los datos JSON/CSV incluyen recuentos, denominadores e intervalos Wilson al 95%. Los intervalos son de proporciones individuales; no sirven por sí solos para declarar diferencias entre variantes.

| Composición | Política | Piso | Fallo de política | Boulder conservado | Boulder + enderezada conservados | Cartas medias, fallo=0 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| original19_b4 | min_two | 4 | 0.60% | 37.95% | 31.25% | 6.612 |
| original19_b4 | seek_boulder_once | 4 | 1.40% | 54.75% | 44.40% | 5.987 |
| original19_b4 | min_two | 3 | 0.15% | 38.10% | 31.40% | 6.625 |
| original19_b4 | seek_boulder_once | 3 | 0.35% | 55.10% | 44.65% | 6.018 |
| original19_b4 | min_two | 2 | 0.00% | 38.10% | 31.40% | 6.628 |
| original19_b4 | seek_boulder_once | 2 | 0.00% | 55.10% | 44.65% | 6.025 |
| original19_b3 | min_two | 4 | 0.50% | 30.00% | 24.80% | 6.592 |
| original19_b3 | seek_boulder_once | 4 | 1.45% | 44.50% | 36.55% | 5.904 |
| original19_b2 | min_two | 4 | 0.55% | 21.05% | 17.45% | 6.603 |
| original19_b2 | seek_boulder_once | 4 | 1.95% | 32.90% | 26.75% | 5.785 |
| citadel_for_vault19_b4 | min_two | 4 | 0.90% | 37.95% | 30.90% | 6.591 |
| citadel_for_vault19_b4 | seek_boulder_once | 4 | 1.95% | 55.30% | 45.35% | 5.935 |
| citadel_for_vault19_b3 | min_two | 4 | 0.70% | 30.30% | 24.85% | 6.604 |
| citadel_for_vault19_b3 | seek_boulder_once | 4 | 1.85% | 45.75% | 37.20% | 5.889 |
| citadel_for_vault19_b2 | min_two | 4 | 0.65% | 20.55% | 16.80% | 6.596 |
| citadel_for_vault19_b2 | seek_boulder_once | 4 | 2.40% | 32.80% | 27.15% | 5.750 |
| citadel_for_bridge19_b4 | min_two | 4 | 0.65% | 37.90% | 33.05% | 6.588 |
| citadel_for_bridge19_b4 | seek_boulder_once | 4 | 1.35% | 54.70% | 46.95% | 5.992 |
| citadel_for_bridge19_b3 | min_two | 4 | 0.65% | 29.45% | 25.65% | 6.580 |
| citadel_for_bridge19_b3 | seek_boulder_once | 4 | 1.70% | 43.75% | 37.70% | 5.902 |
| citadel_for_bridge19_b2 | min_two | 4 | 0.70% | 20.50% | 17.80% | 6.585 |
| citadel_for_bridge19_b2 | seek_boulder_once | 4 | 2.00% | 32.00% | 27.20% | 5.785 |
| add_citadel20_b4 | min_two | 4 | 0.50% | 38.80% | 31.85% | 6.662 |
| add_citadel20_b4 | seek_boulder_once | 4 | 0.90% | 56.45% | 46.40% | 6.066 |
| add_citadel20_b3 | min_two | 4 | 0.40% | 30.60% | 26.00% | 6.663 |
| add_citadel20_b3 | seek_boulder_once | 4 | 1.30% | 47.05% | 39.40% | 5.970 |
| add_citadel20_b2 | min_two | 4 | 0.50% | 21.10% | 17.85% | 6.645 |
| add_citadel20_b2 | seek_boulder_once | 4 | 1.45% | 33.55% | 28.40% | 5.873 |

## Cambios exactos y límites

- **original19_b4**: Sin cambios.
- **original19_b3**: -1 Giant's Boulder; +1 Nihil Spellbomb.
- **original19_b2**: -2 Giant's Boulder; +2 Nihil Spellbomb.
- **citadel_for_vault19_b4**: +1 Darksteel Citadel; -1 Vault of Whispers.
- **citadel_for_vault19_b3**: +1 Darksteel Citadel; -1 Giant's Boulder; +1 Nihil Spellbomb; -1 Vault of Whispers.
- **citadel_for_vault19_b2**: +1 Darksteel Citadel; -2 Giant's Boulder; +2 Nihil Spellbomb; -1 Vault of Whispers.
- **citadel_for_bridge19_b4**: +1 Darksteel Citadel; -1 Drossforge Bridge.
- **citadel_for_bridge19_b3**: +1 Darksteel Citadel; -1 Drossforge Bridge; -1 Giant's Boulder; +1 Nihil Spellbomb.
- **citadel_for_bridge19_b2**: +1 Darksteel Citadel; -1 Drossforge Bridge; -2 Giant's Boulder; +2 Nihil Spellbomb.
- **add_citadel20_b4**: +1 Darksteel Citadel; -1 Nihil Spellbomb.
- **add_citadel20_b3**: +1 Darksteel Citadel; -1 Giant's Boulder.
- **add_citadel20_b2**: +1 Darksteel Citadel; -2 Giant's Boulder; +1 Nihil Spellbomb.

Controles Monte Carlo frente a fórmulas exactas: 168/168 dentro de la tolerancia predefinida de depuración (seis errores estándar + 1/N). No es una banda de confianza al 95% ni prueba de precisión fina.

Se conserva la distribución completa de cartas finales y una muestra de trazas. La biblioteca conserva todas las cartas y el orden del fondo. La misma semilla por intento comparte azar entre celdas, pero aquí no se calculan intervalos de diferencias emparejadas.

Citadel se prueba reemplazando Vault, reemplazando Drossforge y como tierra 20. Las comparaciones mezclan velocidad potencial y cambios de colores; todavía no se evalúa cuál funciona mejor durante la partida. La resistencia de indestructible frente a destrucción es una propiedad de las cartas, no un resultado simulado en esta etapa.

Los reemplazos de Boulder por Spellbomb tampoco son neutrales. Este piloto puede medir manos, pero su efecto en robos, afinidad y jugadas debe evaluarse en el motor de turnos.

## Siguiente etapa

Verificar textos y legalidad del catálogo completo; implementar mesa, recursos y secuenciación T1–T6 con Boulder/scry, Cryogen, Thoughtcast, afinidad, Glint Hawk y sacrificios. Solo entonces medir el primer turno de acceso a W/U/B/R y después agregar escenarios de exilio/destrucción y recuperación.
