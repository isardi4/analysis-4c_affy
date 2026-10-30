# Universo activo: 6–12 bridges, sin básicas

19/20 tierras, 6–12 bridges totales, ninguna básica y 0–4 copias de cada tierra del catálogo W/U/B/R, incluyendo Citadel. El resto son tierras artefacto enderezadas. Boulder se cruza en cantidades 3/4, con reemplazos explícitos para mantener 60 cartas.

Todas las cantidades del rango activo se incluyen sin anticipar cuál será mejor.

| Tierras | Bridges | Enderezadas | Bases distintas |
| ---: | ---: | ---: | ---: |
| 19 | 6 | 13 | 108,630 |
| 19 | 7 | 12 | 213,120 |
| 19 | 8 | 11 | 347,115 |
| 19 | 9 | 10 | 474,726 |
| 19 | 10 | 9 | 549,690 |
| 19 | 11 | 8 | 539,520 |
| 19 | 12 | 7 | 446,505 |
| 20 | 6 | 14 | 78,810 |
| 20 | 7 | 13 | 169,830 |
| 20 | 8 | 12 | 304,320 |
| 20 | 9 | 11 | 454,790 |
| 20 | 10 | 10 | 573,786 |
| 20 | 11 | 9 | 615,390 |
| 20 | 12 | 8 | 560,320 |

## Totales por rango

| Tierras | 6–12 (activo) | Total |
| ---: | ---: | ---: |
| 19 | 2,679,306 | 2,679,306 |
| 20 | 2,757,246 | 2,757,246 |

Total activo **wubr_core: 5,436,552 bases**. El conteo anterior de 32.205.701 incluía básicas y cantidades de bridges excluidas ahora; ya no es el alcance activo.

## Qué se evaluó

Conteo exhaustivo y controles exactos de aperturas por perfiles con multiplicidad: menos de dos tierras en siete, Boulder en siete y al menos dos tierras + Boulder + tierra enderezada en siete. Para estas métricas la partición representa exactamente todas las bases del dominio.

No se simularon aquí turnos, acceso W/U/B/R, scry, robos adicionales, mulligans estratégicos ni hate. Bases con igual total de bridges pueden ser distintas en esos resultados. No se añadieron partidas Monte Carlo.

El generador aplica el límite de bridges durante la generación; no materializa primero bases excluidas. Se contrastó contra fuerza bruta en dominios pequeños.

## Alcance y continuación

- Seis bridges W/U/B/R, Ancient Den, Seat of the Synod, Vault of Whispers, Great Furnace y Darksteel Citadel. La extensión verde previa queda inactiva, no demostrada inferior.
- Todas las distribuciones dentro de 6–12, sin fijar cantidades de Vault/Synod/Furnace/Citadel.
- Básicas y su análisis de Cleansing Wildfire excluidos por indicación del jugador.
- El motor debe separar cantidad de bridges, identidad/colores y política de juego dentro del rango activo.
- Publicar cobertura y distinguir conteo/evaluación exacta de partidas simuladas; confirmar candidatos con nuevas semillas.
