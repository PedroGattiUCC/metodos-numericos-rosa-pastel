# Guía de defensa — "Rosa Pastel" (Métodos Numéricos 2026-2)

> Documento de estudio para el grupo. **No subirlo al Drive.** Versión final (28/10), al día con la presentación de 14 diapositivas.

---

## 0. Qué leer la noche anterior (en este orden)
1. La presentación completa (`ENTREGABLES/…pptx`).
2. Esta guía: secciones 1 (la historia), 2 (números), 3 (cada método) y 5 (preguntas).
3. La sección 6 (el script): cada uno, las funciones de su parte.
4. El informe, solo una mirada por arriba.

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

## 4. Guion (15 min, 3 personas; el reparto es el del guion de Facu, en `DOCS/`)

| Min | Diap. | Quién | Qué |
|---|---|---|---|
| 0–5 | 1–5 | Pedro | Caso (TikTok 2023), por qué es ingeniería (pronóstico de demanda), datos reales de kworb, mínimos cuadrados + Gauss y R² |
| 5–10 | 6–9 | Facundo | Hito: bisección vs. Newton (una iteración a mano), trazadora e incertidumbre, convergencia, derivadas y pico |
| 10–15 | 10–14 | Gonzalo | Ancho de banda, generalización (global vs. local), limitaciones y conclusiones |

Muestren ustedes las limitaciones antes de que pregunten.

> **Ojo con el guion de Facu (`DOCS/Guion de la exposición`):** en la diapositiva 11 dice que "el pico solo se detecta en Rosa Pastel" y que "los estrenos arrancan en su pico". Eso era antes de la regresión local. Gonzalo tiene que decir lo de la sección 3.7 de esta guía: con la cúbica global el pico solo sale en Rosa Pastel; con la cúbica local (±6 semanas) sale en las tres. Los estrenos llegan al pico en la semana 5–6, no en la 0.

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

## 6. Cómo funciona el script (`CODIGO/analisis_resurgimiento_rosa_pastel.py`)

Se corre con `python3 CODIGO/analisis_resurgimiento_rosa_pastel.py`. Imprime todas las tablas (datos, sistema 4×4, iteraciones, diferencias, comparación, dimensionamiento) y guarda los 5 gráficos en `GRAFICOS/` y la tabla `CODIGO/comparacion_canciones.csv`. Son unas 700 líneas, pero los métodos son 10 funciones cortas; el resto es imprimir y graficar.

**Lo primero que van a preguntar: "¿qué hicieron ustedes y qué hizo una librería?"**
- **A mano:** eliminación gaussiana, ecuaciones normales, trazadora, bisección, Newton-Raphson y diferencias finitas.
- **NumPy solo para cuentas auxiliares:** vectores, sumatorias (`np.sum`), acumulado (`np.cumsum`) y evaluar/derivar un polinomio ya calculado (`np.poly1d`, `.deriv()`). **No se usa `np.polyfit` ni `np.linalg.solve`**: el sistema lo resuelve nuestra función.
- **Matplotlib:** solo para los gráficos.

### 6.1 Arriba del archivo: la configuración
- `CANCIONES`: lista de (nombre, CSV). **Para analizar otra canción se agrega una línea acá** y un CSV en `datos/` con `fecha,streams`.
- `TOLERANCIA = 1e-4`: el criterio de parada |εa| < 10⁻⁴ %.
- `VENTANA_PICO = 6`: semanas a cada lado del pico para la cúbica local.
- Supuestos de ingeniería: `DURACION_S = 186` (3:06), `BITRATES_KBPS = (96, 160, 320)`, `FACTOR_HORA_PICO = 2`, `CAPACIDAD_MBPS = 150`.

### 6.2 Las funciones, una por una (en el orden del archivo)

| Función | Qué hace | Lo que tienen que poder explicar |
|---|---|---|
| `cargar_csv(ruta)` | Lee el CSV, ignora las líneas `#` y pasa los streams a millones. | Controla que no haya streams negativos y que las fechas estén separadas por 7 días (si no, h ≠ 1 y las diferencias finitas estarían mal). |
| `error_porcentual(nuevo, anterior)` | \|εa\| = \|(nuevo − anterior)/nuevo\| · 100. | Es el criterio de parada de bisección y Newton. Si nuevo = 0 evita dividir por cero. |
| `eliminacion_gaussiana(A, b)` | Arma la matriz ampliada [A \| b]. **Triangulación:** para cada fila i y cada fila k debajo, m_ki = a_ki / a_ii y fila_k = fila_k − m_ki · fila_i. **Sustitución hacia atrás:** x_i = (b_i − Σ a_ij x_j) / a_ii, desde la última fila hacia arriba. | Sin pivoteo; solo frena si un pivote es exactamente 0. La matriz está mal condicionada (κ ≈ 2,3·10¹⁰) pero da igual que NumPy hasta 10⁻¹². |
| `regresion_polinomica(x, y, m)` | Arma las **ecuaciones normales**: A[j][k] = Σ x^(j+k) y b[j] = Σ x^j · y, para j, k = 0..m, y llama a Gauss. | Con m = 3 es el sistema 4×4. Devuelve [d, c, b, a] (de menor a mayor grado); por eso después se invierte con `[::-1]`. |
| `pico_local(t, S, centro, w)` | Toma solo las semanas [centro − w, centro + w] (recortadas a [0, n−1]), ajusta ahí la cúbica con `regresion_polinomica` y calcula t = −b/(3a) y el ritmo S'(t) = 3at² + 2bt + c. | **Es la generalización.** Es válido si a < 0 y t cae dentro de la ventana. Exige al menos 4 puntos (4 incógnitas). |
| `trazadora_cubica_natural(x, y)` | Algoritmo de Burden-Faires, pasos 1 a 6: h_i (paso 1), α_i (paso 2), sistema tridiagonal resuelto con l, μ, z (pasos 3 a 5) y coeficientes b, c, d de cada tramo (paso 6). | Cada tramo es S_i(x) = a_i + b_i(x−x_i) + c_i(x−x_i)² + d_i(x−x_i)³, con a_i = dato. "Natural" = c en los extremos vale 0 (S'' = 0). |
| `evaluar_trazadora(coefs, nodos, x, derivada)` | Paso 7: busca en qué tramo cae x y evalúa el polinomio, o su 1.ª o 2.ª derivada. | Sirve para hacer bisección y Newton sobre la trazadora (Newton usa la derivada del tramo). |
| `biseccion(f, a, b)` | Verifica el cambio de signo (si no, error). Repite: xr = (a+b)/2; si f(a)·f(xr) < 0 → b = xr, si no → a = xr; corta cuando \|εa\| < tolerancia. Máximo 100 iteraciones. | Devuelve la raíz, las iteraciones y la tabla. Si no converge devuelve `None` en lugar de una raíz falsa. |
| `newton_raphson(f, df, x0, limite)` | Repite x_{i+1} = x_i − f(x_i)/f'(x_i) hasta \|εa\| < tolerancia. Máximo 50 iteraciones. | **Controles:** corta si f'(x) ≈ 0 (tangente horizontal) o si el nuevo x se sale de las semanas medidas [0, n−1]. |
| `diferencias_finitas(S)` | Para cada semana: adelante S(i+1) − S(i), atrás S(i) − S(i−1), centrada [S(i+1) − S(i−1)]/2 (h = 1). | En la primera semana la centrada usa adelante y en la última usa atrás (no hay vecino). Atrás = streams de esa semana. |
| `analizar_cancion(nombre, csv, meta)` | **El corazón:** junta todo para una canción (ver 6.3). | Devuelve un diccionario con todos los resultados; con `detalle=True` imprime las tablas (solo para Rosa Pastel). |
| `mbps`, `megabits_por_reproduccion`, `streams_para_mbps` | Conversiones: una reproducción = kbps × 186 s / 1000 megabits; Mbps = streams/semana × megabits ÷ 604 800 s. | Es regla de tres; los supuestos están arriba del archivo. |
| `dimensionamiento(r)` | Pasa la capacidad C = 150 Mbps a streams por semana y resuelve **g(t) = S'(t) − C = 0** con bisección y Newton (g' = S''). Busca una raíz a cada lado del pico. Calcula también Mbps del pico y TB transferidos. | La raíz izquierda es cuándo la demanda **supera** la capacidad (2/06) y la derecha cuándo **vuelve a bajar** (23/11). Newton arranca en el extremo lejano al pico, porque en el pico S'' = 0 y Newton dividiría por cero. |
| `main()` | Recorre `CANCIONES`: Rosa Pastel con todo el detalle, sus gráficos 1, 2, 3 y 5 y el dimensionamiento; después la tabla comparativa y el gráfico 4. | El dimensionamiento se hace solo para Rosa Pastel porque la duración (3:06) es de esa canción. |

Las funciones `imprimir_*`, `graficar_*`, `fila_comparativa` y `guardar_comparacion` solo muestran resultados: no calculan nada nuevo.

### 6.3 Qué hace `analizar_cancion`, paso a paso
1. Lee el CSV y arma t = 0, 1, …, n−1 y el acumulado S = suma acumulada de los streams.
2. **Regresión cúbica:** ecuaciones normales + Gauss → a, b, c, d. Calcula Sr, St, R² y Sy/x = √(Sr/(n − 4)).
3. **Validez física:** comprueba que S'(t) > 0 en todo el período (un acumulado no puede bajar).
4. **Trazadora** sobre los mismos datos.
5. **Diferencias finitas** → semana del pico de los datos (la de más streams).
6. **Pico global:** t = −b/(3a), válido si a < 0 y 0 ≤ t ≤ n−1. **Pico local** con ±6 semanas, y sensibilidad con ±4, ±6 y ±8.
7. **Hito de la meta (100 M):** busca la primera semana k en la que S ≥ 100 → intervalo [k−1, k]. Hace la interpolación lineal de control. Si la regresión no cambia de signo en ese intervalo (pasa en Tití, porque la curva no pasa por los puntos), busca el intervalo donde sí cambia el signo **del modelo**.
8. **Bisección y Newton** sobre la regresión (x₀ = extremo izquierdo). Calcula la fecha y la incertidumbre Δt = Sy/x ÷ S'(t*).
9. **Bisección y Newton sobre la trazadora** en [k−1, k] (la trazadora siempre pasa por los datos, así que ahí siempre cambia de signo).
10. **Diagnóstico:** "global y local", "solo local", "solo global" o "no aplica", según qué picos son válidos.

### 6.4 Si piden "mostrame dónde está X en el código"
| Les preguntan por… | Vayan a… |
|---|---|
| El sistema 4×4 | `regresion_polinomica` (lo arma) y `eliminacion_gaussiana` (lo resuelve) |
| El criterio de parada | `TOLERANCIA` y `error_porcentual` |
| Por qué no diverge Newton | Los dos `break` de `newton_raphson` |
| El pico y la regla a < 0 | `t_pico` y `pico_valido` en `analizar_cancion`, y `pico_local` |
| El ancho de banda | `mbps` y `dimensionamiento` |
| Agregar una canción | `CANCIONES` y la carpeta `CODIGO/datos/` |

### 6.5 El Excel (`ENTREGABLES/Modelo_Numerico_Rosa_Pastel_Belanova.xlsx`)
Los mismos cálculos de Rosa Pastel con fórmulas de Excel, al estilo de las planillas de clase, en 5 hojas: **Datos** (fecha, t, streams y acumulado con fórmula), **Regresion** (coeficientes, S del modelo y residuos), **Biseccion** y **Newton** (una fila por iteración) y **Derivadas** (adelante, atrás y centrada). Sirve para mostrar una iteración "a mano" si la profe la pide.

---

## 7. Archivos
- `CODIGO/`: el script y los datos (`datos/*.csv`, una canción por archivo).
- `GRAFICOS/`: los 5 gráficos que genera el script.
- `ENTREGABLES/`: informe (docx y pdf), presentación (pptx y pdf) y el Excel.
- `DOCS/`: el guion y la guía de estudio de Facu, en PDF (ver el aviso de la sección 4).

**Fuentes:** [kworb.net — Rosa Pastel](https://kworb.net/spotify/track/6Z0ybnsUBhbZ9ZjPW64eoF.html) · [Chilango (2023)](https://www.chilango.com/agenda/otros/rosa-pastel-tiktok-tendencia/)
