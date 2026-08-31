# Cómo ejecutar

## 1. Instalar dependencias

Se debe abrir una terminal en la carpeta del proyecto y correr:

```
pip install numpy pandas matplotlib scipy tabulate
```

`tabulate` es fácil de olvidar, pero sin él pandas falla al generar las tablas en markdown del reporte.

## 2. Ubicarse en `code/`

Se debe descomprimir el zip y entrar a la carpeta `code/` (ahí vive `rana_multidimensional.py` y la carpeta `pruebas/` con `generador_rapido.py`). Todos los comandos siguientes se corren desde ahí:

```
cd Caminata_aleatoria-main/code
```

## 3. Correr la prueba rápida primero

No se debe empezar por la corrida completa. Se debe correr:

```
python rana_multidimensional.py
```

Sin argumentos usa 5.000 pasos y 20 réplicas por defecto, tarda segundos y permite ver si algo falla (import, matplotlib, etc.) antes de invertir 15 minutos.

## 4. Revisar la carpeta `output/`

Debe haber aparecido:

- `1_histograma_1d.png`
- `2_trayectoria_heatmap_2d.png`
- `3_trayectoria_proyecciones_3d.png`
- `4_eficiencia_comparativa.png`
- `tabla_eficiencia.csv`
- `reporte_punto2.md`

Se deben abrir y confirmar que las imágenes no estén vacías o con errores visuales.

## 5. Hacer 3 verificaciones de sanidad

En la consola se debe buscar:

1. `P(retorno en 2 saltos)=0.5` y en 3 saltos `=0.0` — son fórmulas fijas, siempre deben salir así.
2. En el histograma 1D, `sigma_empirica` debe estar cerca de `sigma_TCL` (= raíz de `n_pasos`).
3. En la tabla de eficiencia, `prob_retorno_origen_1000_pasos` normalmente sale 1D ≥ 2D ≥ 3D, aunque con pocas réplicas el ruido estadístico puede alterar el orden — con 100 réplicas se estabiliza.

## 6. Correr la simulación final

Cuando la prueba rápida se vea bien, se debe correr la versión que exige el taller:

```
python rana_multidimensional.py --pasos 1000000 --simulaciones 100
```

Tarda entre 12 y 15 minutos (lo medimos). No se debe cerrar la terminal ni poner la laptop a dormir mientras corre.

## 7. Reunir la evidencia para el informe

El taller pide capturas de pantalla de la ejecución y de los gráficos. Se debe tomar pantallazo de:

- La consola con las probabilidades y la tabla de eficiencia impresas.
- Cada uno de los 4 PNG generados.

Se debe usar `reporte_punto2.md` como base de texto y completar ahí los TODO con el análisis propio antes de pasarlo al informe IEEE.

> Se utilizó un asistente de IA para generar un borrador inicial de la estructura y redacción de este README a partir del funcionamiento real del programa de simulación propio. Cada instrucción y cada paso descrito fue revisado, verificado y ajustado según el criterio técnico propio.
