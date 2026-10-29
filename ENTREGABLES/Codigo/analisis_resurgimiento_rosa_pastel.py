#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taller de Métodos Numéricos - Universidad Católica de Córdoba (UCC)
Docente: Ing. Carlos Arnaudo
Proyecto Integrador: Modelado Numérico del Resurgimiento de 'Rosa Pastel' (Belanova)
Alumnos: Gatti Pedro, Grillo Facundo, Marin Gonzalo
Comisión: 46324 - Ciclo Lectivo: 2026-2

Métodos usados (todos de la materia):
  1. Interpolación polinomial de Newton (diferencias divididas) con los 4 datos
     que rodean la meta -> polinomio P(t) de grado 3
  2. Bisección y Newton-Raphson -> semana en que P(t) = 100 millones
Aplicación de ingeniería: el pico de reproducciones semanales se traduce a
ancho de banda (Mbps) para dimensionar la red.
"""

import csv
import os
from datetime import date, timedelta

import numpy as np
import matplotlib.pyplot as plt


# Para analizar otra canción alcanza con agregar una línea y su CSV en datos/
CANCIONES = [
    ("Rosa Pastel (Belanova)", "datos/rosa_pastel_belanova.csv"),
    ("Ella Baila Sola (Eslabón Armado y Peso Pluma)", "datos/ella_baila_sola_eslabon_armado_peso_pluma.csv"),
    ("Tití me preguntó (Bad Bunny)", "datos/titi_me_pregunto_bad_bunny.csv"),
]
CARPETA = os.path.dirname(os.path.abspath(__file__))
GRAFICOS = os.path.join(CARPETA, "graficos")
META = 100.0          # millones de reproducciones acumuladas
TOLERANCIA = 1e-4     # error relativo porcentual aproximado |Ea| (%)

# Supuestos para pasar reproducciones a ancho de banda (no son datos de Spotify)
DURACION_S = 186      # "Rosa Pastel" dura 3:06 (listado del álbum Dulce Beat)
BITRATE_KBPS = 160    # calidad de audio estándar de Spotify
SEGUNDOS_SEMANA = 7 * 24 * 3600


def cargar_csv(ruta):
    """Lee fecha,streams (ignora las líneas #) y devuelve los streams en millones."""
    with open(ruta, encoding="utf-8") as archivo:
        filas = list(csv.DictReader(l for l in archivo if l.strip() and not l.startswith("#")))
    fechas = [fila["fecha"] for fila in filas]
    streams = np.array([float(fila["streams"]) for fila in filas]) / 1e6
    return fechas, streams


def diferencias_divididas(x, y):
    """Tabla de diferencias divididas. La fila 0 tiene los coeficientes b0, b1, b2, b3."""
    n = len(x)
    tabla = np.zeros((n, n))
    tabla[:, 0] = y
    for j in range(1, n):
        for i in range(n - j):
            tabla[i, j] = (tabla[i + 1, j - 1] - tabla[i, j - 1]) / (x[i + j] - x[i])
    return tabla


def polinomio_newton(x, b):
    """P(t) = b0 + b1(t-x0) + b2(t-x0)(t-x1) + b3(t-x0)(t-x1)(t-x2), desarrollado."""
    P = np.poly1d([0.0])
    producto = np.poly1d([1.0])
    for xi, bi in zip(x, b):
        P = P + bi * producto
        producto = producto * np.poly1d([1.0, -xi])
    return P


def error_porcentual(nuevo, anterior):
    return abs((nuevo - anterior) / nuevo) * 100.0


def biseccion(f, a, b):
    """Método cerrado: parte el intervalo a la mitad hasta que |Ea| < TOLERANCIA."""
    registros = []      # (iteración, a, b, xr, f(xr), |Ea|)
    anterior = None
    for it in range(1, 101):
        xr = (a + b) / 2.0
        ea = 100.0 if anterior is None else error_porcentual(xr, anterior)
        registros.append((it, a, b, xr, f(xr), ea))
        if f(xr) == 0 or ea < TOLERANCIA:
            break
        if f(a) * f(xr) < 0:
            b = xr
        else:
            a = xr
        anterior = xr
    return xr, registros


def newton_raphson(f, df, x):
    """Método abierto: x_(i+1) = x_i - f(x_i) / f'(x_i) hasta que |Ea| < TOLERANCIA."""
    registros = []      # (iteración, x_i, f(x_i), f'(x_i), x_(i+1), |Ea|)
    for it in range(1, 51):
        if abs(df(x)) < 1e-12:
            raise ValueError("Newton-Raphson: la derivada es casi cero.")
        siguiente = x - f(x) / df(x)
        ea = error_porcentual(siguiente, x)
        registros.append((it, x, f(x), df(x), siguiente, ea))
        x = siguiente
        if ea < TOLERANCIA:
            break
    return x, registros


def mbps(millones_por_semana):
    """Ancho de banda promedio de una semana: reproducciones x megabits por reproducción / segundos."""
    megabits_por_reproduccion = BITRATE_KBPS * DURACION_S / 1000.0
    return millones_por_semana * 1e6 * megabits_por_reproduccion / SEGUNDOS_SEMANA


def analizar_cancion(nombre, ruta, detalle=False):
    fechas, streams = cargar_csv(ruta)
    t = np.arange(len(streams), dtype=float)
    S = np.cumsum(streams)                       # reproducciones acumuladas (M)

    # Semana k: la última con S < META. Se usan los datos k-1, k, k+1 y k+2.
    k = int(np.argmax(S >= META)) - 1
    puntos = slice(k - 1, k + 3)
    tabla = diferencias_divididas(t[puntos], S[puntos])
    P = polinomio_newton(t[puntos], tabla[0])

    # Raíz de f(t) = P(t) - 100 en [t_k, t_k+1], donde f cambia de signo
    f = lambda x: P(x) - META
    raiz_b, reg_b = biseccion(f, t[k], t[k + 1])
    raiz_n, reg_n = newton_raphson(f, P.deriv(), t[k])
    fecha_hito = date.fromisoformat(fechas[0]) + timedelta(days=raiz_n * 7)

    # Aplicación: semana con más reproducciones -> ancho de banda necesario
    pico = int(np.argmax(streams))

    r = {"nombre": nombre, "fechas": fechas, "streams": streams, "t": t, "S": S,
         "k": k, "puntos": puntos, "tabla": tabla, "P": P,
         "raiz_b": raiz_b, "reg_b": reg_b, "raiz_n": raiz_n, "reg_n": reg_n,
         "fecha_hito": fecha_hito, "pico": pico, "mbps_pico": mbps(streams[pico])}
    if detalle:
        imprimir_detalle(r)
    return r


def imprimir_detalle(r):
    print("=" * 70)
    print(f"1. DATOS - {r['nombre']}")
    print("=" * 70)
    print(f"{'t':>3} | {'Fecha':^10} | {'Streams (M)':>11} | {'S(t) acumulado':>14}")
    for i, fecha in enumerate(r["fechas"]):
        print(f"{i:>3} | {fecha} | {r['streams'][i]:>11.4f} | {r['S'][i]:>14.3f}")

    print("\n" + "=" * 70)
    print("2. INTERPOLACIÓN DE NEWTON (diferencias divididas)")
    print("=" * 70)
    x = r["t"][r["puntos"]]
    print(f"{'t':>4} | {'S(t)':>9} | {'1ra':>9} | {'2da':>9} | {'3ra':>10}")
    for i in range(4):
        valores = " | ".join(f"{r['tabla'][i, j]:>9.5f}" for j in range(1, 4 - i))
        print(f"{x[i]:>4.0f} | {r['tabla'][i, 0]:>9.3f} | {valores}")
    b0, b1, b2, b3 = r["tabla"][0]
    print(f"\nP(t) = {b0:.3f} {b1:+.5f}(t-{x[0]:.0f}) {b2:+.5f}(t-{x[0]:.0f})(t-{x[1]:.0f})"
          f" {b3:+.6f}(t-{x[0]:.0f})(t-{x[1]:.0f})(t-{x[2]:.0f})")
    a, b, c, d = r["P"].coeffs
    print(f"Desarrollado: P(t) = {a:.6f} t^3 {b:+.6f} t^2 {c:+.6f} t {d:+.6f}")

    k = r["k"]
    print("\n" + "=" * 70)
    print(f"3. RAÍZ DE f(t) = P(t) - {META:g} = 0   (intervalo [{k}, {k + 1}])")
    print("=" * 70)
    print(f"f({k}) = {r['S'][k] - META:.4f} < 0  y  f({k + 1}) = {r['S'][k + 1] - META:.4f} > 0")
    print("Bisección")
    print(f"{'it':>3} | {'a':>9} | {'b':>9} | {'xr':>10} | {'f(xr)':>9} | {'|Ea| %':>10}")
    for it, a0, b0, xr, fxr, ea in r["reg_b"]:
        print(f"{it:>3} | {a0:>9.5f} | {b0:>9.5f} | {xr:>10.6f} | {fxr:>9.4f} | {ea:>10.6f}")
    print(f">> t* = {r['raiz_b']:.6f} semanas en {len(r['reg_b'])} iteraciones")
    print(f"\nNewton-Raphson (t0 = {k})")
    print(f"{'it':>3} | {'x_i':>10} | {'f(x_i)':>10} | {'f´(x_i)':>9} | {'x_i+1':>10} | {'|Ea| %':>10}")
    for it, x0, fx, dfx, sig, ea in r["reg_n"]:
        print(f"{it:>3} | {x0:>10.6f} | {fx:>10.6f} | {dfx:>9.4f} | {sig:>10.6f} | {ea:>10.6f}")
    print(f">> t* = {r['raiz_n']:.6f} semanas en {len(r['reg_n'])} iteraciones -> {r['fecha_hito']:%d/%m/%Y}")

    print("\n" + "=" * 70)
    print("4. APLICACIÓN: ANCHO DE BANDA EN LA SEMANA PICO")
    print("=" * 70)
    p = r["pico"]
    print(f"Supuestos: {DURACION_S} s por reproducción a {BITRATE_KBPS} kbps (órdenes de magnitud).")
    print(f"Semana pico: {p} ({r['fechas'][p]}) con {r['streams'][p]:.3f} M de reproducciones")
    print(f"Ancho de banda promedio en esa semana: {r['mbps_pico']:.1f} Mbps")


def dibujar_hito(eje, r, zoom):
    """Datos acumulados, polinomio interpolante y el punto donde cruza la meta."""
    x = r["t"][r["puntos"]]
    eje.scatter(r["t"], r["S"], color='#9b59b6', s=18, label="Datos acumulados (kworb.net)")
    t_fino = np.linspace(x[0], x[-1], 100)
    eje.plot(t_fino, r["P"](t_fino), color='#2c3e50', linewidth=2, label="Polinomio de Newton (4 datos)")
    eje.axhline(META, color='#c0392b', linestyle='--', linewidth=1.2, label="Meta: 100 M")
    eje.scatter([r["raiz_n"]], [META], color='#c0392b', s=55, zorder=5,
                label=f"t* = {r['raiz_n']:.2f} sem ({r['fecha_hito']:%d/%m/%Y})")
    if zoom:
        eje.set_xlim(x[0] - 0.5, x[-1] + 0.5)
        eje.set_ylim(r["S"][r["puntos"]].min() - 2, r["S"][r["puntos"]].max() + 2)
    eje.set_xlabel(f"Semanas desde {r['fechas'][0]}")
    eje.set_ylabel("Millones acumulados")
    eje.grid(True, linestyle='--', alpha=0.6)


def grafico_interpolacion(r):
    fig, (izq, der) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=200)
    dibujar_hito(izq, r, zoom=False)
    izq.set_title("Reproducciones acumuladas", fontsize=12, fontweight='bold')
    izq.legend(loc='upper left', fontsize=9)
    dibujar_hito(der, r, zoom=True)
    der.set_title("Zoom: interpolación cerca de la meta", fontsize=12, fontweight='bold')
    der.legend(loc='upper left', fontsize=9)
    fig.suptitle("'Rosa Pastel': cuándo superó los 100 millones", fontsize=13, fontweight='bold')
    fig.tight_layout()
    fig.savefig(os.path.join(GRAFICOS, "grafico_1_ajuste_curva_streams.png"))
    plt.close(fig)


def grafico_convergencia(r):
    plt.figure(figsize=(10, 6), dpi=200)
    plt.semilogy([x[0] for x in r["reg_b"]], [x[5] for x in r["reg_b"]], 'o-', color='#2980b9',
                 label=f"Bisección ({len(r['reg_b'])} iteraciones)")
    plt.semilogy([x[0] for x in r["reg_n"]], [x[5] for x in r["reg_n"]], 's-', color='#c0392b',
                 label=f"Newton-Raphson ({len(r['reg_n'])} iteraciones)")
    plt.axhline(TOLERANCIA, color='gray', linestyle='--', label="Tolerancia 10⁻⁴ %")
    plt.title("Convergencia: Bisección vs. Newton-Raphson", fontsize=13, fontweight='bold')
    plt.xlabel("Iteración")
    plt.ylabel("|Ea| (%)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS, "grafico_2_convergencia_biseccion_vs_newton.png"))
    plt.close()


def grafico_canciones(resultados):
    fig, ejes = plt.subplots(1, len(resultados), figsize=(15, 5), dpi=200)
    for eje, r in zip(ejes, resultados):
        dibujar_hito(eje, r, zoom=False)
        eje.set_title(r["nombre"], fontsize=11, fontweight='bold')
        eje.legend(loc='lower right', fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(GRAFICOS, "grafico_3_comparacion_canciones.png"))
    plt.close(fig)


def tabla_comparativa(resultados):
    columnas = ["Canción", "Semanas", "Total M", "Datos usados (semanas)", "Hito 100 M (semana)",
                "Fecha hito", "Iter. bisección", "Iter. Newton", "Semana pico", "Pico (M/semana)"]
    filas = [[r["nombre"], len(r["t"]), f"{r['S'][-1]:.1f}", f"{r['k'] - 1} a {r['k'] + 2}",
              f"{r['raiz_n']:.2f}", f"{r['fecha_hito']:%d/%m/%Y}", len(r["reg_b"]), len(r["reg_n"]),
              r["pico"], f"{r['streams'][r['pico']]:.3f}"] for r in resultados]
    print("\n" + "=" * 70)
    print("5. EL MISMO MÉTODO APLICADO A OTRAS CANCIONES")
    print("=" * 70)
    print("(El ancho de banda se calcula solo para Rosa Pastel: depende de la duración de cada canción.)")
    for fila in filas:
        print(" | ".join(f"{c}: {v}" for c, v in zip(columnas, fila)))
    with open(os.path.join(CARPETA, "comparacion_canciones.csv"), "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(columnas)
        escritor.writerows(filas)


def main():
    os.makedirs(GRAFICOS, exist_ok=True)
    resultados = [analizar_cancion(nombre, os.path.join(CARPETA, ruta), detalle=(i == 0))
                  for i, (nombre, ruta) in enumerate(CANCIONES)]
    grafico_interpolacion(resultados[0])
    grafico_convergencia(resultados[0])
    grafico_canciones(resultados)
    tabla_comparativa(resultados)
    print("\n[OK] Gráficos en graficos/ y tabla en comparacion_canciones.csv")


if __name__ == '__main__':
    main()
