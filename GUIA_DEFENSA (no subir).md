# Guía de defensa — "Rosa Pastel" (Métodos Numéricos 2026-2)

> Documento de estudio para el grupo. **No subirlo al Drive.**

---

## 1. Qué estaba mal y qué se corrigió

| # | Problema en la versión anterior | Cómo quedó |
|---|---|---|
| 1 | **Los datos eran inventados.** La versión anterior decía que los streams "se relevaron de Spotify y YouTube", pero los números no coincidían con la realidad: el proyecto mostraba picos de 21,5 M/semana y el pico real en Spotify México fue de 4,17 M. Además, las referencias "Spotify for Artists" e "IFPI" no se podían verificar. | Ahora se usan **datos reales**: los streams semanales de Spotify México en 2023, tomados de kworb.net, que recopila los charts oficiales de Spotify. Son 47 semanas, del 26/01 al 14/12/2023. Se borraron las referencias falsas. |
| 2 | El hito de 100 M daba **después** de la semana en la que la tabla ya mostraba 102 M. | Se agregó un **control por interpolación lineal** y se explica la diferencia (2,75 días) como error del ajuste. |
| 3 | La cúbica "se daba vuelta" al final: los acumulados bajaban en la semana 12, cosa imposible. | Con los datos reales, S'(t) > 0 en todo el rango (0–46). Igual figura como limitación: no sirve para extrapolar. |
| 4 | La columna se llamaba "derivada exacta". | Ahora se llama "**Derivada del modelo S'(t)**", porque también es una aproximación. |
| 5 | Había frases exageradas ("Disco de Platino", "día, hora y minuto exactos", "fórmulas nativas"). | Se borraron y el lenguaje quedó simple. |

**Pertinencia del tema:** la consigna pide "una aplicación real en el ámbito de la ingeniería". Se justifica como ingeniería de datos/infraestructura: anticipar picos de demanda para dimensionar servidores. Es defendible, pero **consúltenlo con el profe** (sección 6).

---

## 2. Cómo se armó el proyecto

```
kworb.net (charts semanales de Spotify México) → 47 semanas de 2023
   streams semanales w(t)  →  acumulados S(t) = w(0) + … + w(t)
      │
      ├─► [1] Regresión cúbica por mínimos cuadrados → S(t) continua
      │       S(t) = −0,000839 t³ + 0,076977 t² + 1,081162 t + 2,072898
      │       R² = 0,99953   Sy/x = 0,93 M
      │
      ├─► [2] Raíz de f(t) = S(t) − 100 (¿cuándo se llega a 100 M?)
      │       Bisección [35, 36] → 15 iteraciones | Newton (t0 = 35) → 3 iteraciones
      │       t* = 35,52 semanas ≈ 1/10/2023   (control: interpolación lineal = 35,13)
      │
      └─► [3] Diferenciación numérica (adelante, atrás, centrada, h = 1 semana)
              Pico del modelo: S''(t) = 0 → t = −b/(3a) = 30,6 sem (≈ fines de agosto 2023), 3,44 M/sem
              Pico de los datos: semana 26 (27/07/2023), 4,17 M  ← coincide con el trend de TikTok de julio 2023
```

Archivos para entregar:
- `analisis_resurgimiento_rosa_pastel.py`: **es el proyecto.** Contiene los datos, hace los cálculos e imprime las tablas y los 3 gráficos. Se corre con `python3 analisis_resurgimiento_rosa_pastel.py` (necesita numpy y matplotlib).
- `Modelo_Numerico_Rosa_Pastel_Belanova.xlsx`: los mismos cálculos hechos con fórmulas de Excel.
- El informe y la presentación, en PDF.

La carpeta `no_subir/` tiene los scripts que generan el Word, el PowerPoint y el Excel. No son parte del método numérico.

---

## 3. Lo que TIENEN que saber de cada método

### 3.1 Regresión polinómica por mínimos cuadrados (Chapra cap. 17; apunte Arnaudo 4)
- **Idea:** se elige el polinomio que **minimiza** Sr = Σ(yᵢ − p(tᵢ))². El polinomio **no pasa por los puntos**; queda lo más cerca posible de todos a la vez.
- **Diferencia con la interpolación:** la interpolación (Newton, Lagrange) pasa exactamente por cada punto. Con 47 datos medidos, que tienen ruido, interpolar daría un polinomio de grado 46 que oscila muchísimo (fenómeno de Runge). La regresión da una curva suave que se puede derivar.
- **Cómo se calculan los coeficientes:** se deriva Sr respecto de a, b, c y d, se iguala a 0 y queda un **sistema lineal de 4 ecuaciones normales** (tema 3 de la materia). `np.polyfit` arma ese sistema y lo resuelve.
- **¿Por qué grado 3?** La curva acumulada primero acelera (cóncava hacia arriba) y después frena (cóncava hacia abajo). Ese cambio de concavidad necesita un **punto de inflexión**, y la cúbica es el polinomio de menor grado que lo tiene.
- **Métricas:** St = 79 137,6 · Sr = 36,94 · **R² = 1 − Sr/St = 0,99953** (explica el 99,95 % de la variación) · **Sy/x = √(Sr/(n − 4)) = 0,93 M**. Se divide por n − 4 porque se estimaron 4 coeficientes.
- **Ojo:** un R² alto en datos acumulados es "fácil", porque cualquier curva creciente ajusta bien. Lo importante es que el error típico (0,93 M) es chico comparado con 100 M.

### 3.2 Bisección (método cerrado; apunte Arnaudo 2)
- **Requisito:** f continua y **cambio de signo** en [a, b] (Bolzano). De la tabla: S(35) = 99,60 < 100 < S(36) = 102,74, así que f(35) < 0 < f(36).
- **Algoritmo:** xr = (a + b)/2. Si f(a)·f(xr) < 0, b = xr; si no, a = xr.
- **Criterio de corte:** |εa| = |(xr_nuevo − xr_viejo)/xr_nuevo|·100 < 10⁻⁴ %.
- **Convergencia lineal:** el intervalo se divide por 2 en cada paso. Partiendo de un intervalo de 1 semana, después de 15 pasos queda 1/2¹⁵ ≈ 3·10⁻⁵ semanas. Coincide con las 15 iteraciones.
- Siempre converge, pero es lenta.

### 3.3 Newton-Raphson (método abierto)
- **Fórmula:** x_{i+1} = x_i − f(x_i)/f'(x_i). Sale de la **recta tangente** (Taylor de primer orden).
- **Se puede usar** porque f es un polinomio y f'(t) = S'(t) se calcula exactamente.
- **Ejemplo a mano** (llévenlo preparado): x₀ = 35, f(35) = −1,7584, f'(35) = 3,3865 → x₁ = 35 + 1,7584/3,3865 = **35,5192**. Con una sola iteración ya tiene 3 cifras correctas.
- **Convergencia cuadrática:** εa pasa de 1,46 % a 0,0026 % y después a ≈ 0 en 3 iteraciones.
- **Puede fallar** si f'(x) ≈ 0 (tangente horizontal), si x₀ está lejos de la raíz o si no se conoce la derivada.

| | Bisección | Newton-Raphson |
|---|---|---|
| Tipo | Cerrado | Abierto |
| Necesita | Cambio de signo | f'(x) |
| Convergencia | Lineal, garantizada | Cuadrática, no garantizada |
| Iteraciones | 15 | 3 |
| Raíz | 35,520172 | 35,520148 |

### 3.4 Diferenciación numérica (apunte Arnaudo 5)
- Salen de Taylor: adelante [S(t+h) − S(t)]/h y atrás [S(t) − S(t−h)]/h tienen error **O(h)**. La centrada [S(t+h) − S(t−h)]/(2h) tiene error **O(h²)** porque, al restar los dos desarrollos, se cancela el término de h².
- En los extremos (t = 0 y t = 46) no se puede usar la centrada porque falta un vecino.
- **Dato curioso:** la diferencia hacia atrás sobre S(t) devuelve exactamente los streams de esa semana, porque S(t) − S(t−1) = w(t). Sirve como chequeo.
- **Pico:** el máximo de S'(t) está donde S''(t) = 6at + 2b = 0, es decir, t = −b/(3a) = **30,6 semanas**. Los datos tienen el pico en la semana 26 (27/07/2023, 4,17 M), justo cuando explotó el trend de TikTok. El modelo cúbico **suaviza**: corre el pico ~4 semanas y lo achata (3,44 M). Es una limitación honesta para mencionar.

### 3.5 Generalización a otras canciones (pedido de la profe)
El script ya no está atado a Rosa Pastel:
- cada canción es un CSV en `datos/` (fecha, streams);
- `analizar_cancion(nombre, csv, meta)` hace todo el análisis;
- agregar una canción = un CSV + una línea en la lista `CANCIONES`.

| Canción | R² | Hito 100 M | Iter. bis./Newton | Pico modelo | Pico datos | ¿Aplica? |
|---|---|---|---|---|---|---|
| Rosa Pastel (resurgimiento) | 0,9995 | sem. 35,52 | 15 / 3 | sem. 30,6 | sem. 26 | **sí** |
| Ella Baila Sola (estreno 2023) | 0,9963 | sem. 3,55 | 19 / 3 | no detecta | sem. 5 | no |
| Tití Me Preguntó (estreno 2022) | 0,9997 | sem. 9,87 | 17 / 3 | no detecta | sem. 6 | no |

**Lo que tienen que entender (y decir):**
- **Regla:** S''(t) = 6at + 2b = 0 da t = −b/(3a). Ese punto es un **máximo** del ritmo S'(t) solo si **a < 0** (la parábola S' abre hacia abajo) y si cae dentro de las semanas medidas. Con **a > 0**, la parábola abre hacia arriba y ese punto es un **mínimo**.
- **Rosa Pastel** sube despacio durante meses y después baja, que es la forma que la cúbica puede representar.
- **Los estrenos** arrancan casi en su pico y después solo bajan. La cúbica da a > 0 y su derivada **vuelve a subir al final** (en el gráfico 4, Ella Baila Sola), lo cual es irreal.
- **Lección clave: un R² de 0,9997 no garantiza que el modelo sirva.** El R² mide qué tan cerca pasa la curva de los puntos acumulados, no si su forma tiene sentido.
- **Lo que sí sirve para todas:** el hito de 100 M (bisección y Newton convergen siempre) y el pico de los datos por diferencias finitas.
- En Tití, los datos cruzan los 100 M entre las semanas 10 y 11, pero el modelo cruza entre 9 y 10. El programa lo detecta y usa el intervalo donde cambia el signo del **modelo**, porque Bolzano se aplica a f, que es el modelo.
- **Por qué es ingeniería:** es una herramienta reutilizable. Entra la demanda de cualquier contenido y sale cuándo se alcanza una meta y cuándo es el pico. Además **avisa cuando el modelo no sirve**, en lugar de dar un pico falso.
- **Mejora futura** (si preguntan): para los estrenos convendría un modelo de decaimiento exponencial w(t) = A·e^(−kt), que se ajusta por regresión lineal sobre ln(w). Está en el apunte de ajuste de curvas.

---

## 4. Guion para la exposición (15 min, 3 personas)

| Min | Quién | Qué |
|---|---|---|
| 0–3 | Integrante 1 | Problema: la canción vuelve a ser viral por TikTok en 2023. Por qué interesa: anticipar picos de demanda. Datos reales de kworb (Spotify México). |
| 3–6 | Integrante 1 | Regresión cúbica: por qué grado 3, gráfico 1, R² y Sy/x. |
| 6–10 | Integrante 2 | f(t) = S(t) − 100. Bisección y Newton, una iteración de Newton a mano, gráfico 2 y comparación. Control por interpolación. |
| 10–13 | Integrante 3 | Diferencias finitas, tabla de las semanas 24–27, pico del modelo frente al de los datos (gráfico 3). |
| 12–14 | Integrante 3 | **Generalización:** gráfico 4 y tabla de las 3 canciones. Regla a < 0 y "R² alto no alcanza". |
| 14–15 | Integrante 3 | Conclusiones y **limitaciones** (mostrarlas ustedes antes de que pregunten). |

(Para hacerle lugar a la generalización, acorten la parte de diferencias finitas a ~2 minutos.)

---

## 5. Preguntas probables del profe (con respuesta)

1. **"¿De dónde sacaron los datos?"** → De kworb.net, que publica el historial de los charts semanales de Spotify por país. Usamos México, de enero a diciembre de 2023. Son streams de Spotify México solamente.
2. **"La tabla muestra que en t = 35 hay 99,6 M y en t = 36 hay 102,7 M. ¿Por qué el modelo da 35,52 y no 35,13?"** → La cúbica no pasa por los puntos (es regresión). La raíz es la del modelo; la interpolación lineal da 35,13. La diferencia, de 2,75 días, es coherente con el error típico de 0,93 M.
3. **"¿Por qué no interpolaron directamente?"** → Para la raíz, la interpolación lineal sirve y la usamos como control. Pero para derivar y encontrar el pico hace falta una función suave en todo el rango; un polinomio interpolante de grado 46 oscilaría.
4. **"¿Por qué grado 3?"** → Es el menor grado con punto de inflexión.
5. **"¿Cómo eligieron el intervalo y el x₀?"** → De la tabla, donde S cruza 100 (semanas 35 y 36). x₀ = 35 está a menos de una semana de la raíz y f'(35) = 3,39 ≠ 0.
6. **"¿Cuántas iteraciones esperaban para bisección?"** → El intervalo se divide por 2 cada vez: con un ancho de 1 semana y una precisión de ~3·10⁻⁵ semanas, salen ≈ 15.
7. **"¿Qué error tiene la diferencia centrada?"** → O(h²), por cancelación en la serie de Taylor.
8. **"¿Por qué el pico del modelo no coincide con el de los datos?"** → La regresión suaviza y un polinomio de grado 3 tiene una sola "joroba" en su derivada. El pico real es más agudo (dura 1 o 2 semanas).
9. **"¿Qué es R²?"** → La proporción de variación que explica el modelo: 1 − Sr/St.
10. **"¿Sirve para cualquier canción?"** → Las raíces y las diferencias finitas sirven para todas. El pico por la cúbica solo sirve si a < 0 y la inflexión cae dentro de los datos. El programa lo verifica y avisa. Con estrenos no aplica (gráfico 4).
11. **"Si el R² es 0,9997, ¿por qué dicen que no sirve?"** → Porque el R² solo mide la cercanía a los puntos. La derivada del modelo vuelve a subir, cosa que nunca pasa en los datos.
12. **"¿Qué harían con los estrenos?"** → Usar decaimiento exponencial, linealizado con ln, sobre los streams semanales.
13. **"¿Qué usaron de IA?"** → Lo que dice la declaración. Tienen que poder explicar cada línea del script.

---

## 6. Qué consultarle al profe (antes de entregar)

1. **Tema:** "¿Sirve un caso de streaming musical enfocado como demanda de infraestructura, o prefiere un caso más clásico de ingeniería?"
2. **Regresión polinómica:** "El apunte trabaja regresión lineal y linealizaciones. ¿Podemos usar regresión polinómica de grado 3 (Chapra cap. 17)?"
3. **`np.polyfit`:** "¿Está bien usar la función de la librería o quiere que armemos y resolvamos las ecuaciones normales nosotros?" (Si quiere que lo hagan ustedes, son unas 10 líneas.)
4. **Criterio de corte:** "¿Prefiere error relativo porcentual aproximado (como usamos) o |b − a| < tolerancia?"
5. **Entrega:** "¿El código y el Excel van aparte en el Drive o como anexo del informe? ¿Hay límite de páginas?"
6. **Comparación:** "¿Alcanza con bisección contra Newton, o conviene sumar la secante?"

---

## 7. Simplicidad

- Tres temas (regresión, raíces y derivación) más una comparación es suficiente. No agreguen más métodos.
- Un solo script con todo. Los generadores de Word, PowerPoint y Excel quedan en `no_subir/`.
- Si el profe pide algo distinto, solo hay que tocar `DATOS` o el bloque del método correspondiente.

---

**Fuentes de los datos:** [kworb.net — Rosa Pastel, Spotify Chart History](https://kworb.net/spotify/track/6Z0ybnsUBhbZ9ZjPW64eoF.html) · [Chilango (2023) — Rosa Pastel, tendencia de TikTok](https://www.chilango.com/agenda/otros/rosa-pastel-tiktok-tendencia/) · [Wikipedia — Rosa Pastel](https://en.wikipedia.org/wiki/Rosa_Pastel_(Belanova_song))
