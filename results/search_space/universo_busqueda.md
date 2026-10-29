# Universo activo: 9–14 bridges, sin básicas

19/20 tierras, 9–14 bridges totales, ninguna básica y 0–4 copias de cada tierra del catálogo W/U/B/R, incluyendo Citadel. El resto son tierras artefacto enderezadas. Boulder se cruza en cantidades 0–4, con reemplazos explícitos para mantener 60 cartas.

Rango principal propuesto: 9–12 bridges. Rango exploratorio: 13–14, para medir su efecto en colores, velocidad y solidez. Esta división organiza el estudio; no anticipa el resultado.

| Tierras | Bridges | Enderezadas | Bases distintas |
| ---: | ---: | ---: | ---: |
| 19 | 9 | 10 | 474,726 |
| 19 | 10 | 9 | 549,690 |
| 19 | 11 | 8 | 539,520 |
| 19 | 12 | 7 | 446,505 |
| 19 | 13 | 6 | 311,910 |
| 19 | 14 | 5 | 182,226 |
| 20 | 9 | 11 | 454,790 |
| 20 | 10 | 10 | 573,786 |
| 20 | 11 | 9 | 615,390 |
| 20 | 12 | 8 | 560,320 |
| 20 | 13 | 7 | 429,930 |
| 20 | 14 | 6 | 278,610 |

## Totales por rango

| Tierras | 9–12 bridges | 13–14 bridges | Total |
| ---: | ---: | ---: | ---: |
| 19 | 2,010,441 | 494,136 | 2,504,577 |
| 20 | 2,204,286 | 708,540 | 2,912,826 |

Total activo **wubr_core: 5,417,403 bases**. El conteo anterior de 32.205.701 incluía básicas y cantidades de bridges excluidas ahora; ya no es el alcance activo.

## Qué se evaluó

Conteo exhaustivo y controles exactos de aperturas por perfiles con multiplicidad: menos de dos tierras en siete, Boulder en siete y al menos dos tierras + Boulder + tierra enderezada en siete. Para estas métricas la partición representa exactamente todas las bases del dominio.

No se simularon aquí turnos, acceso W/U/B/R, scry, robos adicionales, mulligans estratégicos ni hate. Bases con igual total de bridges pueden ser distintas en esos resultados. No se añadieron partidas Monte Carlo.

El generador aplica el límite de bridges durante la generación; no materializa primero bases excluidas. Se contrastó contra fuerza bruta en dominios pequeños.

## Alcance y continuación

- Seis bridges W/U/B/R, Ancient Den, Seat of the Synod, Vault of Whispers, Great Furnace y Darksteel Citadel. La extensión verde previa queda inactiva, no demostrada inferior.
- Todas las distribuciones dentro de 9–14, sin fijar cantidades de Vault/Synod/Furnace/Citadel.
- Básicas y su análisis de Cleansing Wildfire excluidos por indicación del jugador.
- El motor debe separar cantidad de bridges, identidad/colores y política de juego; estudiar 13–14 sin descartarlos por su entrada girada.
- Publicar cobertura y distinguir conteo/evaluación exacta de partidas simuladas; confirmar candidatos con nuevas semillas.
