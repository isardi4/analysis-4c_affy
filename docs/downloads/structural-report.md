# Parte 1 y 2: cantidad de tierras y coste de entrar giradas

**Modelo estructural, no recomendación final del mazo.** Solo robos naturales y tierras. Sin colores, spells, scry, robos extra, afinidad ni rival. Cada no tierra es un marcador inerte. La capa siguiente incorporará el motor real y puede cambiar decisiones provisionales.

Las probabilidades centrales son exactas por enumeración de estados. El Monte Carlo de 2.000 intentos por celda verifica la implementación; no decide entre resultados exactos.

## Mano inicial y mulligan

Ambos modos deciden el mulligan con siete cartas. OTD roba una al inicio de T1; OTP no. Conservar requiere al menos dos tierras desde la primera mano; el piso de cuatro y la selección del fondo son propuestas explícitas en la configuración. Con la misma regla, el mulligan tiene la misma distribución en OTP y OTD.

| Tierras en las siete originales | Base de 19 | Base de 20 |
| ---: | ---: | ---: |
| 0 | 5.82% | 4.83% |
| 1 | 22.12% | 19.88% |
| 2 | 33.18% | 32.37% |
| 3 | 25.41% | 26.98% |
| 4 | 10.70% | 12.39% |
| 5 | 2.47% | 3.13% |
| 6 | 0.29% | 0.40% |
| 7 | 0.01% | 0.02% |

## Parte 1: 19 contra 20, control ideal de tierras enderezadas

Este control elimina el tipo de tierra para aislar su cantidad. No propone jugar cero bridges. Lands on curve es ≥3/4/5 tierras en mesa al terminar T3/T4/T5. Screw es ≤2 en mesa al terminar T4, condicionado a haber conservado mano. Los land drops usan todos los intentos como denominador, incluidos fallos de política.

| Base | Modo | Curve T3 | Curve T4 | Curve T5 | Screw T4 entre keeps | Fallo mulligan |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 19 | OTP | 78.05% | 50.95% | 28.96% | 14.33% | 0.61% |
| 19 | OTD | 85.15% | 61.85% | 38.98% | 9.46% | 0.61% |
| 20 | OTP | 80.83% | 55.49% | 33.49% | 12.22% | 0.37% |
| 20 | OTD | 87.46% | 66.32% | 44.17% | 7.82% | 0.37% |

20 mejora indicadores de cantidad de tierras en este control. Eso no establece que sea mejor para Affinity: no hay motor de robo ni utilidad de las cartas que reemplaza. El JSON conserva también la cantidad de no tierras vistas y un proxy explícito de ≥6 tierras vistas a T5; no llamarlo derrota por flood.

## Parte 2: bridges frente a tierras artefacto enderezadas

Se mantienen ambos totales como control, para no cerrar 19/20 por adelantado. Las dos políticas son priorizar siempre enderezadas, o abrir con bridge T1 y después priorizar enderezadas. No usan información futura ni colores. La selección del fondo es común y prefiere conservar enderezadas.

Capacidad es el maná disponible tras jugar tierra y antes de spells. Una tierra que acaba de entrar girada cuenta como tierra en mesa pero no como maná utilizable en ese turno. No es maná gastado ni desperdiciado.

| Tierras | Bridges | Enderezadas | Modo | Política | ≥1 maná T1 | ≥2 manás T2 | ≥3 manás T3 | Capacidad acumulada media T1–T3 |
| ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| 19 | 6 | 13 | OTP | untapped_first | 94.59% | 73.35% | 46.42% | 5.125 |
| 19 | 6 | 13 | OTP | bridge_t1_then_untapped | 36.97% | 95.77% | 65.03% | 4.959 |
| 19 | 6 | 13 | OTD | untapped_first | 95.77% | 78.53% | 53.34% | 5.258 |
| 19 | 6 | 13 | OTD | bridge_t1_then_untapped | 32.84% | 96.68% | 73.71% | 5.014 |
| 19 | 7 | 12 | OTP | untapped_first | 92.36% | 67.55% | 40.90% | 4.990 |
| 19 | 7 | 12 | OTP | bridge_t1_then_untapped | 30.14% | 93.96% | 61.12% | 4.834 |
| 19 | 7 | 12 | OTD | untapped_first | 93.96% | 73.14% | 47.22% | 5.125 |
| 19 | 7 | 12 | OTD | bridge_t1_then_untapped | 26.20% | 95.21% | 69.80% | 4.894 |
| 19 | 8 | 11 | OTP | untapped_first | 89.59% | 61.38% | 35.50% | 4.846 |
| 19 | 8 | 11 | OTP | bridge_t1_then_untapped | 24.17% | 91.62% | 56.68% | 4.706 |
| 19 | 8 | 11 | OTD | untapped_first | 91.62% | 67.20% | 41.09% | 4.981 |
| 19 | 8 | 11 | OTD | bridge_t1_then_untapped | 20.56% | 93.27% | 65.21% | 4.772 |
| 19 | 9 | 10 | OTP | untapped_first | 86.20% | 54.90% | 30.31% | 4.696 |
| 19 | 9 | 10 | OTP | bridge_t1_then_untapped | 19.00% | 88.69% | 51.72% | 4.576 |
| 19 | 9 | 10 | OTD | untapped_first | 88.69% | 60.75% | 35.08% | 4.827 |
| 19 | 9 | 10 | OTD | bridge_t1_then_untapped | 15.81% | 90.75% | 59.94% | 4.647 |
| 19 | 10 | 9 | OTP | untapped_first | 82.13% | 48.18% | 25.40% | 4.539 |
| 19 | 10 | 9 | OTP | bridge_t1_then_untapped | 14.59% | 85.06% | 46.27% | 4.441 |
| 19 | 10 | 9 | OTD | untapped_first | 85.06% | 53.86% | 29.30% | 4.664 |
| 19 | 10 | 9 | OTD | bridge_t1_then_untapped | 11.87% | 87.54% | 54.01% | 4.516 |
| 19 | 11 | 8 | OTP | untapped_first | 77.30% | 41.30% | 20.84% | 4.376 |
| 19 | 11 | 8 | OTP | bridge_t1_then_untapped | 10.87% | 80.64% | 40.42% | 4.301 |
| 19 | 11 | 8 | OTD | untapped_first | 80.64% | 46.60% | 23.87% | 4.493 |
| 19 | 11 | 8 | OTD | bridge_t1_then_untapped | 8.64% | 83.52% | 47.48% | 4.378 |
| 19 | 12 | 7 | OTP | untapped_first | 71.64% | 34.38% | 16.71% | 4.209 |
| 19 | 12 | 7 | OTP | bridge_t1_then_untapped | 7.80% | 75.30% | 34.24% | 4.155 |
| 19 | 12 | 7 | OTD | untapped_first | 75.30% | 39.10% | 18.90% | 4.315 |
| 19 | 12 | 7 | OTD | bridge_t1_then_untapped | 6.05% | 78.55% | 40.45% | 4.232 |
| 20 | 6 | 14 | OTP | untapped_first | 95.57% | 76.63% | 51.01% | 5.221 |
| 20 | 6 | 14 | OTP | bridge_t1_then_untapped | 38.47% | 96.64% | 69.09% | 5.031 |
| 20 | 6 | 14 | OTD | untapped_first | 96.64% | 81.63% | 58.21% | 5.354 |
| 20 | 6 | 14 | OTD | bridge_t1_then_untapped | 34.16% | 97.44% | 77.46% | 5.080 |
| 20 | 7 | 13 | OTP | untapped_first | 93.67% | 71.36% | 45.59% | 5.095 |
| 20 | 7 | 13 | OTP | bridge_t1_then_untapped | 31.71% | 95.13% | 65.53% | 4.913 |
| 20 | 7 | 13 | OTD | untapped_first | 95.13% | 76.85% | 52.33% | 5.232 |
| 20 | 7 | 13 | OTD | bridge_t1_then_untapped | 27.57% | 96.26% | 74.01% | 4.967 |
| 20 | 8 | 12 | OTP | untapped_first | 91.31% | 65.72% | 40.21% | 4.961 |
| 20 | 8 | 12 | OTP | bridge_t1_then_untapped | 25.78% | 93.19% | 61.46% | 4.793 |
| 20 | 8 | 12 | OTD | untapped_first | 93.19% | 71.53% | 46.35% | 5.100 |
| 20 | 8 | 12 | OTD | bridge_t1_then_untapped | 21.93% | 94.68% | 69.93% | 4.854 |
| 20 | 9 | 11 | OTP | untapped_first | 88.42% | 59.73% | 34.94% | 4.820 |
| 20 | 9 | 11 | OTP | bridge_t1_then_untapped | 20.62% | 90.75% | 56.88% | 4.671 |
| 20 | 9 | 11 | OTD | untapped_first | 90.75% | 65.69% | 40.37% | 4.957 |
| 20 | 9 | 11 | OTD | bridge_t1_then_untapped | 17.16% | 92.63% | 65.19% | 4.739 |
| 20 | 10 | 10 | OTP | untapped_first | 84.94% | 53.44% | 29.88% | 4.671 |
| 20 | 10 | 10 | OTP | bridge_t1_then_untapped | 16.17% | 87.71% | 51.81% | 4.546 |
| 20 | 10 | 10 | OTD | untapped_first | 87.71% | 59.37% | 34.50% | 4.805 |
| 20 | 10 | 10 | OTD | bridge_t1_then_untapped | 13.15% | 90.01% | 59.81% | 4.618 |
| 20 | 11 | 9 | OTP | untapped_first | 80.82% | 46.91% | 25.08% | 4.517 |
| 20 | 11 | 9 | OTP | bridge_t1_then_untapped | 12.38% | 84.01% | 46.27% | 4.415 |
| 20 | 11 | 9 | OTD | untapped_first | 84.01% | 52.62% | 28.86% | 4.644 |
| 20 | 11 | 9 | OTD | bridge_t1_then_untapped | 9.84% | 86.71% | 53.79% | 4.492 |
| 20 | 12 | 8 | OTP | untapped_first | 75.96% | 40.23% | 20.62% | 4.357 |
| 20 | 12 | 8 | OTP | bridge_t1_then_untapped | 9.20% | 79.53% | 40.36% | 4.280 |
| 20 | 12 | 8 | OTD | untapped_first | 79.53% | 45.52% | 23.55% | 4.475 |
| 20 | 12 | 8 | OTD | bridge_t1_then_untapped | 7.14% | 82.62% | 47.21% | 4.359 |

## Lectura correcta

- Esta etapa cuantifica el coste de velocidad de 6–12 bridges. Al omitir fixing y resiliencia, entrar girado pierde sus compensaciones; no se puede descubrir un equilibrio interior completo con esta capa sola.
- Las políticas pueden repartir capacidad de manera distinta entre T1 y T2. Más capacidad en un turno no prueba que se lanzaran más hechizos.
- Una elección de 19/20 y ratio queda provisional hasta añadir colores, Boulder y robos. No trasladar automáticamente el resultado Grixis del video.
- All four colours by T3 y Needed colours met quedan para la etapa de composición y spells. No hay resultados simulados de esos indicadores aquí.
- Los CSV y JSON separan OTP/OTD, mantienen denominadores y guardan trazas. Los fallos del mulligan no se excluyen silenciosamente.

Controles de depuración Monte Carlo: 2520/2520 dentro de seis errores estándar + 1/N. No es una banda del 95% ni una selección de ganadores.
