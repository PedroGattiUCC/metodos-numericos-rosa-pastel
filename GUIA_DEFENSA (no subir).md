# Guía de defensa — "Rosa Pastel" (Métodos Numéricos 2026-2)

> Documento de estudio para el grupo. **No subirlo al Drive.** Versión final (28/10), al día con la presentación de 14 diapositivas.

---

## 0. Qué leer la noche anterior (en este orden)
1. La presentación completa (`ENTREGABLES/…pptx`).
2. Esta guía: secciones 1 (la historia), 2 (números), 3 (cada método) y 5 (preguntas).
3. El informe, solo una mirada por arriba.

Todos tienen que entender todo: la profe le pregunta a cualquiera.

---

## 1. La historia en 30 segundos
En 2023, "Rosa Pastel" (Belanova, 2006) se volvió viral por un trend de TikTok. Tomamos **47 semanas reales de streams de Spotify México** (kworb.net, que recopila los charts oficiales). El problema se plantea como **pronóstico de demanda de un servicio informático**: con métodos numéricos estimamos cuándo se cruza una meta, cuál es el ritmo de demanda y cuál es su pico, y eso se traduce a ancho de banda para dimensionar la red. Después generalizamos el método y lo probamos con otras dos canciones.

```
streams semanales w(t) ──► acumulado S(t)
   ├─ [1] Mínimos cuadrados (cúbica) → ecuaciones normales 4×4 → eliminación gaussiana
   ├─ [1b] Trazadora cúbica natural (pasa por los 47 datos) → modelo de contraste
   ├─ [2] Raíz de S(t) − 100 = 0 → Bisección y Newton-Raphson (sobre la regresión y la trazadora)
   ├─ [3] Diferencias finitas → ritmo S'(t) y pico (S'' = 0)
   ├─ [4] Ingeniería: ritmo → Mbps; acumulado → TB; S'(t) = C → ventana de saturación
   └─ [5] Generalización: regla a < 0 + regresión cúbica LOCAL alrededor del pico
```

---

## 2. Números que tienen que saber de memoria

| Qué | Valor |
|---|---|
| Datos | 47 semanas (26/01 al 14/12/2023), 132,9 M en total |
| Ajuste | **R² = 0,9995**, Sy/x = 0,93 M, Sr = 36,94 |
| Hito 100 M (regresión) | Bisección **15 it.**, Newton **3 it.**, t* = 35,52 sem (≈ 2/10) |
| Hito adoptado (trazadora) | **t* = 35,124 sem → 29/09/2023**; interpolación lineal 35,127 |
| Precisión | Δt = Sy/x ÷ S'(t*) ≈ ±1,92 días; la regresión se aparta 2,77 días → se adopta la trazadora |
| Pico de los datos | **Semana 26 (fines de julio), 4,17 M/sem** |
| Pico de la cúbica global | Semana 30,6, 3,44 M/sem (achata 18 %, corre ~4,6 sem) |
| Pico de la cúbica local (±6 sem) | Semana 28,6, 3,78 M/sem |
| Ancho de banda (160 kbps) | **≈ 205 Mbps** promedio en el pico (≈ 410 en hora pico); modelo 169 Mbps |
| Volumen | 100 M de streams ≈ **372 TB** |
| Capacidad de ejemplo 150 Mbps | Se supera del **2/06 al 23/11/2023** (semanas 18,18 a 42,99) |
| Condición del sistema 4×4 | κ₁ ≈ **2,3 × 10¹⁰** (mal condicionado) |

---

## 3. Lo que TIENEN que saber de cada método

### 3.1 Mínimos cuadrados + eliminación gaussiana (Chapra cap. 17; apunte 4 y tema de sistemas)
- **Idea:** se busca el polinomio que **minimiza** Sr = Σ(yᵢ − p(tᵢ))². No pasa por los puntos; queda lo más cerca posible de todos.
- **Ecuaciones normales:** se deriva Sr respecto de d, c, b y a, se iguala a 0 y queda un **sistema 4×4**. Las entradas son sumatorias de potencias de t (Σ1 = 47, Σt = 1081, …, Σt⁶ ≈ 1,7·10⁹).
- **Eliminación gaussiana a mano:** triangulación (hacer ceros debajo de la diagonal) + sustitución hacia atrás. Da lo mismo que NumPy con diferencias de 10⁻¹².
- **Condicionamiento:** las sumatorias van de 47 a 10⁹, así que la matriz está **mal condicionada** (κ₁ ≈ 2,3·10¹⁰, orden 10). Python trabaja con ~16 cifras: quedan ~6 cifras confiables, suficientes para los coeficientes. El código **no pivotea**: solo controla que ningún pivote sea cero. (Mejora posible: centrar t o pivoteo parcial.)
- **¿Por qué grado 3?** El acumulado primero acelera y después frena: necesita un **punto de inflexión**, y la cúbica es el polinomio de menor grado que lo tiene.
- **Métricas:** R² = 1 − Sr/St = 0,9995 · Sy/x = √(Sr/(n − 4)) = 0,93 M (n − 4 porque se estiman 4 coeficientes).
- **Validez física:** S'(t) > 0 en todo el período (el acumulado nunca baja).

### 3.2 Trazadora cúbica natural (Burden-Faires, apunte de interpolación)
- Una cúbica distinta en cada intervalo entre dos semanas, que **pasa exactamente por los 47 datos**, con primera y segunda derivada continuas. "Natural" = S'' = 0 en los extremos.
- Se arma con un sistema tridiagonal (pasos 1 a 7 del algoritmo).
- **Para qué la usamos:** como modelo de contraste para el hito. La regresión no pasa por los puntos y corre el cruce 2,77 días; la trazadora sí pasa y coincide con la interpolación lineal (diferencia de 0,4 horas).
- **¿Por qué no usar solo la trazadora?** Porque sigue el ruido semana a semana, son 46 tramos y no da una fórmula de tendencia ni un pico limpio. La regresión da la tendencia; la trazadora respeta los datos.

### 3.3 Bisección (método cerrado)
- **Requisito:** f continua y cambio de signo (Bolzano). S(35) = 99,60 < 100 < S(36) = 102,74.
- xr = (a + b)/2; se queda la mitad donde cambia el signo. Corte: |εa| < 10⁻⁴ %.
- **Convergencia lineal:** el intervalo se divide por 2; de 1 semana a ~3·10⁻⁵ en 15 pasos. Siempre converge, pero es lenta.

### 3.4 Newton-Raphson (método abierto)
- x_{i+1} = x_i − f(x_i)/f'(x_i) (recta tangente). Se puede usar porque f es un polinomio y f'(t) = S'(t) se conoce.
- **Ejemplo a mano:** x₀ = 35, f(35) = −1,7584, f'(35) = 3,3865 → x₁ = **35,5192**.
- **Convergencia cuadrática:** 3 iteraciones. Puede fallar si f' ≈ 0 o si x₀ está lejos.

| | Bisección | Newton-Raphson |
|---|---|---|
| Tipo | Cerrado | Abierto |
| Necesita | Cambio de signo | f'(x) y un buen x₀ |
| Convergencia | Lineal, garantizada | Cuadrática, no garantizada |
| Iteraciones | 15 | 3 |

### 3.5 Diferenciación numérica
- Adelante y atrás: error **O(h)**. Centrada: **O(h²)** (en Taylor se cancela el término de h²). En los extremos no hay centrada.
- Chequeo: la diferencia hacia atrás sobre S devuelve exactamente los streams de esa semana.
- **Pico:** S''(t) = 6at + 2b = 0 → t = −b/(3a) = 30,6 sem. El dato real es la semana 26: la regresión **suaviza** (achata 18 % y corre ~4,6 semanas).

### 3.6 Aplicación de ingeniería: dimensionamiento
- **Ancho de banda (sale del ritmo S'):** Mbps = streams/semana × (kbps × duración) ÷ 604 800 s. Supuestos: canción de 3:06 a 160 kbps (rango 96–320), hora pico = 2 × promedio, sin descontar descargas. Son **órdenes de magnitud**, no datos de Spotify.
- **Volumen (sale del acumulado S):** 100 M de streams ≈ 372 TB.
- **Ventana de saturación:** ¿cuándo la demanda supera una capacidad C? Se resuelve g(t) = S'(t) − C = 0 con **bisección y Newton** (g' = S''). Dos raíces: entra el 2/06 y sale el 23/11.
- **Conclusión de ingeniería:** hay que dimensionar con el pico medido (205 Mbps), no con el del modelo (169 Mbps), que lo subestima un 18 %.

### 3.7 Generalización: ¿sirve para cualquier canción?
**Por qué falla la cúbica global en los estrenos.** La derivada de una cúbica es una **parábola**: una sola joroba **simétrica**. Rosa Pastel sube durante meses y baja durante meses, con el pico en la mitad (semana 26 de 47): una parábola lo representa. En los estrenos (Ella Baila Sola, Tití Me Preguntó) el pico está en la **semana 5–6** y siguen ~46 semanas de caída lenta. Como mínimos cuadrados pesa igual todas las semanas, la parábola sigue la cola larga y termina abriendo hacia arriba: **a > 0**, y t = −b/(3a) es un **mínimo** del ritmo, no un máximo. Aun así el R² da 0,996–0,9997: **un R² alto no garantiza que el modelo sirva.**

**La solución: regresión cúbica local.** Mismo método, aplicado solo donde importa:
1. Diferencias finitas → semana m del pico de los datos.
2. Mínimos cuadrados (con la misma eliminación gaussiana) **solo en la ventana [m − 6, m + 6]**.
3. Mismo pico t = −b/(3a) y la misma regla (válido si a < 0 y cae dentro de la ventana).

| Canción | Pico datos | Cúbica global | Cúbica local (±6) | Sensibilidad (±4 / ±6 / ±8) |
|---|---|---|---|---|
| Rosa Pastel | sem. 26 | 30,6 | **28,6** | 27,0 / 28,6 / 29,8 |
| Ella Baila Sola | sem. 5 | no detecta (a > 0) | **3,8** | 4,0 / 3,8 / 2,8 |
| Tití Me Preguntó | sem. 6 | no detecta (a > 0) | **6,4** | 5,9 / 6,4 / 6,9 |

- En ventana, una joroba sí es simétrica, así que la parábola de S' la representa bien. En Rosa además da un pico más cercano al real que la global.
- **¿Por qué ±6 semanas?** Un trimestre (13 semanas) centrado en el pico. La tabla de sensibilidad muestra que con ±4 o ±8 el pico se mueve 1 o 2 semanas: el resultado es estable.
- **Lo que siempre fue general:** la trazadora + bisección/Newton para hitos, las diferencias finitas para el ritmo y el pico medido, y el ancho de banda.
- **Por qué es una herramienta de ingeniería:** entra la serie de cualquier contenido (CSV), sale cuándo se alcanza una meta, el pico y el ancho de banda. Además **valida el modelo** (regla a < 0) y, si la cúbica global no sirve, usa la local. No devuelve un pico falso.
- **Límites:** la local necesita que el pico esté dentro de los datos; no sirve para pronosticar un pico futuro, y la ventana es un parámetro elegido.

---

## 4. Guion (15 min, 3 personas)

| Min | Diap. | Quién | Qué |
|---|---|---|---|
| 0–4 | 1–4 | Integrante 1 | Caso (TikTok 2023), por qué es ingeniería (pronóstico de demanda), datos reales de kworb |
| 4–9 | 5–8 | Integrante 2 | Mínimos cuadrados + Gauss, R². Hito: bisección vs. Newton (una iteración a mano), trazadora e incertidumbre |
| 9–15 | 9–13 | Integrante 3 | Derivadas y pico, ancho de banda, generalización (global vs. local), limitaciones y conclusiones |

Muestren ustedes las limitaciones antes de que pregunten.

---

## 5. Preguntas probables (con respuesta)

1. **"¿Por qué esto es ingeniería?"** → Es pronóstico de demanda para dimensionar la red de un servicio: diapositiva 10 (205 Mbps, 372 TB, ventana de saturación). Y el método es reutilizable y se valida a sí mismo.
2. **"¿De dónde sacaron los datos?"** → kworb.net, historial de los charts semanales oficiales de Spotify México, 2023. Solo Spotify México y solo semanas en el Top 200.
3. **"¿Está bien condicionada la matriz?"** → No: κ₁ ≈ 2,3·10¹⁰. Con 16 cifras de precisión quedan ~6 confiables; alcanza. No pivoteamos; controlamos pivotes nulos. Se podría mejorar centrando t.
4. **"¿Por qué el modelo da 35,52 y la tabla cruza en 35,13?"** → La regresión no pasa por los puntos. Por eso hicimos la trazadora (35,124) y calculamos Δt ≈ ±1,9 días: la diferencia de 2,77 días es mayor, así que adoptamos la trazadora.
5. **"¿Por qué dos métodos de raíces?"** → Para compararlos: bisección es segura y lenta (lineal, 15 it.); Newton es rápido (cuadrático, 3 it.) pero necesita la derivada y un buen x₀.
6. **"¿Cómo eligieron el intervalo y x₀?"** → De la tabla: S cruza 100 entre las semanas 35 y 36. x₀ = 35, con f'(35) = 3,39 ≠ 0.
7. **"¿Cuántas iteraciones esperaban en bisección?"** → n ≥ log₂(ancho/tolerancia) ≈ 15.
8. **"¿Qué error tiene la diferencia centrada?"** → O(h²), por cancelación en Taylor.
9. **"¿Por qué grado 3 y no más?"** → Es el menor con punto de inflexión. Más grado oscila y no tiene un único pico.
10. **"¿Por qué el pico del modelo no coincide con el de los datos?"** → La regresión global suaviza. La local (±6 semanas) se acerca más: 28,6.
11. **"¿Sirve para cualquier canción?"** → Con la cúbica global, solo si a < 0. Con la regresión local, sí para las 3 probadas, siempre que el pico esté dentro de los datos (sección 3.7).
12. **"Si el R² es 0,9997, ¿por qué no servía?"** → El R² mide cercanía a los puntos acumulados, no si la forma tiene sentido. La derivada global volvía a subir al final.
13. **"¿Por qué una ventana de ±6?"** → Un trimestre centrado en el pico; con ±4 y ±8 cambia 1–2 semanas (sensibilidad).
14. **"¿Qué usaron de IA?"** → Lo que dice la declaración del informe (Claude y Gemini para programar, gráficos y redacción; los cálculos los verificamos). Tienen que poder explicar cada parte del script.

---

## 6. Archivos
- `CODIGO/analisis_resurgimiento_rosa_pastel.py`: el proyecto. `python3 CODIGO/analisis_resurgimiento_rosa_pastel.py` imprime todas las tablas y genera los gráficos de `GRAFICOS/`.
- `CODIGO/datos/*.csv`: una canción por archivo. Para agregar otra: un CSV + una línea en `CANCIONES`.
- `ENTREGABLES/`: informe (docx y pdf), presentación (pptx y pdf) y el Excel con fórmulas.

**Fuentes:** [kworb.net — Rosa Pastel](https://kworb.net/spotify/track/6Z0ybnsUBhbZ9ZjPW64eoF.html) · [Chilango (2023)](https://www.chilango.com/agenda/otros/rosa-pastel-tiktok-tendencia/)
