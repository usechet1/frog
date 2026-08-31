import numpy as np
import pandas as pd

def generar(x_o, k, c, g, n):
    registros = []
    a = 1 + 2 * k
    x_a = x_o
    m = 2 ** g

    for i in range(n):
        x_i = np.mod(((a * x_a) + c), m)
        x_a = x_i
        r_i = truncar_decimales_inteligente(x_i / m)

        registros.append({
            "i": i+1,
            "Xi": int(x_i),
            "Ri": r_i
        })

    df = pd.DataFrame(registros)
    return df

def truncar_decimales_inteligente(numero):

    # Truncar a 5 decimales máximo usando truncamiento, no redondeo
    factor = 10.0 ** 5
    truncado = int(numero * factor) / factor

    # Convertir a string para eliminar ceros trailing
    resultado_str = f"{truncado:.5f}".rstrip('0').rstrip('.')

    # Si queda vacío después del punto, agregar un 0
    if resultado_str.endswith('.'):
        resultado_str = resultado_str[:-1]

    # Convertir de vuelta a float
    return float(resultado_str)