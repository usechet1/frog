# Punto 2 — Resultados de la simulación (insumo para el informe IEEE)

## 1. Probabilidad de retorno al origen en 2, 3 y 4 saltos (analítico, 1D)

| n (saltos) | Paridad | P(retorno exacto) |
|---|---|---|
| 2 | par | 0.500000 |
| 3 | impar | 0.000000 |
| 4 | par | 0.375000 |

**Generalización:** para n impar, P = 0 — la posición tras n pasos y n siempre comparten paridad, así que es imposible estar en 0 tras un número impar de pasos. Para n par, P(retorno) = C(n, n/2) / 2^n (coeficiente binomial central).

## 2. Probabilidad empírica de retorno al origen dentro de los primeros 1000 pasos

| dimension   |   prob_retorno_origen_1000_pasos |
|:------------|---------------------------------:|
| 1D          |                             0.97 |
| 2D          |                             0.67 |
| 3D          |                             0.32 |

> TODO (tuyo, con cita IEEE): interpreta esta tabla con el teorema de recurrencia de caminatas aleatorias de Pólya (1921): las caminatas simétricas en 1D y 2D son recurrentes (retornan al origen con probabilidad 1 si se deja pasar tiempo suficiente), mientras que en 3D son transitorias (probabilidad límite de retorno ≈ 0.3405). Con solo 1000 pasos estás viendo una aproximación parcial a esos valores límite, no el límite exacto — coméntalo explícitamente en el análisis.

## 3. Eficiencia computacional

| dimension   |   n_pasos |   n_simulaciones |   tiempo_total_seg |   tiempo_promedio_por_replica_seg |   memoria_pico_mb |   prob_retorno_origen_1000_pasos |
|:------------|----------:|-----------------:|-------------------:|----------------------------------:|------------------:|---------------------------------:|
| 1D          |   1000000 |              100 |            151.169 |                           1.5116  |             61.04 |                             0.97 |
| 2D          |   1000000 |              100 |            150.83  |                           1.50821 |            106.82 |                             0.67 |
| 3D          |   1000000 |              100 |            151.115 |                           1.51107 |            144.97 |                             0.32 |

> TODO (tuyo): interpreta por qué el tiempo/memoria cambian (o no) con la dimensión, y qué tanto depende de la implementación (vectorización con numpy) frente a un enfoque con bucles puros en Python.

## 4. Punto de partida para las referencias bibliográficas de la discusión

- Pólya, G. (1921). *Über eine Aufgabe der Wahrscheinlichkeitsrechnung betreffend die Irrfahrt im Straßennetz* — el teorema de recurrencia de caminatas aleatorias (búscalo y cítalo en formato IEEE).
- Cualquier texto de procesos estocásticos con caminatas aleatorias simples (p. ej. Grimmett & Stirzaker, *Probability and Random Processes*) — agrégalo como tu segunda referencia formal.