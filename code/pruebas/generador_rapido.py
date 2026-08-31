# Misma matemática que pruebas/generador.py (LCG con a = 1 + 2k, m = 2^g),
# pero vectorizada con numpy para poder generar millones de números rápido.
# generador.py se conserva intacto porque es el entregable "desde cero";
# este módulo es solo una versión rápida para las corridas masivas.
import numpy as np


def generar_rapido(x_o: int, k: int, c: int, g: int, n: int):
    # LCG x_{i+1} = (a*x_i + c) mod m, con a = 1 + 2k y m = 2^g.
    # Devuelve (xs, r): las semillas X_i y los uniformes R_i = X_i / m
    # truncados a 5 decimales, igual que el generador original.
    a = 1 + 2 * k
    m = 2 ** g

    xs = np.empty(n, dtype=np.int64)
    x = x_o
    # Cada Xi depende del anterior, así que este bucle no se puede vectorizar
    for i in range(n):
        x = (a * x + c) % m
        xs[i] = x

    r = xs / m
    r = np.trunc(r * 1e5) / 1e5  # trunca (no redondea) a 5 decimales
    return xs, r


def semilla_derivada(semilla_base: int, indice: int) -> int:
    # Deriva una semilla distinta y reproducible para cada réplica `indice`,
    # para que las simulaciones sean independientes entre sí.
    a2, c2, m2 = 6364136223846793005, 1442695040888963407, 2 ** 64
    x = (semilla_base ^ 0x9E3779B97F4A7C15) & (m2 - 1)
    for _ in range(indice + 1):
        x = (a2 * x + c2) % m2
    return int(x % (2 ** 31))  # acotado a 32 bits para ser compatible con g <= 32
