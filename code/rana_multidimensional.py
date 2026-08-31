
import os
import time
import tracemalloc
import argparse
from math import comb

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (registra la proyección 3d)
from scipy.stats import norm

from pruebas.generador_rapido import generar_rapido, semilla_derivada


# Probabilidad de retorno al origen en 1D (fórmula cerrada)

def probabilidad_retorno_teorica(n: int) -> float:
    # P(la caminata 1D está exactamente en el origen tras n pasos).
    # Solo es posible si n es par: se necesitan n/2 pasos +1 y n/2 pasos -1,
    # cuyo número de combinaciones es C(n, n/2), cada una con probabilidad (1/2)^n.
    if n % 2 != 0:
        return 0.0
    return comb(n, n // 2) / (2 ** n)


def tabla_probabilidades_iniciales():
    # Devuelve [(n, 'par'|'impar', P), ...] para n = 2, 3, 4
    filas = []
    for n in (2, 3, 4):
        p = probabilidad_retorno_teorica(n)
        filas.append((n, "par" if n % 2 == 0 else "impar", p))
    return filas


# Conversión vectorizada (numpy) de números uniformes a pasos en 1D/2D/3D.
# Usa los mismos umbrales y direcciones que CaminataAleatoria1D/2D/3D.py,
# pero vectorizados para poder procesar millones de números por réplica.

_DIRS_2D = np.array([
    [0, 1],   # Norte   -> r en [0.00, 0.25)
    [1, 0],   # Este    -> r en [0.25, 0.50)
    [0, -1],  # Sur     -> r en [0.50, 0.75)
    [-1, 0],  # Oeste   -> r en [0.75, 1.00)
])

_DIRS_3D = np.array([
    [0, 1, 0],   # Norte  -> r en [0/6, 1/6)
    [0, -1, 0],  # Sur    -> r en [1/6, 2/6)
    [1, 0, 0],   # Este   -> r en [2/6, 3/6)
    [-1, 0, 0],  # Oeste  -> r en [3/6, 4/6)
    [0, 0, 1],   # Arriba -> r en [4/6, 5/6)
    [0, 0, -1],  # Abajo  -> r en [5/6, 6/6)
])


def trayectoria_1d(r: np.ndarray, pos_inicial: int = 0) -> np.ndarray:
    pasos = np.where(r >= 0.5, 1, -1)
    return pos_inicial + np.concatenate(([0], np.cumsum(pasos)))


def trayectoria_2d(r: np.ndarray, pos_inicial=(0, 0)):
    idx = np.minimum((r * 4).astype(int), 3)
    deltas = _DIRS_2D[idx]
    cum = np.cumsum(deltas, axis=0)
    x = np.concatenate(([pos_inicial[0]], pos_inicial[0] + cum[:, 0]))
    y = np.concatenate(([pos_inicial[1]], pos_inicial[1] + cum[:, 1]))
    return x, y


def trayectoria_3d(r: np.ndarray, pos_inicial=(0, 0, 0)):
    idx = np.minimum((r * 6).astype(int), 5)
    deltas = _DIRS_3D[idx]
    cum = np.cumsum(deltas, axis=0)
    x = np.concatenate(([pos_inicial[0]], pos_inicial[0] + cum[:, 0]))
    y = np.concatenate(([pos_inicial[1]], pos_inicial[1] + cum[:, 1]))
    z = np.concatenate(([pos_inicial[2]], pos_inicial[2] + cum[:, 2]))
    return x, y, z


# Simulación en lote: réplicas independientes por dimensión

def simular_lote(dim: int, n_pasos: int, n_simulaciones: int,
                  semilla_base: int, k: int, c: int, g: int,
                  pasos_verificacion_retorno: int = 1000):
    # Corre n_simulaciones réplicas independientes de una caminata de n_pasos
    # en la dimensión dim (1, 2 o 3), cada una con su propia semilla derivada.
    # Solo guarda la trayectoria completa de la primera réplica (para graficar
    # un ejemplo); guardar todas sería demasiado pesado en memoria.
    assert dim in (1, 2, 3)
    tracemalloc.start()

    tiempos = np.empty(n_simulaciones)
    retorno_1000 = np.zeros(n_simulaciones, dtype=bool)
    finales = (np.empty(n_simulaciones, dtype=np.int64) if dim == 1
               else np.empty((n_simulaciones, dim), dtype=np.int64))

    trayectoria_ejemplo = None
    limite_check = min(pasos_verificacion_retorno, n_pasos)

    t_inicio_total = time.perf_counter()
    for s in range(n_simulaciones):
        semilla_s = semilla_derivada(semilla_base, s)
        t0 = time.perf_counter()
        _, r = generar_rapido(semilla_s, k, c, g, n_pasos)

        if dim == 1:
            traj = trayectoria_1d(r)
            finales[s] = traj[-1]
            retorno_1000[s] = np.any(traj[1:limite_check + 1] == 0)
            if s == 0:
                trayectoria_ejemplo = (traj,)
        elif dim == 2:
            tx, ty = trayectoria_2d(r)
            finales[s] = (tx[-1], ty[-1])
            en_origen = (tx[1:limite_check + 1] == 0) & (ty[1:limite_check + 1] == 0)
            retorno_1000[s] = np.any(en_origen)
            if s == 0:
                trayectoria_ejemplo = (tx, ty)
        else:
            tx, ty, tz = trayectoria_3d(r)
            finales[s] = (tx[-1], ty[-1], tz[-1])
            en_origen = ((tx[1:limite_check + 1] == 0) &
                         (ty[1:limite_check + 1] == 0) &
                         (tz[1:limite_check + 1] == 0))
            retorno_1000[s] = np.any(en_origen)
            if s == 0:
                trayectoria_ejemplo = (tx, ty, tz)

        tiempos[s] = time.perf_counter() - t0

    tiempo_total = time.perf_counter() - t_inicio_total
    _, memoria_pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "dim": dim,
        "n_pasos": n_pasos,
        "n_simulaciones": n_simulaciones,
        "posiciones_finales": finales,
        "retorno_1000": retorno_1000,
        "prob_retorno_1000": float(np.mean(retorno_1000)),
        "tiempos": tiempos,
        "tiempo_total_seg": tiempo_total,
        "memoria_pico_mb": memoria_pico / (1024 ** 2),
        "trayectoria_ejemplo": trayectoria_ejemplo,
    }


# Gráficos

def _mostrar_y_guardar(ruta_salida):
    if ruta_salida:
        plt.savefig(ruta_salida, dpi=130)
    try:
        plt.show()
    except Exception:
        pass  # sin pantalla disponible (p.ej. servidor); el PNG ya quedó guardado
    plt.close()


def graficar_histograma_1d(resultado, ruta_salida=None):
    # Histograma de posiciones finales (1D) + curva Normal predicha por el TCL
    finales = resultado["posiciones_finales"].astype(float)
    n_pasos = resultado["n_pasos"]
    media = float(np.mean(finales))
    sigma_emp = float(np.std(finales))
    sigma_tcl = float(np.sqrt(n_pasos))  # Var(posición) = n para pasos +-1 equiprobables

    plt.figure(figsize=(9, 5.5))
    plt.hist(finales, bins=min(30, max(5, len(finales) // 3)),
             color="skyblue", edgecolor="black", alpha=0.8, density=True)
    if sigma_tcl > 0:
        xs = np.linspace(finales.min(), finales.max(), 300)
        plt.plot(xs, norm.pdf(xs, 0, sigma_tcl), "r-", lw=2,
                 label=f"Normal(0, σ={sigma_tcl:.1f}) — predicción TCL")
    plt.axvline(media, color="darkred", ls="--", label=f"Media empírica: {media:.1f}")
    plt.title(f"Distribución de posiciones finales — Caminata 1D\n"
              f"({resultado['n_simulaciones']} réplicas, {n_pasos:,} pasos c/u)")
    plt.xlabel("Posición final")
    plt.ylabel("Densidad")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    _mostrar_y_guardar(ruta_salida)

    return {"media_empirica": media, "sigma_empirica": sigma_emp, "sigma_teorica_TCL": sigma_tcl}


def graficar_2d(resultado, ruta_salida=None):
    # Trayectoria de una réplica de muestra + heatmap de posiciones finales
    tx, ty = resultado["trayectoria_ejemplo"]
    finales = resultado["posiciones_finales"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.plot(tx, ty, lw=0.6, alpha=0.6, color="steelblue")
    ax1.scatter([tx[0]], [ty[0]], c="green", s=80, marker="s", label="Inicio", zorder=3)
    ax1.scatter([tx[-1]], [ty[-1]], c="red", s=80, marker="X", label="Final", zorder=3)
    ax1.set_title(f"Trayectoria de muestra 2D ({resultado['n_pasos']:,} pasos)")
    ax1.set_xlabel("X"); ax1.set_ylabel("Y")
    ax1.legend(); ax1.grid(alpha=0.3); ax1.set_aspect("equal", adjustable="box")

    h = ax2.hist2d(finales[:, 0], finales[:, 1], bins=25, cmap="viridis")
    plt.colorbar(h[3], ax=ax2, label="Frecuencia")
    ax2.scatter([0], [0], c="red", marker="*", s=150, label="Origen")
    ax2.set_title(f"Heatmap de posiciones finales\n({resultado['n_simulaciones']} réplicas)")
    ax2.set_xlabel("X"); ax2.set_ylabel("Y"); ax2.legend()

    plt.tight_layout()
    _mostrar_y_guardar(ruta_salida)


def graficar_3d(resultado, ruta_salida=None):
    # Trayectoria 3D de una réplica de muestra + proyecciones ortogonales XY/XZ/YZ
    tx, ty, tz = resultado["trayectoria_ejemplo"]
    finales = resultado["posiciones_finales"]

    fig = plt.figure(figsize=(15, 8))
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax1.plot(tx, ty, tz, lw=0.5, alpha=0.6, color="steelblue")
    ax1.scatter([tx[0]], [ty[0]], [tz[0]], c="green", s=60, marker="s", label="Inicio")
    ax1.scatter([tx[-1]], [ty[-1]], [tz[-1]], c="red", s=60, marker="X", label="Final")
    ax1.set_title(f"Trayectoria de muestra 3D ({resultado['n_pasos']:,} pasos)")
    ax1.set_xlabel("X"); ax1.set_ylabel("Y"); ax1.set_zlabel("Z")
    ax1.legend()

    proyecciones = [("XY", finales[:, 0], finales[:, 1]),
                    ("XZ", finales[:, 0], finales[:, 2]),
                    ("YZ", finales[:, 1], finales[:, 2])]
    for i, (nombre, a, b) in enumerate(proyecciones):
        ax = fig.add_subplot(3, 2, 2 + 2 * i if i < 2 else 6)
        ax.scatter(a, b, s=12, alpha=0.6, color="teal")
        ax.scatter([0], [0], c="red", marker="*", s=100)
        ax.set_title(f"Proyección {nombre} (posiciones finales, {resultado['n_simulaciones']} réplicas)")
        ax.set_xlabel(nombre[0]); ax.set_ylabel(nombre[1]); ax.grid(alpha=0.3)

    plt.tight_layout()
    _mostrar_y_guardar(ruta_salida)


def graficar_eficiencia(df_eficiencia, ruta_salida=None):
    colores = ["#4C72B0", "#55A868", "#C44E52"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.bar(df_eficiencia["dimension"], df_eficiencia["tiempo_total_seg"], color=colores)
    ax1.set_ylabel("Tiempo total (s)")
    ax1.set_title("Tiempo de ejecución por dimensión")
    ax1.grid(alpha=0.3, axis="y")

    ax2.bar(df_eficiencia["dimension"], df_eficiencia["memoria_pico_mb"], color=colores)
    ax2.set_ylabel("Memoria pico (MB)")
    ax2.set_title("Memoria pico por dimensión")
    ax2.grid(alpha=0.3, axis="y")

    plt.tight_layout()
    _mostrar_y_guardar(ruta_salida)


# Tabla de eficiencia comparativa + reporte de texto

def tabla_eficiencia(resultados: dict) -> pd.DataFrame:
    filas = []
    for dim in sorted(resultados.keys()):
        r = resultados[dim]
        filas.append({
            "dimension": f"{dim}D",
            "n_pasos": r["n_pasos"],
            "n_simulaciones": r["n_simulaciones"],
            "tiempo_total_seg": round(r["tiempo_total_seg"], 3),
            "tiempo_promedio_por_replica_seg": round(float(np.mean(r["tiempos"])), 5),
            "memoria_pico_mb": round(r["memoria_pico_mb"], 2),
            "prob_retorno_origen_1000_pasos": round(r["prob_retorno_1000"], 4),
        })
    return pd.DataFrame(filas)


def generar_reporte_texto(tabla_inicial, df_eficiencia, ruta_salida):
    lineas = []
    lineas.append("# Punto 2 — Resultados de la simulación (insumo para el informe IEEE)\n")

    lineas.append("## 1. Probabilidad de retorno al origen en 2, 3 y 4 saltos (analítico, 1D)\n")
    lineas.append("| n (saltos) | Paridad | P(retorno exacto) |")
    lineas.append("|---|---|---|")
    for n, paridad, p in tabla_inicial:
        lineas.append(f"| {n} | {paridad} | {p:.6f} |")
    lineas.append(
        "\n**Generalización:** para n impar, P = 0 — la posición tras n pasos y n "
        "siempre comparten paridad, así que es imposible estar en 0 tras un número "
        "impar de pasos. Para n par, P(retorno) = C(n, n/2) / 2^n (coeficiente "
        "binomial central).\n"
    )

    lineas.append("## 2. Probabilidad empírica de retorno al origen dentro de los primeros 1000 pasos\n")
    lineas.append(df_eficiencia[["dimension", "prob_retorno_origen_1000_pasos"]].to_markdown(index=False))
    lineas.append(
        "\n> TODO (tuyo, con cita IEEE): interpreta esta tabla con el teorema de "
        "recurrencia de caminatas aleatorias de Pólya (1921): las caminatas "
        "simétricas en 1D y 2D son recurrentes (retornan al origen con "
        "probabilidad 1 si se deja pasar tiempo suficiente), mientras que en 3D "
        "son transitorias (probabilidad límite de retorno ≈ 0.3405). Con solo "
        "1000 pasos estás viendo una aproximación parcial a esos valores límite, "
        "no el límite exacto — coméntalo explícitamente en el análisis.\n"
    )

    lineas.append("## 3. Eficiencia computacional\n")
    lineas.append(df_eficiencia.to_markdown(index=False))
    lineas.append(
        "\n> TODO (tuyo): interpreta por qué el tiempo/memoria cambian (o no) con "
        "la dimensión, y qué tanto depende de la implementación (vectorización "
        "con numpy) frente a un enfoque con bucles puros en Python.\n"
    )

    lineas.append("## 4. Punto de partida para las referencias bibliográficas de la discusión\n")
    lineas.append(
        "- Pólya, G. (1921). *Über eine Aufgabe der Wahrscheinlichkeitsrechnung "
        "betreffend die Irrfahrt im Straßennetz* — el teorema de recurrencia de "
        "caminatas aleatorias (búscalo y cítalo en formato IEEE)."
    )
    lineas.append(
        "- Cualquier texto de procesos estocásticos con caminatas aleatorias "
        "simples (p. ej. Grimmett & Stirzaker, *Probability and Random Processes*) "
        "— agrégalo como tu segunda referencia formal."
    )

    contenido = "\n".join(lineas)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(contenido)
    return contenido


# CLI

def main():
    parser = argparse.ArgumentParser(
        description="Punto 2: La rana en mundos paralelos (1D/2D/3D)")
    parser.add_argument("--pasos", type=int, default=5000,
                         help="Pasos por caminata. Entrega final del taller: 1000000")
    parser.add_argument("--simulaciones", type=int, default=20,
                         help="Réplicas independientes por dimensión. Entrega final: >=100")
    parser.add_argument("--semilla", type=int, default=12345, help="Semilla base (x_0)")
    parser.add_argument("--k", type=int, default=832262, help="Parámetro k del LCG (a=1+2k)")
    parser.add_argument("--c", type=int, default=1013904223, help="Constante aditiva c")
    parser.add_argument("--g", type=int, default=32, help="Exponente de módulo, m=2^g")
    parser.add_argument("--salida", type=str, default="output", help="Carpeta de salida")
    parser.add_argument("--sin-mostrar", action="store_true",
                         help="No abrir ventanas de matplotlib (solo guardar PNG)")
    args = parser.parse_args()

    if args.sin_mostrar:
        matplotlib.use("Agg")

    os.makedirs(args.salida, exist_ok=True)

    print("=" * 70)
    print("PUNTO 2 — LA RANA ESTADÍSTICA EN MUNDOS PARALELOS")
    print("=" * 70)
    print(f"Pasos por caminata: {args.pasos:,} | Réplicas por dimensión: {args.simulaciones}")
    if args.pasos < 1_000_000 or args.simulaciones < 100:
        print("AVISO: esta es una corrida de PRUEBA. El taller exige 1,000,000 de "
              "pasos y al menos 100 réplicas por dimensión para la entrega final "
              "(usa --pasos 1000000 --simulaciones 100).")

    print("\n--- 1. Probabilidad analítica de retorno (1D) ---")
    tabla_inicial = tabla_probabilidades_iniciales()
    for n, paridad, p in tabla_inicial:
        print(f"  P(retorno en {n} saltos, {paridad}) = {p:.6f}")

    resultados = {}
    for dim in (1, 2, 3):
        print(f"\n--- 2. Simulando {dim}D: {args.simulaciones} réplicas x {args.pasos:,} pasos ---")
        r = simular_lote(dim, args.pasos, args.simulaciones, args.semilla, args.k, args.c, args.g)
        resultados[dim] = r
        print(f"  Tiempo total: {r['tiempo_total_seg']:.2f}s | "
              f"Memoria pico: {r['memoria_pico_mb']:.2f} MB | "
              f"P(retorno <=1000 pasos): {r['prob_retorno_1000']:.4f}")

    print("\n--- 3. Generando gráficos ---")
    stats_1d = graficar_histograma_1d(resultados[1], os.path.join(args.salida, "1_histograma_1d.png"))
    print(f"  1D -> media={stats_1d['media_empirica']:.2f}, "
          f"sigma_empirica={stats_1d['sigma_empirica']:.2f}, "
          f"sigma_TCL={stats_1d['sigma_teorica_TCL']:.2f}")
    graficar_2d(resultados[2], os.path.join(args.salida, "2_trayectoria_heatmap_2d.png"))
    graficar_3d(resultados[3], os.path.join(args.salida, "3_trayectoria_proyecciones_3d.png"))

    df_efic = tabla_eficiencia(resultados)
    graficar_eficiencia(df_efic, os.path.join(args.salida, "4_eficiencia_comparativa.png"))
    df_efic.to_csv(os.path.join(args.salida, "tabla_eficiencia.csv"), index=False)

    print("\n--- 4. Tabla comparativa de eficiencia ---")
    print(df_efic.to_string(index=False))

    generar_reporte_texto(tabla_inicial, df_efic, os.path.join(args.salida, "reporte_punto2.md"))

    print(f"\nListo. Resultados guardados en: {args.salida}/")
    print("  - 1_histograma_1d.png")
    print("  - 2_trayectoria_heatmap_2d.png")
    print("  - 3_trayectoria_proyecciones_3d.png")
    print("  - 4_eficiencia_comparativa.png")
    print("  - tabla_eficiencia.csv")
    print("  - reporte_punto2.md  (con TODOs para tu análisis y referencias)")


if __name__ == "__main__":
    main()
