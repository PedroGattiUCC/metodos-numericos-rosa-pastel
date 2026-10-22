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
- Resolución del sistema de ecuaciones normales para minimizar la suma de cuadrados de los residuos ($S_r$).
- Evaluación de bondad de ajuste mediante coeficiente de determinación ($R^2$) y error estándar de la estimación ($S_{y/x}$).

### 2. Búsqueda de Raíces de Ecuaciones No Lineales
Resolución de $f(t) = S(t) - 100 = 0$ con una tolerancia de convergencia de $\varepsilon_a < 10^{-4}\,\%$:
- **Método de Bisección (Cerrado):** Búsqueda sistemática por intervalo con convergencia lineal garantizada.
- **Método de Newton-Raphson (Abierto):** Método iterativo $t_{i+1} = t_i - \frac{f(t_i)}{f'(t_i)}$ con convergencia cuadrática.
- Comparación cuantitativa de velocidad y número de iteraciones requeridas.

### 3. Diferenciación Numérica
- Estimación del ritmo semanal de streams $S'(t) \approx \frac{dS}{dt}$ utilizando fórmulas de diferencias finitas:
  - **Diferencia finita hacia adelante:** $O(h)$
  - **Diferencia finita hacia atrás:** $O(h)$
  - **Diferencia finita centrada:** $O(h^2)$
- Determinación analítica y numérica del pico de viralidad mediante la anulación de la segunda derivada ($S''(t) = 0$).

---

## 📊 Resultados Principales

- **Bondad de ajuste:** $R^2 \approx 99.8\%$ ($S_{y/x} \approx 0.72\text{ M}$ streams).
- **Hito de 100 Millones:**
  - **Bisección:** alcanzó la raíz en **18 iteraciones** ($t^* \approx 31.95\text{ semanas}$).
  - **Newton-Raphson:** alcanzó la misma precisión en sólo **4 iteraciones**.
- **Pico del ritmo de viralidad:** semana 27 a 29 (fines de julio / agosto 2023), alcanzando una tasa superior a los $4.1\text{ millones de streams/semana}$.

---

## 📁 Estructura del Repositorio

```text
├── analisis_resurgimiento_rosa_pastel.py      # Script principal con algoritmos numéricos y gráficos
├── grafico_1_ajuste_curva_streams.png          # Visualización del ajuste cúbico y corte en 100M
├── grafico_2_convergencia_biseccion_vs_newton.png # Comparativa de tasas de convergencia (escala log)
├── grafico_3_derivada_tasa_viralidad.png       # Diferenciación numérica y pico de viralidad
├── Informe_Proyecto_Metodos_Numericos_Rosa_Pastel.pdf  # Informe técnico completo del proyecto
├── Informe_Proyecto_Metodos_Numericos_Rosa_Pastel.docx # Formato editable del informe
├── Modelo_Numerico_Rosa_Pastel_Belanova.xlsx   # Planilla Excel con cálculos y tablas paso a paso
├── Presentacion_Rosa_Pastel_Metodos_Numericos.pdf      # Diapositivas de defensa del proyecto
├── Presentacion_Rosa_Pastel_Metodos_Numericos.pptx     # Presentación PowerPoint
├── requirements.txt                            # Dependencias del entorno Python
└── README.md                                   # Documentación general
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
   python3 analisis_resurgimiento_rosa_pastel.py
   ```

---

## 📚 Fuentes de Datos

- **Spotify Charts México (2023):** Datos semanales recopilados a través de [Kworb.net](https://kworb.net/spotify/track/6Z0ybnsUBhbZ9ZjPW64eoF.html) sobre el track *Rosa Pastel* de Belanova (47 semanas del año 2023).
- **Bibliografía:** Chapra, S. C., & Canale, R. P. *Métodos Numéricos para Ingenieros*. McGraw-Hill.
