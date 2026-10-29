# Referencia de Hypergeomancer y adaptación a cuatro colores

Fecha: 2026-10-29. Versión 2: incorpora la transcripción parcial aportada en `message.txt`. Aplicación: diseño del estudio; no se reprodujeron los resultados del autor ni se ejecutó nuestro motor de turnos.

## Fuentes y alcance de la revisión

- [Video solicitado: I Simulated 5 Million Games to Solve Affinity's Manabase](https://www.youtube.com/watch?v=tyQ-Yh1yfRA), Hypergeomancer, publicado el 2026-07-07.
- [Transcripción parcial aportada por el jugador](message.txt): fuente principal de esta actualización. Se conserva sin modificar.
- [Resumen del propio autor y sus aclaraciones metodológicas en Reddit](https://www.reddit.com/r/Pauper/comments/1uq9r58/i_simulated_5_million_games_to_solve_affinitys/).
- [Deck tech anterior del mismo autor](https://www.reddit.com/r/Pauper/comments/1uh9rwe/grixis_affinity_deck_tech_my_current/), como contexto de sus elecciones y exigencias de azul.

Ahora se dispone de una transcripción parcial aportada por el jugador, además de la descripción del video y las explicaciones públicas del autor. No se auditó el código ni se contrastaron los gráficos fotograma a fotograma. Tratar posibles errores de transcripción como incertidumbre, no como errores comprobados del autor.

Las marcas de tiempo mencionadas abajo proceden de `message.txt` y permiten ubicar las premisas en el video; el texto es incompleto y contiene términos mal reconocidos.

## Lo que el autor reporta

El autor describe una simulación Python de turnos 1–5 con mulligans y decisiones heurísticas. La transcripción aclara la escala: 40.000 partidas para comparar cantidades de tierras y 4.920.000 para distribuir las 19 tierras, total 4.960.000. El segundo barrido tiene 246 bases × 10.000 partidas por base y modo × dos modos, play/draw. No son cinco millones por composición.

El origen de 246 queda aclarado en 7:15: tres bridges —Drossforge, Mistvault y Silverbluff— y tres monocolor —Vault, Seat y Furnace—, cada una de 0 a 4 y sumando 19. El coeficiente de `x^19` en `(1+x+x²+x³+x⁴)^6` es exactamente 246. Es un universo distinto del nuestro: seis bridges W/U/B/R, cuatro monocolor y Citadel, con 19/20 tierras y restricciones de bridges.

Su idea central es definir qué se optimiza antes de elegir una base: velocidad, consistencia de colores, desarrollo de tierras y equilibrio pueden favorecer listas distintas. En su Grixis, reporta que la tierra 20 mejora los land drops, pero que 19 resulta mejor en su evaluación conjunta; también identifica 10–11 bridges como una zona de buen equilibrio. Son resultados de su lista, modelo y prioridades, no leyes generales sobre Affinity. [Resumen del autor](https://www.reddit.com/r/Pauper/comments/1uq9r58/i_simulated_5_million_games_to_solve_affinitys/).

En sus respuestas, el autor aclara que:

- Su fallo de mulligan consiste en no obtener al menos dos tierras en cuatro intentos consecutivos y lo clasifica como una pérdida de partida en su modelo.
- Las definiciones de screw/flood son aproximaciones basadas en cantidades de tierras por turno, y no una medida definitiva de funcionalidad.
- Las tierras giradas pueden retrasar hechizos de robo: su efecto no se limita al maná disponible en ese turno, porque cambia las cartas que se llegan a ver después.
- Algunos parámetros y decisiones de su simulador fueron ajustados con su experiencia personal.
- En el momento de esas respuestas no publicaba el código del proyecto.

La descripción del video también identifica el uso de aleatoriedad común entre comparaciones. Debemos implementar y comprobar nuestro propio emparejamiento, no asumir que citar esa técnica demuestra que las diferencias estén bien estimadas. [Video y descripción](https://www.youtube.com/watch?v=tyQ-Yh1yfRA), [aclaraciones del autor](https://www.reddit.com/r/Pauper/comments/1uq9r58/i_simulated_5_million_games_to_solve_affinitys/).

## Qué trasladamos y qué debemos volver a medir

| Premisa o resultado verificable | Aplicación en nuestro estudio |
| --- | --- |
| Definir para qué se optimiza | Mantener rapidez, solidez, cartas conservadas y desarrollo como indicadores separados; mostrar alternativas en lugar de una nota única sin pesos acordados. |
| La base cambia el motor de robo | Pagar realmente Cryogen Relic, Thoughtcast y Bargain; no sustituir el juego por «mirar las primeras N cartas». Incluir scry y Glint Hawk cuando corresponda. |
| 10–11 bridges en su Grixis | Hipótesis central para contrastar, no un filtro que elimine 9, 12, 13 o 14. Nuestra búsqueda conserva todas las distribuciones entre 9–14. |
| 19 frente a 20 tierras | Repetir el contraste con Boulder, demanda de blanco y cada corte de hechizo explícito. El piloto de aperturas ya muestra menos mulligans obligatorios con 20; aún no demuestra cuál funciona mejor al jugar. |
| Mulligans heurísticos | Aplicar las dos tierras desde la primera mano. Informar tamaño de mano y fallos de política, sin convertirlos automáticamente en derrotas. Comparar políticas para detectar conclusiones que dependan de un keep concreto. |
| Criterios de screw/flood aproximados | Registrar bloqueos concretos: falta de color, maná total, entrada girada, artefactos o tierra disponible. Si usamos umbrales de cantidad de tierras, etiquetarlos como tales. |
| Simulaciones emparejadas | Compartir azar de forma reproducible y conservar distribución marginal correcta; usar incertidumbre de diferencias por partida, no solo intervalos separados de cada porcentaje. |
| Heurísticas ajustadas a experiencia | Documentar nuestras prioridades y comprobar sensibilidad. No tratarlas como un piloto perfecto ni como decisiones independientes del matchup. |

## Por qué el cuarto color y Boulder cambian el problema

Lo siguiente es nuestra interpretación para diseñar el experimento, no una afirmación atribuida al autor:

1. **Los colores no tienen la misma demanda temporal.** Azul habilita Relic/Thoughtcast/Monitor; negro habilita Familiar/Bargain/Fountain; blanco habilita Hawk/Dispatch; rojo habilita Blast/Munitions. Hay que medir los costes concretos y los recursos que quedan después de preparar la mesa.
2. **Boulder puede ocultar fragilidad.** Una base puede tener acceso individual a W/U/B/R mediante un único filtro y perderlo al quitar Boulder. Separar fuentes naturales, acceso efectivo y dependencia del filtro.
3. **Más bridges puede mejorar colores y empeorar el arranque de Boulder.** Con 19 tierras, 9–14 bridges dejan 10–5 fuentes enderezadas; con 20, dejan 11–6. El efecto sobre robos y afinidad requiere simular los turnos.
4. **Citadel tiene un papel propio.** Aporta un artefacto enderezado indestructible para arrancar Boulder, a cambio de no aportar W/U/B/R naturalmente. La cantidad óptima puede depender de cuántos filtros haya y de qué colores se necesiten pronto.
5. **La solidez añade otro objetivo.** Destrucción y exilio requieren escenarios separados. Un resultado de consistencia propia no sustituye medir recuperación después de perder una fuente o el filtro.

## Comprobación crítica: 19 tierras y acceso a colores

El autor reporta mejor acceso a colores con 19 en su modelo y ofrece una explicación relacionada con la composición y los keeps. Ese patrón no debe adoptarse como teorema: cambiar de 19 a 20 también puede cambiar qué tierra entra, qué hechizo sale y qué manos se conservan. Hace falta aislar esos efectos.

Controles previstos:

1. Mantener la misma política de mulligan y declarar la tierra agregada y la carta retirada.
2. Comparar el acceso sobre todos los intentos, incluyendo fallos al piso, y separadamente sobre manos conservadas.
3. Desglosar por tamaño de mano y cantidad de tierras conservadas. Una base puede parecer mejor porque su política seleccionó manos diferentes.
4. Contrastar sin mulligan como control analítico; luego incorporar el mulligan real y el motor de robo.
5. Medir velocidad y solidez sin imponer una clasificación global hasta que haya prioridades explícitas.

## Cambios concretos incorporados al plan

- Dominio activo W/U/B/R: 19/20 tierras, 9–14 bridges, 0–4 Citadel y ninguna básica.
- Rango principal 9–12; rango exploratorio 13–14. Es una propuesta de organización del cómputo.
- Comparar hipótesis 10–11 con cantidades vecinas, sin asumir el mismo óptimo que Grixis.
- Mantener cartas conservadas y fallos de política en el informe; no presentar un fallo modelado como una derrota observada.
- Conservar T1–T6 para nuestra evaluación, aunque el autor describe T1–T5: necesitamos también cubrir cinco robos naturales al salir primero.
- Evaluar el acceso a hechizos y el efecto del cuarto color, no solo completar cuatro colores por separado.
- Eliminar básicas y su módulo de Wildfire a pedido del jugador.

Todavía no contamos con los pesos y todos los indicadores que, según el texto, se muestran en pantalla. La transcripción permite analizar la arquitectura y los criterios descritos, pero no reproducir sus puntuaciones exactas.

## Lo que sí copiaría para simplificar nuestro trabajo

| Método descrito en la transcripción | Uso concreto aquí |
| --- | --- |
| Goldfish primero, sin oponente (1:07) | Construir y validar un motor de desarrollo propio; añadir hate después como escenarios separados. Reduce mucho el estado y los supuestos iniciales. |
| Un mazo de referencia fijo por barrido (1:07 y 3:08) | Para cada par tierras/Boulder fijar los demás hechizos y los reemplazos. Reutilizar las mismas reglas y métricas para todas las distribuciones. |
| Enumerar acciones legales y elegir por una heurística (2:04) | Simular pagos, tierra, robo, scry, afinidad y devoluciones; elegir mediante prioridades visibles y deterministas, sin intentar resolver Magic ni jugar con información futura. |
| Revisar trazas (2:43) | Inspeccionar un conjunto pequeño de partidas y convertir errores encontrados en pruebas generales de reglas. Evitar parches que memoricen una mano o favorezcan una lista. |
| Medir muchos indicadores en la misma partida (2:43–3:08) | Una corrida produce colores, land drops, artefactos, robos y bloqueos. Agregar una métrica derivable de la traza no requiere simular otra partida. |
| Reutilizar semillas (3:08) | Emparejar intentos, mulligans y permutaciones; estimar la incertidumbre de la diferencia por partida. Las cartas vistas pueden diferir legítimamente por scry, robos o composición. |
| Varios perfiles sobre la misma tabla (7:40–8:51) | Calcular después perfiles de rapidez, colores y solidez a partir de resultados almacenados; cambiar pesos no vuelve a ejecutar el juego. |
| Millones como presupuesto total, no por base (3:44) | Escalar muestras de candidatos gradualmente. No trasladar 20.000 partidas por base a nuestros 5,4 millones de bases. |

No es necesario implementar combate, daño letal, un rival completo ni respuestas para la primera versión. Sí es necesario modelar las interacciones propias que cambian el maná, la mano y la biblioteca. Los disparos que solo afecten al rival pueden omitirse en goldfish si no modifican nuestros recursos; documentar esa abstracción. Los objetivos exigidos para lanzar o activar no se inventan.

En las mediciones de fin de turno, distinguir falta de color de maná ya gastado. Registrar también cuándo se pudo pagar un objetivo y lo que efectivamente se lanzó; no castigar una base por haber utilizado correctamente sus fuentes.

## Simplificación práctica propuesta para cuatro colores

Nuestro dominio analítico sigue incluyendo las 5.417.403 bases. Para el Monte Carlo, proponer una selección estratificada:

1. Separar por 19/20 tierras, 9–14 bridges, 0–4 Citadel y 3/4 Boulder: **120 perfiles estructurales**. El control con 2 Boulder amplía a 180; el catálogo analítico 0–4 ya tiene 300 perfiles. Cada perfil contiene muchas distribuciones de colores, no una base equivalente para jugar.
2. Dentro de cada perfil, evaluar rápidamente las distribuciones con indicadores analíticos de fuentes y colores. Conservar varias alternativas que prioricen azul temprano, blanco temprano o equilibrio, más muestras de control no seleccionadas. Esos cálculos de cartas vistas no sustituyen el tiempo de acceso real.
3. Como primera asignación de cómputo, llevar unas 2–4 distribuciones representativas por perfil al motor. Esto da un orden de 240–480 candidatas, cercano a la escala del video. La cantidad final depende de las alternativas no dominadas y del benchmark, no de un corte ciego a tres listas.
4. Refinar alrededor de las mejores encontradas mediante intercambios de una o dos tierras y nuevas muestras. Revisar también perfiles menos favorecidos por el filtro, para medir el sesgo de selección.
5. Confirmar con nuevas semillas. Este procedimiento explora todo el dominio analíticamente y prioriza la simulación; no certifica que ninguna base fuera de los candidatos pueda superarlos en el motor.

La gran reducción de tiempo viene de seleccionar dónde invertir simulaciones de juego, no de confundir distribuciones de colores distintas ni de eliminar 13–14 bridges de antemano.

### Ejemplo de presupuesto total, todavía no ejecutado

| Fase | Bases o celdas de base/política | Partidas por modo | Play + draw | Total de partidas |
| --- | ---: | ---: | ---: | ---: |
| Validación de turnos | 12 | 2.000 | 2 | 48.000 |
| Exploración amplia ilustrativa | 360 | 2.000 | 2 | 1.440.000 |
| Refinamiento | 60 | 10.000 | 2 | 1.200.000 |
| Confirmación independiente | 20 | 50.000 | 2 | 2.000.000 |
| Total ilustrativo | | | | 4.688.000 |

Este ejemplo cubre consistencia propia y una política principal por fila. Políticas adicionales y hate consumen presupuesto aparte o requieren redistribuirlo. Las 56.000 aperturas ya ejecutadas no son partidas del futuro motor. Una corrida total cercana a 5M no da precisión de 5M a cada base; en la confirmación del ejemplo son 50.000 por modo. No extrapolar las dos horas del autor a otra máquina o a nuestras reglas más complejas sin benchmark.

## Criterios que no copiaría literalmente

### Área de radar como clasificación

En 8:06 se propone elegir según el área del polígono de indicadores normalizados. El área depende del orden de los ejes, además de los valores. Para ejes equiespaciados, `A = sin(2π/n)/2 × suma(r_i × r_(i+1))`. Por ejemplo, los mismos cuatro valores ordenados como `(100, 100, 10, 10)` dan 6.050 unidades de área; como `(100, 10, 100, 10)` dan 2.000. Reordenar las columnas podría cambiar qué base gana.

Usar radar para visualizar, no como criterio principal. Si se desean puntuaciones, usar pesos y escalas documentados, con indicadores agrupados por concepto y análisis de sensibilidad. Evitar que cinco mediciones correlacionadas del mismo fenómeno cuenten como cinco prioridades independientes.

### Votación de top 25 y diferencias de puntuación

El propio texto de 10:04 describe una ganadora por votación que se deteriora mucho en colores. Contar apariciones en top 25 depende del corte elegido y de cuántos indicadores correlacionados se incluyan. Las diferencias de 48 o 17 puntos mencionadas después tampoco son, por sí solas, intervalos de confianza ni evidencia de diferencia práctica. Mantener una frontera de alternativas y verificar diferencias en métricas interpretables.

### Descartar los ceros y unos de la distribución inicial

En 5:50 el texto se concentra en la diferencia de 0,81 puntos de manos con exactamente dos tierras porque cero/una se mulliganean. El número es coherente, pero esas manos rechazadas también cuestan cartas y oportunidades:

| Tierras | P(exactamente dos en siete) | P(cero o una en siete) |
| ---: | ---: | ---: |
| 19 | 33,1809% | 27,9418% |
| 20 | 32,3716% | 24,7047% |

La diferencia de 0,8093 pp de exactamente dos no resume todo el efecto de pasar a 20. Bajo nuestra regla, también hay 3,2372 pp menos de aperturas que exigen mulligan. Eso no demuestra que 20 gane en juego; demuestra que hay que conservar ambos indicadores y el coste del hechizo retirado. La distribución inicial tampoco prueba por sí sola que 19 sea mejor al ejecutar robos y jugadas.

## Inconsistencias que requieren cautela en la transcripción

- En 7:15 llama enderezados a los bridges: tratarlos según las reglas reales, entrando girados.
- La lista balanceada de 10:42, tal como está escrita, tiene 4 Drossforge + 4 Mistvault + 4 Silverbluff = **12 bridges**; la agresiva tiene 10 y la midrange 11. Por eso el cierre «10–11 independientemente del criterio» no coincide con todas las cantidades transcritas. Verificar contra el gráfico antes de atribuirle una conclusión universal al autor.
- Se mencionan 11 indicadores y luego 12, con parte del contenido solo en pantalla. No inventar el indicador faltante ni los pesos.
- El texto fija los hechizos, pero cambiar entre 19/20 tierras o cantidades de Boulder en 60 cartas exige declarar al menos un reemplazo. Mantener el resto fijo dentro de cada barrido, no afirmar que toda la lista permanece idéntica.
- «Promedio de partidas válidas» necesita denominador definido. Aquí se informan todos los intentos, incluidos fallos de política, y también los resultados condicionados cuando sirvan.

Estas observaciones sirven para diseñar un estudio más claro; no sustituyen una auditoría del código o del video original.
