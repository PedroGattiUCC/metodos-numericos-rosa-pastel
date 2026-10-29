# Guía de defensa — "Rosa Pastel" (versión final)

> Para estudiar los tres. No subir al Drive. **Solo usamos métodos vistos en clase** (apuntes de Arnaudo): interpolación de Newton (unidad 4) y bisección / Newton-Raphson (unidad 2). La versión larga anterior quedó en la rama `version-completa` del repo.

## 1. La historia en 30 segundos
En 2023, "Rosa Pastel" (Belanova, 2006) volvió a ser viral por un trend de TikTok. Tomamos **47 semanas reales** de reproducciones en Spotify México (kworb.net, que recopila los charts oficiales). Los datos son semanales: sabemos que el acumulado estaba en 99,6 M en la semana 35 y en 102,7 M en la 36, pero no **en qué momento exacto pasó los 100 millones**. Lo estimamos con **interpolación de Newton** y una **raíz** (bisección vs. Newton-Raphson). Con la semana pico calculamos **cuánto ancho de banda hizo falta**: es pronóstico de demanda para dimensionar la red de un servicio de streaming. El mismo programa sirve para cualquier canción; lo probamos con otras dos.

```
reproducciones semanales ──► acumulado S(t)
   ├─ 1. Interpolación de Newton con 4 datos (semanas 34–37) → P(t)
   ├─ 2. f(t) = P(t) − 100 = 0 → Bisección vs. Newton-Raphson
   └─ Ingeniería: semana pico → Mbps
```

## 2. Números para saber de memoria
| Qué | Valor |
|---|---|
| Datos | 47 semanas (26/01 al 14/12/2023), 132,9 M en total |
| Datos que rodean la meta | S(34) = 96,349 · S(35) = 99,602 · S(36) = 102,738 · S(37) = 105,700 |
| Polinomio | P(t) = 96,349 + 3,25351(t−34) − 0,05879(t−34)(t−35) − 0,009340(t−34)(t−35)(t−36) |
| Intervalo | [35, 36]: f(35) = −0,40 < 0 < f(36) = 2,74 |
| Bisección | **15 iteraciones**, t* = 35,124481 |
| Newton (t₀ = 35) | **3 iteraciones**, t* = 35,124460 |
| Hito | **t* ≈ 35,12 semanas → 28 de septiembre de 2023** (0,12 sem ≈ 0,87 días después del dato del 28/09; el programa redondea al día) |
| Semana pico | **26 (27/07/2023)**, 4,17 M de reproducciones |
| Ancho de banda | **≈ 205 Mbps** promedio (a 160 kbps y 3:06) |

## 3. Los métodos
### 3.1 Interpolación de Newton (diferencias divididas)
- **Qué hace:** arma un polinomio que **pasa exactamente** por los puntos medidos, y con él estimamos valores **entre** mediciones (justo lo que dice el apunte: "interpolar valores entre los medidos").
- **Por qué 4 datos (grado 3) y no los 47:** con 47 puntos el polinomio sería de grado 46 y oscila mucho (el apunte lo advierte: con muchos puntos el grado crece). Con los 4 más cercanos a la meta (2 antes y 2 después) el grado 3 sigue la curvatura de esa zona.
- **Tabla de diferencias divididas:**

| t | S(t) | 1ra | 2da | 3ra |
|---|---|---|---|---|
| 34 | 96,349 | 3,25351 | −0,05879 | −0,00934 |
| 35 | 99,602 | 3,13594 | −0,08681 | |
| 36 | 102,738 | 2,96232 | | |
| 37 | 105,700 | | | |

- Ejemplo de cuenta: 1ra = (99,602 − 96,349)/(35 − 34) = 3,253. Los coeficientes b₀…b₃ son la primera fila.

### 3.2 Bisección (método cerrado)
- Necesita **cambio de signo** en [a, b] (Bolzano): f(35) < 0 < f(36).
- xr = (a + b)/2; se queda la mitad donde cambia el signo. Corta cuando |Ea| = |(nuevo − anterior)/nuevo| · 100 < 10⁻⁴ %.
- **Convergencia lineal:** el intervalo se divide por 2 en cada paso → 15 iteraciones. Siempre converge, pero es lenta.

### 3.3 Newton-Raphson (método abierto)
- x_{i+1} = x_i − f(x_i)/f'(x_i): sigue la recta tangente. La derivada se conoce porque P es un polinomio.
- **Iteración a mano:** x₀ = 35, f(35) = −0,3978, f'(35) = 3,2041 → x₁ = 35 + 0,3978/3,2041 = **35,1242**.
- **Convergencia cuadrática:** 3 iteraciones. Puede fallar si f' ≈ 0 o si x₀ está lejos de la raíz.

| | Bisección | Newton-Raphson |
|---|---|---|
| Tipo | Cerrado | Abierto |
| Necesita | Cambio de signo | f'(x) y un buen x₀ |
| Convergencia | Lineal, siempre converge | Cuadrática, no garantizada |
| Iteraciones | 15 | 3 |

### 3.4 Aplicación de ingeniería
- **Mbps = reproducciones/semana × 160 kbps × 186 s ÷ 1000 ÷ 604 800 s.** En la semana 26: 4,17 M → ≈ 205 Mbps de promedio, solo para esta canción en México.
- Los 160 kbps (calidad estándar de Spotify) y los 3:06 son **supuestos con fuente**: dan un orden de magnitud, no un dato de Spotify.

### 3.5 Generalización: la idea sirve para cualquier canción
El programa busca solo dónde el acumulado cruza la meta, toma los 4 datos de alrededor y hace lo mismo. Para otro caso se cambian **los datos** (su CSV), **la meta** (`META`) y, para el ancho de banda, **la duración** (`DURACION_S`).

| Canción | Datos usados | Hito 100 M | Bisección / Newton |
|---|---|---|---|
| Rosa Pastel | semanas 34–37 | 28/09/2023 | 15 / 3 |
| Ella Baila Sola | semanas 2–5 | 19/04/2023 | 18 / 4 |
| Tití Me Preguntó | semanas 9–12 | 21/07/2022 | 17 / 3 |

Sirve para estimar cuándo cualquier contenido alcanzó una meta de demanda (o cualquier acumulado medido por períodos).

## 4. Reparto (13 diapositivas, ~15 min)
| Quién | Diap. | Tema |
|---|---|---|
| Pedro | 1–5 | Portada, contexto, por qué es ingeniería, datos, interpolación de Newton |
| Facundo | 6–8 | Hito de 100 M: bisección vs. Newton (con la iteración a mano), convergencia, ancho de banda |
| Gonzalo | 9–11 | Otras canciones, limitaciones, conclusiones |

## 5. Preguntas probables
1. **¿Por qué es ingeniería?** → Es pronóstico de demanda para dimensionar la red: ≈ 205 Mbps en la semana pico. Y el método sirve para cualquier contenido.
2. **¿De dónde salen los datos?** → kworb.net, que recopila los charts semanales oficiales de Spotify México (Top 200).
3. **¿Por qué interpolación y no regresión?** → Queremos un valor **entre** dos mediciones reales, y la interpolación respeta los datos (pasa por ellos). Además la curva no es una recta, y con los modelos linealizables de clase el ajuste corría el hito más de una semana.
4. **¿Por qué 4 puntos?** → Con 2 sería una recta (no sigue la curvatura); con todos sería grado 46 y oscila. 4 puntos cercanos → grado 3.
5. **¿Por qué usar bisección/Newton si ya tienen el polinomio?** → P(t) = 100 es una ecuación cúbica: no se despeja t de forma simple. Y así comparamos los dos métodos.
6. **¿Cómo eligieron el intervalo y x₀?** → En los datos, S cruza 100 entre las semanas 35 y 36. x₀ = 35, donde f'(35) = 3,20 ≠ 0.
7. **¿Cuántas iteraciones esperaban en bisección?** → El intervalo se divide por 2 cada vez: con 1 semana de ancho y esa tolerancia, salen ≈ 15.
8. **¿Qué hicieron ustedes y qué una librería?** → Las diferencias divididas, bisección y Newton están programadas a mano (y en el Excel con fórmulas). NumPy solo maneja arreglos y polinomios; Matplotlib hace los gráficos.
9. **¿Sirve para otra canción?** → Sí: se cambia el CSV (y si hace falta la meta y la duración). Lo probamos con dos estrenos.
10. **¿Qué usaron de IA?** → Claude y Gemini para programar, hacer gráficos y redactar; los datos y los cálculos los verificamos nosotros.

## 6. Limitaciones (díganlas ustedes)
- Solo Spotify México y solo semanas en el Top 200.
- Datos semanales: suponemos que el acumulado crece suave dentro de la semana.
- La interpolación sirve entre datos medidos, no para predecir a futuro.
- El ancho de banda usa supuestos (3:06, 160 kbps).

## 7. El script en 1 minuto (`CODIGO/analisis_resurgimiento_rosa_pastel.py`)
| Función | Qué hace |
|---|---|
| `cargar_csv` | Lee fecha y reproducciones; pasa a millones |
| `diferencias_divididas` | Arma la tabla de diferencias divididas |
| `polinomio_newton` | Arma P(t) con los coeficientes de la primera fila |
| `biseccion` / `newton_raphson` | Los dos métodos, con el criterio \|Ea\| < 10⁻⁴ % |
| `mbps` | La cuenta del ancho de banda |
| `analizar_cancion` | Hace todo para una canción: busca dónde cruza la meta, interpola, raíces, fecha y semana pico |
| `main` | Corre las 3 canciones, hace los 3 gráficos y la tabla |

Arriba del archivo están `CANCIONES` (para agregar otra), `META`, `TOLERANCIA`, `DURACION_S` y `BITRATE_KBPS`. El Excel (`ENTREGABLES/Modelo_Numerico_Rosa_Pastel_Belanova.xlsx`) hace las mismas cuentas con fórmulas.
