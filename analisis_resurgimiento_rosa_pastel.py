#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taller de Métodos Numéricos - Universidad Católica de Córdoba (UCC)
Docente: Ing. Carlos Arnaudo
Proyecto Integrador: Modelado Numérico del Resurgimiento de 'Rosa Pastel' (Belanova)
Alumnos: Gatti Pedro, Grillo Facundo, Marin Gonzalo
Comisión: 46324 - Ciclo Lectivo: 2026-2

Métodos usados:
  1. Regresión polinómica cúbica por mínimos cuadrados -> modelo continuo S(t)
  2. Bisección y Newton-Raphson -> semana en que S(t) = 100 millones
  3. Diferenciación numérica (adelante, atrás, centrada) -> ritmo de streams y pico
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# DATOS REALES
# Streams semanales de 'Rosa Pastel' en el chart semanal de Spotify México.
# Fuente: kworb.net/spotify/track/6Z0ybnsUBhbZ9ZjPW64eoF.html (datos de charts.spotify.com)
# Son 47 semanas consecutivas de 2023 (fecha = cierre de la semana del chart).
# -------------------------------------------------------------
DATOS = [
    ("2023-01-26", 1137349), ("2023-02-02", 1445318), ("2023-02-09", 1417458), ("2023-02-16", 1667194),
    ("2023-02-23", 1778948), ("2023-03-02", 1889805), ("2023-03-09", 1954026), ("2023-03-16", 2169923),
    ("2023-03-23", 2635047), ("2023-03-30", 2788541), ("2023-04-06", 2564692), ("2023-04-13", 2148814),
    ("2023-04-20", 2221385), ("2023-04-27", 2368056), ("2023-05-04", 2217941), ("2023-05-11", 2277461),
    ("2023-05-18", 2647092), ("2023-05-25", 2617613), ("2023-06-01", 2842061), ("2023-06-08", 2899192),
    ("2023-06-15", 3024138), ("2023-06-22", 3092700), ("2023-06-29", 3160985), ("2023-07-06", 3102254),
    ("2023-07-13", 3084357), ("2023-07-20", 3563141), ("2023-07-27", 4170775), ("2023-08-03", 3508445),
    ("2023-08-10", 3799664), ("2023-08-17", 3829770), ("2023-08-24", 3612550), ("2023-08-31", 3507013),
    ("2023-09-07", 4064808), ("2023-09-14", 3759711), ("2023-09-21", 3380414), ("2023-09-28", 3253511),
    ("2023-10-05", 3135938), ("2023-10-12", 2962324), ("2023-10-19", 2770651), ("2023-10-26", 2736409),
    ("2023-11-02", 3060277), ("2023-11-09", 3068245), ("2023-11-16", 3244273), ("2023-11-23", 3051800),
    ("2023-11-30", 3246738), ("2023-12-07", 3206277), ("2023-12-14", 2811829),
]


def main():
    # -------------------------------------------------------------
    # 1. DATOS: t = semana (0 = semana del 26/01/2023), streams en millones
    # -------------------------------------------------------------
    fechas = [d for d, _ in DATOS]
    weekly_streams = np.array([v for _, v in DATOS], dtype=float) / 1e6
    t = np.arange(len(DATOS), dtype=float)
    S_accum = np.cumsum(weekly_streams)  # S(t): streams acumulados al cierre de la semana t
    n = len(t)

    print("=" * 80)
    print("PROYECTO: MODELADO NUMÉRICO DEL RESURGIMIENTO DE 'ROSA PASTEL' (SPOTIFY MÉXICO 2023)")
    print("Alumnos: Pedro Gatti, Facundo Grillo, Gonzalo Marin - UCC 2026")
    print("=" * 80)
    print("\n1. DATOS REALES (fuente: kworb.net / Spotify Charts México):")
    print(f"{'t':^5}|{'Semana':^12}|{'Streams semana (M)':^20}|{'Acumulado S(t) (M)':^20}")
    print("-" * 60)
    for i in range(n):
        print(f"{t[i]:^5.0f}|{fechas[i]:^12}|{weekly_streams[i]:^20.3f}|{S_accum[i]:^20.3f}")

    # -------------------------------------------------------------
    # 2. AJUSTE DE CURVAS: REGRESIÓN POLINÓMICA CÚBICA POR MÍNIMOS CUADRADOS
    # -------------------------------------------------------------
    # S(t) = a*t^3 + b*t^2 + c*t + d
    coeffs = np.polyfit(t, S_accum, 3)  # resuelve las ecuaciones normales
    a, b, c, d = coeffs
    poly = np.poly1d(coeffs)
    poly_deriv = poly.deriv()

    y_pred = poly(t)
    Sr = np.sum((S_accum - y_pred) ** 2)          # suma de cuadrados de los residuos
    St = np.sum((S_accum - np.mean(S_accum)) ** 2)  # suma total de cuadrados
    r2 = 1.0 - Sr / St                            # coeficiente de determinación
    syx = np.sqrt(Sr / (n - 4))                   # error estándar (4 coeficientes estimados)

    print("\n" + "=" * 80)
    print("2. REGRESIÓN POLINÓMICA CÚBICA (MÍNIMOS CUADRADOS):")
    print("=" * 80)
    print(f"Modelo: S(t) = ({a:.6f})*t^3 + ({b:.6f})*t^2 + ({c:.6f})*t + ({d:.6f})")
    print(f"Sr = {Sr:.4f}   St = {St:.4f}")
    print(f"R^2 = {r2:.6f} ({r2*100:.2f}%)   Sy/x = {syx:.4f} M streams")

    # -------------------------------------------------------------
    # 3. BÚSQUEDA DE RAÍCES: ¿EN QUÉ SEMANA SE LLEGA A 100 MILLONES?
    # -------------------------------------------------------------
    TARGET = 100.0
    f = lambda x: poly(x) - TARGET
    df = lambda x: poly_deriv(x)
    tol = 1e-4  # error relativo porcentual

    # Intervalo inicial tomado de la tabla: última semana con S < 100 y la siguiente
    k = int(np.argmax(S_accum >= TARGET))
    a0, b0 = t[k - 1], t[k]

    print("\n" + "=" * 80)
    print("3. RAÍCES DE f(t) = S(t) - 100 = 0")
    print("=" * 80)

    # 3.1 Bisección
    print(f"\n3.1 BISECCIÓN. Intervalo inicial [{a0:.0f}, {b0:.0f}] "
          f"(S({a0:.0f}) = {S_accum[k-1]:.2f} < 100 < S({b0:.0f}) = {S_accum[k]:.2f})")
    print(f"{'Iter':^6}|{'a':^10}|{'b':^10}|{'xr':^12}|{'f(a)':^10}|{'f(xr)':^10}|{'|Ea%|':^12}")
    print("-" * 74)
    a_bis, b_bis = a0, b0
    xr_old = None
    bis_records = []
    for it in range(1, 101):
        xr = (a_bis + b_bis) / 2.0
        fa, fxr = f(a_bis), f(xr)
        ea = abs((xr - xr_old) / xr) * 100.0 if xr_old is not None else 100.0
        bis_records.append((it, ea))
        print(f"{it:^6d}|{a_bis:^10.5f}|{b_bis:^10.5f}|{xr:^12.6f}|{fa:^10.4f}|{fxr:^10.4f}|{ea:^12.6f}")
        if ea < tol:
            break
        if fa * fxr < 0:
            b_bis = xr
        else:
            a_bis = xr
        xr_old = xr
    root_bisection, bisection_iters = xr, it
    print(f">> Bisección: t* = {root_bisection:.6f} semanas en {bisection_iters} iteraciones.")

    # 3.2 Newton-Raphson
    print(f"\n3.2 NEWTON-RAPHSON. Valor inicial t0 = {a0:.0f}")
    print(f"{'Iter':^6}|{'x_i':^12}|{'f(x_i)':^12}|{'f_prima(x_i)':^14}|{'x_i+1':^12}|{'|Ea%|':^12}")
    print("-" * 72)
    x = a0
    newton_records = []
    for it in range(1, 51):
        fx, dfx = f(x), df(x)
        x_next = x - fx / dfx
        ea = abs((x_next - x) / x_next) * 100.0
        newton_records.append((it, ea))
        print(f"{it:^6d}|{x:^12.6f}|{fx:^12.6f}|{dfx:^14.6f}|{x_next:^12.6f}|{ea:^12.6f}")
        x = x_next
        if ea < tol:
            break
    root_newton, newton_iters = x, it
    print(f">> Newton-Raphson: t* = {root_newton:.6f} semanas en {newton_iters} iteraciones.")

    # Control: interpolación lineal directa sobre los datos
    t_lineal = t[k - 1] + (TARGET - S_accum[k - 1]) / (S_accum[k] - S_accum[k - 1])
    print(f"\nControl con interpolación lineal entre las semanas {k-1} y {k}: t = {t_lineal:.4f} semanas")
    print(f"Diferencia modelo - interpolación: {(root_newton - t_lineal)*7:.2f} días "
          f"(error típico del ajuste: ±{syx:.2f} M streams)")

    # -------------------------------------------------------------
    # 4. DIFERENCIACIÓN NUMÉRICA: RITMO DE STREAMS dS/dt (h = 1 semana)
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("4. DIFERENCIACIÓN NUMÉRICA (h = 1 semana), en M streams/semana")
    print("=" * 80)
    h = 1.0
    print(f"{'t':^5}|{'Adelante O(h)':^15}|{'Atrás O(h)':^13}|{'Centrada O(h^2)':^17}|{'Modelo S_prima(t)':^19}")
    print("-" * 74)
    for i in range(n):
        fwd = (S_accum[i + 1] - S_accum[i]) / h if i < n - 1 else np.nan
        bwd = (S_accum[i] - S_accum[i - 1]) / h if i > 0 else np.nan
        cnt = (S_accum[i + 1] - S_accum[i - 1]) / (2 * h) if 0 < i < n - 1 else np.nan
        fmt = lambda v, w: f"{v:^{w}.3f}" if not np.isnan(v) else f"{'---':^{w}}"
        print(f"{t[i]:^5.0f}|{fmt(fwd, 15)}|{fmt(bwd, 13)}|{fmt(cnt, 17)}|{poly_deriv(t[i]):^19.3f}")

    # Pico del ritmo de streams: S''(t) = 6at + 2b = 0
    t_peak = -b / (3.0 * a)
    peak_rate = df(t_peak)
    i_max = int(np.argmax(weekly_streams))
    print(f"\nPICO SEGÚN EL MODELO (S''(t) = 0): t = {t_peak:.2f} semanas, "
          f"ritmo = {peak_rate:.3f} M streams/semana")
    print(f"PICO EN LOS DATOS: semana {i_max} ({fechas[i_max]}), {weekly_streams[i_max]:.3f} M streams")

    # -------------------------------------------------------------
    # 5. GRÁFICOS
    # -------------------------------------------------------------
    output_dir = os.path.dirname(os.path.abspath(__file__))
    t_dense = np.linspace(0, n - 1, 300)

    # Gráfico 1: ajuste de curva y hito de 100 M
    plt.figure(figsize=(10, 6), dpi=200)
    plt.scatter(t, S_accum, color='#e91e63', s=30, zorder=5, label='Datos reales acumulados (Spotify México)')
    plt.plot(t_dense, poly(t_dense), color='#2c3e50', linewidth=2.2, label=f'Ajuste cúbico ($R^2 = {r2:.4f}$)')
    plt.axhline(TARGET, color='#d32f2f', linestyle='--', linewidth=1.3, label='100 millones de streams')
    plt.axvline(root_newton, color='#27ae60', linestyle=':', linewidth=2, label=f'Raíz $t^* = {root_newton:.2f}$ semanas')
    plt.title("'Rosa Pastel' (Belanova) en Spotify México, 2023\nStreams acumulados y ajuste por mínimos cuadrados", fontsize=13, fontweight='bold')
    plt.xlabel("Semanas desde el 26/01/2023")
    plt.ylabel("Streams acumulados (millones)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "grafico_1_ajuste_curva_streams.png"))
    plt.close()

    # Gráfico 2: convergencia de bisección vs Newton-Raphson
    plt.figure(figsize=(10, 6), dpi=200)
    plt.semilogy([r[0] for r in bis_records], [r[1] for r in bis_records], marker='o', color='#3498db', label=f'Bisección ({bisection_iters} iteraciones)')
    plt.semilogy([r[0] for r in newton_records], [max(r[1], 1e-12) for r in newton_records], marker='s', color='#e67e22', label=f'Newton-Raphson ({newton_iters} iteraciones)')
    plt.axhline(tol, color='#e74c3c', linestyle='--', label='Tolerancia $10^{-4}$ %')
    plt.title("Convergencia: Bisección (lineal) vs Newton-Raphson (cuadrática)", fontsize=13, fontweight='bold')
    plt.xlabel("Iteración")
    plt.ylabel("Error relativo aproximado $|E_a|$ % (escala log)")
    plt.grid(True, which="both", linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "grafico_2_convergencia_biseccion_vs_newton.png"))
    plt.close()

    # Gráfico 3: ritmo de streams (derivada) y pico
    plt.figure(figsize=(10, 6), dpi=200)
    plt.bar(t, weekly_streams, width=0.7, color='#9b59b6', alpha=0.45, label='Streams semanales medidos')
    plt.plot(t_dense, poly_deriv(t_dense), color='#8e44ad', linewidth=2.2, label="Derivada del modelo $S'(t)$")
    plt.axvline(t_peak, color='#c0392b', linestyle='--', linewidth=1.8, label=f'Pico del modelo: t = {t_peak:.1f} sem ({peak_rate:.2f} M/sem)')
    plt.title("Ritmo de streams por semana (diferenciación)", fontsize=13, fontweight='bold')
    plt.xlabel("Semanas desde el 26/01/2023")
    plt.ylabel("Millones de streams por semana")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "grafico_3_derivada_tasa_viralidad.png"))
    plt.close()
    print("\n[OK] Gráficos guardados en la carpeta del proyecto.")


if __name__ == '__main__':
    main()
