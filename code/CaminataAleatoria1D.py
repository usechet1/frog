# Simula la caminata aleatoria de una rana en 1D usando números
# pseudoaleatorios validados con pruebas estadísticas.
import json
import matplotlib.pyplot as plt
import os
import numpy as np
import time

from pruebas.generador import generar
from pruebas.prueba_de_medias import prueba_de_medias
from pruebas.prueba_de_varianza import prueba_de_varianza
from pruebas.prueba_chi2_2 import prueba_chi_cuadrado
from pruebas.ks import kolmogorov_smirnov_test
from pruebas.poker import poker_test_json
from pruebas.rachas import prueba_rachas

ARCHIVO_HISTORICO = "caminatas.json"

# Mapea el nombre de cada prueba con su función, para poder llamarlas dinámicamente
PRUEBAS_DISPONIBLES = {
    "medias": prueba_de_medias,
    "varianza": prueba_de_varianza,
    "chi": prueba_chi_cuadrado,
    "kolmogorov": kolmogorov_smirnov_test,
    "poker": poker_test_json,
    "rachas": prueba_rachas
}

def cargar_historico():
    # Lee el histórico de posiciones finales guardado en el JSON
    try:
        if os.path.exists(ARCHIVO_HISTORICO):
            with open(ARCHIVO_HISTORICO, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    except (json.JSONDecodeError, FileNotFoundError):
        print("Archivo de histórico corrupto o no encontrado. Creando nuevo histórico.")
        return []

def guardar_historico(posiciones_finales):
    # Escribe el histórico completo en el JSON
    try:
        with open(ARCHIVO_HISTORICO, 'w', encoding='utf-8') as f:
            json.dump(posiciones_finales, f, indent=2)
        return True
    except Exception as e:
        print(f"Error al guardar histórico: {e}")
        return False

def agregar_posicion_final_al_historico(posicion_final):
    # Añade una posición final al histórico y lo guarda
    historico = cargar_historico()
    historico.append(posicion_final)

    if guardar_historico(historico):
        print(f"\nPosición final guardada en el histórico: {posicion_final}")
        return True
    else:
        print("\nError al guardar la posición final en el histórico")
        return False

def generar_histograma_posiciones_finales():
    # Grafica un histograma con las posiciones finales de todas las simulaciones guardadas
    posiciones_finales = cargar_historico()

    if not posiciones_finales:
        print("\nNo hay datos para generar el histograma")
        return

    plt.figure(figsize=(10, 6))
    num_bins = min(20, len(set(posiciones_finales)))
    plt.hist(posiciones_finales, bins=num_bins, alpha=0.7, color='skyblue', edgecolor='black')

    media = np.mean(posiciones_finales)
    plt.axvline(media, color='red', linestyle='--', label=f'Media: {media:.2f}')

    plt.xlabel('Posición Final')
    plt.ylabel('Frecuencia')
    plt.title(f'Histograma de Posiciones Finales\n({len(posiciones_finales)} simulaciones)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    print(f"\nESTADÍSTICAS DE LAS POSICIONES FINALES:")
    print(f"  Total de simulaciones: {len(posiciones_finales)}")
    print(f"  Media: {np.mean(posiciones_finales):.3f}")
    print(f"  Desviación estándar: {np.std(posiciones_finales):.3f}")
    print(f"  Mediana: {np.median(posiciones_finales):.3f}")
    print(f"  Mínima: {min(posiciones_finales)}")
    print(f"  Máxima: {max(posiciones_finales)}")

def limpiar_historico():
    # Borra el histórico si el usuario escribe "CONFIRMAR"
    posiciones_finales = cargar_historico()

    if not posiciones_finales:
        print("\nNo hay datos para limpiar")
        return

    print(f"\nADVERTENCIA: Esta acción eliminará todas las {len(posiciones_finales)} posiciones finales guardadas")
    confirmacion = input("¿Está seguro de que desea limpiar el histórico? (escriba 'CONFIRMAR' para continuar): ")

    if confirmacion == "CONFIRMAR":
        if guardar_historico([]):
            print("Histórico limpiado exitosamente")
        else:
            print("Error al limpiar el histórico")
    else:
        print("Operación cancelada")

def menu_historico():
    while True:
        posiciones_finales = cargar_historico()

        print(f"\nMENÚ DE HISTÓRICO")
        print(f"{'='*30}")
        print(f"Simulaciones guardadas: {len(posiciones_finales)}")
        print("1. Generar histograma de posiciones finales")
        print("2. Limpiar histórico")
        print("3. Volver al menú principal")

        opcion = input("\nSeleccione una opción (1-3): ").strip()

        if opcion == "1":
            generar_histograma_posiciones_finales()
        elif opcion == "2":
            limpiar_historico()
        elif opcion == "3":
            break
        else:
            print("Opción inválida. Por favor, seleccione entre 1 y 3.")

def ejecutar_pruebas(datos, pruebas, alpha):
    # Corre cada prueba estadística que el usuario haya habilitado
    resultados = {}

    for nombre, info in pruebas.items():
        # Kolmogorov y chi-cuadrado necesitan el parámetro k
        if nombre == "kolmogorov" and info != False and nombre in PRUEBAS_DISPONIBLES:
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, k=info.get("k"), alpha=alpha)
        elif nombre == "chi" and info != False and nombre in PRUEBAS_DISPONIBLES:
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, k=info.get("k"), alpha=alpha)
        elif info and nombre in PRUEBAS_DISPONIBLES:
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, alpha=alpha)

    return resultados

def mostrar_resultados_pruebas(resultados):
    # Imprime el resultado de cada prueba y devuelve si todas pasaron
    print("\n=== RESULTADOS DE PRUEBAS ESTADÍSTICAS ===")

    pruebas_pasadas = 0
    total_pruebas = 0

    for nombre, resultado_json in resultados.items():
        try:
            resultado = json.loads(resultado_json)
            total_pruebas += 1

            aprobado = resultado.get("isApproved", "False").lower() == "true"
            if aprobado:
                pruebas_pasadas += 1
                status = "PASÓ"
            else:
                status = "NO PASÓ"

            print(f"\n{resultado['test_name']}: {status}")
            print(f"  Decisión: {resultado['decision']}")

            # Cada prueba guarda sus estadísticas con nombres distintos
            if 'statistics' in resultado:
                stats = resultado['statistics']

                if 'chi2_total' in stats:
                    print(f"  Chi² calculado: {stats['chi2_total']:.4f}")
                    print(f"  Chi² crítico: {stats['chi2_critico']:.4f}")
                elif 'max_difference' in stats:
                    print(f"  Diferencia máxima: {stats['max_difference']:.4f}")
                    print(f"  Valor crítico: {stats['critical_value']:.4f}")
                elif 'Chi2_calculado' in stats:
                    print(f"  Chi² calculado: {stats['Chi2_calculado']:.4f}")
                    print(f"  Valor crítico: {stats['critical_value']:.4f}")

        except json.JSONDecodeError:
            print(f"{nombre}: Error al procesar resultado")

    print(f"\nRESUMEN: {pruebas_pasadas}/{total_pruebas} pruebas pasadas")

    return pruebas_pasadas == total_pruebas

def obtener_parametros():
    # Pide al usuario los parámetros del generador congruencial lineal
    print("=== GENERACIÓN DE NÚMEROS PSEUDOALEATORIOS ===")
    print("Ingrese los parámetros para el generador congruencial lineal:")

    try:
        x_o = int(input("Semilla inicial (x_0): "))
        k = int(input("Parámetro k: "))
        c = int(input("Constante aditiva (c): "))
        g = int(input("Exponente de módulo (g) donde m = 2^g: "))
        n = int(input("Cantidad de números a generar: "))

        if n < 10:
            print("Advertencia: Se recomienda al menos 10 números para las pruebas estadísticas")

        return x_o, k, c, g, n

    except ValueError:
        print("Error: Ingrese solo números enteros")
        return obtener_parametros()

def configurar_pruebas():
    # Pregunta al usuario qué pruebas ejecutar y con qué parámetros
    print("\n=== CONFIGURACIÓN DE PRUEBAS ESTADÍSTICAS ===")
    print("¿Qué pruebas desea ejecutar? (s/n)")

    pruebas = {}

    pruebas["medias"] = input("Prueba de Medias (s/n): ").lower().startswith('s')
    pruebas["varianza"] = input("Prueba de Varianza (s/n): ").lower().startswith('s')
    pruebas["rachas"] = input("Prueba de Rachas (s/n): ").lower().startswith('s')
    pruebas["poker"] = input("Prueba de Póker (s/n): ").lower().startswith('s')

    if input("Prueba Chi-Cuadrado (s/n): ").lower().startswith('s'):
        k = int(input("  Número de intervalos (k): "))
        pruebas["chi"] = {"k": k}
    else:
        pruebas["chi"] = False

    if input("Prueba Kolmogorov-Smirnov (s/n): ").lower().startswith('s'):
        k = int(input("  Número de intervalos (k): "))
        pruebas["kolmogorov"] = {"k": k}
    else:
        pruebas["kolmogorov"] = False

    alpha = float(input("Nivel de significancia (alpha, ej: 0.05): ") or "0.05")

    return pruebas, alpha

def obtener_numero_pasos(max_pasos):
    # Pide el número de pasos, validando que no supere max_pasos
    while True:
        try:
            pasos = int(input(f"¿Cuántos pasos quiere que dé la rana? (máximo {max_pasos}): "))
            if 1 <= pasos <= max_pasos:
                return pasos
            else:
                print(f"Error: El número de pasos debe estar entre 1 y {max_pasos}")

        except ValueError:
            print("Error: Ingrese un número entero válido")

def simular_caminata(numeros_aleatorios, posicion_inicial=0, num_pasos=None):
    # Mueve la rana paso a paso: r >= 0.5 avanza, r < 0.5 retrocede
    if num_pasos is None:
        num_pasos = len(numeros_aleatorios)

    numeros_a_usar = numeros_aleatorios[:num_pasos]

    print(f"\n=== SIMULACIÓN DE CAMINATA ALEATORIA ===")
    print(f"Posición inicial: {posicion_inicial}")
    print(f"Probabilidad de avanzar: 0.5")
    print(f"Número de pasos a simular: {num_pasos}")
    print(f"Números disponibles: {len(numeros_aleatorios)}")

    posiciones = [posicion_inicial]
    posicion_actual = posicion_inicial

    print("\nPasos de la rana:")
    for i, numero in enumerate(numeros_a_usar):
        if numero >= 0.5:
            posicion_actual += 1
            movimiento = "→ (+1)"
        else:
            posicion_actual -= 1
            movimiento = "← (-1)"

        posiciones.append(posicion_actual)
        print(f"Paso {i+1:2d}: r={numero:.5f} {movimiento} → Posición: {posicion_actual}")

    return posiciones

def graficar_caminata(posiciones):
    # Grafica la trayectoria de la rana y muestra estadísticas finales
    pasos = list(range(len(posiciones)))

    plt.figure(figsize=(12, 6))
    plt.plot(pasos, posiciones, 'b-o', linewidth=2, markersize=4)
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Posición inicial')

    plt.xlabel('Número de Pasos')
    plt.ylabel('Posición de la Rana')
    plt.title('Caminata Aleatoria de una Rana')
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.annotate(f'Inicio\nPos: {posiciones[0]}',
                 xy=(0, posiciones[0]),
                 xytext=(5, posiciones[0]+0.5),
                 arrowprops=dict(arrowstyle='->', color='green'))

    plt.annotate(f'Final\nPos: {posiciones[-1]}',
                 xy=(len(posiciones)-1, posiciones[-1]),
                 xytext=(len(posiciones)-6, posiciones[-1]+0.5),
                 arrowprops=dict(arrowstyle='->', color='red'))

    plt.tight_layout()
    plt.show()

    print(f"\nESTADÍSTICAS DE LA CAMINATA:")
    print(f"  Posición inicial: {posiciones[0]}")
    print(f"  Posición final: {posiciones[-1]}")
    print(f"  Rango de posiciones: [{min(posiciones)}, {max(posiciones)}]")
    print(f"  Distancia total recorrida: {len(posiciones)-1} pasos")

def main():
    while True:
        print(f"\nMENÚ PRINCIPAL")
        print(f"{'='*30}")
        print("1. Nueva simulación")
        print("2. Ver/gestionar histórico")
        print("3. Salir")

        opcion = input("\nSeleccione una opción (1-3): ").strip()

        if opcion == "1":
            ejecutar_simulacion()
        elif opcion == "2":
            menu_historico()
        elif opcion == "3":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida. Por favor, seleccione entre 1 y 3.")

def ejecutar_simulacion():
    # Flujo completo: generar números, probarlos, simular y graficar
    tiempo_inicio = time.time()

    x_o, k, c, g, n = obtener_parametros()

    print(f"\nGenerando {n} números pseudoaleatorios...")
    df = generar(x_o, k, c, g, n)
    numeros = df['Ri'].tolist()
    print(f"Números generados exitosamente")
    print(f"Primeros 5 números: {numeros[:5]}")

    pruebas, alpha = configurar_pruebas()

    if any(pruebas.values()):
        print(f"\nEjecutando pruebas estadísticas...")
        resultados = ejecutar_pruebas(numeros, pruebas, alpha)

        todas_pasaron = mostrar_resultados_pruebas(resultados)

        if not todas_pasaron:
            print("\nADVERTENCIA: No todos los números pasaron las pruebas estadísticas")
            continuar = input("¿Desea continuar con la simulación de todos modos? (s/n): ")
            if not continuar.lower().startswith('s'):
                print("Simulación cancelada. Intente con otros parámetros.")
                return
    else:
        print("No se ejecutaron pruebas estadísticas")
        continuar = input("¿Desea continuar sin pruebas? (s/n): ")
        if not continuar.lower().startswith('s'):
            return

    print(f"\nIniciando simulación de caminata aleatoria...")
    posicion_inicial = int(input("Posición inicial de la rana (0): ") or "0")

    num_pasos = obtener_numero_pasos(len(numeros))

    posiciones = simular_caminata(numeros, posicion_inicial, num_pasos)

    print(f"\nGenerando gráfica...")
    graficar_caminata(posiciones)

    agregar_posicion_final_al_historico(posiciones[-1])

    tiempo_fin = time.time()
    tiempo_total = tiempo_fin - tiempo_inicio
    print(f"\nTiempo total de ejecución: {tiempo_total:.3f} segundos")
    print(f"Simulación completada exitosamente!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulación interrumpida por el usuario")
    except Exception as e:
        print(f"\nError inesperado: {e}")
