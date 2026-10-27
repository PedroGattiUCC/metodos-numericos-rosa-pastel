# Modelado Numérico del Resurgimiento de 'Rosa Pastel' (Belanova)

Proyecto integrador de la cátedra **Métodos Numéricos** — **Universidad Católica de Córdoba (UCC)**.  
**Comisión:** 46324 — **Ciclo Lectivo:** 2026-2  
**Docente:** Ing. Carlos Arnaudo  

---

## 👥 Integrantes del Equipo

- **Pedro Gatti** ([@PedroGattiUCC](https://github.com/PedroGattiUCC))
- **Facundo Grillo**
- **Gonzalo Marin**

---

## 🎯 Objetivo del Proyecto

Modelar numéricamente el fenómeno viral y resurgimiento de la canción *"Rosa Pastel"* del grupo mexicano **Belanova** en **Spotify México** durante 2023, a partir del auge generado por tendencias en TikTok.

A través de herramientas numéricas fundamentales, el trabajo aborda tres interrogantes clave:
1. **Modelado continuo:** ¿Cómo representar matemáticamente la trayectoria de reproducciones acumuladas a partir de datos discretos semanales?
2. **Cálculo de hitos:** ¿En qué momento exacto se superó la barrera histórica de los **100 millones de reproducciones**?
3. **Dinámica y pico viral:** ¿Cuál fue el ritmo instantáneo de reproducciones y en qué semana se alcanzó la tasa máxima de viralidad?

---

## 🔬 Métodos Numéricos Implementados

### 1. Ajuste de Curvas por Mínimos Cuadrados (Regresión Polinómica Cúbica)
- **Modelo:** $S(t) = a\,t^3 + b\,t^2 + c\,t + d$
- Resolución del sistema de ecuaciones normales para minimizar la suma de cuadrados de los residuos ($S_r$), mediante **eliminación gaussiana** programada a mano (triangulación y sustitución hacia atrás).
- Evaluación de bondad de ajuste mediante coeficiente de determinación ($R^2$) y error estándar de la estimación ($S_{y/x}$).
- Control de validez física: el modelo debe ser creciente ($S'(t) > 0$) en todo el período.

### 2. Trazadora Cúbica Natural
- Modelo de contraste que pasa exactamente por todos los datos medidos (algoritmo de Burden-Faires, pasos 1 a 7).

### 3. Búsqueda de Raíces de Ecuaciones No Lineales
Resolución de $f(t) = S(t) - 100 = 0$ con una tolerancia de convergencia de $\varepsilon_a < 10^{-4}\,\%$, sobre la regresión y sobre la trazadora:
- **Método de Bisección (Cerrado):** Búsqueda sistemática por intervalo con convergencia lineal garantizada.
- **Método de Newton-Raphson (Abierto):** Método iterativo $t_{i+1} = t_i - \frac{f(t_i)}{f'(t_i)}$ con convergencia cuadrática.
- **Control:** interpolación lineal entre las dos semanas que encierran el cruce.
- **Precisión real:** incertidumbre que el ajuste traslada al tiempo, $\Delta t \approx S_{y/x} / S'(t^*)$.
- Comparación cuantitativa de velocidad y número de iteraciones requeridas.

### 4. Diferenciación Numérica
- Estimación del ritmo semanal de streams $S'(t) \approx \frac{dS}{dt}$ utilizando fórmulas de diferencias finitas:
  - **Diferencia finita hacia adelante:** $O(h)$
  - **Diferencia finita hacia atrás:** $O(h)$
  - **Diferencia finita centrada:** $O(h^2)$
- Determinación analítica y numérica del pico de viralidad mediante la anulación de la segunda derivada ($S''(t) = 0$).

---

## 📊 Resultados Principales

- **Bondad de ajuste:** $R^2 \approx 99.95\%$ ($S_{y/x} \approx 0.927\text{ M}$ streams).
- **Hito de 100 Millones:**
  - **Bisección:** alcanzó la raíz de la regresión en **15 iteraciones** ($t^* \approx 35.52\text{ semanas}$).
  - **Newton-Raphson:** alcanzó la misma precisión en sólo **3 iteraciones**.
  - **Trazadora cúbica natural:** $t^* \approx 35.124\text{ semanas}$ (≈ 29/09/2023), igual a la interpolación lineal de control ($35.127$).
  - **Precisión:** la regresión se aparta 2.77 días de la trazadora, más que su incertidumbre $\Delta t \approx \pm 1.92$ días, por lo que se adopta el resultado de la trazadora.
- **Pico del ritmo de viralidad:** semana 26 (fines de julio de 2023), alcanzando una tasa de $4.171\text{ millones de streams/semana}$ en los datos ($t \approx 30.59\text{ semanas}$ según el modelo cúbico).

---

## 🔄 Generalización a Otras Canciones

A pedido de la cátedra para evaluar la aplicabilidad del método como herramienta general de ingeniería, el flujo se modularizó mediante la función `analizar_cancion(nombre, csv, meta)`. Se contrastó el resurgimiento gradual de *Rosa Pastel* frente a dos estrenos comerciales masivos:

| Canción | Semanas (desde) | Total M | R² | Sy/x M | Hito 100 M (semana, Newton) | Iter. bis./Newton | Pico modelo | Pico datos | Diagnóstico |
|---|---|---|---|---|---|---|---|---|---|
| Rosa Pastel (Belanova) | 47 (26/01/2023) | 132.9 | 0.999533 | 0.927 | 35.52 (≈1/10/2023) | 15 / 3 | semana 30.59 | semana 26, 4.171 M | aplica |
| Ella Baila Sola (Eslabón Armado y Peso Pluma) | 52 (23/03/2023, estreno) | 409.6 | 0.996265 | 6.656 | 3.55 (≈16/04/2023) | 19 / 3 | no detecta (a = +0.005926) | semana 5, 26.140 M | no aplica |
| Tití Me Preguntó (Bad Bunny) | 52 (12/05/2022, estreno) | 298.3 | 0.999692 | 1.596 | 9.87 (≈20/07/2022) | 17 / 3 | no detecta (a = +0.000279) | semana 6, 9.860 M | no aplica |

### 🛠️ Cómo analizar otra canción

Para incorporar y procesar una nueva canción con el método generalizado:

1. **Descargar serie temporal:** Bajar el historial semanal de Spotify desde [Kworb.net](https://kworb.net/spotify/) para el país y canción deseada.
2. **Crear archivo CSV en `CODIGO/datos/`:** Guardar el archivo en esa carpeta (ej. `CODIGO/datos/mi_cancion.csv`) con el formato estándar `fecha,streams` (fechas ISO `YYYY-MM-DD` separadas por 7 días y reproducciones semanales enteras).
3. **Agregar la canción a la lista del script:** En `CODIGO/analisis_resurgimiento_rosa_pastel.py`, añadir una línea a la lista `CANCIONES` (las rutas son relativas a `CODIGO/`):
   ```python
   CANCIONES = [
       ("Rosa Pastel (Belanova)", "datos/rosa_pastel_belanova.csv"),
       # ...
       ("Nombre Canción (Artista)", "datos/mi_cancion.csv"),
   ]
   ```
4. **Ejecutar el script:** Al correr `python3 CODIGO/analisis_resurgimiento_rosa_pastel.py`, el sistema ajustará automáticamente la regresión cúbica, resolverá el hito de streams (bisección y Newton-Raphson, sobre la regresión y la trazadora), calculará las diferencias finitas, validará la regla de concavidad ($a < 0$) y actualizará `CODIGO/comparacion_canciones.csv` y los gráficos de `GRAFICOS/`.

---

## 📁 Estructura del Repositorio

```text
├── CODIGO/
│   ├── analisis_resurgimiento_rosa_pastel.py           # Script principal modularizado y generalizado
│   ├── comparacion_canciones.csv                       # Tabla comparativa de resultados entre canciones
│   └── datos/                                          # Series temporales semanales en formato CSV (kworb.net)
│       ├── ella_baila_sola_eslabon_armado_peso_pluma.csv
│       ├── rosa_pastel_belanova.csv
│       └── titi_me_pregunto_bad_bunny.csv
├── ENTREGABLES/
│   ├── Informe_Proyecto_Metodos_Numericos_Rosa_Pastel.docx  # Informe técnico completo del proyecto
│   ├── Modelo_Numerico_Rosa_Pastel_Belanova.xlsx            # Planilla Excel con cálculos y tablas paso a paso
│   └── Presentacion_Rosa_Pastel_Metodos_Numericos.pptx      # Presentación PowerPoint (14 diapositivas)
├── GRAFICOS/                                           # Generados por el script
│   ├── grafico_1_ajuste_curva_streams.png              # Ajuste cúbico, trazadora y corte en 100M
│   ├── grafico_2_convergencia_biseccion_vs_newton.png  # Comparativa de convergencia (escala log)
│   ├── grafico_3_derivada_tasa_viralidad.png           # Diferenciación numérica y pico de viralidad
│   └── grafico_4_comparacion_canciones.png             # Derivadas y picos de las tres canciones
├── requirements.txt                                    # Dependencias del entorno Python
└── README.md                                           # Documentación general
```

---

## 🚀 Requisitos e Instalación

Para ejecutar el código de simulación y reproducir los resultados:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/PedroGattiUCC/metodos-numericos-rosa-pastel.git
   cd metodos-numericos-rosa-pastel
   ```

2. **Crear y activar un entorno virtual (opcional pero recomendado):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar el análisis:**
   ```bash
   python3 CODIGO/analisis_resurgimiento_rosa_pastel.py
   ```

---

## 📚 Fuentes de Datos

- **Spotify Charts México (Kworb.net):**
  - Track *Rosa Pastel* de Belanova: [kworb.net/spotify/track/6Z0ybnsUBhbZ9ZjPW64eoF.html](https://kworb.net/spotify/track/6Z0ybnsUBhbZ9ZjPW64eoF.html)
  - Track *Ella Baila Sola* de Eslabón Armado y Peso Pluma: [kworb.net/spotify/track/3qQbCzHBycnDpGskqOWY0E.html](https://kworb.net/spotify/track/3qQbCzHBycnDpGskqOWY0E.html)
  - Track *Tití Me Preguntó* de Bad Bunny: [kworb.net/spotify/track/1IHWl5LamUGEuP4ozKQSXZ.html](https://kworb.net/spotify/track/1IHWl5LamUGEuP4ozKQSXZ.html)
- **Bibliografía:** Chapra, S. C., & Canale, R. P. *Métodos Numéricos para Ingenieros*. McGraw-Hill.
