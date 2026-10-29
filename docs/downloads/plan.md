# Plan de análisis de maná: 4c Affinity

Fecha: 2026-10-29. Versión: 7. Secuencia activa: primero 19/20 tierras; después ratio bridges/enderezadas; recién después composición de colores. Ya hay resultados estructurales sin spells. El motor completo y el hate siguen pendientes. No se eligió una composición final.

## 0. Orden de trabajo actualizado: partes 1 y 2 primero

El jugador pide simplificar y ordenar el análisis. Las secciones posteriores conservan la metodología de la etapa completa, pero la búsqueda de millones de bases y la selección de 120 perfiles quedan pausadas hasta revisar estas dos partes.

### Parte 1: 19 o 20 tierras

Comparar OTP y OTD por separado. Primera capa: tratar las tierras como enderezadas, para aislar cantidad y robos naturales. Es un control analítico, no una propuesta de jugar cero bridges.

Medir distribución de tierras en las siete originales (0–7), mulligans, cartas conservadas, lands on curve T3/T4/T5, screw (≤2 tierras en mesa al terminar T4), tierras/no tierras vistas y excedente como proxy declarado. Los fallos de política permanecen en denominadores de éxito; screw entre keeps usa un denominador separado.

Ambos modos deciden el mulligan sobre siete; OTD roba al comenzar T1 y OTP no. El tamaño conservado puede ser menor si hubo mulligan. Bajo una misma política de keep/fondo, la distribución de mulligan es igual entre modos. No mirar la futura octava carta para decidir el keep.

19 es una hipótesis del video, no una decisión ya demostrada para esta lista. Esta capa mide consistencia de tierras; no valora el spell retirado ni el flood real del motor de robo. La decisión queda provisional hasta validar el mazo completo.

### Parte 2: bridges frente a artefactos enderezados

Comparar ratios con 9–14 bridges para el total elegido provisionalmente. Mantener el otro total como control de sensibilidad barato: solo son 12 ratios por modo, sin enumerar millones de listas.

| Bridges | Enderezadas con 19 | Enderezadas con 20 |
| ---: | ---: | ---: |
| 9 | 10 | 11 |
| 10 | 9 | 10 |
| 11 | 8 | 9 |
| 12 | 7 | 8 |
| 13 | 6 | 7 |
| 14 | 5 | 6 |

Separar tierra en mesa de maná utilizable tras el land drop. Medir ≥1 maná T1, ≥2 T2, ≥3 T3, capacidad por turno y acumulada. Comparar controles de secuenciación: priorizar enderezadas; o abrir con bridge T1 y después priorizar enderezadas. No son un piloto estratégico definitivo.

En esta capa solo hay tierras y robos naturales. No se simulan Boulder, scry, Cryogen, Thoughtcast, afinidad ni hate: los no terrenos son marcadores inertes. Al omitir fixing y resistencia se quitan las compensaciones de los bridges; medimos el coste de velocidad, no el equilibrio final. Que menos bridges sea más rápido no demuestra que esa sea la mejor construcción.

### Parte 3: composición y validación

Después estudiar parejas de bridges, Vault/Synod/Furnace/Den/Citadel y Boulder, incorporando pagos y motor de robo. Allí se miden All four colours by T3 y Needed colours met. Revalidar cantidad y ratio: el orden por etapas organiza el trabajo, pero no prueba que los parámetros sean independientes.

### Ejecución inicial

- Configuración: `configs/structural_stages.json`; implementación: `src/structural_stages.py`.
- Distribución exacta de estados con London, mínimo de dos tierras, piso de cuatro propuesto y fondo documentado; robo OTP/OTD y entrada girada.
- 52 celdas entre ambas partes y las dos políticas. 2.000 trayectorias de control por celda: 104.000 en total, con azar compartido. No son partidas completas de Affinity.
- 22 pruebas satisfactorias; 2.184 comprobaciones Monte Carlo dentro de la tolerancia frente a resultados exactos.
- [Informe](results/structural_stages/informe.md), [CSV](results/structural_stages/metrics.csv), [JSON con parámetros y trazas](results/structural_stages/results.json).

Los porcentajes principales son analíticos; el piloto Monte Carlo valida la implementación. No fue necesaria una corrida de 5M para resolver esta capa estructural.

## 1. Objetivo y preguntas

Comparar composiciones legales de 60 cartas para entender qué ganan y pierden en velocidad, acceso a W/U/B/R, desarrollo de artefactos y dependencia de Giant's Boulder. El resultado final será un informe HTML estático versionado en GitHub, apto para GitHub Pages, con metodología, datos descargables y ejemplos de juego.

Preguntas centrales:

- ¿Qué combinación de tierras artefacto enderezadas, bridges y filtros permite ejecutar las jugadas deseadas a tiempo?
- ¿Cuándo aparece Boulder, cuándo se puede lanzar y cuándo permite pagar un hechizo que de otro modo quedaría bloqueado?
- ¿Cuánto cambia el resultado con el orden de las tierras, mulligans, scry y robos adicionales?
- ¿Qué composiciones ofrecen mejores intercambios entre velocidad, estabilidad y resistencia a interacción definida?

El análisis de consistencia no estima por sí solo el porcentaje de victorias contra otros mazos.

## 2. Lista de referencia y procedencia

Lista solicitada: [MTGGoldfish 7987749](https://www.mtggoldfish.com/deck/7987749#paper), W-U-B-R Affinity de pintofmilk, British Pauper Open, 2026-10-03.

La página identifica jugador y torneo, pero no expuso las cantidades en la vista de texto y su exportación devolvió HTTP 403. La composición siguiente fue recuperada del índice público de [MTGTop8, mismo jugador y torneo](https://www.mtgtop8.com/event?d=896355&e=91683&f=PAU). Se conserva como referencia candidata hasta contrastarla con la lista solicitada o confirmarla con el usuario. El desglose agregado del arquetipo de Goldfish no reemplaza la lista individual.

### Tierras: 19

| Carta | Copias | Colores | Entrada |
| --- | ---: | --- | --- |
| Ancient Den | 1 | W | Enderezada |
| Great Furnace | 1 | R | Enderezada |
| Seat of the Synod | 4 | U | Enderezada |
| Vault of Whispers | 3 | B | Enderezada |
| Drossforge Bridge | 3 | B/R | Girada |
| Mistvault Bridge | 2 | U/B | Girada |
| Razortide Bridge | 4 | W/U | Girada |
| Rustvale Bridge | 1 | R/W | Girada |

Son 10 bridges y 9 tierras artefacto enderezadas. Fuentes naturales nominales: W=6, U=10, B=8, R=5. Cada tierra dual se cuenta para sus dos colores en este inventario, pero solo produce un maná por activación. Estos conteos no son probabilidades ni garantizan disponibilidad en un turno.

### Resto del mazo: 41

| Carta | Copias |
| --- | ---: |
| Glint Hawk | 3 |
| Myr Enforcer | 3 |
| Refurbished Familiar | 4 |
| Utrom Monitor | 4 |
| Dispatch | 3 |
| Galvanic Blast | 4 |
| Reckoner's Bargain | 3 |
| Thoughtcast | 4 |
| Blood Fountain | 2 |
| Cryogen Relic | 4 |
| Giant's Boulder | 4 |
| Makeshift Munitions | 1 |
| Nihil Spellbomb | 2 |

Sideboard de referencia, separado de la simulación inicial: 4 Blue Elemental Blast, 3 Krark-Clan Shaman, 4 Pyroblast, 1 Tithing Blade, 2 Toxin Analysis, 1 Vandalblast.

Antes del motor: fijar textos Oracle, fecha, fuentes y legalidad de las cartas que se modelen. El [texto de Boulder reproducido por Goldfish](https://www.mtggoldfish.com/price/the-hobbit/173/giants-boulder) y las fuentes consultadas indican coste {1}, scry 2 al entrar y filtrado {1}, {T} para agregar un maná de cualquier color. Confirmar estos datos en el catálogo congelado del proyecto.

## 3. Alcance acordado y decisiones operativas

| Tema | Respuesta del jugador y alcance |
| --- | --- |
| Tierras | Comparar 19 y 20. No explorar 18 ni 21 en esta etapa. |
| Boulder | Comparar cantidades; 3 y 4 son las principales, pero no descartar menos si la combinación de tierras lo justifica. |
| Rapidez | Encontrar cuán temprano se consigue acceso a W/U/B/R; no fijar un turno arbitrario como condición de éxito. |
| Solidez | Evaluar resistencia a hate de artefactos, incluyendo Dust to Dust, Vandalblast, Masked Vandal y Gorilla Shaman. |
| Robos | Contar todos los robos, incluidos Thoughtcast y otros efectos; el objetivo es que Boulder llegue a mano y pueda utilizarse. |
| Boulder útil | La prioridad es tenerlo operativo para filtrar y habilitar hechizos, no solamente verlo o conservarlo en mano. |
| Mulligan | Toda mano conservada debe tener al menos dos tierras, incluida la primera de siete antes de hacer ningún mulligan y la mano final de cada mulligan después del fondo. Si las primeras siete tienen cero o una, mulligan obligatorio. Lo demás admite propuestas y análisis de sensibilidad. |
| Secuencia | Referencia orientativa: T1 Boulder, T2 Cryogen Relic, T3 Refurbished Familiar o Utrom Monitor. Priorizar acceso al maná; el orden real depende de la mano y del matchup. |
| Orden del trabajo | Primero sin interacción rival; después escenarios acotados de hate. |
| Cartas | Sin restricciones de presupuesto. En esta etapa, solo tierras artefacto enderezadas y bridges del catálogo W/U/B/R; no analizar básicas. |
| Amplitud de la búsqueda | Todas las distribuciones del catálogo activo con 9–14 bridges; no limitarse a cambios de una carta. Las cantidades individuales de Vault/Synod/Furnace/Citadel y de cada bridge siguen libres entre 0 y 4. |
| Recorte posterior del jugador | Excluir básicas y su análisis de Wildfire. No probar menos de 9 ni más de 14 bridges; 13–14 siguen incluidos como exploración de bases más giradas. |

Propuestas operativas para implementar sin otra ronda de preguntas:

- Horizonte inicial: T1–T6, con métricas de recuperación hasta dos turnos propios después del ataque. T6 cubre también el quinto robo natural de quien sale primero. Si quedan demasiadas partidas sin acceso al final, ampliar el horizonte antes de sacar conclusiones.
- Cantidades: 3/4 Boulder en el estudio principal, 2 como control inicial y 1/0 como diagnósticos secundarios si aportan información. Informar claramente cuáles se probaron; no excluir una cantidad por intuición.
- Políticas: mínimo dos tierras obligatorio; comparar una política de desarrollo con una que favorezca Boulder solo entre manos que cumplan ese mínimo. No asumir que hay que hacer mulligan a toda mano sin Boulder.
- Mulligan London: propuesta inicial de piso de cuatro cartas, con sensibilidad a pisos de tres y dos. Si al piso no existe mano conservable con dos tierras, registrar «sin mano admisible bajo esta política», contar el intento en el denominador y como fallo del objetivo operativo. No conservar una mano ilegal para la política, volver a muestrear gratis ni interpretar esto como una derrota según las reglas del juego. Los pisos son propuestas, no preferencias ya expresadas por el jugador.
- Todas las composiciones mantienen 60 cartas y un máximo de cuatro copias de cada carta. Los reemplazos de hechizos se declaran como parte de la composición.

Pendientes que no impiden el diseño: contrastar la lista individual original, verificar el catálogo Oracle, determinar el reparto de los 5M después del benchmark e identificar el repositorio de GitHub al preparar la publicación. Git reconoce actualmente un repositorio en un directorio superior; no asumir que esta carpeta ya tiene repositorio remoto propio.

## 4. Definiciones de acceso al maná

Separar las siguientes mediciones:

1. **Fuentes vistas:** cartas encontradas, aunque estén en mano o entren giradas.
2. **Acceso natural por color:** se puede generar al menos un maná del color en el estado evaluado sin filtros.
3. **Acceso efectivo por color:** también se permiten filtros legales y se pagan sus costes.
4. **Cobertura W/U/B/R:** cada color es accesible por separado desde el mismo estado. No implica poder producir cuatro manás de colores diferentes juntos. Un Boulder disponible puede ampliar mucho esta cobertura sin aumentar la cantidad de maná.
5. **Pago simultáneo:** se puede pagar un coste específico o una secuencia de hechizos sin reutilizar recursos gastados. WUBR simultáneo se puede informar como diagnóstico adicional; no se usará como requisito si no representa el plan del mazo.
6. **Ejecución real:** hechizos efectivamente lanzados y recursos que quedaron disponibles bajo una política de juego concreta.

Tomar un estado de referencia por turno después del robo natural y de las acciones de preparación elegidas por la política, antes de gastar recursos en las jugadas objetivo. Evaluar los pagos de diagnóstico en copias del estado; no sumar resultados de ramas incompatibles. Registrar también el estado final del turno y los hechizos realmente lanzados.

Reportar por separado salir primero (play) y robar primero (draw). La cobertura histórica «alguna vez hasta T» y la disponibilidad actual en T serán métricas diferentes: sacrificar o devolver un artefacto puede quitar acceso ya obtenido.

### Rapidez: distribución del tiempo hasta acceso

Registrar el primer turno y punto de acción en que se cumple cada objetivo: acceso natural W/U/B/R, acceso efectivo W/U/B/R, Boulder operativo y costes relevantes pagables. En el perfil inicial, «Boulder operativo» exige que esté enderezado en mesa y exista maná disponible para pagar su activación; bajarlo con la única tierra de T1 no satisface esto en ese momento.

Publicar `P(primer acceso ≤ T)` para cada turno, mediana y percentiles cuando se alcancen dentro del horizonte, y porcentaje que no llega al final. No promediar solamente las partidas exitosas: eso puede favorecer una composición rápida en pocos casos pero inconsistente. Como resumen complementario puede usarse el número esperado de turnos sin acceso dentro del horizonte, contando también los intentos sin mano admisible.

La cobertura se comprueba sobre recursos actuales, sin contar tierras giradas ni tierras en mano. La capacidad de volver a habilitarla al siguiente enderezado se informa aparte. Para poder usar los hechizos, añadir pruebas de pago con el coste vigente de afinidad y de secuencias concretas; disponer de todos los colores por separado no garantiza cantidad suficiente de maná.

### Solidez: conservar y recuperar capacidad

La solidez se informa por escenario de hate, sin asignar frecuencias de metagame inventadas ni una nota única. Sus componentes serán:

- Fuentes de maná y artefactos perdidos, pérdida de colores naturales/efectivos y de maná utilizable.
- Probabilidad de conservar cobertura W/U/B/R después del efecto, tanto sobre todos los intentos como entre los que tenían cobertura antes.
- Probabilidad de conservar o recuperar los pagos objetivo en el primer y segundo turno propio posterior.
- Turnos sin cobertura, land drops disponibles, caída de metalcraft/afinidad y dependencia de Boulder superviviente.
- Tiempo de recuperación frente a una rama emparejada sin hate; los casos sin recuperación al final se informan, no se eliminan del promedio.

Para comparar ataques en turno rival, medir inmediatamente antes/después con el estado real —incluidos giros— y también desde el siguiente turno propio después de enderezar. No confundir la falta transitoria de recursos gastados con una pérdida permanente por el ataque.

## 5. Indicadores propuestos

| Familia | Indicadores |
| --- | --- |
| Boulder | ≥1 en siete originales y mano conservada; ≥1 obtenido dentro de cinco robos; primer turno de lanzamiento y filtrado disponible; duplicados; Boulder en mano sin poder lanzarse |
| Maná | P(acceso W/U/B/R) por turno, natural y filtrado; cobertura de cuatro colores; maná total utilizable; costes concretos pagables; dependencia de filtros en el estado |
| Tierras | Distribución inicial; segundo/tercer land drop a tiempo; turnos sin tierra; exceso de tierras según umbral definido; bloqueo atribuible a entrada girada |
| Motor | Artefactos en mesa por turno; metalcraft; coste efectivo de afinidad; Thoughtcast, Familiar y Monitor pagables y lanzados; robos extra |
| Jugadas | Secuencias objetivo a tiempo; hechizos retenidos por falta de color, cantidad de maná, artefactos o requisito adicional; reserva de maná para interacción |
| Mulligan | Distribución de mulligans, cartas conservadas, funcionalidad final y beneficio de buscar Boulder frente a perder cartas |
| Rapidez | Curva de primer acceso natural/efectivo, percentiles, turnos sin acceso y porcentaje que no llega dentro del horizonte |
| Solidez | Capacidad retenida y recuperación por tipo de hate, recursos perdidos y diferencia frente a la rama sin interacción |
| Comparación | Diferencia frente a la referencia en puntos porcentuales, intervalo de incertidumbre, coste del cambio y compensaciones |

Para hechizos: informar tanto éxito sobre todas las partidas como éxito condicionado a tener la carta disponible, indicando el denominador. Los subgrupos pequeños necesitan más muestras que el total.

No llamar «efecto causal de Boulder» a comparar simplemente manos con y sin Boulder. Para medir su aporte, usar composiciones emparejadas con reemplazo explícito; las estadísticas condicionadas se identificarán como descriptivas.

## 6. Motor y políticas de juego

Implementar un simulador acotado a las interacciones relevantes para los primeros turnos, con estado de mano, biblioteca ordenada, fondo conocido, mesa, cementerio, maná y uso de tierra por turno. No hace falta construir un motor completo de Magic.

Reglas que necesitan representación real:

- Entrada girada de bridges, enderezado, land drop y pago de colores sin duplicar fuentes.
- Boulder: coste de lanzamiento, scry 2 legal con orden y fondo conservados, filtrado uno por uno y uso de giro. No es aceleración. Su habilidad de destrucción se incorporará si el horizonte/escenario la requiere.
- Afinidad y metalcraft calculadas con los artefactos actuales; quitar un artefacto modifica los costes futuros.
- Glint Hawk: requisito y devolución de artefacto; reinvertir maná para bajar Boulder u otro artefacto, scry y robos resultantes; devolución de tierras y su efecto en desarrollo.
- Cryogen Relic y Reckoner's Bargain: robos, sacrificios y disparos en el orden correcto.
- Blood Fountain y su ficha de Blood: cantidad real de artefactos, pago, descarte y robo cuando corresponda.
- Nihil Spellbomb: sacrificio y pago negro del disparo para robar; no regalar el robo.
- Turno sin robo inicial para quien sale primero y mulligan London según reglas vigentes verificadas.
- Interacción con objetivos rivales solo bajo un escenario definido; no lanzar removal a objetivos ficticios para inflar actividad.

Empezar con una política sencilla, explícita y determinista. Después comparar estrategias que prioricen desarrollo, acceso a colores o Boulder, manteniendo las reglas legales. Las políticas solo ven mano, mesa e información revelada por efectos; nunca el futuro oculto del mazo. Puede buscarse la mejor secuencia del turno usando información conocida; cualquier análisis con información perfecta debe etiquetarse como cota ideal y quedar fuera del ranking práctico.

Primero comparar composiciones bajo una política común. Luego revisar si un candidato pierde por una política inadecuada y medir sensibilidad con otras políticas. Separar ajuste de política y validación con muestras independientes.

### Mulligan y decisiones de desarrollo

La primera mano de siete se evalúa con el mismo mínimo obligatorio de dos tierras: si tiene cero o una, no se conserva. En los mulligans se evalúa la mano final después de elegir las cartas que van al fondo. La regla mínima de dos tierras no depende de tener Boulder y tampoco se satisface contando un filtro como tierra. Se muestrean y registran también las aperturas que incumplen el mínimo; no se fuerza artificialmente un reparto de siete con dos tierras.

Política de referencia propuesta: conservar manos de 2–4 tierras; para manos de 5 o más, exigir al menos una jugada de robo/selección legal que pueda ejecutarse antes de terminar T2 usando solo información visible. Comparar esta propuesta con la regla simple de conservar cualquier mano con al menos dos tierras. Registrar por separado manos con todas las tierras entrando giradas; no rechazarlas automáticamente porque bridge T1 puede ser una buena apertura.

Al elegir el fondo, conservar al menos dos tierras y priorizar colores/entrada compatibles con la mano, una vía útil de robo/selección y una amenaza cuando haya espacio. Duplicados de Boulder y tierras excedentes se evalúan por utilidad. Documentar los desempates para poder reproducir cada decisión.

La secuencia T1 Boulder → T2 Relic → T3 Familiar/Monitor es un objetivo observable, no una acción forzada. Si falta una pieza o la secuencia es impagable, la política debe elegir una alternativa legal. Comparar éxito de cada paso y de la secuencia completa, tanto sobre todas las partidas como condicionado a contar con las cartas. En el primer modelo no se gasta removal contra rivales ficticios; se mide si se podría reservar/pagar.

## 7. Diseño de composiciones

Dominio activo, acordado tras acotar el universo anterior:

- Exactamente 19 o 20 tierras.
- Entre 9 y 14 bridges totales, inclusive.
- Ninguna tierra básica. Omitir también el módulo de básicas frente a Cleansing Wildfire; la intención del jugador era protegerse de Wildfire rival, no agregarlo a nuestro mazo, pero ahora excluye ese análisis.
- Catálogo W/U/B/R: seis bridges, cuatro tierras artefacto monocolor y Darksteel Citadel, cada carta entre 0 y 4 copias.
- Sin cantidades mínimas de Vault, Synod, Furnace, Citadel ni de un bridge concreto. La distribución de colores sigue siendo una variable central.
- El resto del mazo completa 60 cartas con los reemplazos explícitos de la sección siguiente.
- Cantidades de Boulder 0–4 en el dominio analítico; priorizar 3/4 y control de 2 al validar el motor.

Las 12 composiciones del primer piloto son controles de implementación, no el universo de construcción. Las bases sin bridges, solo bridges o con 15–20 bridges ya no están dentro de la búsqueda activa. Esta es una restricción del jugador, no una conclusión estadística sobre esas bases.

### Tierras candidatas

| Grupo | Cartas |
| --- | --- |
| Artefactos monocolor enderezados | Ancient Den, Seat of the Synod, Vault of Whispers, Great Furnace. |
| Bridges | Razortide, Mistvault, Drossforge, Rustvale, Goldmire y Silverbluff Bridge. |
| Incoloro indestructible enderezado | Darksteel Citadel, 0–4 copias. |

La extensión verde previa queda inactiva para centrarnos en W/U/B/R; no se ha probado que toda fuente verde esté dominada. No presentar los resultados como óptimo sobre un catálogo mayor que el activo. Las básicas quedan excluidas por instrucción explícita. El catálogo de aperturas puede conservar metadatos de cartas fuera del alcance, pero la configuración y el generador no las usan.

Fuentes de reglas: [bridges](https://magic.wizards.com/en/news/card-preview/bridges-limited-modern-2021-05-26) y [Citadel](https://magic.wizards.com/en/news/feature/magic-2015-core-set-release-notes-2014-07-07). Verificar Oracle y legalidad actuales antes del motor completo.

### Rangos y tamaño del universo

Configuración versionada: `configs/mana_search_space.json`.

| Rango de bridges | Bases de 19 tierras | Bases de 20 tierras | Total |
| --- | ---: | ---: | ---: |
| 9–12: principal, organización propuesta | 2.010.441 | 2.204.286 | 4.214.727 |
| 13–14: exploratorio | 494.136 | 708.540 | 1.202.676 |
| 9–14: dominio completo activo | 2.504.577 | 2.912.826 | 5.417.403 |

El dominio anterior de 32.205.701 incluía básicas y cantidades de bridges ahora excluidas. El recorte conjunto reduce ese universo aproximadamente un 83,18%. Las dos bandas son disjuntas y juntas cubren todas las bases activas. Separarlas no implica afirmar que 9–12 sea mejor.

Dentro de cada cantidad de bridges se comparan todas las distribuciones legales de los seis pares y de las cinco tierras enderezadas. No confundir «10 bridges» con una base concreta. Con 19 tierras, 9–14 bridges dejan 10–5 tierras enderezadas; con 20, dejan 11–6.

### Método de búsqueda y cobertura

1. Contar exhaustivamente con programación dinámica y aplicar los límites durante la generación, sin generar primero millones de bases excluidas.
2. Calcular controles exactos por grupos cuando su equivalencia esté demostrada para la métrica concreta. No agrupar bases de colores distintos como equivalentes para los turnos.
3. Explorar el motor con estratos por cantidad de bridges, colores y Citadel; conservar 13–14 como parte del estudio.
4. Usar cotas válidas o imposibilidad para descartes certificados; si se prioriza por heurística o Monte Carlo, informarlo como exploración y comprobar muestras fuera de los candidatos elegidos.
5. Confirmar alternativas con nuevas semillas y medir diferencias emparejadas. No declarar un óptimo global si no está certificado.

Los 2.000 intentos son por celda del piloto, no una obligación de simular 2.000 partidas sobre cada una de las 5.417.403 bases antes de validar reglas. El alcance de los 5M se decidirá con el benchmark del motor de turnos y el reparto de muestras.

El informe distingue bases representadas, evaluadas analíticamente, simuladas y descartadas con justificación. Mostrar una frontera de alternativas de rapidez/solidez, sin una nota única arbitraria.

### Simplificación de la exploración inspirada en la transcripción

Se propone un protocolo práctico, todavía no ejecutado en turnos:

- Comenzar con 120 perfiles: 2 cantidades de tierras × 6 cantidades de bridges × 5 cantidades de Citadel × 2 cantidades principales de Boulder (3/4). El control con 2 Boulder amplía a 180; el dominio analítico de 0–4 Boulder ya tiene 300 perfiles. No son bases equivalentes para jugar: cada perfil contiene muchas distribuciones de colores.
- Dentro de cada perfil, calcular indicadores exactos de cartas vistas/fuentes antes de simular: por ejemplo, encontrar fuentes de azul/blanco y cobertura natural de colores. Estas métricas no incorporan aún tierras giradas, mulligans, pagos ni robos extra; no llamarlas acceso efectivo por turno.
- Conservar varias distribuciones de colores según prioridades distintas, además de muestras no seleccionadas para control. Un objetivo inicial de 2–4 candidatas por perfil lleva a unas 240–480 listas, una escala similar al barrido del video. No imponer esa cantidad si la frontera de alternativas necesita más ni declararla exhaustiva en turnos.
- Explorar vecinos de candidatos y revisar muestras de perfiles menos favorecidos. No fijar la distribución original de colores ni cerrar cantidades de tierras/Boulder antes de comprobar sus interacciones.
- Concentrar las muestras grandes en finalistas y confirmarlos con nuevas semillas. Declarar el alcance de la selección y el riesgo de perder una base que el filtro analítico no priorice.

Ejemplo de presupuesto total sin rival: 12 celdas × 2.000 partidas × play/draw para validar (48.000); 360 × 2.000 × play/draw para explorar (1.440.000); 60 × 10.000 × play/draw para refinar (1.200.000); 20 × 50.000 × play/draw para confirmar (2.000.000). Total ilustrativo: 4.688.000 partidas. Políticas adicionales y hate consumen presupuesto aparte o requieren redistribución. Es una propuesta de escala, no corridas realizadas ni promesa de tiempo de ejecución.

La simplificación copia la arquitectura del autor —goldfish acotado, heurísticas, trazas, métricas reutilizables y presupuesto total—, sin trasladar literalmente el tamaño de su universo ni asumir sus conclusiones para cuatro colores.

### Reemplazos y comparación de 19 contra 20

La referencia tiene 37 hechizos distintos de Boulder. El total de huecos para esos hechizos es `60 − tierras − Boulder`:

| Tierras | Boulder | Otros hechizos | Cambio neto respecto de los 37 originales |
| ---: | ---: | ---: | --- |
| 19 | 4 | 37 | Ninguno |
| 19 | 3 | 38 | Agregar un hechizo |
| 20 | 4 | 36 | Quitar un hechizo |
| 20 | 3 | 37 | Cambiar un Boulder por una tierra |
| 19 | 2 | 39 | Agregar dos hechizos |
| 20 | 2 | 38 | Agregar un hechizo |

Propuesta inicial de balanceo: para 20 tierras/4 Boulder, cortar una Nihil Spellbomb; para huecos libres al bajar Boulder, aumentar Nihil Spellbomb hasta cuatro, luego Myr Enforcer hasta cuatro y luego Glint Hawk hasta cuatro. En finalistas repetir con otra familia: cortar un Myr Enforcer para 20/4 y llenar huecos priorizando Myr, luego Hawk y después Spellbomb. Esto permite comparar incluso 1/0 Boulder sin cartas ficticias ni superar cuatro copias.

Estos reemplazos son propuestas metodológicas modificables, no recomendaciones de construcción ni cambios neutrales. Spellbomb, Myr y Hawk tienen efectos distintos en robos, afinidad y desarrollo. Informar cada lista completa y comprobar que una conclusión no dependa solamente de la carta usada para llenar/quitar un hueco. La comparación 19/4 contra 20/3 mantiene intactos los otros 37 hechizos y es un control especialmente interpretable.

## 7A. Segunda etapa: escenarios de hate

Primero completar y validar el estudio sin rival. Después agregar perturbaciones controladas a las mismas composiciones y políticas. Son escenarios condicionados a que el rival tenga el hate y los recursos necesarios; no probabilidades de que una partida real lo presente.

### Interacciones que deben distinguirse

| Hate | Efecto relevante | Bridges/Citadel | Tierra artefacto destructible |
| --- | --- | --- | --- |
| Dust to Dust | Exilia dos artefactos objetivo distintos; requiere ambos al lanzarlo. | Puede exiliarlas. | Puede exiliarla. |
| Vandalblast | Destruye un artefacto ajeno o todos con sobrecarga. | Indestructible evita destrucción. | Puede destruirla. |
| Masked Vandal | Puede exiliar un artefacto rival si se exilia una criatura de su cementerio al resolver. | Puede exiliarlas. | Puede exiliarla. |
| Gorilla Shaman | Destruye artefacto no criatura de valor X pagando {X}{X}{1}. | Indestructible evita destrucción. | Una tierra de valor cero cuesta un maná por activación. |

Gorilla también puede atacar Boulder, pero su valor de maná uno exige tres manás por activación; la activación no requiere girar al Shaman. No asumir que todo hate solo apunta a tierras: quitar Boulder puede cortar varios colores aunque sobrevivan bridges. Del mismo modo, Vandalblast sobrecargado puede dejar tierras indestructibles en mesa y destruir filtros, fichas y criaturas artefacto destructibles.

Verificar costes/textos en el catálogo antes de implementar cada evento. Fuentes oficiales disponibles: [Masked Vandal en notas de Kaldheim](https://magic.wizards.com/en/news/feature/kaldheim-release-notes-2021-01-22) y [Vandalblast en notas de Commander Masters](https://media.wizards.com/2023/downloads/CMM_Release_Notes/EN_MTGCMM_ReleaseNotes_20230616.pdf). Contrastar Dust to Dust y Gorilla Shaman con Oracle antes de activar sus escenarios; las reproducciones consultadas son [Dust to Dust](https://mtg.wtf/card/drk/5/Dust-to-Dust) y [Gorilla Shaman](https://mtg.wtf/card/mh2/280/Gorilla-Shaman).

Básicas y el análisis asociado a Cleansing Wildfire quedan fuera del alcance activo.

### Primer conjunto de escenarios propuesto

| Escenario | Momento y recursos condicionados |
| --- | --- |
| Sin hate | Referencia emparejada. |
| Vandalblast individual | Turno rival 2 y, por separado, 3; un maná rojo para lanzarlo. |
| Dust to Dust | Turno rival 3; {1}{W}{W} y dos objetivos legales. Si no se puede lanzar, registrar el caso sin inventar un segundo objetivo. |
| Masked Vandal | Turno rival 2 o 3, en escenarios separados; {1}{G} y una criatura en su cementerio disponible para el disparo. |
| Gorilla Shaman | Lanzado en T1 rival; hasta dos manás para activar en T2 rival y hasta tres en T3 rival. Es el escenario persistente y puede repetir ataques respetando presupuestos. |
| Vandalblast sobrecargado | Turno rival 5; {4}{R}. Representa un ataque tardío distinto del modo individual. |

En play, el T3 rival ocurre después de nuestro T3; en draw, antes de nuestro T3. Registrar el orden real y medir recuperación en turnos propios. El coste de lanzar Shaman en T1 no se reutiliza para activar ese turno; los presupuestos de turnos posteriores son supuestos explícitos de recursos del rival.

Selección de objetivos: una regla reproducible basada en información pública prioriza reducir colores efectivos, luego capacidad total de maná y después desarrollo de artefactos, con desempates fijos. También puede informarse el peor daño inmediato entre objetivos legales como prueba de estrés, etiquetado como tal. El rival no consulta nuestra mano oculta ni futuros robos.

Primera versión: medir el efecto una vez resuelto, sin respuestas nuestras, como prueba de exposición. No presentar ese resultado como juego óptimo o resultado de matchup. Segunda versión, si cambia decisiones: permitir respuestas legales visibles de la mano, como sacrificar un artefacto objetivo con Bargain o vaciar el cementerio rival con Spellbomb antes de resolver Masked Vandal. Incluir los costes, robos y la legalidad de los objetivos remanentes. El escenario persistente de Shaman se reporta separado de ataques únicos.

No sumar escenarios con el mismo peso para declarar una «solidez total». Presentar perfiles separados; ponderarlos solo si más adelante hay una distribución de matchups o preferencias explícita. Otros hates se agregarán cuando representen una mecánica o ventana diferente y se haya verificado su legalidad en Pauper.

## 8. Validación antes de escalar

### Controles exactos

Sin mulligan, scry, robos adicionales ni cambios en la biblioteca, con K Boulder en 60 cartas:

`P(≥1 en n cartas) = 1 − C(60 − K, n) / C(60, n)`.

| Copias | Primeras 7 | Primeras 12 (7 + 5) |
| ---: | ---: | ---: |
| 1 | 11,67% | 20,00% |
| 2 | 22,15% | 36,27% |
| 3 | 31,54% | 49,46% |
| 4 | 39,95% | 60,10% |

Con cuatro copias, si no hubo Boulder en las primeras siete, encontrarlo en las cinco siguientes tiene probabilidad 33,55% bajo esos mismos supuestos. Este es un denominador distinto de la probabilidad acumulada del 60,10%.

En la referencia candidata, la probabilidad de tener Boulder y al menos una de las nueve tierras enderezadas en las siete originales es 26,26%. En ausencia de interacción, permite lanzarlo T1; no implica tener maná restante para filtrar ese mismo turno.

En play, cinco robos naturales se completan en T6; en draw, en T5. Los robos de hechizos pueden completar cinco cartas robadas antes. El scry propio del primer Boulder nunca debe facilitar encontrar ese mismo primer Boulder antes de lanzarlo.

### Verificaciones del simulador

- Casos manuales de Boulder, bridges, doble uso imposible de una fuente, afinidad, sacrificio y Glint Hawk.
- Casos de mulligan: mínimo de dos tierras después del fondo, manos de alta cantidad de tierras, agotamiento al piso y denominadores sin descartar intentos fallidos.
- En el perfil inicial sin aceleración adicional, Boulder bajado con el único maná de T1 no se registra operativo T1; sí puede habilitar cobertura de cuatro colores en T2 si hay recursos disponibles. Distinguir esa cobertura de pagar cuatro manás a la vez.
- Para hate: indestructibilidad frente a destrucción/exilio, dos objetivos de Dust to Dust, coste y repetición de Gorilla, requisito de cementerio de Masked y orden play/draw.
- Biblioteca y fondo de scry/mulligan conservan las cartas y el orden legal; no se vuelve a barajar arbitrariamente.
- Semilla fija reproduce resultados y trazas.
- Con la manipulación desactivada, comparar resultados con probabilidades exactas usando tolerancia estadística predefinida.
- Revisar trazas cortas de éxitos, bloqueos y decisiones dudosas antes de aumentar el volumen.
- Las variantes de rendimiento deben coincidir con el motor de referencia en casos deterministas antes de usarse en la corrida final.

## 9. Tamaño de muestra y rendimiento

Una simulación es una partida completa hasta el horizonte acordado. Cada celda experimental identifica composición, política, play/draw y escenario del rival. Siempre publicar N por celda y por subgrupo; un total grande dividido entre muchas celdas no da precisión grande en cada una.

| Etapa | Partidas por celda | Uso | Semiancho orientativo del IC 95% máximo |
| --- | ---: | --- | ---: |
| Depuración | 2.000 | Reglas, trazas y problemas grandes | ±2,19 pp |
| Exploración | 10.000 | Primeros indicios comparativos | ±0,98 pp |
| Selección | 50.000–200.000 | Afinar alternativas prometedoras | ±0,44–0,22 pp |
| Confirmación | Hasta 5.000.000, alcance pendiente | Finalistas y métricas acordadas | ±0,044 pp si son 5M en esa celda |

Los semianchos usan `1,96 * sqrt(0,25 / N)` para una proporción binaria independiente. No son el error de una diferencia entre dos composiciones ni corrigen la selección entre muchos candidatos. Para el informe usar intervalos Wilson en proporciones y estimación apropiada de incertidumbre de diferencias emparejadas. Los grupos condicionados usan su N efectivo.

Comparar candidatos con aleatoriedad compartida cuando se pueda construir un acoplamiento correcto; cada lista debe conservar una distribución marginal uniforme y se emparejan partidas completas. Usar nuevas semillas para confirmar los finalistas y reducir el sesgo de elegir al máximo observado. Definir de antemano una mejora mínima relevante y reportar resultados inconclusos cuando la precisión no alcance.

Hacer benchmark después de validar el motor: partidas por segundo, memoria y tiempo por política/celda. Con ese dato estimar el coste de 5M por celda frente a 5M totales. Procesar por lotes, guardar acumuladores y una muestra limitada de trazas, permitir reanudación sin repetir ni omitir partidas y evitar almacenar millones de partidas completas.

Cinco millones reducen ruido aleatorio; la calidad depende también de las reglas y políticas del modelo. No se necesita correr 5M sobre candidatos ya dominados.

## 10. Entregables y secuencia

| Paso | Entregable | Condición para avanzar |
| --- | --- | --- |
| 0. Acordar alcance | Respuestas incorporadas en esta versión; contraste de lista y supuestos propuestos | Objetivos y políticas reproducibles |
| 1. Inventario y base exacta | Catálogo, composición, fuentes de colores, probabilidades exactas | 60 cartas y textos relevantes verificados |
| 2. Motor mínimo | Estado, pagos, mulligan/scry/robo, trazas | Casos manuales y controles exactos satisfactorios |
| 3. Piloto de referencia | 2.000 partidas por celda, sin interacción inicialmente | Decisiones revisables, sin incoherencias conocidas |
| 4. Exploración | Dominio completo y controles exactos por grupos; exploración Monte Carlo amplia y estratificada, 10.000 por celda que se simule | Cobertura de familias, compensaciones e incertidumbre visibles; sin atribuir exhaustividad al Monte Carlo |
| 5. Solidez y refinamiento | Escenarios de hate sobre candidatos prometedores; 50.000–200.000 cuando haga falta y sensibilidad a políticas/reemplazos | Estabilidad práctica o incertidumbre explícita |
| 6. Confirmación | Corrida de hasta 5M según presupuesto acordado | Semillas independientes, resultados reproducibles |
| 7. Informe final | HTML, datos, metodología y guía de decisiones | Revisión visual, datos coherentes y publicación en GitHub Pages |

Crear una primera versión local del informe con el piloto para revisar la utilidad de los indicadores antes de invertir en la corrida grande. Cada etapa del informe debe indicar si los datos son piloto, exploración o confirmación.

Estructura sugerida cuando comience la implementación:

```text
data/          # Lista congelada, catálogo y fuentes
configs/       # Composiciones, políticas y experimentos
src/           # Motor, muestreo, métricas y generación del informe
tests/         # Reglas y verificaciones estadísticas relevantes
results/       # Acumuladores, tablas y manifiestos por corrida
docs/          # Informe estático y archivos descargables para GitHub Pages
PLAN_ANALISIS.md
```

Python es una opción inicial para el motor y HTML/CSS/JavaScript para el informe; decidir optimizaciones después del benchmark. Cada corrida registra versión del código, hash de lista/configuración, semillas, N, horizonte, política y tiempo. El navegador consume resultados precalculados; cambiar una composición fuera de los datos disponibles debe indicarlo y requerir una corrida nueva.

## 11. Contenido del informe HTML

- Explicación del mazo, de sus fuentes y de las diferencias entre cobertura y pagos reales.
- Lista original y tabla de cambios de cada composición.
- Dominio completo de búsqueda, filtros por cantidades y cobertura: distinguir bases representadas, evaluadas analíticamente, simuladas y descartadas. Mostrar resultados agrupados y comparadores de listas sin cargar millones de filas en el navegador.
- Curvas por turno y color, filtros play/draw y políticas, N e intervalos.
- Rapidez: distribución del primer acceso, porcentaje sin acceso al horizonte y costes objetivo pagables.
- Solidez: matriz de hate con recursos retenidos y recuperación; distinguir bridges, Citadel y tierras artefacto destructibles.
- Comparador contra la referencia con ganancias/pérdidas en puntos porcentuales y cantidades de cartas cambiadas.
- Análisis de Boulder, mulligans, primeras cinco cartas robadas y duplicados.
- Afinidad, metalcraft, secuencias objetivo y motivos de bloqueo.
- Ejemplos trazables de manos y decisiones, incluyendo cuándo conviene bridge T1 y cuándo tierra enderezada + Boulder.
- Alternativas según prioridades del jugador, con pros y contras respaldados por indicadores.
- Escenarios de interacción separados del modelo sin rival, cuando existan.
- Metodología, supuestos, alcance de la búsqueda, limitaciones, fecha, versión y descarga CSV/JSON/configuraciones.

No presentar una composición como ganadora por diferencias menores que la incertidumbre. La recomendación final debe explicar para qué prioridad y bajo qué política se sostiene.

## 12. Próxima ejecución concreta

1. Contrastar y guardar las 60 cartas de referencia y sus textos relevantes; mantener separada la incertidumbre de la fuente si no se puede obtener la exportación original.
2. Usar el manifiesto exhaustivo `configs/mana_search_space.json`: 19/20 tierras, 9–14 bridges, ninguna básica y todas las distribuciones del catálogo W/U/B/R, cruzado con Boulder 0–4 y reemplazos explícitos. Las listas pequeñas siguen sirviendo para depurar el motor, pero no limitan la búsqueda de construcción.
3. Implementar primero muestreo y mulligan, luego pagos/tierras/Boulder, después robo, afinidad y devoluciones. Validar cada interacción antes de usar sus resultados.
4. Correr 2.000 partidas por celda sin rival y revisar trazas junto con controles exactos. Subir a 10.000 solo cuando el modelo sea coherente.
5. Generar el primer informe con rapidez, cartas conservadas, desarrollo y fallos de maná. Todavía no atribuirle solidez simulada a una composición sin haber corrido el módulo de hate.
6. Agregar las pruebas de solidez, conservar varias alternativas y confirmar resultados con nuevas semillas y el presupuesto grande definido después del benchmark.

## 13. Ejecución realizada: piloto 01 de aperturas

Implementado en `src/opening_pilot.py`, con biblioteca estándar de Python y configuración en `configs/opening_pilot.json`. Referencia y procedencia guardadas en `data/reference_deck.json`; catálogo limitado a inventario de manos en `data/opening_catalog.json`. Este catálogo todavía no contiene todas las reglas necesarias para simular turnos y no certifica la legalidad actual de la lista.

Se generaron 12 composiciones: base original de 19 tierras, Citadel por Vault, Citadel por Drossforge y Citadel como tierra 20; cada una con 4/3/2 Boulder y reemplazos nominales explícitos. Se compararon dos políticas sencillas:

- `min_two`: conservar toda mano con al menos dos tierras. Sirve para aislar el mínimo exigido; no es la política estratégica final.
- `seek_boulder_once`: en siete exigir también Boulder; después del primer mulligan solo exigir las dos tierras. Permite medir el coste de un mulligan voluntario por falta de Boulder sin obligar a buscarlo hasta agotar cartas.

Ambas aplican el mínimo de tierras desde la primera mano de siete y lo preservan al elegir el fondo. El piso principal propuesto es cuatro cartas; sobre la referencia también se ensayaron pisos de tres y dos. Estos pisos y políticas adicionales no fueron elegidos expresamente por el usuario y siguen siendo controles metodológicos modificables. La política de desarrollo más completa de la sección 6 queda para el motor de turnos.

Resultado de ejecución:

- 28 celdas × 2.000 intentos = **56.000 aperturas completas**, no partidas con turnos.
- Semilla 20261029; cálculo aproximado de 5,80 segundos en esta ejecución. Este rendimiento no permite estimar todavía el coste del futuro motor de turnos.
- Nueve pruebas automatizadas satisfactorias: inventario, probabilidades exactas, normalización del mulligan, mínimo de dos tierras desde siete, selección del fondo, conservación de biblioteca, reproducibilidad e intervalos.
- 168 controles Monte Carlo frente a fórmulas exactas dentro de la tolerancia amplia de depuración predefinida; eso detecta errores grandes, no acredita precisión comparativa fina.
- Ninguna mano conservada con menos de dos tierras. Los intentos sin mano admisible al piso permanecen en el denominador.

Primer resultado exacto: `P(menos de dos tierras en las primeras siete)` es **27,94% con 19 tierras** y **24,70% con 20**. Agregar una tierra evita aproximadamente 3,24 mulligans obligatorios por cada 100 primeras manos, con independencia de la estrategia posterior; todavía hay que medir el coste del hechizo retirado y el exceso de tierras durante los turnos.

Artefactos de salida:

- [Informe del piloto](results/pilot_01/informe_piloto.md).
- [Métricas y denominadores CSV](results/pilot_01/metrics.csv).
- [Composiciones completas, trazas, intervalos y manifiesto JSON](results/pilot_01/results.json).
- [Instrucciones reproducibles](README.md).

Próximo bloque pendiente: verificar el catálogo completo y construir estados/pagos/secuencias T1–T6. Este piloto no simuló scry, robos extra, filtrado operativo, afinidad ni hate; no usar sus porcentajes de Boulder en mano como acceso efectivo a los cuatro colores.

## 14. Dominio acotado ejecutado y referencia externa

Se actualizó `src/mana_search_space.py` para aplicar los límites de bridges durante el conteo, la partición y la generación concreta. Se recalcularon 300 filas de perfiles exactos, cuyas multiplicidades cubren las 5.417.403 bases activas para los controles actuales: menos de dos tierras en siete, Boulder en siete y al menos dos tierras + Boulder + tierra enderezada en siete.

Pruebas acumuladas: 14 satisfactorias, incluyendo coincidencia del generador con fuerza bruta y ausencia de omisiones/duplicados al aplicar un intervalo de bridges. No se añadieron partidas de turnos en esta etapa. Los conteos anteriores ampliados dejaron de ser el dominio activo.

Resultados actualizados: [universo de búsqueda](results/search_space/universo_busqueda.md), [manifiesto](results/search_space/manifest.json) y [perfiles exactos](results/search_space/exact_opening_profiles.csv).

Referencia solicitada por el jugador: [video de Hypergeomancer](https://www.youtube.com/watch?v=tyQ-Yh1yfRA). Además de la descripción y las aclaraciones públicas del autor, ahora está disponible [message.txt](message.txt), transcripción parcial aportada por el jugador, que se conserva sin modificar. El análisis actualizado y sus límites están en [ANALISIS_VIDEO_HYPERGEOMANCER.md](ANALISIS_VIDEO_HYPERGEOMANCER.md).

Incorporar al protocolo:

- Contrastar 9–14 en cuatro colores, sin asumir el óptimo de Grixis. La lista balanceada transcrita suma 12 bridges, mientras otras y el cierre mencionan 10/11; verificar la figura antes de adoptar una conclusión universal.
- La transcripción aclara las 246 bases: seis tipos de tierra, cada uno 0–4, sumando 19. El barrido usa 246 × 10.000 × dos modos = 4,92M, más 40.000 para 19/20, total 4,96M. Nuestro universo usa once tipos y otro alcance.
- Documentar parámetros y decisiones del piloto; conservar cartas medias de la mano y fallos de política como métricas independientes de victorias/derrotas.
- Aislar el efecto de mulligans, composición y cortes al comparar 19/20; desglosar por tamaño de mano y cantidad de tierras conservadas.
- Medir la dependencia de Boulder, la exigencia temprana de blanco y el efecto real de tierras giradas sobre los robos.
- No trasladar sus pesos o porcentajes sin disponer de las definiciones completas y comprobar que representen nuestra lista.
- Usar el radar para visualizar, no para clasificar por área: el área depende del orden de ejes. Evitar también contar indicadores correlacionados como votos independientes.
- Mantener probabilidades de cero/una tierra y coste de mulligans: la diferencia de 0,81 pp en exactamente dos tierras no representa por sí sola el cambio completo en calidad de apertura.
- Recoger múltiples métricas de cada partida y recalcular rankings desde resultados almacenados, sin volver a simular para cada combinación de pesos.
