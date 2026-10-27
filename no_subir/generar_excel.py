#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar el archivo Excel oficial del Proyecto Integrador:
Modelo_Numerico_Rosa_Pastel_Belanova.xlsx (UCC 2026-2).

Genera las hojas:
  1. Datos (fecha, t, streams semanales, acumulado con fórmula =C+D anterior)
  2. Regresion (coeficientes como valores, S modelo y residuo con fórmulas)
  3. Biseccion (iteraciones con fórmulas de Excel, al estilo de planilla de clase)
  4. Newton (iteraciones con fórmulas de Excel, al estilo de planilla de clase)
  5. Derivadas (adelante, atrás y centrada con fórmulas)

Los datos se importan directamente de analisis_resurgimiento_rosa_pastel.py.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import numpy as np

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analisis_resurgimiento_rosa_pastel import DATOS


def create_workbook():
    wb = openpyxl.Workbook()
    # Remover la hoja default
    wb.remove(wb.active)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # carpeta del proyecto
    xlsx_path = os.path.join(base_dir, "Modelo_Numerico_Rosa_Pastel_Belanova.xlsx")

    # Paleta de colores institucional UCC
    navy_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=13, bold=True, color="1F4E79")
    subtitle_font = Font(name="Calibri", size=10, italic=True, color="595959")
    bold_font = Font(name="Calibri", size=10, bold=True)
    regular_font = Font(name="Calibri", size=10)
    card_header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    card_header_font = Font(name="Calibri", size=10, bold=True, color="1F4E79")

    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9")
    )
    header_border = Border(
        left=Side(style="thin", color="1F4E79"),
        right=Side(style="thin", color="1F4E79"),
        top=Side(style="thin", color="1F4E79"),
        bottom=Side(style="medium", color="1F4E79")
    )

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    n = len(DATOS)
    weekly_streams_m = [v / 1e6 for _, v in DATOS]
    t_vals = np.arange(n, dtype=float)
    accum_vals = np.cumsum(weekly_streams_m)

    # Coeficientes exactos por polyfit
    coeffs = np.polyfit(t_vals, accum_vals, 3)
    a, b, c, d = coeffs

    # -------------------------------------------------------------
    # 1. HOJA: Datos
    # -------------------------------------------------------------
    ws_datos = wb.create_sheet(title="Datos")
    ws_datos.views.sheetView[0].showGridLines = True

    ws_datos["A1"] = "PROYECTO INTEGRADOR: MODELADO NUMÉRICO DE 'ROSA PASTEL' (SPOTIFY MÉXICO 2023)"
    ws_datos["A1"].font = title_font
    ws_datos["A2"] = "Fuente oficial: kworb.net (charts semanales oficiales del Top 200 de Spotify México)"
    ws_datos["A2"].font = subtitle_font

    headers_datos = ["Fecha de Cierre", "Semana (t)", "Streams Semanales (M)", "Streams Acumulados S(t) (M)"]
    for col_idx, h in enumerate(headers_datos, start=1):
        cell = ws_datos.cell(row=4, column=col_idx, value=h)
        cell.fill = navy_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = header_border

    # Fila 5: t = 0
    ws_datos.cell(row=5, column=1, value=DATOS[0][0]).alignment = align_center
    ws_datos.cell(row=5, column=2, value=0).alignment = align_center
    ws_datos.cell(row=5, column=3, value=weekly_streams_m[0]).alignment = align_right
    ws_datos.cell(row=5, column=4, value="=C5").alignment = align_right

    for r in range(5, 5 + n):
        idx = r - 5
        fecha, _ = DATOS[idx]
        w_val = weekly_streams_m[idx]

        c_fecha = ws_datos.cell(row=r, column=1, value=fecha)
        c_fecha.alignment = align_center
        c_fecha.font = regular_font
        c_fecha.border = thin_border

        c_t = ws_datos.cell(row=r, column=2, value=idx)
        c_t.alignment = align_center
        c_t.font = regular_font
        c_t.border = thin_border

        c_w = ws_datos.cell(row=r, column=3, value=round(w_val, 6))
        c_w.alignment = align_right
        c_w.font = regular_font
        c_w.number_format = "0.000"
        c_w.border = thin_border

        # Acumulado: =C5 para fila 5, =D(r-1)+Cr para r > 5
        if r == 5:
            c_acc = ws_datos.cell(row=r, column=4, value="=C5")
        else:
            c_acc = ws_datos.cell(row=r, column=4, value=f"=D{r-1}+C{r}")
        c_acc.alignment = align_right
        c_acc.font = bold_font if r == 5 + n - 1 else regular_font
        c_acc.number_format = "0.000"
        c_acc.border = thin_border

    # -------------------------------------------------------------
    # 2. HOJA: Regresion
    # -------------------------------------------------------------
    ws_reg = wb.create_sheet(title="Regresion")
    ws_reg.views.sheetView[0].showGridLines = True

    ws_reg["A1"] = "AJUSTE DE CURVAS: REGRESIÓN POLINÓMICA CÚBICA (MÍNIMOS CUADRADOS)"
    ws_reg["A1"].font = title_font
    ws_reg["A2"] = "Modelo continuo: S(t) = a*t^3 + b*t^2 + c*t + d"
    ws_reg["A2"].font = subtitle_font

    # Columnas principales
    headers_reg = [
        "t",
        "S(t) Real (M)",
        "S(t) Modelo (M)",
        "Residuo (S - S_mod)",
        "Residuo^2 [Sr_i]",
        "(S - Media)^2 [St_i]"
    ]
    for col_idx, h in enumerate(headers_reg, start=1):
        cell = ws_reg.cell(row=4, column=col_idx, value=h)
        cell.fill = navy_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = header_border

    for r in range(5, 5 + n):
        t_idx = r - 5
        # Col A: t
        cA = ws_reg.cell(row=r, column=1, value=f"=Datos!B{r}")
        cA.alignment = align_center
        cA.font = regular_font
        cA.border = thin_border

        # Col B: S Real
        cB = ws_reg.cell(row=r, column=2, value=f"=Datos!D{r}")
        cB.alignment = align_right
        cB.font = regular_font
        cB.number_format = "0.000"
        cB.border = thin_border

        # Col C: S Modelo: =$I$5*A{r}^3 + $I$6*A{r}^2 + $I$7*A{r} + $I$8
        cC = ws_reg.cell(row=r, column=3, value=f"=$I$5*A{r}^3 + $I$6*A{r}^2 + $I$7*A{r} + $I$8")
        cC.alignment = align_right
        cC.font = regular_font
        cC.number_format = "0.000"
        cC.border = thin_border

        # Col D: Residuo: =B{r}-C{r}
        cD = ws_reg.cell(row=r, column=4, value=f"=B{r}-C{r}")
        cD.alignment = align_right
        cD.font = regular_font
        cD.number_format = "0.0000"
        cD.border = thin_border

        # Col E: Residuo^2: =D{r}^2
        cE = ws_reg.cell(row=r, column=5, value=f"=D{r}^2")
        cE.alignment = align_right
        cE.font = regular_font
        cE.number_format = "0.0000"
        cE.border = thin_border

        # Col F: (S - Media)^2: =(B{r}-AVERAGE($B$5:$B${4+n}))^2
        cF = ws_reg.cell(row=r, column=6, value=f"=(B{r}-AVERAGE($B$5:$B${4+n}))^2")
        cF.alignment = align_right
        cF.font = regular_font
        cF.number_format = "0.00"
        cF.border = thin_border

    # Tabla lateral: Parámetros del modelo (Columnas H e I)
    ws_reg.cell(row=4, column=8, value="Parámetro").fill = card_header_fill
    ws_reg.cell(row=4, column=8).font = card_header_font
    ws_reg.cell(row=4, column=8).alignment = align_center
    ws_reg.cell(row=4, column=8).border = thin_border

    ws_reg.cell(row=4, column=9, value="Valor").fill = card_header_fill
    ws_reg.cell(row=4, column=9).font = card_header_font
    ws_reg.cell(row=4, column=9).alignment = align_center
    ws_reg.cell(row=4, column=9).border = thin_border

    params_data = [
        ("a (t^3)", a, "0.00000000"),
        ("b (t^2)", b, "0.00000000"),
        ("c (t)", c, "0.00000000"),
        ("d (ind)", d, "0.00000000"),
        ("n (observaciones)", n, "0")
    ]
    for idx, (lbl, val, fmt) in enumerate(params_data, start=5):
        c_lbl = ws_reg.cell(row=idx, column=8, value=lbl)
        c_lbl.font = bold_font
        c_lbl.border = thin_border
        c_val = ws_reg.cell(row=idx, column=9, value=val)
        c_val.font = regular_font
        c_val.alignment = align_right
        c_val.number_format = fmt
        c_val.border = thin_border

    # Tabla lateral: Métricas de bondad de ajuste
    ws_reg.cell(row=11, column=8, value="Estadístico").fill = card_header_fill
    ws_reg.cell(row=11, column=8).font = card_header_font
    ws_reg.cell(row=11, column=8).alignment = align_center
    ws_reg.cell(row=11, column=8).border = thin_border

    ws_reg.cell(row=11, column=9, value="Fórmula / Valor").fill = card_header_fill
    ws_reg.cell(row=11, column=9).font = card_header_font
    ws_reg.cell(row=11, column=9).alignment = align_center
    ws_reg.cell(row=11, column=9).border = thin_border

    stats_data = [
        ("Sr (Suma Cuadrados Residuos)", f"=SUM(E5:E{4+n})", "0.0000"),
        ("St (Suma Total de Cuadrados)", f"=SUM(F5:F{4+n})", "0.00"),
        ("R^2 (Coef. de Determinación)", "=1-(I12/I13)", "0.000000"),
        ("R^2 Porcentual", "=I14*100", "0.00%"),
        ("Sy/x (Error Estándar M)", f"=SQRT(I12/(I9-4))", "0.0000")
    ]
    for idx, (lbl, form, fmt) in enumerate(stats_data, start=12):
        c_lbl = ws_reg.cell(row=idx, column=8, value=lbl)
        c_lbl.font = bold_font
        c_lbl.border = thin_border
        c_val = ws_reg.cell(row=idx, column=9, value=form)
        c_val.font = bold_font if "R^2" in lbl else regular_font
        c_val.alignment = align_right
        c_val.number_format = fmt
        c_val.border = thin_border

    # -------------------------------------------------------------
    # 3. HOJA: Biseccion
    # -------------------------------------------------------------
    ws_bis = wb.create_sheet(title="Biseccion")
    ws_bis.views.sheetView[0].showGridLines = True

    ws_bis["A1"] = "BÚSQUEDA DE RAÍCES: MÉTODO DE BISECCIÓN (HITO DE 100 MILLONES)"
    ws_bis["A1"].font = title_font
    ws_bis["A2"] = "Ecuación: f(t) = S(t) - 100 = 0 | Intervalo inicial: [35, 36] | Criterio de parada: |Ea%| < 1e-4 %"
    ws_bis["A2"].font = subtitle_font

    headers_bis = ["Iter (i)", "a", "b", "xr", "f(a)", "f(xr)", "f(a)*f(xr)", "|Ea%|"]
    for col_idx, h in enumerate(headers_bis, start=1):
        cell = ws_bis.cell(row=4, column=col_idx, value=h)
        cell.fill = navy_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = header_border

    # Fila 5 (Iter 1)
    ws_bis.cell(row=5, column=1, value=1).alignment = align_center
    ws_bis.cell(row=5, column=2, value=35.0).alignment = align_right
    ws_bis.cell(row=5, column=3, value=36.0).alignment = align_right
    ws_bis.cell(row=5, column=4, value="=(B5+C5)/2").alignment = align_right
    ws_bis.cell(row=5, column=5, value="=Regresion!$I$5*B5^3 + Regresion!$I$6*B5^2 + Regresion!$I$7*B5 + Regresion!$I$8 - 100").alignment = align_right
    ws_bis.cell(row=5, column=6, value="=Regresion!$I$5*D5^3 + Regresion!$I$6*D5^2 + Regresion!$I$7*D5 + Regresion!$I$8 - 100").alignment = align_right
    ws_bis.cell(row=5, column=7, value="=E5*F5").alignment = align_right
    ws_bis.cell(row=5, column=8, value=100.0).alignment = align_right

    for c in range(1, 9):
        cell = ws_bis.cell(row=5, column=c)
        cell.font = regular_font
        cell.border = thin_border
        if c in [2, 3]:
            cell.number_format = "0.00000"
        elif c == 4:
            cell.number_format = "0.000000"
        elif c in [5, 6]:
            cell.number_format = "0.0000"
        elif c == 7:
            cell.number_format = "0.000000"
        elif c == 8:
            cell.number_format = "0.000000"

    # Filas 6 a 19 (Iteraciones 2 a 15)
    for it in range(2, 16):
        r = 4 + it
        p = r - 1

        c1 = ws_bis.cell(row=r, column=1, value=it)
        c1.alignment = align_center

        # a = IF(G_prev < 0, a_prev, xr_prev)
        c2 = ws_bis.cell(row=r, column=2, value=f"=IF(G{p}<0, B{p}, D{p})")
        c2.alignment = align_right
        c2.number_format = "0.00000"

        # b = IF(G_prev < 0, xr_prev, b_prev)
        c3 = ws_bis.cell(row=r, column=3, value=f"=IF(G{p}<0, D{p}, C{p})")
        c3.alignment = align_right
        c3.number_format = "0.00000"

        # xr = (a + b)/2
        c4 = ws_bis.cell(row=r, column=4, value=f"=(B{r}+C{r})/2")
        c4.alignment = align_right
        c4.number_format = "0.000000"

        # f(a)
        c5 = ws_bis.cell(row=r, column=5, value=f"=Regresion!$I$5*B{r}^3 + Regresion!$I$6*B{r}^2 + Regresion!$I$7*B{r} + Regresion!$I$8 - 100")
        c5.alignment = align_right
        c5.number_format = "0.0000"

        # f(xr)
        c6 = ws_bis.cell(row=r, column=6, value=f"=Regresion!$I$5*D{r}^3 + Regresion!$I$6*D{r}^2 + Regresion!$I$7*D{r} + Regresion!$I$8 - 100")
        c6.alignment = align_right
        c6.number_format = "0.0000"

        # f(a)*f(xr)
        c7 = ws_bis.cell(row=r, column=7, value=f"=E{r}*F{r}")
        c7.alignment = align_right
        c7.number_format = "0.000000"

        # |Ea%| = ABS((xr - xr_prev)/xr)*100
        c8 = ws_bis.cell(row=r, column=8, value=f"=ABS((D{r}-D{p})/D{r})*100")
        c8.alignment = align_right
        c8.number_format = "0.000000"

        for cell in [c1, c2, c3, c4, c5, c6, c7, c8]:
            cell.font = regular_font
            cell.border = thin_border

    # Cuadro resumen
    ws_bis.cell(row=21, column=1, value="Resultado Bisección:").font = bold_font
    ws_bis.cell(row=21, column=2, value="Raíz t* =").font = bold_font
    c_res_bis = ws_bis.cell(row=21, column=3, value="=D19")
    c_res_bis.font = bold_font
    c_res_bis.number_format = "0.000000"

    ws_bis.cell(row=22, column=2, value="Iteraciones =").font = bold_font
    ws_bis.cell(row=22, column=3, value=15).font = bold_font

    ws_bis.cell(row=23, column=2, value="|Ea%| final =").font = bold_font
    c_ea_bis = ws_bis.cell(row=23, column=3, value="=H19")
    c_ea_bis.font = bold_font
    c_ea_bis.number_format = "0.000000"

    # -------------------------------------------------------------
    # 4. HOJA: Newton
    # -------------------------------------------------------------
    ws_new = wb.create_sheet(title="Newton")
    ws_new.views.sheetView[0].showGridLines = True

    ws_new["A1"] = "BÚSQUEDA DE RAÍCES: MÉTODO DE NEWTON-RAPHSON (HITO DE 100 MILLONES)"
    ws_new["A1"].font = title_font
    ws_new["A2"] = "Fórmula: x_{i+1} = x_i - f(x_i)/f'(x_i) | Valor inicial: t0 = 35.00 | Tol: |Ea%| < 1e-4 %"
    ws_new["A2"].font = subtitle_font

    headers_new = ["Iter (i)", "x_i", "f(x_i)", "f'(x_i)", "x_{i+1}", "|Ea%|"]
    for col_idx, h in enumerate(headers_new, start=1):
        cell = ws_new.cell(row=4, column=col_idx, value=h)
        cell.fill = navy_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = header_border

    # Fila 5 (Iter 1)
    ws_new.cell(row=5, column=1, value=1).alignment = align_center
    ws_new.cell(row=5, column=2, value=35.0).alignment = align_right
    ws_new.cell(row=5, column=3, value="=Regresion!$I$5*B5^3 + Regresion!$I$6*B5^2 + Regresion!$I$7*B5 + Regresion!$I$8 - 100").alignment = align_right
    ws_new.cell(row=5, column=4, value="=3*Regresion!$I$5*B5^2 + 2*Regresion!$I$6*B5 + Regresion!$I$7").alignment = align_right
    ws_new.cell(row=5, column=5, value="=B5-(C5/D5)").alignment = align_right
    ws_new.cell(row=5, column=6, value="=ABS((E5-B5)/E5)*100").alignment = align_right

    for c in range(1, 7):
        cell = ws_new.cell(row=5, column=c)
        cell.font = regular_font
        cell.border = thin_border
        if c in [2, 5]:
            cell.number_format = "0.000000"
        elif c == 3:
            cell.number_format = "0.000000"
        elif c == 4:
            cell.number_format = "0.000000"
        elif c == 6:
            cell.number_format = "0.000000"

    # Filas 6 y 7 (Iter 2 y 3)
    for it in range(2, 4):
        r = 4 + it
        p = r - 1

        c1 = ws_new.cell(row=r, column=1, value=it)
        c1.alignment = align_center

        # x_i = x_{i+1}_prev
        c2 = ws_new.cell(row=r, column=2, value=f"=E{p}")
        c2.alignment = align_right
        c2.number_format = "0.000000"

        # f(x_i)
        c3 = ws_new.cell(row=r, column=3, value=f"=Regresion!$I$5*B{r}^3 + Regresion!$I$6*B{r}^2 + Regresion!$I$7*B{r} + Regresion!$I$8 - 100")
        c3.alignment = align_right
        c3.number_format = "0.000000"

        # f'(x_i)
        c4 = ws_new.cell(row=r, column=4, value=f"=3*Regresion!$I$5*B{r}^2 + 2*Regresion!$I$6*B{r} + Regresion!$I$7")
        c4.alignment = align_right
        c4.number_format = "0.000000"

        # x_{i+1} = x_i - f/f'
        c5 = ws_new.cell(row=r, column=5, value=f"=B{r}-(C{r}/D{r})")
        c5.alignment = align_right
        c5.number_format = "0.000000"

        # |Ea%|
        c6 = ws_new.cell(row=r, column=6, value=f"=ABS((E{r}-B{r})/E{r})*100")
        c6.alignment = align_right
        c6.number_format = "0.000000"

        for cell in [c1, c2, c3, c4, c5, c6]:
            cell.font = regular_font
            cell.border = thin_border

    # Cuadro comparativo con interpolación lineal directa
    ws_new.cell(row=9, column=1, value="Control con Interpolación Lineal sobre los datos:").font = bold_font
    ws_new.cell(row=10, column=1, value="Raíz modelo Newton t* =").font = bold_font
    c_rn = ws_new.cell(row=10, column=3, value="=E7")
    c_rn.font = bold_font
    c_rn.number_format = "0.000000"

    # En hoja Datos, semana 35 está en fila 40 (t=35), semana 36 en fila 41 (t=36)
    ws_new.cell(row=11, column=1, value="Interpolación lineal t (sem 35 y 36) =").font = bold_font
    c_il = ws_new.cell(row=11, column=3, value="=Datos!B40 + (100 - Datos!D40)/(Datos!D41 - Datos!D40)")
    c_il.font = bold_font
    c_il.number_format = "0.0000"

    ws_new.cell(row=12, column=1, value="Diferencia en días = (t_modelo - t_lineal) * 7 =").font = bold_font
    c_dif = ws_new.cell(row=12, column=3, value="=(C10-C11)*7")
    c_dif.font = bold_font
    c_dif.number_format = "0.00"

    ws_new.cell(row=13, column=1, value="Explicación:").font = bold_font
    ws_new.cell(row=13, column=2, value="La discrepancia de 2.75 días se debe al error propio de ajuste (Sy/x = ±0.93 M).").font = subtitle_font

    # -------------------------------------------------------------
    # 5. HOJA: Derivadas
    # -------------------------------------------------------------
    ws_der = wb.create_sheet(title="Derivadas")
    ws_der.views.sheetView[0].showGridLines = True

    ws_der["A1"] = "DIFERENCIACIÓN NUMÉRICA: RITMO SEMANAL DE STREAMS (dS/dt)"
    ws_der["A1"].font = title_font
    ws_der["A2"] = "Fórmulas de diferencias finitas con paso h = 1 semana vs. Derivada del modelo S'(t) (en M streams/sem)"
    ws_der["A2"].font = subtitle_font

    headers_der = [
        "Semana (t)",
        "Fecha de Cierre",
        "S(t) Acumulado (M)",
        "Dif. Adelante O(h)",
        "Dif. Atrás O(h)",
        "Dif. Centrada O(h^2)",
        "Derivada del modelo S'(t)"
    ]
    for col_idx, h in enumerate(headers_der, start=1):
        cell = ws_der.cell(row=4, column=col_idx, value=h)
        cell.fill = navy_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = header_border

    for r in range(5, 5 + n):
        t_idx = r - 5

        # Col A: t
        cA = ws_der.cell(row=r, column=1, value=f"=Datos!B{r}")
        cA.alignment = align_center
        cA.font = regular_font
        cA.border = thin_border

        # Col B: Fecha
        cB = ws_der.cell(row=r, column=2, value=f"=Datos!A{r}")
        cB.alignment = align_center
        cB.font = regular_font
        cB.border = thin_border

        # Col C: Acumulado
        cC = ws_der.cell(row=r, column=3, value=f"=Datos!D{r}")
        cC.alignment = align_right
        cC.font = regular_font
        cC.number_format = "0.000"
        cC.border = thin_border

        # Col D: Adelante = (S[i+1] - S[i])/1 para i < n-1, sino "---"
        if t_idx < n - 1:
            cD = ws_der.cell(row=r, column=4, value=f"=(C{r+1}-C{r})/1")
            cD.number_format = "0.000"
        else:
            cD = ws_der.cell(row=r, column=4, value="---")
        cD.alignment = align_right if t_idx < n - 1 else align_center
        cD.font = regular_font
        cD.border = thin_border

        # Col E: Atrás = (S[i] - S[i-1])/1 para i > 0, sino "---"
        if t_idx > 0:
            cE = ws_der.cell(row=r, column=5, value=f"=(C{r}-C{r-1})/1")
            cE.number_format = "0.000"
        else:
            cE = ws_der.cell(row=r, column=5, value="---")
        cE.alignment = align_right if t_idx > 0 else align_center
        cE.font = regular_font
        cE.border = thin_border

        # Col F: Centrada = (S[i+1] - S[i-1])/2 para 0 < i < n-1, sino "---"
        if 0 < t_idx < n - 1:
            cF = ws_der.cell(row=r, column=6, value=f"=(C{r+1}-C{r-1})/2")
            cF.number_format = "0.000"
        else:
            cF = ws_der.cell(row=r, column=6, value="---")
        cF.alignment = align_right if 0 < t_idx < n - 1 else align_center
        cF.font = regular_font
        cF.border = thin_border

        # Col G: Derivada del modelo S'(t) = 3*a*t^2 + 2*b*t + c
        cG = ws_der.cell(row=r, column=7, value=f"=3*Regresion!$I$5*A{r}^2 + 2*Regresion!$I$6*A{r} + Regresion!$I$7")
        cG.alignment = align_right
        cG.font = regular_font
        cG.number_format = "0.000"
        cG.border = thin_border

    # Cuadro lateral: Análisis del Pico
    ws_der.cell(row=4, column=9, value="Análisis del Pico de Demanda").fill = card_header_fill
    ws_der.cell(row=4, column=9).font = card_header_font
    ws_der.cell(row=4, column=9).alignment = align_center
    ws_der.cell(row=4, column=9).border = thin_border

    ws_der.cell(row=4, column=10, value="Valor").fill = card_header_fill
    ws_der.cell(row=4, column=10).font = card_header_font
    ws_der.cell(row=4, column=10).alignment = align_center
    ws_der.cell(row=4, column=10).border = thin_border

    peak_items = [
        ("Pico del Modelo: t_pico (S''=0)", "=-Regresion!$I$6/(3*Regresion!$I$5)", "0.00 sem"),
        ("Ritmo pico del modelo S'(t_pico)", "=3*Regresion!$I$5*J5^2 + 2*Regresion!$I$6*J5 + Regresion!$I$7", "0.000 M/sem"),
        ("Pico en los Datos Reales: Semana t", 26, "0"),
        ("Fecha del pico real", "2023-07-27", "@"),
        ("Streams semanales en el pico real", 4.171, "0.000 M"),
        ("Efecto de suavizado del modelo", "Desplaza el pico ~4 sem y lo achata", "@")
    ]
    for idx, (lbl, val, fmt) in enumerate(peak_items, start=5):
        c_lbl = ws_der.cell(row=idx, column=9, value=lbl)
        c_lbl.font = bold_font
        c_lbl.border = thin_border
        c_val = ws_der.cell(row=idx, column=10, value=val)
        c_val.font = regular_font
        c_val.alignment = align_right if fmt != "@" else align_left
        if fmt != "@":
            c_val.number_format = fmt
        c_val.border = thin_border

    # Autoajuste de anchos de columna en todas las hojas
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                # Ignorar títulos largos en filas 1 y 2 para el ancho de la columna A
                if cell.row in [1, 2] and cell.column == 1:
                    continue
                if len(val_str) > max_len:
                    max_len = len(val_str)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

    wb.save(xlsx_path)
    print(f"[OK] Archivo Excel guardado exitosamente en: {xlsx_path}")


if __name__ == "__main__":
    create_workbook()
