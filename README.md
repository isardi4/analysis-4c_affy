# 4c Affinity: análisis de maná

Estudio reproducible de composiciones con 19/20 tierras y distintas cantidades de Giant's Boulder. El objetivo final es un informe HTML en GitHub con rapidez, solidez y compensaciones entre alternativas.

El diseño completo y las respuestas del jugador están en [PLAN_ANALISIS.md](PLAN_ANALISIS.md).

## Informe web

- Sitio: [isardi4.github.io/analysis-4c_affy](https://isardi4.github.io/analysis-4c_affy/).
- Código: [GitHub](https://github.com/isardi4/analysis-4c_affy).
- Pestaña **Partes 1 y 2**: gráficos interactivos OTP/OTD, 19/20 tierras, ratios y secuenciación.
- Otras pestañas: vista general, metodología/pilotos y documentos/datos descargables.

HTML/CSS/JavaScript estático, sin servicios externos de gráficos ni instalación de dependencias. Los gráficos consumen las salidas existentes; no ejecutan simulaciones nuevas en el navegador. GitHub Actions valida las pruebas, empaqueta y publica `docs/` en cada push a `main`.

## Estado actual

Prioridad actual: **parte 1, 19/20 tierras; parte 2, ratio de 8–12 bridges; parte 3, colores y spells.** Ya hay un control con turnos de tierras, mulligans y robos naturales, separado OTP/OTD. Ese control estructural no simula hechizos ni scry. La nueva pestaña agrega un goldfish con cinco prioridades de color para decidir el ratio, manteniendo 19 tierras; el hate y la composición final siguen pendientes. La referencia sigue pendiente de contraste con la exportación original de Goldfish.

Resultados actuales: [informe de partes 1 y 2](results/structural_stages/informe.md), [CSV](results/structural_stages/metrics.csv) y [JSON con trazas](results/structural_stages/results.json). Se calcularon probabilidades por estados y se validaron con 88.000 trayectorias (2.000 por celda). Los no terrenos son marcadores inertes: se cuantifica consistencia y coste de entrar girado, no el equilibrio final de Affinity.

El catálogo de la posterior composición comprende distribuciones W/U/B/R con 19/20 tierras, 8–12 bridges y ninguna básica. Su búsqueda detallada queda pausada hasta revisar cantidad y ratio. Las 12 listas del primer piloto no son el universo de construcción; los conteos previos quedan como preparación para esa etapa.

Regla obligatoria: toda mano conservada debe tener al menos dos tierras, incluida la primera de siete y cualquier mano posterior después de poner cartas al fondo.

## Ejecutar

Python 3.9 o posterior, sin dependencias externas. Desde esta carpeta:

```sh
python3 -m unittest discover -s tests -v
python3 -m src.opening_pilot
python3 -m src.mana_search_space
python3 -m src.structural_stages
python3 scripts/build_report.py
python3 scripts/validate_report.py
```

La configuración inicial tiene 12 composiciones y 28 celdas, 2.000 intentos por celda. Una celda es composición × política de mulligan × piso de cartas. Son 56.000 aperturas completas en total, no 56.000 partidas jugadas. Play/draw no se duplica hasta que se modelen los turnos.

```sh
python3 -m src.opening_pilot --trials 10000 --output results/exploration_openings
```

El piso de cuatro cartas y las políticas adicionales de mulligan son propuestas metodológicas. Si no se consigue una mano admisible al llegar al piso, se cuenta el intento como fallo de política, sin inventar un keep de una tierra ni eliminar el intento. El piloto comprueba también pisos de tres y dos sobre la referencia.

## Archivos

- [Referencia y procedencia](data/reference_deck.json).
- [Catálogo limitado a aperturas](data/opening_catalog.json).
- [Configuración del piloto](configs/opening_pilot.json).
- [Primer informe](results/pilot_01/informe_piloto.md).
- [Métricas CSV](results/pilot_01/metrics.csv).
- [Resultados, trazas y manifiesto](results/pilot_01/results.json).
- [Dominio exhaustivo de composiciones](configs/mana_search_space.json).
- [Universo y cobertura del análisis exacto](results/search_space/universo_busqueda.md).
- [Perfiles de aperturas exactos](results/search_space/exact_opening_profiles.csv).

El dominio activo tiene 4.866.162 bases con 8–12 bridges (2.357.556 de 19 tierras y 2.508.606 de 20). Se permiten 0–4 copias de cada tierra del catálogo W/U/B/R, incluyendo Citadel; básicas y su análisis de Wildfire quedan excluidos. La extensión verde anterior está inactiva, sin asumir que haya sido demostrada inferior. Los 250 perfiles actuales cubren todas las bases activas para controles de aperturas; todavía no evalúan colores, secuencias ni hate. No confundir conteo/evaluación analítica con partidas Monte Carlo ejecutadas.

La revisión de la referencia está en [ANALISIS_VIDEO_HYPERGEOMANCER.md](ANALISIS_VIDEO_HYPERGEOMANCER.md). Ahora incorpora la [transcripción parcial aportada por el jugador](message.txt), además de las fuentes del autor. Incluye métodos reutilizables, controles críticos y una propuesta para seleccionar candidatas dentro de 120 perfiles estructurales antes de invertir en Monte Carlo de turnos. No se ejecutó todavía esa selección ni el motor de turnos.

Se guardan semillas, versiones y hashes de los archivos de entrada y del motor. Los intervalos de proporciones individuales no se usan para declarar diferencias emparejadas ni elegir un ganador.

Siguiente etapa: catálogo completo verificado y motor T1–T6 para pagos, filtrado, scry, robos y afinidad. Después se incorporan escenarios de destrucción/exilio y recuperación.

## Colores tempranos y bridges

La pestaña **Perfiles predefinidos** abre por defecto. Compara cinco prioridades de fuentes con 8–12 bridges, 19 tierras, cuatro Boulder y los mismos 41 hechizos. El piloto tiene 100.000 partidas; la confirmación independiente, 500.000. Incluye pagos, scry, afinidad, robo y rebotes, con una política común y sin rival. Son 25 bases representativas, no todas las composiciones.

[Informe y alcance](results/color_bridges/informe.md), [resultados](results/color_bridges/results.json), [CSV](results/color_bridges/metrics.csv).

```sh
python3 -m src.color_bridge_study --trials 10000 --seed 2026102902 --workers 4 --output results/color_bridges
python3 scripts/write_color_bridge_report.py
python3 scripts/build_report.py
python3 scripts/validate_report.py
```

## Pesos independientes de color

En **Composición a medida → Qué colores pueden esperar**, cada color W/U/B/R tiene un control de 0 a 1. Se pueden reducir varios a la vez. El explorador busca exactamente entre las bases de 19 tierras con el ratio elegido (8–12 bridges), máximo cuatro copias por tierra, sin básicas ni Citadel. Con 10 bridges son 120.480 bases. Cuatro Boulder y los hechizos permanecen fijos. La configuración se comparte por URL y se descarga como JSON.

El objetivo es la suma ponderada de probabilidades de encontrar una fuente natural entre nueve cartas sin mulligan. Los empates usan cobertura de fuentes enderezadas entre siete según los mismos pesos; no se favorece un color fijo. Pesos relativos iguales producen la misma elección. Cero deja de exigir ese color en el objetivo, sin retirar sus hechizos. Todos en cero requiere corregir los pesos.

Esta búsqueda genera una base orientativa, con fuentes, cambios frente a pesos iguales y probabilidades hipergeométricas. No simula pagos, Boulder ni partidas; los resultados Monte Carlo previos siguen separados y sin cambios. No se puede interpretar peso 0,50 como 50% de acceso ni como una fecha de llegada.

```sh
node --test tests/composition.test.cjs
```

El rango activo 8–12 se aplica a ambas pestañas y a los controles estructurales. **Composición a medida** está separada de **Perfiles predefinidos**. Se verificó que las 40 celdas de colores y 36 estructurales superpuestas con el rango anterior conservaran exactamente sus resultados; [registro de comparación](results/color_bridges/range_update_check.json).
