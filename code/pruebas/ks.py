import json
import numpy as np

def ks_critical_classic_table(n, alpha):
    # Calcula valores críticos usando la fórmula clásica de las tablas KS
    if alpha == 0.20:
        c_alpha = 1.073
    elif alpha == 0.15:
        c_alpha = 1.138
    elif alpha == 0.10:
        c_alpha = 1.224
    elif alpha == 0.05:
        c_alpha = 1.358  # Este es el valor clave
    elif alpha == 0.01:
        c_alpha = 1.628
    elif alpha == 0.005:
        c_alpha = 1.731
    elif alpha == 0.002:
        c_alpha = 1.855
    elif alpha == 0.001:
        c_alpha = 1.950
    else:
        c_alpha = np.sqrt(-0.5 * np.log(alpha/2))
    
    return c_alpha / np.sqrt(n)

def kolmogorov_smirnov_test(data, k=10, alpha=0.05):
    n = len(data)
    
    data_sorted = sorted(data)
    
    minimo, maximo = data_sorted[0], data_sorted[-1]
    amplitud = (maximo - minimo) / k
    critical_value = ks_critical_classic_table(n, alpha)

    print(f"Valor crítico KS (tabla clásica) para n={n}, alpha={alpha}: {critical_value}")
    
    # Construcción de intervalos
    intervalos = [(minimo + i * amplitud, minimo + (i+1) * amplitud) for i in range(k)]
    
    # Resultados de intervalos
    intervalos_data = []
    frec_acum = 0 
    max_diferencia = 0
    diferencias = []
    
    for i, (ini, fin) in enumerate(intervalos, start=1):
        # Frecuencia observada
        if i == 1:
            # Primer intervalo incluye ambos límites
            frec = sum(ini <= x <= fin for x in data_sorted)
        else:
            # Otros intervalos excluyen límite inferior
            frec = sum(ini < x <= fin for x in data_sorted)
        
        frec_acum += frec
        
        # Probabilidad observada acumulada
        p_obt = frec_acum / n
        
        # Frecuencia esperada acumulada
        frec_esp_acum = (i / k) * n
        
        # Probabilidad esperada acumulada
        p_esp = i / k
        
        # Diferencia
        dif = abs(p_obt - p_esp)
        diferencias.append(dif)
        max_diferencia = max(diferencias)
        
        intervalos_data.append({
            "No": i,
            "Inicial": ini,
            "Final": fin,
            "frecuencia_obt": frec,
            "frecuencia_obt_acu": frec_acum,
            "P_Obt": p_obt,
            "frecuencia_esp_acu": frec_esp_acum,
            "P_Esp_A": p_esp,
            "Dif": dif
        })
    
    # Estructura del JSON con información de la prueba KS
    resultado = {
        "test_name": "Prueba KS",
        "sample_size": n,
        "intervals": k,
        "range": {
            "minimum": minimo,
            "maximum": maximo,
            "amplitude": amplitud,
        },
        "intervals_data": intervalos_data,
        "statistics": {
            "max_difference": max_diferencia, 
            "critical_value": critical_value
        },
        "decision": "Pasa la prueba de ks." if max_diferencia <= critical_value else "No pasa la prueba de ks.",
        "isApproved": str(max_diferencia <= critical_value)
    }
    
    return json.dumps(resultado, indent=4, ensure_ascii=False)