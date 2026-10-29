# Guía completa — Proyecto "Rosa Pastel" (desde cero)

> Guía de estudio del grupo (Pedro, Facu, Gonza). **No va al Drive**; lo que se entrega está en `ENTREGABLES/`.
> Está pensada para alguien que **no sabe nada del tema**: léanla en orden. Si tienen poco tiempo, lean como mínimo las secciones **1, 2, 9 y 10**.
> Todo lo que usamos se vio en clase (apuntes de Arnaudo): **interpolación de Newton** (unidad 4, Ajuste de curvas) y **bisección / Newton-Raphson** (unidad 2, Raíces). Nada más.

## Índice
0. Qué hay que entregar y dónde está
1. El proyecto en 1 minuto
2. Números para saber de memoria
3. Conceptos básicos (métodos numéricos, errores, tolerancia)
4. Los datos
5. Método 1: interpolación de Newton (paso a paso)
6. Método 2: raíces — bisección y Newton-Raphson (paso a paso)
7. Comparación de los dos métodos de raíces
8. La aplicación de ingeniería: ancho de banda
9. Generalización: sirve para cualquier canción
10. Qué decir en cada diapositiva (guion)
11. Preguntas que nos pueden hacer (con respuesta)
12. Limitaciones
13. El código, explicado
14. El Excel, explicado
15. Glosario

---

## 0. Qué hay que entregar y dónde está
La consigna pide **informe escrito** y **presentación oral (~15 min)**, subidos a la carpeta "2026-2" del Drive. El semestre pasado (2026-1) los grupos subieron informe (Word/PDF), presentación (PowerPoint/PDF), Excel y algunos el código. Nosotros subimos **la carpeta `ENTREGABLES/` completa**:

| Archivo | Qué es |
|---|---|
| `Informe_Proyecto_Metodos_Numericos_Rosa_Pastel.docx` / `.pdf` | Informe (16 páginas) con la estructura de la consigna; la sección 3.1 justifica por qué elegimos estos métodos y no los otros de los apuntes |
| `Presentacion_Rosa_Pastel_Metodos_Numericos.pptx` / `.pdf` | Presentación (14 diapositivas; la 5 justifica la elección de los métodos) |
| `Modelo_Numerico_Rosa_Pastel_Belanova.xlsx` | Excel con **fórmulas**: datos, diferencias divididas, bisección y Newton |
| `Codigo/` | Script de Python, datos (CSV), gráficos, `LEEME.txt` |

Cómo se compara con el semestre pasado: ellos usaron 1 a 3 métodos y aplicaciones parecidas (ej.: tiempo de recupero de una inversión con bisección vs. Newton; scrap de una fábrica con bisección vs. Newton; consumo de combustible con interpolación de Newton; acción de Apple con regresión e interpolación). Nuestro proyecto está a la misma altura.

---

## 1. El proyecto en 1 minuto
- **Historia:** "Rosa Pastel" es una canción de Belanova de 2006. En 2023 volvió a ser viral por un trend de TikTok y empezó a escucharse muchísimo en Spotify México.
- **Datos:** 47 semanas reales de reproducciones (del 26/01/2023 al 14/12/2023), sacadas de kworb.net, que recopila los rankings semanales oficiales de Spotify (Top 200).
- **Pregunta 1 (métodos numéricos):** ¿en qué momento la canción superó los **100 millones** de reproducciones acumuladas? Los datos son semanales: en la semana 35 iba por 99,6 M y en la 36 por 102,7 M. El cruce está *entre* dos mediciones, y lo estimamos con:
  1. **Interpolación de Newton**: armamos un polinomio que pasa por los 4 datos más cercanos.
  2. **Bisección y Newton-Raphson**: buscamos dónde ese polinomio vale 100 y comparamos los dos métodos.
- **Pregunta 2 (ingeniería):** ¿cuánto **ancho de banda** necesitó la red en la semana de más reproducciones? → **≈ 205 Mbps**. Esto es dimensionar infraestructura (lo que hace un ingeniero en un servicio de streaming).
- **Generalización:** el mismo programa funciona para cualquier canción; solo se cambia el archivo de datos. Lo probamos con "Ella Baila Sola" y "Tití Me Preguntó".

```
reproducciones semanales ──► acumulado S(t)
   ├─ 1. Interpolación de Newton con 4 datos (semanas 34–37) → polinomio P(t)
   ├─ 2. f(t) = P(t) − 100 = 0 → Bisección vs. Newton-Raphson → t* = 35,12 semanas (28/09/2023)
   └─ Ingeniería: semana pico (4,17 M) → ≈ 205 Mbps
```

---

## 2. Números para saber de memoria
| Qué | Valor |
|---|---|
| Datos | 47 semanas, del 26/01/2023 (t = 0) al 14/12/2023 (t = 46); 132,9 M en total |
| Datos alrededor de la meta | S(34) = 96,349 · S(35) = 99,602 · S(36) = 102,738 · S(37) = 105,700 (millones) |
| Polinomio | P(t) = 96,349 + 3,25351(t−34) − 0,05879(t−34)(t−35) − 0,009340(t−34)(t−35)(t−36) |
| Ecuación | f(t) = P(t) − 100 = 0 |
| Intervalo | [35, 36], porque f(35) = −0,3978 < 0 y f(36) = 2,7381 > 0 |
| Tolerancia | \|Ea\| < 0,0001 % |
| Bisección | **15 iteraciones**, t* = 35,124481 |
| Newton-Raphson (t₀ = 35) | **3 iteraciones**, t* = 35,124460 |
| Hito | **t* ≈ 35,12 semanas → 28 de septiembre de 2023** (0,12 semanas ≈ 0,87 días después del dato del 28/09) |
| Volumen hasta el hito | 100 M reproducciones × 3,72 MB ≈ **372 TB** transferidos |
| Control (interpolación lineal) | t = 35,1269 (a 0,4 horas del resultado) |
| Semana pico | **semana 26 (27/07/2023)** con **4,17 M** reproducciones |
| Ancho de banda | **≈ 205 Mbps** promedio en esa semana |
| Otras canciones | Ella Baila Sola: 19/04/2023 (18 / 4 iter.) · Tití Me Preguntó: 21/07/2022 (17 / 3 iter.) |

---

## 3. Conceptos básicos

### 3.1 ¿Qué es un método numérico?
Es una forma de resolver un problema matemático **de manera aproximada**, con operaciones simples (sumas, restas, multiplicaciones, divisiones) repetidas muchas veces. Se usa cuando:
- no hay una fórmula exacta, o es muy difícil de obtener, o
- solo tenemos **datos medidos** (puntos sueltos) y no la función.

Nuestro caso tiene las dos cosas: tenemos datos semanales (no una función), y la ecuación final es de grado 3 (no se despeja fácil).

### 3.2 Errores
- **Error verdadero:** diferencia entre el valor exacto y el aproximado. Casi nunca se conoce (si supiéramos el exacto, no haríamos el método).
- **Error relativo porcentual aproximado (Ea):** compara la aproximación nueva con la anterior:

  **|Ea| = | (nuevo − anterior) / nuevo | × 100 %**

  Si entre una iteración y la otra el resultado casi no cambia, Ea es chico y podemos parar.
- **Tolerancia:** el límite que elegimos para parar. Usamos **|Ea| < 0,0001 %** (10⁻⁴ %). Es muy exigente: el resultado queda con unas 6 cifras correctas.

### 3.3 ¿Qué es una "iteración"?
Una repetición del método: con el valor que tenemos calculamos uno nuevo, mejor. Contar iteraciones sirve para comparar qué método llega más rápido.

---

## 4. Los datos
- **Fuente:** kworb.net, página de "Rosa Pastel". Kworb copia los rankings semanales oficiales de Spotify (Top 200 de México). Cada fila es una semana con su cantidad de reproducciones.
- **Archivo:** `ENTREGABLES/Codigo/datos/rosa_pastel_belanova.csv`, columnas `fecha,streams`.
- **Variable de tiempo:** t = número de semana. t = 0 es la semana del 26/01/2023; t = 46 la del 14/12/2023.
- **Acumulado S(t):** suma de todas las reproducciones desde la semana 0 hasta la semana t, en **millones**. Por ejemplo, S(0) = 1,137 M; S(1) = 1,137 + 1,445 = 2,583 M; y así.
- **Detalle importante:** S(t) solo se conoce en números enteros de t (una vez por semana). Entre semana y semana no hay datos → por eso **interpolamos**.
- **Lo que muestran los datos:** la semana 35 (28/09/2023) el acumulado era 99,602 M y la semana 36 (05/10/2023) 102,738 M. O sea, los 100 M se pasaron entre esas dos semanas.
- **Semana pico:** la semana 26 (27/07/2023) tuvo la mayor cantidad de reproducciones: 4.170.775 (≈ 4,17 M). Al principio tenía ≈ 1,1 M por semana (casi 4 veces menos).

---

## 5. Método 1: interpolación de Newton (paso a paso)

### 5.1 ¿Qué es interpolar?
Tenemos puntos medidos y queremos saber valores **entre** esos puntos. Interpolar es armar un **polinomio que pasa exactamente por los puntos** y usarlo para estimar valores intermedios.
- Con 2 puntos → recta (grado 1).
- Con 3 puntos → parábola (grado 2).
- Con 4 puntos → cúbica (grado 3). **Regla: n puntos → grado n − 1.**

**Interpolación vs. regresión** (pregunta típica): la regresión busca la curva que pasa *lo más cerca posible* de todos los puntos, pero no necesariamente por ellos. La interpolación pasa *exactamente* por los puntos. Como nuestros datos son reales y queremos un valor entre dos mediciones, interpolar respeta los datos.

### 5.2 ¿Por qué 4 puntos y no los 47?
- Con los 47 puntos el polinomio sería de **grado 46**: oscila muchísimo entre los puntos (el apunte lo advierte: con muchos puntos el grado crece y el polinomio se vuelve malo).
- Con **2 puntos** sería una recta: no sigue la curvatura (el ritmo de reproducciones va bajando un poco cada semana).
- Con **4 puntos cercanos** (2 antes y 2 después de la meta: semanas 34, 35, 36 y 37) → grado 3: sigue la forma de la curva justo en la zona que nos interesa.

### 5.3 La forma de Newton
El polinomio se escribe así:

**P(t) = b₀ + b₁(t − x₀) + b₂(t − x₀)(t − x₁) + b₃(t − x₀)(t − x₁)(t − x₂)**

donde x₀, x₁, x₂, x₃ son las semanas (34, 35, 36, 37) y los b son las **diferencias divididas**. Ventaja: los b salen de una tabla fácil de calcular a mano, y si se agrega un punto solo se agrega un término.

### 5.4 Tabla de diferencias divididas (hecha a mano)
Cada columna se calcula con la anterior: **(valor de abajo − valor de arriba) / (diferencia de los t que abarca)**.

**1ras diferencias** (t de distancia 1):
- (99,602 − 96,349) / (35 − 34) = **3,25351**
- (102,738 − 99,602) / (36 − 35) = **3,13594**
- (105,700 − 102,738) / (37 − 36) = **2,96232**

(Son las reproducciones de cada semana: 3,25 M, 3,14 M, 2,96 M. Van bajando.)

**2das diferencias** (t de distancia 2):
- (3,13594 − 3,25351) / (36 − 34) = −0,11757 / 2 = **−0,05879**
- (2,96232 − 3,13594) / (37 − 35) = −0,17362 / 2 = **−0,08681**

**3ra diferencia** (t de distancia 3):
- (−0,08681 − (−0,05879)) / (37 − 34) = −0,02802 / 3 = **−0,00934**

| t | S(t) | 1ra | 2da | 3ra |
|---|---|---|---|---|
| 34 | **96,349** | **3,25351** | **−0,05879** | **−0,00934** |
| 35 | 99,602 | 3,13594 | −0,08681 | |
| 36 | 102,738 | 2,96232 | | |
| 37 | 105,700 | | | |

Los coeficientes son **la primera fila** (en negrita): b₀ = 96,349; b₁ = 3,25351; b₂ = −0,05879; b₃ = −0,00934.

### 5.5 El polinomio
**P(t) = 96,349 + 3,25351(t−34) − 0,05879(t−34)(t−35) − 0,009340(t−34)(t−35)(t−36)**

Desarrollado (multiplicando todo): P(t) = −0,009340 t³ + 0,921931 t² − 27,005993 t + 315,906072.

**Comprobación rápida:** en t = 35, los términos con (t − 35) se anulan: P(35) = 96,349 + 3,25351 × 1 = 99,602 ✔ (pasa por el dato).

---

## 6. Método 2: raíces — bisección y Newton-Raphson

### 6.1 ¿Qué es una raíz y por qué la buscamos?
Una **raíz** de f(t) es un valor de t donde **f(t) = 0**. Queremos el t donde P(t) = 100, así que definimos:

**f(t) = P(t) − 100**

Cuando f(t) = 0, P(t) vale exactamente 100. Como P es de grado 3, despejar t a mano es complicado → usamos métodos numéricos de raíces.

### 6.2 Elección del intervalo (cambio de signo)
Como dice el apunte de Raíces: si f es continua en [a, b] y **f(a) · f(b) < 0** (cambia de signo), hay al menos una raíz entre a y b.
- f(35) = 99,602 − 100 = **−0,3978** (negativo)
- f(36) = 102,738 − 100 = **+2,7381** (positivo)

→ La raíz está en **[35, 36]**. El programa busca solo esta semana: la primera donde el acumulado pasa de estar debajo de 100 a estar arriba.

### 6.3 Bisección
**Idea:** partir el intervalo a la mitad una y otra vez, quedándose siempre con la mitad donde f cambia de signo.

Pasos:
1. xr = (a + b) / 2
2. Si f(a) · f(xr) < 0 → la raíz está en [a, xr] → b = xr. Si no → a = xr.
3. Calcular |Ea|. Si es menor que la tolerancia, parar. Si no, volver a 1.

**Primeras iteraciones a mano:**
| it | a | b | xr | f(xr) | ¿qué se hace? | \|Ea\| % |
|---|---|---|---|---|---|---|
| 1 | 35 | 36 | 35,5 | +1,1883 | f(a)<0 y f(xr)>0 → b = 35,5 | — (100 por convención) |
| 2 | 35 | 35,5 | 35,25 | +0,3993 | b = 35,25 | \|(35,25−35,5)/35,25\|·100 = 0,709 |
| 3 | 35 | 35,25 | 35,125 | +0,0017 | b = 35,125 | 0,356 |
| 4 | 35 | 35,125 | 35,0625 | −0,1978 | ahora f(xr)<0 → a = 35,0625 | 0,178 |
| … | | | | | | |
| 15 | 35,12445 | 35,12451 | **35,124481** | 0,00007 | \|Ea\| < 0,0001 % → **para** | 0,000087 |

**Características:**
- **Necesita un intervalo** con cambio de signo.
- **Confiable:** si hay cambio de signo, siempre llega a la raíz.
- **Convergencia lenta** (inconveniente que marca el apunte): el intervalo solo se reduce a la mitad por iteración. Por eso tarda **15 iteraciones**.
- Otro inconveniente del apunte: no sirve si la raíz no produce cambio de signo (raíces múltiples de orden par).

### 6.4 Newton-Raphson (método abierto)
**Idea:** parado en un punto, trazamos la **recta tangente** a la curva y vemos dónde corta el eje (donde valdría 0). Ese corte es la nueva aproximación.

**Fórmula:** x_{i+1} = x_i − f(x_i) / f'(x_i)

**Necesitamos la derivada.** Como P es un polinomio, se deriva fácil:
f'(t) = P'(t) = −0,028020 t² + 1,843862 t − 27,005993
(se deriva cada término: t³ → 3t², t² → 2t, t → 1, la constante → 0).

**Primera iteración a mano** (arrancamos en x₀ = 35):
- f(35) = −0,3978
- f'(35) = 3,2041 (es la pendiente: ≈ 3,2 M por semana)
- x₁ = 35 − (−0,3978 / 3,2041) = 35 + 0,1242 = **35,1242**

| it | x_i | f(x_i) | f'(x_i) | x_{i+1} | \|Ea\| % |
|---|---|---|---|---|---|
| 1 | 35,000000 | −0,397848 | 3,2041 | 35,124170 | 0,353517 |
| 2 | 35,124170 | −0,000924 | 3,1890 | 35,124460 | 0,000825 |
| 3 | 35,124460 | ≈ 0 | 3,1890 | **35,124460** | ≈ 0 → **para** |

**Características:**
- **Método abierto:** no necesita intervalo, solo un valor inicial x₀ cercano a la raíz.
- **Alto grado de convergencia (rápido):** el apunte lo destaca como el método más usado en ingeniería. Por eso solo **3 iteraciones**.
- **Puede divergir** (inconvenientes del apunte): en curvas muy "planas" la tangente lleva lejos, y si la función es complicada obtener la derivada es tedioso. También falla si f'(x) ≈ 0 (tangente horizontal). El programa avisa si la derivada es casi cero. Acá f'(35) = 3,2 ≠ 0 y x₀ está muy cerca, así que anda perfecto.

### 6.5 Resultado
- Bisección: t* = 35,124481 · Newton: t* = 35,124460. Coinciden en **35,1245** (la diferencia es menor que la tolerancia).
- t* = 35,12 semanas desde el 26/01/2023. La semana 35 es el 28/09/2023, y 0,12 semanas ≈ 0,87 días → **fines del 28 de septiembre de 2023** (el programa muestra 28/09/2023 porque se queda con el día completo).

---

## 7. Comparación de los dos métodos de raíces
| | Bisección | Newton-Raphson |
|---|---|---|
| Arranca con | Un intervalo con cambio de signo | Un valor inicial (método abierto) |
| Necesita | Cambio de signo en [a, b] | f'(x) y un buen x₀ |
| Convergencia | Lenta | Rápida (alto grado de convergencia) |
| ¿Siempre llega? | Sí (confiable) | No siempre (puede divergir) |
| Iteraciones (Rosa Pastel) | 15 | 3 |
| Resultado | 35,124481 | 35,124460 |

**Conclusión:** Newton es **5 veces más rápido** acá porque tenemos la derivada exacta (es un polinomio) y un buen punto inicial. Bisección es más lenta pero **más segura**. En el gráfico 2 se ve: bisección baja el error en línea recta (escala logarítmica) y Newton cae en picada.

---

## 8. La aplicación de ingeniería: ancho de banda

### 8.1 ¿Por qué es ingeniería?
Un servicio de streaming tiene que **dimensionar su red** (servidores, enlaces, CDN) para que aguante la demanda. Una canción viral multiplica las reproducciones de golpe. Saber **cuándo** se alcanza una meta y **cuánto tráfico** genera el pico es un problema de **pronóstico de demanda y capacidad**, típico de Ingeniería Informática / redes.

### 8.2 La cuenta, paso a paso
**Supuestos (con fuente, no son datos de Spotify):**
- Duración de la canción: **3:06 = 186 s** (Wikipedia, álbum Dulce Beat).
- Calidad de audio: **160 kbps** (calidad estándar de Spotify, página de ayuda de Spotify).

1. Datos por reproducción: 160 kbps × 186 s = 29.760 kilobits = **29,76 megabits** (÷ 1000 para pasar de kilo a mega).
2. Datos en la semana pico: 4.170.775 reproducciones × 29,76 Mb = 124.122.264 Mb.
3. Segundos en una semana: 7 × 24 × 3600 = **604.800 s**.
4. Ancho de banda promedio: 124.122.264 Mb ÷ 604.800 s ≈ **205 Mbps**.

**Fórmula:** Mbps = reproducciones/semana × 160 × 186 ÷ 1000 ÷ 604.800

### 8.3 Volumen transferido hasta el hito (une el método con la aplicación)
Cuando la canción llegó a los 100 M (t* = 35,12, el resultado de los métodos), ¿cuántos datos se habían enviado?
1. Por reproducción: 160 kbps × 186 s = 29.760 kilobits ÷ 8 = 3.720 kilobytes = **3,72 MB** (÷ 8 porque 1 byte = 8 bits).
2. 100.000.000 × 3,72 MB = 372.000.000 MB = **372 TB** (1 TB = 1.000.000 MB).

Sirve para estimar costos de distribución (lo que cobra una CDN por dato enviado). El script lo imprime en la sección 4.

### 8.4 Cómo interpretarlo
La red tuvo que transferir en promedio **unos 205 megabits por segundo, solo para esta canción y solo en México**, durante la semana pico. Es un **orden de magnitud** (promedio de la semana; en la hora pico real sería más). No calculamos el ancho de banda de las otras canciones porque cada una tiene otra duración y no queremos inventar datos.

---

## 9. Generalización: sirve para cualquier canción
El programa no está "atado" a Rosa Pastel. Hace siempre lo mismo:
1. Lee el CSV de la canción.
2. Calcula el acumulado y busca **la semana donde cruza la meta**.
3. Toma los **4 datos de alrededor**, arma la tabla de diferencias divididas y el polinomio.
4. Busca la raíz con bisección y Newton, y calcula la fecha.
5. Encuentra la semana pico.

**Para otra canción solo se cambia:** el archivo CSV (y si se quiere, la meta `META` o la duración `DURACION_S`). Lo probamos con dos canciones reales:

| Canción | Datos usados | Hito 100 M | Bisección / Newton |
|---|---|---|---|
| Rosa Pastel (Belanova) | semanas 34–37 | 28/09/2023 | 15 / 3 |
| Ella Baila Sola (Eslabón Armado y Peso Pluma) | semanas 2–5 | 19/04/2023 | 18 / 4 |
| Tití Me Preguntó (Bad Bunny) | semanas 9–12 | 21/07/2022 | 17 / 3 |

En las tres funciona sin tocar el código. Las dos de comparación son estrenos (llegan a 100 M en pocas semanas); Rosa Pastel tardó 35 semanas porque fue un resurgimiento. La misma idea sirve para cualquier **acumulado medido por períodos** (descargas, visitas, ventas) y para cualquier meta.

---

## 10. Qué decir en cada diapositiva (guion, ~15 min)
**Reparto:** Pedro 1–6 · Facundo 7–9 · Gonzalo 10–12 (13 y 14 son cierre y fuentes).

| # | Diapositiva | Quién | Qué decir (idea, no leer) |
|---|---|---|---|
| 1 | Portada | Pedro | Presentarse. "Modelamos numéricamente el resurgimiento de 'Rosa Pastel' con interpolación de Newton y bisección vs. Newton-Raphson, con datos reales." |
| 2 | Contexto | Pedro | Canción de 2006, viral en TikTok en 2023. Pasó de ~1,1 M a 4,17 M reproducciones por semana (casi 4 veces). |
| 3 | Justificación técnica | Pedro | Para un servicio de streaming esto es un problema de **demanda**: hay que dimensionar la red. Los datos son **discretos** (semanales), por eso necesitamos métodos numéricos para estimar entre mediciones. |
| 4 | Datos | Pedro | 47 semanas de kworb (Top 200 Spotify México), 132,9 M en total. Mostrar el gráfico: el acumulado cruza los 100 M entre las semanas 35 y 36 (zoom a la derecha). |
| 5 | ¿Por qué estos métodos? | Pedro | Newton frente a las alternativas de los apuntes: la lineal ignora la curvatura (da 35,127, sirve de control); Lagrange da el mismo polinomio sin la tabla; la trazadora necesita más datos; la regresión del apunte es la recta y no pasa por los datos. Para la raíz, uno que trabaja con un intervalo (bisección) y uno abierto (Newton); la secante no hace falta porque la derivada de P(t) es exacta. |
| 6 | Interpolación de Newton | Pedro | Usamos los 4 datos alrededor de la meta → polinomio de grado 3 que pasa exactamente por ellos. Explicar la tabla (primera fila = coeficientes). No usamos los 47 porque grado 46 oscila. |
| 7 | Hito de 100 M | Facundo | f(t) = P(t) − 100, intervalo [35; 36] por cambio de signo. Bisección 15 iteraciones, Newton 3. Hacer la iteración de Newton a mano: 35 − (−0,3978/3,2041) = 35,1242. Resultado: 35,12 semanas ≈ 28/09/2023, cerca de las 21 h. |
| 8 | Convergencia | Facundo | El gráfico en escala logarítmica: bisección baja de a poco (convergencia lenta), Newton cae de golpe (convergencia rápida). Bisección = segura, Newton = rápido pero necesita derivada y buen inicio. |
| 9 | Volumen y ancho de banda | Facundo | Hito: 100 M × 3,72 MB ≈ 372 TB transferidos. Pico: 4,17 M × 160 kbps × 186 s ÷ 604.800 s ≈ 205 Mbps. Aclarar que son supuestos con fuente y un orden de magnitud. |
| 10 | Generalización | Gonzalo | Mismo programa, solo cambia el CSV. Probado con Ella Baila Sola y Tití: funciona igual. Sirve para cualquier contenido y cualquier meta. |
| 11 | Limitaciones | Gonzalo | Solo Spotify México Top 200; datos semanales; interpola, no predice a futuro; supuestos de audio. |
| 12 | Conclusiones | Gonzalo | Hito 28/09/2023 (≈ 372 TB); Newton 3 vs bisección 15; ≈ 205 Mbps. Lo que aprendimos: elegir el método según lo que se tiene (derivada, intervalo) y que con pocos datos bien elegidos alcanza. |
| 13 | Gracias / preguntas | Todos | — |
| 14 | Fuentes de imágenes | — | No se dice nada. |

---

## 11. Preguntas que nos pueden hacer (con respuesta)
1. **¿Por qué esto es ingeniería y no solo música?** → Porque es un problema de **demanda y capacidad de red**: un servicio de streaming tiene que saber cuánto tráfico genera un contenido para dimensionar servidores y enlaces. Calculamos ≈ 205 Mbps en el pico. Y el método sirve para cualquier contenido.
2. **¿De dónde salen los datos? ¿Son reales?** → Sí, de kworb.net, que recopila los rankings semanales oficiales de Spotify México (Top 200). Están en `Codigo/datos/` con el link de la fuente.
3. **¿Por qué interpolación y no regresión?** → Queremos un valor **entre** dos mediciones reales, y la interpolación pasa exactamente por los datos. En clase vimos regresión lineal y modelos linealizables (exponencial, potencial, crecimiento); los probamos y no siguen bien la curva cerca de la meta (corrían el resultado más de una semana).
4. **¿Por qué 4 puntos y no 2 o 47?** → Con 2 es una recta y no sigue la curvatura. Con 47 sería grado 46 y oscila. 4 cercanos → grado 3, sigue la forma local.
5. **¿Por qué Newton y no Lagrange?** → Dan **el mismo polinomio** (por n puntos pasa un único polinomio de grado n − 1). Elegimos Newton porque la tabla de diferencias divididas es más fácil de hacer a mano y en Excel.
5b. **¿Probaron con interpolación lineal (una recta entre las semanas 35 y 36)?** → Sí, como control: da t = 35,1269, a solo 0,4 horas del resultado. La cúbica es mejor porque sigue la curvatura, pero el control muestra que el resultado es coherente.
6. **¿Por qué no trazadoras (splines)?** → Las trazadoras sirven para muchos puntos sin oscilar, pero requieren resolver un sistema de ecuaciones. Para un solo cruce, 4 puntos alcanzan y es más simple.
7. **Si ya tienen el polinomio, ¿para qué bisección/Newton?** → Porque P(t) = 100 es una ecuación de **grado 3**: no se despeja t de forma simple. Además así comparamos los dos métodos.
8. **¿Cómo eligieron el intervalo?** → Por cambio de signo, como en el apunte: f(35) · f(36) < 0 (f(35) < 0 y f(36) > 0), y f es continua.
9. **¿Por qué x₀ = 35 en Newton?** → Es el extremo del intervalo, está muy cerca de la raíz y f'(35) = 3,2 ≠ 0.
10. **¿Cuándo falla Newton?** → Si f'(x) ≈ 0 o si x₀ está lejos de la raíz (puede alejarse o ciclar). El programa verifica la derivada.
11. **¿Por qué bisección tarda 15 iteraciones?** → El intervalo empieza en 1 semana y se divide por 2 cada vez; para llegar a |Ea| < 0,0001 % (≈ 0,00004 semanas de precisión) hacen falta unas 15 mitades (2¹⁵ ≈ 32.000).
12. **¿Por qué en "Ella Baila Sola" Newton tardó 4?** → El punto inicial (semana 3) estaba más lejos de la raíz (3,87) que en Rosa Pastel (35 vs. 35,12); igual converge rápido.
13. **¿Qué significa |Ea|?** → Error relativo porcentual aproximado: cuánto cambió el resultado respecto a la iteración anterior, en %.
13b. **¿Qué son los 372 TB?** → El volumen total de datos enviado hasta llegar a los 100 M: 100 M × 3,72 MB por reproducción. Es la parte de la aplicación que usa directamente el resultado del método (el hito).
14. **¿Qué es el 205 Mbps exactamente?** → El **promedio** de tráfico durante la semana de más reproducciones, solo de esta canción en México, suponiendo 160 kbps y 3:06.
15. **¿Por qué no calcularon el ancho de banda de las otras canciones?** → Porque cada canción dura distinto y no queríamos inventar datos. Se puede hacer cambiando `DURACION_S`.
16. **¿Qué programaron ustedes y qué hizo una librería?** → Las diferencias divididas, la bisección y Newton-Raphson están programadas a mano (y en el Excel con fórmulas). NumPy solo maneja listas de números y polinomios; Matplotlib hace los gráficos.
17. **¿Usaron inteligencia artificial?** → Sí, Claude y Gemini para programar, hacer gráficos y redactar. Está declarado en el informe. Los datos y los cálculos los verificamos nosotros (el Excel da lo mismo que el programa).
18. **¿Qué aprendieron?** → Que con datos discretos se puede estimar lo que pasa entre mediciones; que el método de raíces se elige según lo que se tiene (Newton si hay derivada y buen inicio, bisección si se quiere seguridad); y a llevar un problema real a una ecuación.
19. **"Esto ya pasó: ¿cómo te sirve para prepararte?"** (pregunta difícil, respondan así):
    - **Primero, la verdad:** sí, es un análisis de algo que ya pasó, y lo decimos en las limitaciones. La interpolación estima **entre** datos medidos; no predice el futuro, y no lo usamos para eso.
    - **Uno: los datos llegan "de a saltos".** Spotify (o cualquier sistema) registra por períodos: semanas, días, horas. El momento exacto en que se pasó un umbral queda **entre dos registros**, y el método lo reconstruye. Es lo mismo que hace un ingeniero con un registro que mide cada cierto tiempo, por ejemplo para saber cuándo un tanque pasó el nivel máximo.
    - **Dos: así se dimensiona en ingeniería.** La infraestructura se diseña con **casos históricos**: una represa con las crecidas pasadas, la red eléctrica con la demanda de años anteriores. Este caso deja números concretos de un fenómeno viral: la demanda se multiplicó casi por 4 (de 1,1 M a 4,17 M por semana), hubo un pico de ≈ 205 Mbps y se transfirieron ≈ 372 TB hasta los 100 M. Con eso, la empresa sabe qué esperar y cuánto margen dejar la próxima vez que algo se viralice.
    - **Tres: el procedimiento queda listo para el próximo caso.** El programa se corre igual con cualquier canción y cualquier meta. Cada semana que llega un dato nuevo se puede volver a correr y saber al instante si se cruzó la meta y cuándo.
    - **Si insiste en predecir:** para eso habría que ajustar un modelo y **extrapolar**, y el apunte advierte que fuera de los datos el polinomio puede oscilar. Preferimos un resultado confiable entre datos reales antes que una predicción sin respaldo.

---

## 12. Limitaciones (díganlas ustedes antes de que se las pregunten)
- Solo Spotify **México** y solo semanas en el **Top 200** (no es el total mundial).
- Datos **semanales**: suponemos que el acumulado crece suave dentro de la semana.
- La interpolación sirve **entre** datos medidos; no sirve para predecir el futuro.
- El ancho de banda usa **supuestos** (3:06, 160 kbps); es un orden de magnitud.

---

## 13. El código, explicado (`ENTREGABLES/Codigo/analisis_resurgimiento_rosa_pastel.py`)
**Cómo correrlo:**
```bash
pip install -r ENTREGABLES/Codigo/requirements.txt
```
```bash
python3 ENTREGABLES/Codigo/analisis_resurgimiento_rosa_pastel.py
```
Imprime todas las tablas (datos, diferencias divididas, iteraciones, ancho de banda, comparación) y guarda los gráficos en `Codigo/graficos/`.

**Arriba del archivo (configuración):**
- `CANCIONES`: lista de canciones (nombre y archivo). Para agregar una, se agrega una línea.
- `META = 100.0`: la meta en millones.
- `TOLERANCIA = 1e-4`: el |Ea| máximo en %.
- `DURACION_S = 186` y `BITRATE_KBPS = 160`: supuestos del ancho de banda.

**Funciones:**
| Función | Qué hace |
|---|---|
| `cargar_csv` | Lee el CSV (ignora las líneas que empiezan con #) y pasa las reproducciones a millones |
| `diferencias_divididas` | Arma la tabla de diferencias divididas (sección 5.4) |
| `polinomio_newton` | Arma P(t) con los coeficientes de la primera fila (sección 5.5) |
| `error_porcentual` | \|(nuevo − anterior)/nuevo\| × 100 |
| `biseccion` | El método de la sección 6.3; guarda cada iteración para las tablas |
| `newton_raphson` | El método de la sección 6.4; avisa si la derivada es casi cero |
| `mbps` | La cuenta del ancho de banda (sección 8.2) |
| `volumen_tb` | El volumen hasta el hito en TB (sección 8.3) |
| `analizar_cancion` | Hace todo para una canción: acumulado, busca el cruce, interpola, raíces, fecha y pico |
| `imprimir_detalle` | Imprime las tablas de Rosa Pastel |
| `grafico_interpolacion`, `grafico_convergencia`, `grafico_canciones` | Los 3 gráficos |
| `tabla_comparativa` | Imprime y guarda la tabla de las 3 canciones |
| `main` | Corre todo |

**Línea clave para encontrar el cruce:** `k = int(np.argmax(S >= META)) - 1` → busca la primera semana con acumulado ≥ 100 y se queda con la anterior (la última debajo de 100). Así el intervalo es [k, k+1] y los 4 datos son k−1, k, k+1 y k+2.

---

## 14. El Excel, explicado (`Modelo_Numerico_Rosa_Pastel_Belanova.xlsx`)
Hace **las mismas cuentas con fórmulas** (sirve para mostrar que no es una "caja negra"):
- **Datos:** semana, fecha, reproducciones, millones y acumulado (cada celda suma la anterior). Abajo: semana pico y ancho de banda.
- **Interpolacion:** la tabla de diferencias divididas con fórmulas `=(abajo − arriba)/(t − t)` y los coeficientes b₀…b₃.
- **Biseccion:** las 15 iteraciones; a y b se actualizan con `SI(f(a)·f(xr) < 0, …)`.
- **Newton:** las 3 iteraciones con f y f' calculadas con el polinomio, y la fecha final.

Da exactamente los mismos números que Python.

---

## 15. Glosario
- **Acumulado S(t):** total de reproducciones desde el inicio hasta la semana t.
- **Ancho de banda (Mbps):** cantidad de datos por segundo que pasa por la red (megabits por segundo).
- **Bitrate (kbps):** cantidad de datos por segundo de audio (kilobits por segundo).
- **Cambio de signo:** si f es continua en [a, b] y f(a)·f(b) < 0, tiene al menos una raíz ahí.
- **Convergencia lenta / rápida:** qué tan rápido baja el error. Bisección: lenta. Newton-Raphson: alto grado de convergencia (rápida).
- **Diferencias divididas:** cocientes de diferencias que dan los coeficientes del polinomio de Newton.
- **Interpolación:** polinomio que pasa exactamente por los puntos dados.
- **Iteración:** cada repetición de un método.
- **kworb.net:** sitio que recopila los rankings oficiales de Spotify.
- **Método abierto:** arranca desde un valor inicial y no necesita que la raíz esté dentro de un intervalo (Newton-Raphson, secante, punto fijo). Bisección, en cambio, trabaja con un intervalo con cambio de signo.
- **Raíz:** valor donde la función vale 0.
- **Tolerancia:** error máximo aceptado para parar.
- **Top 200:** ranking semanal de las 200 canciones más escuchadas en un país.
