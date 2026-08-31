import numpy as np
import scipy.stats as stats
import json
from scipy.stats import chi2

def prueba_chi_cuadrado(datos, k=8, alpha=0.05):
    # Prueba Chi-cuadrado de uniformidad
    # datos: lista o array de números pseudoaleatorios
    # k: número de intervalos
    # alpha: nivel de significancia
    n = len(datos)
    datos = np.array(datos)

    # Usar el rango real de los datos
    minimo, maximo = np.min(datos), np.max(datos)
    intervalos = np.linspace(minimo, maximo, k+1)
    
    # Frecuencias observadas
    frecuencias_obs, _ = np.histogram(datos, bins=intervalos)
    
    # Frecuencia esperada
    freq_esp = n / k
    
    # Chi2 por intervalo
    chi2_vals = ((frecuencias_obs - freq_esp) ** 2) / freq_esp
    
    # Chi2 total
    chi2_total = np.sum(chi2_vals)
    
    # Valor crítico
    chi2_critico = chi2.ppf(1 - alpha, 7)
    
    # Construcción de la respuesta en formato JSON
    resultado = {
        "test_name": "Prueba Chi-Cuadrado",
        "intervals": k,
        "n": n,
        "range": {
            "minimum": minimo,
            "maximum": maximo
        },
        "intervals_data": [],
        "statistics": {
            "frecuencia_obt_total": int(np.sum(frecuencias_obs)),
            "frecuencia_esp_total": int(freq_esp * k),
            "chi2_total": chi2_total,
            "chi2_critico": chi2_critico,
        },
        "decision": "Pasa la prueba chi-cuadrado." if chi2_total <= chi2_critico else "No pasa la prueba chi-cuadrado.",
        "isApproved": str(chi2_total <= chi2_critico)
    }

    for i in range(k):
        resultado["intervals_data"].append({
            "no": i+1,
            "inicio": round(float(intervalos[i]), 8),
            "fin": round(float(intervalos[i+1]), 8),
            "frecuencia_obt": int(frecuencias_obs[i]),
            "frecuencia_esp": round(float(freq_esp), 3),
            "chi2": round(float(chi2_vals[i]), 3)
        })

    return json.dumps(resultado, ensure_ascii=False, indent=2)