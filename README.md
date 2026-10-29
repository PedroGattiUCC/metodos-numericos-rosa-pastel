# Modelado numérico del resurgimiento de "Rosa Pastel" (Belanova)

Proyecto integrador de **Taller de Métodos Numéricos**, Universidad Católica de Córdoba.
Docente: Ing. Carlos Arnaudo · Comisión 46324 · 2026-2.
Integrantes: Pedro Gatti, Facundo Grillo y Gonzalo Marin.

## Objetivo
En 2023 "Rosa Pastel" (2006) volvió a ser viral por un trend de TikTok. Con 47 semanas reales de reproducciones en Spotify México se estima **cuándo la canción superó los 100 millones de reproducciones** y **qué ancho de banda exigió su semana pico**. Es un problema de pronóstico de demanda para dimensionar la red de un servicio de streaming.

## Métodos
Solo métodos vistos en la materia:
1. **Interpolación polinomial de Newton** (diferencias divididas) con los 4 datos semanales que rodean los 100 M → polinomio P(t) de grado 3.
2. **Bisección y Newton-Raphson** para la raíz de f(t) = P(t) − 100, con tolerancia |Ea| < 10⁻⁴ %, y comparación de los dos métodos.

## Aplicación de ingeniería
Ancho de banda (Mbps) = reproducciones por semana × 160 kbps × 186 s ÷ 1000 ÷ 604 800 s.
Supuestos: duración de 3:06 ([Dulce Beat, Wikipedia](https://es.wikipedia.org/wiki/Dulce_Beat)) y calidad de 160 kbps ([Spotify, calidad de audio](https://support.spotify.com/us/article/audio-quality/)). Son órdenes de magnitud, no datos de Spotify.

## Resultados (Rosa Pastel)
- Los datos muestran que el acumulado pasa de 99,60 M (semana 35) a 102,74 M (semana 36).
- Interpolación con las semanas 34 a 37: P(t) = 96,349 + 3,25351(t−34) − 0,05879(t−34)(t−35) − 0,009340(t−34)(t−35)(t−36).
- Hito de 100 M: t* = 35,12 semanas (≈ 28/09/2023). Bisección: 15 iteraciones. Newton-Raphson: 3.
- Semana pico: 26 (27/07/2023), con 4,17 M de reproducciones ≈ **205 Mbps** de promedio.

## El mismo método en otras canciones
| Canción | Semanas | Datos usados | Hito 100 M | Iter. bisección / Newton |
|---|---|---|---|---|
| Rosa Pastel (Belanova) | 47 | 34 a 37 | 28/09/2023 | 15 / 3 |
| Ella Baila Sola (Eslabón Armado y Peso Pluma) | 52 | 2 a 5 | 19/04/2023 | 18 / 4 |
| Tití Me Preguntó (Bad Bunny) | 52 | 9 a 12 | 21/07/2022 | 17 / 3 |

Para analizar otra canción:
1. Bajar su historial semanal de [kworb.net](https://kworb.net/spotify/).
2. Guardarlo en `CODIGO/datos/` con las columnas `fecha,streams`.
3. Agregar una línea a `CANCIONES` en el script.

Si se quiere otra meta, se cambia `META`. Para el ancho de banda de otra canción, se cambia `DURACION_S`.

## Cómo correrlo
```bash
pip install -r requirements.txt
python3 CODIGO/analisis_resurgimiento_rosa_pastel.py
```
Imprime las tablas, guarda los 3 gráficos en `GRAFICOS/` y la tabla `CODIGO/comparacion_canciones.csv`.

## Archivos
- `CODIGO/`: script y datos.
- `GRAFICOS/`: interpolación, convergencia y comparación de canciones.
- `ENTREGABLES/`: informe, presentación (Word, PowerPoint y PDF) y planilla de Excel (con fórmulas: datos, diferencias divididas, bisección y Newton).

## Fuentes de datos
Historial de charts semanales de Spotify México en kworb.net: [Rosa Pastel](https://kworb.net/spotify/track/6Z0ybnsUBhbZ9ZjPW64eoF.html) · [Ella Baila Sola](https://kworb.net/spotify/track/3qQbCzHBycnDpGskqOWY0E.html) · [Tití Me Preguntó](https://kworb.net/spotify/track/1IHWl5LamUGEuP4ozKQSXZ.html).
