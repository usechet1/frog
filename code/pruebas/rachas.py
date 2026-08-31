import numpy as np
from scipy.stats import norm
import json

def prueba_rachas(muestra, alpha=0.05, mediana_teorica=0.5):
    # Prueba de rachas: evalúa la aleatoriedad de la muestra
    muestra = np.array(muestra)
    
    # Obtener mediana muestral
    mediana_muestral = np.median(muestra)
    
    # Convertir la secuencia a signos respecto a la mediana teórica
    signos = ['+' if x >= mediana_teorica else '-' for x in muestra]
    
    # Contar total de "+" y "-"
    n_pos = signos.count('+')
    n_neg = signos.count('-')
    n = n_pos + n_neg
    
    # Contar número de rachas
    rachas = 1
    for i in range(1, len(signos)):
        if signos[i] != signos[i-1]:
            rachas += 1
    
    # Valor esperado y varianza de las rachas
    ur = ((2 * n_pos * n_neg) / n) + 1
    varianza = (2 * n_pos * n_neg * (2 * n_pos * n_neg - n)) / (n**2 * (n - 1))
    
    # Estadístico Z
    z = (rachas - ur) / np.sqrt(varianza)
    
    # Valores críticos
    z_crit = norm.ppf(1 - alpha/2)
    rango_min, rango_max = -z_crit, z_crit
    
    # Decisión
    cumple = rango_min <= z <= rango_max
    result = {
        "test_name": "Prueba de Rachas",
        "Mediana_muestral": mediana_muestral,
        "Mediana_teorica": mediana_teorica,
        "Total_may": n_pos,
        "Total_min": n_neg,
        "Total": n,
        "Rachas": rachas,
        "UR": ur,
        "Varianza": varianza,
        "Z": z,
        "Rango_min": rango_min,
        "Rango_max": rango_max,
        "decision": "Pasa la prueba de rachas." if cumple else "No pasa la prueba de rachas.",
        "isApproved": str(cumple)
    }
    
    return json.dumps(result, indent=4)

if __name__ == "__main__":
    np.random.seed(0)
    muestra = [0.37542, 0.42051, 0.53542, 0.58091, 0.89271, 0.22247, 0.42658, 0.95416, 
 0.82947, 0.54548, 0.47858, 0.62576, 0.81228, 0.50782, 0.92641, 0.10523, 
 0.99464, 0.87205, 0.69877, 0.13299, 0.95006, 0.52785, 0.89887, 0.97217, 
 0.21287, 0.22876, 0.32705, 0.72710, 0.07937, 0.85431, 0.77654, 0.90773, 
 0.57653, 0.71085, 0.07017, 0.80816, 0.30918, 0.98221, 0.10197, 0.19320, 
 0.26009, 0.66588, 0.47821, 0.13881, 0.12873, 0.22713, 0.34787, 0.67177, 
 0.75884, 0.81982]
    
    print(prueba_rachas(muestra))

