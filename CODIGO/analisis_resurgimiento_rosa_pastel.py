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
     (ecuaciones normales resueltas por eliminación gaussiana)
  2. Trazadora cúbica natural -> modelo de contraste que pasa por los datos
  3. Bisección y Newton-Raphson -> semana en que S(t) = 100 millones
     (sobre la regresión y sobre la trazadora, con interpolación lineal de control)
  4. Diferenciación numérica (adelante, atrás, centrada) -> ritmo de streams y pico
  5. Aplicación de ingeniería: ancho de banda, volumen transferido y ventana en la
     que la demanda S'(t) supera una capacidad C (Bisección y Newton sobre S'(t) - C)
"""

import csv
import os
from datetime import date, timedelta

import numpy as np
import matplotlib.pyplot as plt


# Para agregar una canción, alcanza con sumar una tupla a esta lista.
CANCIONES = [
    ("Rosa Pastel (Belanova)", "datos/rosa_pastel_belanova.csv"),
    ("Ella Baila Sola (Eslabón Armado y Peso Pluma)", "datos/ella_baila_sola_eslabon_armado_peso_pluma.csv"),
    ("Tití me preguntó (Bad Bunny)", "datos/titi_me_pregunto_bad_bunny.csv"),
]
CARPETA = os.path.dirname(os.path.abspath(__file__))
# Los gráficos van a la carpeta GRAFICOS/ de la raíz del repositorio
GRAFICOS = os.path.normpath(os.path.join(CARPETA, os.pardir, "GRAFICOS"))
TOLERANCIA = 1e-4  # error relativo porcentual, igual al trabajo original
VENTANA_PICO = 6  # semanas a cada lado del máximo de streams semanales

# Supuestos del dimensionamiento (ver informe, sección de aplicación de ingeniería).
# Son supuestos de planificación, no datos de Spotify.
DURACION_S = 186                 # "Rosa Pastel": 3:06 según el listado del álbum Dulce Beat
BITRATES_KBPS = (96, 160, 320)   # calidad baja, la de referencia y la máxima de Spotify
BITRATE_REF_KBPS = 160
FACTOR_HORA_PICO = 2.0           # cuántas veces supera la hora pico al promedio semanal
CAPACIDAD_MBPS = 150.0           # capacidad de ejemplo reservada para la canción
SEGUNDOS_SEMANA = 7 * 24 * 3600


def cargar_csv(ruta):
    """Lee fecha,streams, omite comentarios y convierte los streams a millones."""
    fechas = []
    streams = []
    with open(ruta, encoding="utf-8", newline="") as archivo:
        filas = csv.DictReader(linea for linea in archivo
                               if linea.strip() and not linea.lstrip().startswith("#"))
        for fila in filas:
            fecha = date.fromisoformat(fila["fecha"])
            valor = int(fila["streams"])
            if valor < 0:
                raise ValueError("Los streams no pueden ser negativos.")
            if fechas and (fecha - date.fromisoformat(fechas[-1])).days != 7:
                raise ValueError("Las fechas deben ser semanas consecutivas, separadas por 7 días.")
            fechas.append(fecha.isoformat())
            streams.append(valor)
    return fechas, np.array(streams, dtype=float) / 1e6


def error_porcentual(nuevo, anterior):
    """Evita dividir por cero si una raíz cae en la semana cero."""
    if nuevo == 0:
        return 0.0 if anterior == 0 else float("inf")
    return abs((nuevo - anterior) / nuevo) * 100.0


def eliminacion_gaussiana(A, b):
    """Eliminación gaussiana (apunte 4.2): triangulación con m_ki = a_ki / a_ii
    y sustitución hacia atrás."""
    M = np.hstack([np.array(A, dtype=float), np.array(b, dtype=float).reshape(-1, 1)])
    n = len(b)
    for i in range(n - 1):
        if M[i, i] == 0.0:
            raise ZeroDivisionError(f"Pivote nulo en la fila {i + 1}.")
        for k in range(i + 1, n):
            m_ki = M[k, i] / M[i, i]
            M[k, i:] = M[k, i:] - m_ki * M[i, i:]
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (M[i, n] - np.dot(M[i, i + 1:n], x[i + 1:n])) / M[i, i]
    return x


def regresion_polinomica(x, y, m):
    """Mínimos cuadrados de grado m (extensión de la regresión lineal, apunte 5.2).
    Ecuaciones normales: sum(x^(j+k)) * a_k = sum(x^j * y). Devuelve [a0, ..., am]."""
    A = np.array([[np.sum(x ** (j + k)) for k in range(m + 1)] for j in range(m + 1)])
    b = np.array([np.sum((x ** j) * y) for j in range(m + 1)])
    return eliminacion_gaussiana(A, b), A, b


def pico_local(t, S, centro, w=VENTANA_PICO):
    """Ajusta el acumulado en una ventana y busca el máximo de su derivada."""
    izquierda = max(0, centro - w)
    derecha = min(len(t) - 1, centro + w)
    if derecha - izquierda + 1 < 4:
        raise ValueError("Se necesitan al menos 4 puntos para la cúbica local.")
    ascendentes, _, _ = regresion_polinomica(t[izquierda:derecha + 1],
                                           S[izquierda:derecha + 1], 3)
    coeficientes = ascendentes[::-1]  # [a, b, c, d], igual que el modelo global
    a, b, c, d = coeficientes
    t_pico = -b / (3.0 * a) if a != 0 else None
    ritmo = float(3.0 * a * t_pico ** 2 + 2.0 * b * t_pico + c) if t_pico is not None else None
    ventana = (float(t[izquierda]), float(t[derecha]))
    valido = bool(a < 0 and ventana[0] <= t_pico <= ventana[1])
    return {"coeficientes": coeficientes, "ventana": ventana,
            "t_pico": t_pico, "ritmo": ritmo, "valido": valido}


def trazadora_cubica_natural(x, y):
    """Trazadora cúbica natural (apunte 5.5, algoritmo de Burden-Faires, pasos 1 a 6).
    Coeficientes de S_i(x) = a_i + b_i(x-x_i) + c_i(x-x_i)^2 + d_i(x-x_i)^3."""
    N = len(x) - 1
    a = np.array(y, dtype=float)
    h = np.diff(x)                                               # PASO 1
    alfa = np.zeros(N + 1)
    for j in range(1, N):                                        # PASO 2
        alfa[j] = 3.0 / h[j] * (a[j + 1] - a[j]) - 3.0 / h[j - 1] * (a[j] - a[j - 1])
    l, mu, z = np.ones(N + 1), np.zeros(N + 1), np.zeros(N + 1)   # PASOS 3 y 5
    for j in range(1, N):                                        # PASO 4
        l[j] = 2.0 * (x[j + 1] - x[j - 1]) - h[j - 1] * mu[j - 1]
        mu[j] = h[j] / l[j]
        z[j] = (alfa[j] - h[j - 1] * z[j - 1]) / l[j]
    c, b, d = np.zeros(N + 1), np.zeros(N), np.zeros(N)
    for i in range(N - 1, -1, -1):                               # PASO 6
        c[i] = z[i] - mu[i] * c[i + 1]
        b[i] = (a[i + 1] - a[i]) / h[i] - h[i] * (c[i + 1] + 2.0 * c[i]) / 3.0
        d[i] = (c[i + 1] - c[i]) / (3.0 * h[i])
    return a[:-1], b, c[:-1], d


def evaluar_trazadora(coefs, x_nodos, xv, derivada=0):
    """PASO 7: evalúa el tramo que contiene a xv (o su primera / segunda derivada)."""
    a, b, c, d = coefs
    i = int(np.clip(np.searchsorted(x_nodos, xv, side='right') - 1, 0, len(a) - 1))
    dx = xv - x_nodos[i]
    if derivada == 0:
        return a[i] + b[i] * dx + c[i] * dx ** 2 + d[i] * dx ** 3
    if derivada == 1:
        return b[i] + 2.0 * c[i] * dx + 3.0 * d[i] * dx ** 2
    return 2.0 * c[i] + 6.0 * d[i] * dx


def biseccion(f, izquierda, derecha, detalle=False):
    """Bisección escrita a mano; requiere un intervalo con cambio de signo."""
    if f(izquierda) == 0:
        return izquierda, 0, []
    if f(derecha) == 0:
        return derecha, 0, []
    if f(izquierda) * f(derecha) > 0:
        raise ValueError("Bisección requiere un cambio de signo.")
    if detalle:
        print(f"{'Iter':^6}|{'a':^10}|{'b':^10}|{'xr':^12}|{'f(a)':^10}|{'f(xr)':^10}|{'|Ea%|':^12}")
        print("-" * 74)
    anterior = None
    registros = []
    for it in range(1, 101):
        xr = (izquierda + derecha) / 2.0
        fa, fxr = f(izquierda), f(xr)
        ea = error_porcentual(xr, anterior) if anterior is not None else 100.0
        registros.append((it, ea, izquierda, derecha, xr, fa, fxr))
        if detalle:
            print(f"{it:^6d}|{izquierda:^10.5f}|{derecha:^10.5f}|{xr:^12.6f}|{fa:^10.4f}|{fxr:^10.4f}|{ea:^12.6f}")
        if fxr == 0 or ea < TOLERANCIA:
            return xr, it, registros
        if fa * fxr < 0:
            derecha = xr
        else:
            izquierda = xr
        anterior = xr
    return None, it, registros  # no presentar como raíz si no hubo convergencia


def newton_raphson(f, df, inicial, limite, detalle=False):
    """Newton escrito a mano, con controles de derivada y dominio observado."""
    if detalle:
        print(f"{'Iter':^6}|{'x_i':^12}|{'f(x_i)':^12}|{'f_prima(x_i)':^14}|{'x_i+1':^12}|{'|Ea%|':^12}")
        print("-" * 72)
    x = inicial
    registros = []
    if f(x) == 0:
        return x, 0, registros
    for it in range(1, 51):
        fx, dfx = f(x), df(x)
        if abs(dfx) < 1e-12:
            break
        siguiente = x - fx / dfx
        if not np.isfinite(siguiente) or not 0 <= siguiente <= limite:
            break
        ea = error_porcentual(siguiente, x)
        registros.append((it, ea, x, fx, dfx, siguiente))
        if detalle:
            print(f"{it:^6d}|{x:^12.6f}|{fx:^12.6f}|{dfx:^14.6f}|{siguiente:^12.6f}|{ea:^12.6f}")
        x = siguiente
        if f(x) == 0 or ea < TOLERANCIA:
            return x, it, registros
    return None, len(registros), registros


def diferencias_finitas(acumulado):
    """h = 1 semana; la centrada usa adelante/atrás en los extremos."""
    n = len(acumulado)
    adelante = np.full(n, np.nan)
    atras = np.full(n, np.nan)
    centrada = np.full(n, np.nan)
    for i in range(n):
        if i < n - 1:
            adelante[i] = acumulado[i + 1] - acumulado[i]
        if i > 0:
            atras[i] = acumulado[i] - acumulado[i - 1]
        if 0 < i < n - 1:
            centrada[i] = (acumulado[i + 1] - acumulado[i - 1]) / 2.0
    centrada[0] = adelante[0]
    centrada[-1] = atras[-1]
    return adelante, atras, centrada


def analizar_cancion(nombre, ruta_csv, meta=100.0, detalle=False):
    """Ajusta S(t), busca el hito y compara el pico del modelo con los datos.

    Las semanas se cuentan desde t = 0. Un resultado de raíz None indica
    que el hito no se pudo calcular dentro de las semanas observadas.
    """
    if not np.isfinite(meta) or meta <= 0:
        raise ValueError("La meta debe ser un número positivo y finito.")
    fechas, streams = cargar_csv(ruta_csv)
    n = len(fechas)
    if n < 5:
        raise ValueError("Se necesitan al menos 5 semanas para la cúbica y su Sy/x.")
    t = np.arange(n, dtype=float)
    acumulado = np.cumsum(streams)
    # Ecuaciones normales por eliminación gaussiana; vienen como [d, c, b, a]
    ascendentes, matriz_normal, vector_normal = regresion_polinomica(t, acumulado, 3)
    coeficientes = ascendentes[::-1]
    a, b, c, d = coeficientes
    modelo = np.poly1d(coeficientes)
    derivada = modelo.deriv()
    sr = np.sum((acumulado - modelo(t)) ** 2)
    st = np.sum((acumulado - np.mean(acumulado)) ** 2)
    r2 = 1.0 - sr / st if st > 0 else float("nan")
    syx = np.sqrt(sr / (n - 4))
    # Un acumulado nunca decrece: el modelo solo es físicamente válido si S'(t) > 0
    modelo_creciente = bool(np.all(derivada(np.linspace(0, n - 1, 20 * n)) > 0))
    trazadora = trazadora_cubica_natural(t, acumulado)
    # Cuántas veces cambia de signo S'' en los datos: mide cuánto ruido tiene la serie
    segundas = acumulado[2:] - 2.0 * acumulado[1:-1] + acumulado[:-2]
    cambios_signo_d2 = int(np.sum(segundas[:-1] * segundas[1:] < 0))
    adelante, atras, centrada = diferencias_finitas(acumulado)
    # Pico real: la semana con más streams (equivale a la diferencia hacia atrás de S)
    semana_pico_datos = int(np.argmax(streams))
    t_pico = -b / (3.0 * a) if a != 0 else None
    ritmo_pico = float(derivada(t_pico)) if t_pico is not None else None
    pico_valido = bool(a < 0 and 0 <= t_pico <= n - 1)
    local = pico_local(t, acumulado, semana_pico_datos)
    sensibilidad = {w: pico_local(t, acumulado, semana_pico_datos, w) for w in (4, 6, 8)}

    resultado = {
        "nombre": nombre, "n": n, "fechas": fechas, "streams": streams,
        "t": t, "acumulado": acumulado, "total_millones": float(acumulado[-1]),
        "coeficientes": coeficientes, "a": a, "b": b, "c": c, "d": d,
        "modelo": modelo, "derivada": derivada, "r2": r2, "syx": syx,
        "sr": sr, "st": st, "meta": meta, "intervalo": None,
        "intervalo_modelo": None, "raiz_biseccion": None, "iteraciones_biseccion": 0,
        "raiz_newton": None, "iteraciones_newton": 0, "t_lineal": None,
        "registros_biseccion": [], "registros_newton": [], "fecha_hito": None,
        "t_pico_modelo": t_pico, "ritmo_pico_modelo": ritmo_pico,
        "pico_valido": pico_valido, "semana_pico_datos": semana_pico_datos,
        "valor_pico_datos": float(streams[semana_pico_datos]),
        "adelante": adelante, "atras": atras, "centrada": centrada,
        "pico_local": local, "sensibilidad": sensibilidad,
        "diagnostico": ("global y local" if pico_valido and local["valido"] else
                        "solo local" if local["valido"] else
                        "solo global" if pico_valido else "no aplica"),
        "matriz_normal": matriz_normal, "vector_normal": vector_normal,
        "modelo_creciente": modelo_creciente, "trazadora": trazadora,
        "segundas": segundas, "cambios_signo_d2": cambios_signo_d2,
        "raiz_traz_biseccion": None, "iteraciones_traz_biseccion": 0, "registros_traz_biseccion": [],
        "raiz_traz_newton": None, "iteraciones_traz_newton": 0, "registros_traz_newton": [],
        "fecha_hito_trazadora": None, "dt_semanas": None, "dif_modelo_trazadora": None,
    }
    if detalle:
        imprimir_datos_y_regresion(resultado)
        print("\n" + "=" * 80)
        print(f"3. RAÍCES DE f(t) = S(t) - {meta:g} = 0")
        print("=" * 80)

    f = lambda x: modelo(x) - meta
    if acumulado[-1] < meta:
        print(f"{nombre}: no llega a la meta de {meta:g} M; se omiten las raíces.")
    elif acumulado[0] >= meta:
        print(f"{nombre}: la meta de {meta:g} M ya se alcanzó en t = 0; no se interpola ni se extrapolan raíces.")
    else:
        k = int(np.argmax(acumulado >= meta))
        a0, b0 = t[k - 1], t[k]
        resultado["intervalo"] = [float(a0), float(b0)]
        resultado["t_lineal"] = t[k - 1] + (meta - acumulado[k - 1]) / (acumulado[k] - acumulado[k - 1])
        if detalle:
            print(f"\n3.1 BISECCIÓN. Intervalo inicial [{a0:.0f}, {b0:.0f}] "
                  f"(S({a0:.0f}) = {acumulado[k-1]:.2f} < {meta:g} < S({b0:.0f}) = {acumulado[k]:.2f})")
        # El cruce de los datos puede diferir del cruce de la curva ajustada.
        if f(a0) * f(b0) > 0:
            encontrado = False
            for i in range(n - 1):
                if f(t[i]) * f(t[i + 1]) <= 0:
                    a0, b0 = t[i], t[i + 1]
                    encontrado = True
                    print(f"{nombre}: el intervalo de los datos no encierra la raíz del modelo; se usa [{a0:g}, {b0:g}].")
                    break
            if not encontrado:
                a0 = b0 = None
                print(f"{nombre}: el modelo no encierra la meta en las semanas observadas; se omiten las raíces.")
        if a0 is not None:
            resultado["intervalo_modelo"] = [float(a0), float(b0)]
            raiz_bis, it_bis, registros_bis = biseccion(f, a0, b0, detalle)
            resultado.update(raiz_biseccion=raiz_bis, iteraciones_biseccion=it_bis,
                             registros_biseccion=registros_bis)
            if detalle and raiz_bis is not None:
                print(f">> Bisección: t* = {raiz_bis:.6f} semanas en {it_bis} iteraciones.")
            if detalle:
                print(f"\n3.2 NEWTON-RAPHSON. Valor inicial t0 = {a0:.0f}")
            raiz_newton, it_newton, registros_newton = newton_raphson(f, derivada, a0, n - 1, detalle)
            resultado.update(raiz_newton=raiz_newton, iteraciones_newton=it_newton,
                             registros_newton=registros_newton)
            if detalle and raiz_newton is not None:
                print(f">> Newton-Raphson: t* = {raiz_newton:.6f} semanas en {it_newton} iteraciones.")
            if raiz_bis is None or raiz_newton is None:
                print(f"{nombre}: algún método no convergió; su raíz queda sin resultado.")
            if raiz_newton is not None:
                resultado["fecha_hito"] = (date.fromisoformat(fechas[0]) + timedelta(days=float(raiz_newton) * 7)).isoformat()
                # Incertidumbre que el error del ajuste traslada al tiempo: dt = Sy/x / S'(t*)
                resultado["dt_semanas"] = float(syx / derivada(raiz_newton))

        # Contraste con la trazadora: pasa por los datos, así que su raíz queda en [k-1, k]
        f_traz = lambda x: evaluar_trazadora(trazadora, t, x) - meta
        df_traz = lambda x: evaluar_trazadora(trazadora, t, x, derivada=1)
        if detalle:
            print(f"\n3.3 TRAZADORA CÚBICA NATURAL. Bisección en [{t[k-1]:.0f}, {t[k]:.0f}]")
        raiz_tb, it_tb, registros_tb = biseccion(f_traz, t[k - 1], t[k], detalle)
        if detalle:
            print(f"\nNewton-Raphson sobre la trazadora, t0 = {t[k-1]:.0f}")
        raiz_tn, it_tn, registros_tn = newton_raphson(f_traz, df_traz, t[k - 1], n - 1, detalle)
        resultado.update(raiz_traz_biseccion=raiz_tb, iteraciones_traz_biseccion=it_tb,
                         registros_traz_biseccion=registros_tb, raiz_traz_newton=raiz_tn,
                         iteraciones_traz_newton=it_tn, registros_traz_newton=registros_tn)
        if raiz_tn is not None:
            resultado["fecha_hito_trazadora"] = (date.fromisoformat(fechas[0]) + timedelta(days=float(raiz_tn) * 7)).isoformat()
            if resultado["raiz_newton"] is not None:
                resultado["dif_modelo_trazadora"] = float(resultado["raiz_newton"] - raiz_tn)
        if detalle:
            if raiz_tn is not None:
                print(f">> Trazadora: t* = {raiz_tn:.6f} semanas (bisección {it_tb} it., Newton {it_tn} it.)")
            print(f"\nControl con interpolación lineal entre las semanas {k-1} y {k}: t = {resultado['t_lineal']:.4f} semanas")
            if resultado["raiz_newton"] is not None and resultado["dif_modelo_trazadora"] is not None:
                print(f"Diferencia modelo - interpolación: {(resultado['raiz_newton'] - resultado['t_lineal'])*7:.2f} días "
                      f"(error típico del ajuste: ±{syx:.2f} M streams)")
                dt = resultado["dt_semanas"]
                dif = resultado["dif_modelo_trazadora"]
                print(f"Incertidumbre del modelo: dt = Sy/x / S'(t*) = {syx:.4f} / {derivada(resultado['raiz_newton']):.4f} "
                      f"= {dt:.4f} semanas = ±{dt*7:.2f} días")
                print(f"Diferencia modelo - trazadora: {dif*7:.2f} días "
                      f"({'dentro' if abs(dif) <= dt else 'fuera'} de la incertidumbre del modelo)")
    if detalle:
        imprimir_diferencias(resultado)
    if not pico_valido:
        if a > 0:
            motivo = "a > 0: la inflexión es un mínimo del ritmo"
        elif a == 0:
            motivo = "a = 0: no hay un máximo aislado del ritmo por inflexión"
        else:
            motivo = "la inflexión queda fuera de las semanas observadas"
        print(f"{nombre}: la cúbica no detecta el pico ({motivo}).")
    if detalle:
        print("\nRegresión cúbica local")
        print(f"Ventana: [{local['ventana'][0]:.0f}, {local['ventana'][1]:.0f}] semanas (w = {VENTANA_PICO})")
        al, bl, cl, dl = local["coeficientes"]
        print(f"Coeficientes: a = {al:.6f}, b = {bl:.6f}, c = {cl:.6f}, d = {dl:.6f}")
    if local["valido"]:
        print(f"{nombre}: pico local en t = {local['t_pico']:.2f} semanas, ritmo = {local['ritmo']:.2f} M/semana.")
    else:
        print(f"{nombre}: la cúbica local no detecta un pico válido dentro de su ventana.")
    return resultado


def imprimir_datos_y_regresion(r):
    print("=" * 80)
    if r["nombre"] == CANCIONES[0][0]:
        print("PROYECTO: MODELADO NUMÉRICO DEL RESURGIMIENTO DE 'ROSA PASTEL' (SPOTIFY MÉXICO 2023)")
    else:
        print(f"PROYECTO: MODELADO NUMÉRICO DE {r['nombre'].upper()} (SPOTIFY MÉXICO)")
    print("Alumnos: Pedro Gatti, Facundo Grillo, Gonzalo Marin - UCC 2026")
    print("=" * 80)
    print("\n1. DATOS REALES (fuente: kworb.net / Spotify Charts México):")
    print(f"{'t':^5}|{'Semana':^12}|{'Streams semana (M)':^20}|{'Acumulado S(t) (M)':^20}")
    print("-" * 60)
    for i in range(r["n"]):
        print(f"{r['t'][i]:^5.0f}|{r['fechas'][i]:^12}|{r['streams'][i]:^20.3f}|{r['acumulado'][i]:^20.3f}")
    a, b, c, d = r["coeficientes"]
    print("\n" + "=" * 80)
    print("2. REGRESIÓN POLINÓMICA CÚBICA (MÍNIMOS CUADRADOS):")
    print("=" * 80)
    print("Sistema de ecuaciones normales [A | b] (incógnitas d, c, b, a), resuelto por eliminación gaussiana:")
    for j in range(4):
        fila = "".join(f"{r['matriz_normal'][j, k]:>16.0f}" for k in range(4))
        print(f"{fila}  | {r['vector_normal'][j]:>16.3f}")
    print(f"Modelo: S(t) = ({a:.6f})*t^3 + ({b:.6f})*t^2 + ({c:.6f})*t + ({d:.6f})")
    print(f"Sr = {r['sr']:.4f}   St = {r['st']:.4f}")
    print(f"R^2 = {r['r2']:.6f} ({r['r2']*100:.2f}%)   Sy/x = {r['syx']:.4f} M streams")
    print(f"Validez física: S'(t) > 0 en todo el período -> {'sí' if r['modelo_creciente'] else 'NO'}; "
          f"S(0) modelo = {r['modelo'](0):.3f} M frente a {r['acumulado'][0]:.3f} M medido")


def imprimir_diferencias(r):
    print("\n" + "=" * 80)
    print("4. DIFERENCIACIÓN NUMÉRICA (h = 1 semana), en M streams/semana")
    print("=" * 80)
    print(f"{'t':^5}|{'Adelante O(h)':^15}|{'Atrás O(h)':^13}|{'Centrada O(h^2)':^17}|{'Modelo S_prima(t)':^19}")
    print("-" * 74)
    for i in range(r["n"]):
        fmt = lambda v, w: f"{v:^{w}.3f}" if not np.isnan(v) else f"{'---':^{w}}"
        # La tabla conserva --- donde no existe una diferencia centrada pura.
        cnt = r["centrada"][i] if 0 < i < r["n"] - 1 else np.nan
        print(f"{r['t'][i]:^5.0f}|{fmt(r['adelante'][i], 15)}|{fmt(r['atras'][i], 13)}|{fmt(cnt, 17)}|{r['derivada'](r['t'][i]):^19.3f}")
    if r["pico_valido"]:
        print(f"\nPICO SEGÚN EL MODELO (S''(t) = 0): t = {r['t_pico_modelo']:.2f} semanas, "
              f"ritmo = {r['ritmo_pico_modelo']:.3f} M streams/semana")
    i = r["semana_pico_datos"]
    print(f"PICO EN LOS DATOS (semana con más streams): semana {i} "
          f"({r['fechas'][i]}), {r['valor_pico_datos']:.3f} M streams")


def graficar_rosa_pastel(r):
    """Los mismos tres gráficos, con sus nombres y estilo originales."""
    t, S_accum, weekly_streams = r["t"], r["acumulado"], r["streams"]
    poly, poly_deriv = r["modelo"], r["derivada"]
    r2, TARGET = r["r2"], r["meta"]
    root_newton = r["raiz_newton"]
    bis_records, newton_records = r["registros_biseccion"], r["registros_newton"]
    bisection_iters, newton_iters = r["iteraciones_biseccion"], r["iteraciones_newton"]
    t_peak, peak_rate = r["t_pico_modelo"], r["ritmo_pico_modelo"]
    tol = TOLERANCIA
    output_dir = GRAFICOS
    t_dense = np.linspace(0, r["n"] - 1, 300)

    # Gráfico 1: ajuste de curva y hito de 100 M
    plt.figure(figsize=(10, 6), dpi=200)
    plt.scatter(t, S_accum, color='#e91e63', s=30, zorder=5, label='Datos reales acumulados (Spotify México)')
    plt.plot(t_dense, poly(t_dense), color='#2c3e50', linewidth=2.2, label=f'Ajuste cúbico ($R^2 = {r2:.4f}$)')
    traz_dense = [evaluar_trazadora(r["trazadora"], t, x) for x in t_dense]
    plt.plot(t_dense, traz_dense, color='#16a085', linewidth=1.6, linestyle='-.', label='Trazadora cúbica natural (pasa por los datos)')
    plt.axhline(TARGET, color='#d32f2f', linestyle='--', linewidth=1.3, label='100 millones de streams')
    plt.axvline(root_newton, color='#f39c12', linestyle=':', linewidth=2, label=f'Raíz regresión $t^* = {root_newton:.2f}$ semanas')
    if r["raiz_traz_newton"] is not None:
        plt.axvline(r["raiz_traz_newton"], color='#16a085', linestyle=':', linewidth=2,
                    label=f"Raíz trazadora $t^* = {r['raiz_traz_newton']:.2f}$ semanas")
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


def fila_comparativa(r):
    """Una misma fila para la tabla de consola y el archivo CSV."""
    hito = r["raiz_newton"]
    return {
        "Canción": r["nombre"], "Semanas": r["n"],
        "Total M": f"{r['total_millones']:.3f}", "R²": f"{r['r2']:.6f}",
        "Sy/x M": f"{r['syx']:.4f}",
        "Hito 100 M (semana Newton)": f"{hito:.6f}" if hito is not None else "sin resultado",
        "Iter. bisección": r["iteraciones_biseccion"], "Iter. Newton": r["iteraciones_newton"],
        "Hito trazadora (semana)": f"{r['raiz_traz_newton']:.6f}" if r["raiz_traz_newton"] is not None else "sin resultado",
        "Interpolación lineal (semana)": f"{r['t_lineal']:.4f}" if r["t_lineal"] is not None else "sin resultado",
        "Incertidumbre modelo (días)": f"{r['dt_semanas'] * 7:.2f}" if r["dt_semanas"] is not None else "sin resultado",
        "Modelo - trazadora (días)": f"{r['dif_modelo_trazadora'] * 7:.2f}" if r["dif_modelo_trazadora"] is not None else "sin resultado",
        "Pico modelo (semana)": f"{r['t_pico_modelo']:.2f}" if r["pico_valido"] else "no detecta",
        "Pico datos (semana)": r["semana_pico_datos"],
        "Pico datos (M/semana)": f"{r['valor_pico_datos']:.3f}",
        "Pico local (semana)": f"{r['pico_local']['t_pico']:.2f}" if r["pico_local"]["valido"] else "no detecta",
        "Ritmo pico local (M/semana)": f"{r['pico_local']['ritmo']:.2f}" if r["pico_local"]["valido"] else "no detecta",
        "Sensibilidad w=4/6/8": "/".join(f"{p['t_pico']:.2f}" if p["valido"] else "no detecta"
                                       for p in r["sensibilidad"].values()),
        "Diagnóstico": r["diagnostico"],
    }


def guardar_comparacion(resultados):
    filas = [fila_comparativa(r) for r in resultados]
    columnas = list(filas[0])
    anchos = [max(len(col), *(len(str(fila[col])) for fila in filas)) for col in columnas]
    print("\n5. COMPARACIÓN DE CANCIONES (t = 0 en la primera semana de cada CSV)")
    print("Diagnóstico: global y local / solo local / solo global / no aplica, según los máximos válidos de ambos ajustes.")
    print(" | ".join(col.ljust(ancho) for col, ancho in zip(columnas, anchos)))
    print("-+-".join("-" * ancho for ancho in anchos))
    for fila in filas:
        print(" | ".join(str(fila[col]).ljust(ancho) for col, ancho in zip(columnas, anchos)))
    with open(os.path.join(CARPETA, "comparacion_canciones.csv"), "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)


def graficar_comparacion(resultados):
    # Una fila por canción: al agregar una tupla también se amplía este gráfico.
    fig, ejes = plt.subplots(len(resultados), 1, figsize=(10, 4 * len(resultados)), dpi=200, squeeze=False)
    for eje, r in zip(ejes[:, 0], resultados):
        t_dense = np.linspace(0, r["n"] - 1, 300)
        eje.bar(r["t"], r["streams"], width=0.7, color='#9b59b6', alpha=0.45,
                label='Streams semanales medidos')
        eje.plot(t_dense, r["derivada"](t_dense), color='#8e44ad', linewidth=2.2,
                 label="Derivada del modelo $S'(t)$")
        if r["pico_valido"]:
            eje.axvline(r["t_pico_modelo"], color='#c0392b', linestyle='--', linewidth=1.8,
                        label=f"Pico del modelo: t = {r['t_pico_modelo']:.1f} sem")
        local = r["pico_local"]
        t_local = np.linspace(*local["ventana"], 150)
        derivada_local = np.poly1d(local["coeficientes"]).deriv()
        eje.plot(t_local, derivada_local(t_local), color='#168a70', linewidth=2.2,
                 label=f"Derivada local S'(t), w = {VENTANA_PICO}")
        if local["valido"]:
            eje.axvline(local["t_pico"], color='#168a70', linestyle=':', linewidth=1.8,
                        label=f"Pico local: t = {local['t_pico']:.2f} sem")
        eje.scatter(r["semana_pico_datos"], r["valor_pico_datos"], color='#e67e22', marker='D',
                    s=45, zorder=5, label=f"Pico de los datos: t = {r['semana_pico_datos']} sem")
        eje.set_title(r["nombre"], fontsize=13, fontweight='bold')
        eje.set_xlabel(f"Semanas desde {r['fechas'][0]} (t = 0)")
        eje.set_ylabel("Millones de streams por semana")
        eje.grid(True, linestyle='--', alpha=0.6)
        eje.legend(loc='upper right', fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(GRAFICOS, "grafico_4_comparacion_canciones.png"))
    plt.close(fig)


def megabits_por_reproduccion(kbps, duracion_s=DURACION_S):
    """Tamaño de una reproducción completa en megabits."""
    return kbps * duracion_s / 1000.0


def mbps(streams_millones_semana, kbps, duracion_s=DURACION_S):
    """Ancho de banda promedio de una semana (Mbps) para cierta cantidad de reproducciones."""
    return streams_millones_semana * 1e6 * megabits_por_reproduccion(kbps, duracion_s) / SEGUNDOS_SEMANA


def streams_para_mbps(capacidad_mbps, kbps, duracion_s=DURACION_S):
    """Reproducciones por semana (en millones) que ocupan exactamente esa capacidad."""
    return capacidad_mbps * SEGUNDOS_SEMANA / megabits_por_reproduccion(kbps, duracion_s) / 1e6


def dimensionamiento(r, capacidad_mbps=CAPACIDAD_MBPS, detalle=False):
    """Traduce los resultados a magnitudes de ingeniería.

    - La tasa S'(t) dimensiona la capacidad (ancho de banda).
    - El acumulado S(t) dimensiona el volumen total transferido.
    - La ventana en que la demanda supera la capacidad C son las raíces de
      g(t) = S'(t) - C, con g'(t) = S''(t) = 6at + 2b.
    """
    derivada, segunda = r["derivada"], r["derivada"].deriv()
    n, streams = r["n"], r["streams"]
    c_streams = streams_para_mbps(capacidad_mbps, BITRATE_REF_KBPS)
    g = lambda x: derivada(x) - c_streams
    dg = lambda x: segunda(x)

    # La parábola S'(t) tiene su máximo en t_pico: hay una raíz a cada lado si lo supera
    raices = []
    if r["pico_valido"] and derivada(r["t_pico_modelo"]) > c_streams:
        for a0, b0 in ((0.0, r["t_pico_modelo"]), (r["t_pico_modelo"], float(n - 1))):
            if g(a0) * g(b0) < 0:
                rb, ib, reg_b = biseccion(g, a0, b0)
                # Newton arranca en el extremo alejado del pico, donde S''(t) no se anula
                t0 = a0 if a0 == 0.0 else b0
                rn, inn, reg_n = newton_raphson(g, dg, t0, n - 1)
                raices.append({"intervalo": (a0, b0), "biseccion": rb, "it_biseccion": ib, "reg_biseccion": reg_b,
                               "newton": rn, "it_newton": inn, "reg_newton": reg_n, "t0": t0})
    semanas_sobre = [i for i in range(n) if streams[i] > c_streams]
    i_pico = r["semana_pico_datos"]
    resultado = {
        "capacidad_mbps": capacidad_mbps, "capacidad_streams": c_streams, "raices": raices,
        "semanas_sobre_capacidad": semanas_sobre,
        "mb_por_reproduccion": {k: megabits_por_reproduccion(k) / 8 for k in BITRATES_KBPS},
        "pico_datos_mbps": {k: mbps(streams[i_pico], k) for k in BITRATES_KBPS},
        "pico_modelo_mbps": {k: mbps(r["ritmo_pico_modelo"], k) for k in BITRATES_KBPS} if r["pico_valido"] else None,
        # Volumen: millones de reproducciones x megabits / 8 = MB; / 1e6 -> TB
        "volumen_hito_tb": {k: r["meta"] * 1e6 * megabits_por_reproduccion(k) / 8 / 1e6 for k in BITRATES_KBPS},
        "volumen_total_tb": {k: r["total_millones"] * 1e6 * megabits_por_reproduccion(k) / 8 / 1e6 for k in BITRATES_KBPS},
    }
    if detalle:
        imprimir_dimensionamiento(r, resultado)
    return resultado


def imprimir_dimensionamiento(r, d):
    print("\n" + "=" * 80)
    print("6. APLICACIÓN DE INGENIERÍA: DIMENSIONAMIENTO DE LA DEMANDA")
    print("=" * 80)
    print(f"Supuestos: duración {DURACION_S} s, bitrate {'/'.join(str(k) for k in BITRATES_KBPS)} kbps "
          f"(referencia {BITRATE_REF_KBPS}), hora pico = {FACTOR_HORA_PICO:g} x promedio semanal.")
    print("Cota superior: no descuenta las reproducciones guardadas en el dispositivo.")
    print(f"{'Bitrate':^10}|{'MB/reprod.':^12}|{'Pico datos (Mbps)':^19}|{'Pico modelo (Mbps)':^20}|"
          f"{'Hora pico datos':^17}|{'Vol. 100 M (TB)':^17}|{'Vol. total (TB)':^17}")
    print("-" * 118)
    for k in BITRATES_KBPS:
        modelo = d["pico_modelo_mbps"][k] if d["pico_modelo_mbps"] else float("nan")
        print(f"{k:^10d}|{d['mb_por_reproduccion'][k]:^12.2f}|{d['pico_datos_mbps'][k]:^19.1f}|{modelo:^20.1f}|"
              f"{d['pico_datos_mbps'][k] * FACTOR_HORA_PICO:^17.1f}|{d['volumen_hito_tb'][k]:^17.1f}|"
              f"{d['volumen_total_tb'][k]:^17.1f}")
    print(f"\nCapacidad de ejemplo C = {d['capacidad_mbps']:g} Mbps = {d['capacidad_streams']:.4f} M reproducciones/semana "
          f"a {BITRATE_REF_KBPS} kbps")
    for raiz in d["raices"]:
        print(f"  g(t) = S'(t) - C en [{raiz['intervalo'][0]:.2f}, {raiz['intervalo'][1]:.2f}]: "
              f"Bisección t = {raiz['biseccion']:.6f} ({raiz['it_biseccion']} it.), "
              f"Newton (t0 = {raiz['t0']:.2f}) t = {raiz['newton']:.6f} ({raiz['it_newton']} it.)")
    sobre = d["semanas_sobre_capacidad"]
    if sobre:
        print(f"  Datos: {len(sobre)} semanas superan C (de la {sobre[0]} a la {sobre[-1]}).")


def graficar_dimensionamiento(r, d):
    """Ancho de banda semanal medido, el del modelo y la capacidad de ejemplo."""
    t, n = r["t"], r["n"]
    t_dense = np.linspace(0, n - 1, 300)
    a_mbps = lambda s: mbps(s, BITRATE_REF_KBPS)
    plt.figure(figsize=(10, 6), dpi=200)
    plt.bar(t, a_mbps(r["streams"]), width=0.7, color='#9b59b6', alpha=0.45,
            label=f'Ancho de banda medido (promedio semanal, {BITRATE_REF_KBPS} kbps)')
    plt.plot(t_dense, a_mbps(r["derivada"](t_dense)), color='#8e44ad', linewidth=2.2, label="Modelo: S'(t) en Mbps")
    plt.axhline(d["capacidad_mbps"], color='#d32f2f', linestyle='--', linewidth=1.5,
                label=f"Capacidad de ejemplo C = {d['capacidad_mbps']:g} Mbps")
    if len(d["raices"]) == 2:
        t1, t2 = d["raices"][0]["newton"], d["raices"][1]["newton"]
        plt.axvspan(t1, t2, color='#d32f2f', alpha=0.07, label=f"Modelo sobre C: semanas {t1:.1f} a {t2:.1f}")
    i = r["semana_pico_datos"]
    plt.scatter([i], [a_mbps(r["streams"][i])], color='#e67e22', marker='D', s=45, zorder=5,
                label=f"Pico medido: {a_mbps(r['streams'][i]):.0f} Mbps (semana {i})")
    plt.title("'Rosa Pastel': demanda de ancho de banda en Spotify México", fontsize=13, fontweight='bold')
    plt.xlabel("Semanas desde el 26/01/2023")
    plt.ylabel("Mbps (promedio semanal)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper left', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAFICOS, "grafico_5_dimensionamiento.png"))
    plt.close()


def main():
    os.makedirs(GRAFICOS, exist_ok=True)
    resultados = []
    for i, (nombre, ruta) in enumerate(CANCIONES):
        resultado = analizar_cancion(nombre, os.path.join(CARPETA, ruta), detalle=(i == 0))
        resultados.append(resultado)
        if i == 0:
            graficar_rosa_pastel(resultado)
            # La duración del supuesto corresponde a esta canción
            graficar_dimensionamiento(resultado, dimensionamiento(resultado, detalle=True))
    guardar_comparacion(resultados)
    graficar_comparacion(resultados)
    print("\n[OK] Cinco gráficos guardados en GRAFICOS/ y comparacion_canciones.csv en CODIGO/.")


if __name__ == '__main__':
    main()
