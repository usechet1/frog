import json
from collections import Counter
import scipy.stats as stats

# Clasifica los 5 dígitos decimales de cada número como una "mano de poker"
# (par, full, tercia, etc.) y usa chi-cuadrado para comparar las frecuencias
# observadas de cada mano contra las esperadas teóricamente.

def poker_test_json(datos, alpha=0.05):
    n = len(datos)

    # Probabilidad teórica de cada patrón de dígitos
    probs = {
        "D": 0.3024,   # Todos diferentes
        "O": 0.504,    # Un par
        "T": 0.108,    # Dos pares
        "K": 0.072,    # Tercia
        "F": 0.009,    # Full
        "P": 0.0045,   # Poker
        "Q": 0.0001    # Quintilla
    }

    def classify(num):
        # Toma los 5 dígitos decimales del número
        num_str = f"{num:.5f}"
        digits_part = num_str.split('.')[1]

        if len(digits_part) >= 5:
            digits = list(digits_part[:5])
        else:
            digits = list(digits_part.ljust(5, '0'))

        # Cuenta cuántas veces se repite cada dígito
        counts = sorted(Counter(digits).values(), reverse=True)

        if counts == [5]:
            return "Q"
        elif counts == [4, 1]:
            return "P"
        elif counts == [3, 2]:
            return "F"
        elif counts == [3, 1, 1]:
            return "K"
        elif counts == [2, 2, 1]:
            return "T"
        elif counts == [2, 1, 1, 1]:
            return "O"
        else:
            return "D"

    observed = {cat: 0 for cat in probs}
    for num in datos:
        cat = classify(num)
        observed[cat] += 1

    expected = {cat: n * p for cat, p in probs.items()}

    categories_data = []
    suma_chi2 = 0

    for cat in ["D", "O", "T", "K", "F", "P", "Q"]:
        oi = observed[cat]
        prob = probs[cat]
        ei = expected[cat]

        chi2_component = ((oi - ei)**2) / ei if ei > 0 else 0

        categories_data.append({
            "Cat": cat,
            "Oi": oi,
            "Prob": prob,
            "Ei": ei,
            "(Oi-Ei)^2/Ei": chi2_component
        })

        suma_chi2 += chi2_component

    chi2_critical = stats.chi2.ppf(1 - alpha, 6)
    pasa_prueba = suma_chi2 <= chi2_critical

    result = {
        "test_name": "Prueba de Poker",
        "intervals_data": categories_data,
        "statistics": {
            "n": n,
            "Chi2_calculado": suma_chi2,
            "critical_value": chi2_critical,
            "grados_libertad": 6
        },
        "decision": "Pasa la prueba de poker." if pasa_prueba else "No pasa la prueba de poker.",
        "isApproved": str(pasa_prueba)
    }
    return json.dumps(result, indent=4, ensure_ascii=False)
