#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar el Informe Académico Oficial en formato Word (.docx)
para el Proyecto Integrador de Métodos Numéricos (UCC 2026-2).

Modelado Numérico del Resurgimiento de 'Rosa Pastel' (Belanova) en Spotify México (2023).
Datos reales de kworb.net / Spotify Charts México.
"""

import os
import sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # carpeta del proyecto
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import numpy as np

from analisis_resurgimiento_rosa_pastel import DATOS


def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)


def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_custom_heading(doc, text, level, color='1F4E79'):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(15 if level == 1 else (12.5 if level == 2 else 11))
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string(color)
    return p


def format_table_header(table_or_row, headers, col_widths=None):
    row = table_or_row.rows[0] if hasattr(table_or_row, 'rows') else table_or_row
    for idx, text in enumerate(headers):
        cell = row.cells[idx]
        cell.text = text
        set_cell_background(cell, '1F4E79')
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Calibri'
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
        if col_widths and idx < len(col_widths):
            cell.width = col_widths[idx]


def main():
    doc = docx.Document()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # carpeta del proyecto

    # Configuración de márgenes estándar de 1 pulgada
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    # -------------------------------------------------------------
    # CARÁTULA
    # -------------------------------------------------------------
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run('UNIVERSIDAD CATÓLICA DE CÓRDOBA\nFACULTAD DE INGENIERÍA\nINGENIERÍA INFORMÁTICA')
    r_inst.font.name = 'Calibri'
    r_inst.font.size = Pt(14)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor.from_string('1F4E79')
    p_inst.paragraph_format.space_after = Pt(36)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run(
        'PROYECTO INTEGRADOR:\n'
        'MODELADO NUMÉRICO DEL RESURGIMIENTO DE "ROSA PASTEL" (BELANOVA) EN SPOTIFY MÉXICO (2023)'
    )
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(17)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor.from_string('002060')
    p_title.paragraph_format.space_after = Pt(18)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run(
        'Aplicación de Ajuste de Curvas por Mínimos Cuadrados, Búsqueda de Raíces '
        '(Bisección vs. Newton-Raphson) y Diferenciación Numérica'
    )
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor.from_string('595959')
    p_sub.paragraph_format.space_after = Pt(50)

    p_data = doc.add_paragraph()
    p_data.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_data.paragraph_format.space_after = Pt(30)
    r_data = p_data.add_run(
        'Asignatura: Taller de Métodos Numéricos\n'
        'Profesor Titular: Ing. Carlos Arnaudo\n'
        'Comisión: 46324\n\n'
        'Integrantes:\n'
        'Pedro Gatti (Legajo: 2519717)\n'
        'Facundo Grillo (Legajo: 2523057)\n'
        'Gonzalo Marin (Legajo: 2523776)\n\n'
        'Fecha de Entrega: Octubre de 2026\n'
        'Córdoba, República Argentina'
    )
    r_data.font.name = 'Calibri'
    r_data.font.size = Pt(11)

    doc.add_page_break()

    # -------------------------------------------------------------
    # ÍNDICE GENERAL
    # -------------------------------------------------------------
    add_custom_heading(doc, 'ÍNDICE GENERAL', level=1)
    toc_items = [
        ('1. INTRODUCCIÓN', '3'),
        ('   1.1 Objetivo del Trabajo', '3'),
        ('   1.2 Problema y Contexto de Ingeniería', '3'),
        ('   1.3 Introducción a los Métodos Numéricos Involucrados', '3'),
        ('   1.4 Justificación del Enfoque Numérico', '4'),
        ('2. PLANTEO DEL PROBLEMA Y DATOS EXPERIMENTALES', '4'),
        ('   2.1 Origen de los Datos y Contexto del Fenómeno', '4'),
        ('   2.2 Registro Semanal de Streams (Spotify México 2023)', '5'),
        ('3. RESOLUCIÓN METODOLÓGICA Y RESULTADOS', '6'),
        ('   3.1 Ajuste de Curvas: Regresión Polinómica Cúbica (Mínimos Cuadrados)', '6'),
        ('   3.2 Búsqueda de Raíces: Predicción del Hito de 100 Millones de Streams', '8'),
        ('   3.3 Comparación entre el Método de Bisección y Newton-Raphson', '10'),
        ('   3.4 Diferenciación Numérica: Ritmo Semanal de Streams', '11'),
        ('   3.5 Localización del Pico de Demanda y Análisis de Viralidad', '12'),
        ('   3.6 Generalización a otras canciones', '13'),
        ('   3.7 Limitaciones del Modelo Numérico', '15'),
        ('4. CONCLUSIONES Y DISCUSIÓN ACADÉMICA', '16'),
        ('5. BIBLIOGRAFÍA Y DECLARACIÓN DE USO DE IA', '17')
    ]

    for item, page in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r_item = p.add_run(item)
        r_item.font.name = 'Calibri'
        r_item.font.size = Pt(10.5)
        r_dots = p.add_run(' ' + '.' * (68 - len(item)) + ' ')
        r_dots.font.name = 'Calibri'
        r_dots.font.size = Pt(10)
        r_dots.font.color.rgb = RGBColor.from_string('8A8A8A')
        r_page = p.add_run(page)
        r_page.font.name = 'Calibri'
        r_page.font.size = Pt(10.5)
        r_page.font.bold = True

    doc.add_page_break()

    # -------------------------------------------------------------
    # 1. INTRODUCCIÓN
    # -------------------------------------------------------------
    add_custom_heading(doc, '1. INTRODUCCIÓN', level=1)

    add_custom_heading(doc, '1.1 Objetivo del Trabajo', level=2)
    p = doc.add_paragraph(
        'El presente proyecto integrador tiene como objetivo modelar matemáticamente, a través de métodos numéricos, '
        'el resurgimiento de la canción "Rosa Pastel" de la banda mexicana Belanova durante el año 2023 en Spotify México. '
        'La canción, lanzada como sencillo en 2006 (álbum Dulce Beat), volvió a entrar en los rankings (puesto 22 del chart semanal de Spotify México) '
        'tras popularizarse en la red social TikTok a mediados de 2023. '
        'A partir de los registros semanales de streaming recopilados durante ese año, se busca ajustar un modelo continuo, '
        'estimar en qué momento se alcanzaron los 100 millones de reproducciones acumuladas y analizar el ritmo semanal de consumo. '
        'Asimismo, el método se implementó como una herramienta general y se probó con 3 canciones con diversas dinámicas '
        'de consumo para verificar su aplicabilidad, robustez algorítmica y límites de validez en un contexto de ingeniería.'
    )
    p.paragraph_format.space_after = Pt(8)

    add_custom_heading(doc, '1.2 Problema y Contexto de Ingeniería', level=2)
    p = doc.add_paragraph(
        'En las plataformas de distribución de contenido digital, modelar cuantitativamente la evolución temporal de la demanda '
        'permite anticipar picos de consumo para dimensionar adecuadamente la infraestructura de streaming, previendo la capacidad '
        'de los servidores y de las redes de entrega de contenidos (CDN).'
    )
    p.paragraph_format.space_after = Pt(8)

    add_custom_heading(doc, '1.3 Introducción a los Métodos Numéricos Involucrados', level=2)
    p = doc.add_paragraph(
        'Para dar respuesta a los objetivos planteados, se emplean tres métodos numéricos vistos en la cátedra:\n'
        '1. Regresión Polinómica por Mínimos Cuadrados: Se construye una función continua diferenciable S(t) '
        'que aproxima la curva de streams acumulados a partir de los datos discretos semanales.\n'
        '2. Métodos de Búsqueda de Raíces (Bisección y Newton-Raphson): Se aplican para resolver la ecuación f(t) = S(t) - 100 = 0 '
        'y estimar la semana en que se superó el umbral de 100 millones de reproducciones acumuladas.\n'
        '3. Diferenciación Numérica: Mediante fórmulas de diferencias finitas hacia adelante, hacia atrás y centradas, '
        'se estima la tasa instantánea de crecimiento semanal v(t) = dS/dt y se compara con la derivada del modelo para identificar el pico del fenómeno.'
    )
    p.paragraph_format.space_after = Pt(8)

    add_custom_heading(doc, '1.4 Justificación del Enfoque Numérico', level=2)
    p = doc.add_paragraph(
        'Las mediciones de plataformas digitales se obtienen en intervalos discretos (semanas) y presentan variaciones naturales. '
        'No se dispone de antemano de una fórmula analítica cerrada que describa la evolución de las reproducciones. '
        'Los métodos numéricos brindan las herramientas necesarias para deducir un modelo analítico aproximado, '
        'calcular raíces no lineales con la tolerancia requerida y estimar derivadas sobre datos muestreados.'
    )
    p.paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------
    # 2. PLANTEO DEL PROBLEMA Y DATOS EXPERIMENTALES
    # -------------------------------------------------------------
    add_custom_heading(doc, '2. PLANTEO DEL PROBLEMA Y DATOS EXPERIMENTALES', level=1)

    add_custom_heading(doc, '2.1 Origen de los Datos y Contexto del Fenómeno', level=2)
    p = doc.add_paragraph(
        'Los datos experimentales corresponden a las cifras oficiales del chart semanal del Top 200 de Spotify México para el año 2023, '
        'recopiladas a través del portal estadístico kworb.net (página del track 6Z0ybnsUBhbZ9ZjPW64eoF, correspondiente a "Rosa Pastel" de Belanova). '
        'Es fundamental precisar que estos datos reflejan exclusivamente las reproducciones semanales generadas en Spotify México dentro del Top 200, '
        'por lo que no incluyen reproducciones en otros países, ni en otras plataformas de streaming (como YouTube Music o Apple Music), '
        'ni escuchas que no hayan alcanzado el umbral del chart semanal.\n\n'
        'La serie temporal abarca 47 semanas consecutivas de 2023, donde t = 0 corresponde al cierre de la semana del 26 de enero de 2023 '
        'y t = 46 corresponde al cierre de la semana del 14 de diciembre de 2023. '
        'Durante este período, la canción acumuló un total de 132,9 millones de reproducciones en el mercado mexicano. '
        'El auge del tema cobró especial notoriedad en julio de 2023 (semanas 24 a 27), cuando se viralizó masivamente en TikTok '
        'como banda sonora de videos donde usuarios compartían historias de metas académicas y laborales no cumplidas (Chilango, 2023).'
    )
    p.paragraph_format.space_after = Pt(8)

    add_custom_heading(doc, '2.2 Registro Semanal de Streams (Spotify México 2023)', level=2)
    p = doc.add_paragraph(
        'La siguiente tabla reúne las 47 observaciones semanales relevadas, indicando el índice temporal t, '
        'la fecha de cierre del conteo semanal de Spotify, los streams registrados en la semana y el valor acumulado S(t) en millones de reproducciones:'
    )
    p.paragraph_format.space_after = Pt(6)

    # Tabla compacta de 47 filas
    table_data = doc.add_table(rows=1, cols=4)
    table_data.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(table_data.rows[0], ['Semana (t)', 'Fecha de Cierre', 'Streams Semanales (M)', 'Acumulado S(t) (M)'])

    weekly_arr = np.array([v for _, v in DATOS], dtype=float) / 1e6
    accum_arr = np.cumsum(weekly_arr)

    for i in range(len(DATOS)):
        fecha, _ = DATOS[i]
        row_cells = table_data.add_row().cells
        row_cells[0].text = str(i)
        row_cells[1].text = fecha
        row_cells[2].text = f'{weekly_arr[i]:.3f}'
        row_cells[3].text = f'{accum_arr[i]:.3f}'

        for c_idx, cell in enumerate(row_cells):
            set_cell_margins(cell, top=30, bottom=30, left=60, right=60)
            p_c = cell.paragraphs[0]
            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p_c.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(8.5)

    doc.add_page_break()

    # -------------------------------------------------------------
    # 3. RESOLUCIÓN METODOLÓGICA Y RESULTADOS
    # -------------------------------------------------------------
    add_custom_heading(doc, '3. RESOLUCIÓN METODOLÓGICA Y RESULTADOS', level=1)

    add_custom_heading(doc, '3.1 Ajuste de Curvas: Regresión Polinómica Cúbica (Mínimos Cuadrados)', level=2)
    p = doc.add_paragraph(
        'Para representar analíticamente la acumulación temporal de streams se empleó una regresión polinómica cúbica (grado 3) '
        'por el método de mínimos cuadrados. Este orden permite capturar la forma sigmoidea que presentan los consumos acumulados: '
        'una etapa inicial de crecimiento acelerado (concavidad hacia arriba) seguida de una inflexión hacia una etapa de crecimiento '
        'más estable o meseta (concavidad hacia abajo).\n\n'
        'La ecuación general del modelo adoptado es:\n'
        'S(t) = a·t³ + b·t² + c·t + d\n\n'
        'A partir de las 47 observaciones discretas, se resolvieron las ecuaciones normales de Gauss obteniéndose los siguientes coeficientes:\n'
        '• a = -0.000839\n'
        '• b =  0.076977\n'
        '• c =  1.081162\n'
        '• d =  2.072898\n\n'
        'De este modo, la función continua que modela los streams acumulados en millones es:\n'
        'S(t) = -0.000839·t³ + 0.076977·t² + 1.081162·t + 2.072898\n\n'
        'Evaluación estadística de la bondad de ajuste:\n'
        '• Suma de cuadrados de los residuos (Sr): 36.9406\n'
        '• Suma total de cuadrados respecto a la media (St): 79,137.5830\n'
        '• Coeficiente de determinación (R²): 0.999533 (99.95% de la varianza explicada por el modelo)\n'
        '• Error estándar de la estimación (Sy/x): 0.9269 millones de streams\n\n'
        'El valor de R² cercano a 1 y un error estándar menor a un millón de reproducciones confirman que la cúbica ofrece '
        'una muy buena aproximación global de la tendencia acumulada.'
    )
    p.paragraph_format.space_after = Pt(10)

    img1_path = os.path.join(base_dir, 'grafico_1_ajuste_curva_streams.png')
    if os.path.exists(img1_path):
        doc.add_picture(img1_path, width=Inches(6.0))
        p_caption = doc.add_paragraph(
            'Figura 1: Curva de ajuste polinómico cúbico S(t) sobre los datos acumulados de Spotify México (2023) '
            'e identificación del cruce de los 100 millones de streams.'
        )
        p_caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_caption.runs[0].font.italic = True
        p_caption.runs[0].font.size = Pt(9.5)
        p_caption.runs[0].font.color.rgb = RGBColor.from_string('595959')

    doc.add_page_break()

    # 3.2 Búsqueda de Raíces
    add_custom_heading(doc, '3.2 Búsqueda de Raíces: Predicción del Hito de 100 Millones de Streams', level=2)
    p = doc.add_paragraph(
        'Para estimar en qué momento del año la canción superó los 100 millones de reproducciones acumuladas en Spotify México, '
        'se planteó la búsqueda de la raíz de la ecuación no lineal:\n'
        'f(t) = S(t) - 100 = 0\n'
        'f(t) = -0.000839·t³ + 0.076977·t² + 1.081162·t - 97.927102 = 0\n\n'
        'Para la resolución se establecieron dos métodos: el Método de Bisección (método cerrado por intervalos) '
        'y el Método de Newton-Raphson (método abierto mediante aproximación por tangentes), fijando un criterio de parada '
        'con una tolerancia estricta de error relativo porcentual aproximado: |Ea%| < 10⁻⁴ % (0.0001%).\n\n'
        'Definición del intervalo inicial:\n'
        'Al inspeccionar los datos reales acumulados, se observa que en la semana 35 el acumulado fue S(35) = 99.602 M, '
        'mientras que en la semana 36 alcanzó S(36) = 102.738 M. Por eso se toma [35, 36] como intervalo. Evaluando f sobre el modelo ajustado en esos extremos:\n'
        '• f(35) = S_modelo(35) - 100 = 98.2416 - 100 = -1.7584 < 0\n'
        '• f(36) = S_modelo(36) - 100 = 101.6162 - 100 = +1.6162 > 0\n'
        'Al verificarse f(35)·f(36) < 0, el Teorema de Bolzano garantiza la existencia de al menos una raíz en el intervalo [35, 36].'
    )
    p.paragraph_format.space_after = Pt(8)

    # 3.2.1 Bisección
    add_custom_heading(doc, 'A. Aplicación del Método de Bisección', level=3)
    p = doc.add_paragraph(
        'Partiendo del intervalo [a₀, b₀] = [35.0, 36.0], el algoritmo calcula sucesivamente el punto medio xr = (a + b)/2 '
        'y actualiza los límites de acuerdo al signo del producto f(a)·f(xr). '
        'Por su velocidad de convergencia lineal (reducción del intervalo al 50% en cada iteración), el método requirió '
        '15 iteraciones para alcanzar un error relativo |Ea%| = 0.000086% < 10⁻⁴ %, alcanzando la raíz t* = 35.520172 semanas.'
    )
    p.paragraph_format.space_after = Pt(6)

    # Tabla Bisección de salida.txt
    table_bis = doc.add_table(rows=1, cols=7)
    table_bis.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(table_bis.rows[0], ['Iter', 'a', 'b', 'xr', 'f(a)', 'f(xr)', '|Ea%|'])

    bis_data = [
        (1, 35.00000, 36.00000, 35.500000, -1.7584, -0.0680, 100.000000),
        (2, 35.50000, 36.00000, 35.750000, -0.0680, 0.7749, 0.699301),
        (3, 35.50000, 35.75000, 35.625000, -0.0680, 0.3537, 0.350877),
        (4, 35.50000, 35.62500, 35.562500, -0.0680, 0.1429, 0.175747),
        (5, 35.50000, 35.56250, 35.531250, -0.0680, 0.0375, 0.087951),
        (6, 35.50000, 35.53125, 35.515625, -0.0680, -0.0153, 0.043995),
        (7, 35.51562, 35.53125, 35.523438, -0.0153, 0.0111, 0.021993),
        (8, 35.51562, 35.52344, 35.519531, -0.0153, -0.0021, 0.010997),
        (9, 35.51953, 35.52344, 35.521484, -0.0021, 0.0045, 0.005498),
        (10, 35.51953, 35.52148, 35.520508, -0.0021, 0.0012, 0.002749),
        (11, 35.51953, 35.52051, 35.520020, -0.0021, -0.0004, 0.001375),
        (12, 35.52002, 35.52051, 35.520264, -0.0004, 0.0004, 0.000687),
        (13, 35.52002, 35.52026, 35.520142, -0.0004, -0.0000, 0.000344),
        (14, 35.52014, 35.52026, 35.520203, -0.0000, 0.0002, 0.000172),
        (15, 35.52014, 35.52020, 35.520172, -0.0000, 0.0001, 0.000086)
    ]
    for row in bis_data:
        r_cells = table_bis.add_row().cells
        r_cells[0].text = str(row[0])
        r_cells[1].text = f'{row[1]:.5f}'
        r_cells[2].text = f'{row[2]:.5f}'
        r_cells[3].text = f'{row[3]:.6f}'
        r_cells[4].text = f'{row[4]:.4f}'
        r_cells[5].text = f'{row[5]:.4f}'
        r_cells[6].text = f'{row[6]:.6f}'
        for cell in r_cells:
            set_cell_margins(cell, top=30, bottom=30, left=60, right=60)
            p_c = cell.paragraphs[0]
            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p_c.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(8.5)

    p_post_bis = doc.add_paragraph('>> Resultado Bisección: t* = 35.520172 semanas en 15 iteraciones.')
    p_post_bis.runs[0].font.bold = True
    p_post_bis.paragraph_format.space_before = Pt(4)
    p_post_bis.paragraph_format.space_after = Pt(8)

    # 3.2.2 Newton-Raphson
    add_custom_heading(doc, 'B. Aplicación del Método de Newton-Raphson', level=3)
    p = doc.add_paragraph(
        'Al ser la función S(t) un polinomio continuo y diferenciable, se calculó su derivada primera analítica:\n'
        'f\'(t) = S\'(t) = 3·(-0.000839)·t² + 2·(0.076977)·t + 1.081162 = -0.002517·t² + 0.153954·t + 1.081162\n\n'
        'Se adoptó como estimación inicial t₀ = 35.0 semanas (extremo inferior del intervalo de cambio de signo) '
        'y se aplicó la relación de recurrencia:\n'
        't_{i+1} = t_i - [ f(t_i) / f\'(t_i) ]\n\n'
        'Gracias a la convergencia cuadrática del método, Newton-Raphson alcanzó la tolerancia fijada en tan solo 3 iteraciones:'
    )
    p.paragraph_format.space_after = Pt(6)

    # Tabla Newton de salida.txt
    table_new = doc.add_table(rows=1, cols=6)
    table_new.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(table_new.rows[0], ['Iter', 'x_i', 'f(x_i)', "f'(x_i)", 'x_{i+1}', '|Ea%|'])

    new_data = [
        (1, 35.000000, -1.758365, 3.386516, 35.519225, 1.461815),
        (2, 35.519225, -0.003113, 3.374301, 35.520148, 0.002597),
        (3, 35.520148, -0.000000, 3.374278, 35.520148, 0.000000)
    ]
    for row in new_data:
        r_cells = table_new.add_row().cells
        r_cells[0].text = str(row[0])
        r_cells[1].text = f'{row[1]:.6f}'
        r_cells[2].text = f'{row[2]:.6f}'
        r_cells[3].text = f'{row[3]:.6f}'
        r_cells[4].text = f'{row[4]:.6f}'
        r_cells[5].text = f'{row[5]:.6f}'
        for cell in r_cells:
            set_cell_margins(cell, top=40, bottom=40, left=80, right=80)
            p_c = cell.paragraphs[0]
            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p_c.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(9.0)

    p_post_new = doc.add_paragraph('>> Resultado Newton-Raphson: t* = 35.520148 semanas en 3 iteraciones.')
    p_post_new.runs[0].font.bold = True
    p_post_new.paragraph_format.space_before = Pt(4)
    p_post_new.paragraph_format.space_after = Pt(8)

    # Control por interpolación lineal
    add_custom_heading(doc, 'C. Control por Interpolación Lineal Directa sobre los Datos', level=3)
    p = doc.add_paragraph(
        'Como método de contraste independiente del ajuste cúbico, se realizó una interpolación lineal directa '
        'utilizando únicamente los dos puntos empíricos que encierran el hito: semana 35 (S = 99.602 M) y semana 36 (S = 102.738 M):\n\n'
        't_lineal = 35 + [ (100.0 - 99.602) / (102.738 - 99.602) ] = 35 + (0.398 / 3.136) = 35.1269 semanas (≈ 35.127 semanas)\n\n'
        'La diferencia entre la raíz del modelo cúbico (t* = 35.520 semanas) y la interpolación lineal directa (t = 35.127 semanas) '
        'es de (35.520 - 35.127) × 7 ≈ 2.75 días. '
        'Esta discrepancia es esperable y se encuentra dentro de la incertidumbre propia del ajuste polinómico '
        '(error estándar Sy/x = ±0.93 millones de streams), dado que el modelo cúbico suaviza la trayectoria global '
        'sin pasar obligatoriamente por cada punto medido. '
        'Ambos cálculos sitúan el cruce de los 100 millones a fines de septiembre o principios de octubre de 2023 '
        '(entre el 28/09/2023 y el 05/10/2023).'
    )
    p.paragraph_format.space_after = Pt(10)

    img2_path = os.path.join(base_dir, 'grafico_2_convergencia_biseccion_vs_newton.png')
    if os.path.exists(img2_path):
        doc.add_picture(img2_path, width=Inches(6.0))
        p_caption2 = doc.add_paragraph(
            'Figura 2: Comparación de la convergencia en escala semilogarítmica: Bisección (15 iteraciones, orden lineal) '
            'frente a Newton-Raphson (3 iteraciones, orden cuadrático) bajo la tolerancia de error 10⁻⁴ %.'
        )
        p_caption2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_caption2.runs[0].font.italic = True
        p_caption2.runs[0].font.size = Pt(9.5)
        p_caption2.runs[0].font.color.rgb = RGBColor.from_string('595959')

    doc.add_page_break()

    # 3.3 Comparación
    add_custom_heading(doc, '3.3 Comparación entre el Método de Bisección y Newton-Raphson', level=2)
    p = doc.add_paragraph(
        'El análisis comparativo entre ambos métodos numéricos de búsqueda de raíces pone de manifiesto '
        'sus características operativas y teóricas:'
    )
    p.paragraph_format.space_after = Pt(6)

    table_comp = doc.add_table(rows=1, cols=4)
    table_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(table_comp, ['Criterio de Evaluación', 'Método de Bisección', 'Método de Newton-Raphson', 'Análisis Comparativo'])

    comp_items = [
        ('Clasificación', 'Método cerrado (por intervalos)', 'Método abierto (unipuntual)', 'Bisección acota la raíz; Newton traza rectas tangentes sucesivas.'),
        ('Condición inicial', 'Intervalo [35, 36] con f(a)·f(b) < 0', 'Punto inicial t₀ = 35.0', 'Bisección garantiza convergencia si Bolzano se cumple; Newton requiere un t₀ cercano.'),
        ('Iteraciones requeridas', '15 iteraciones', '3 iteraciones', 'Newton converge 5 veces más rápido en cantidad de pasos computacionales.'),
        ('Orden de convergencia', 'Lineal (orden 1, factor 0.5)', 'Cuadrático (orden 2)', 'Newton duplica aproximadamente los dígitos significativos en cada iteración.'),
        ('Raíz hallada (t*)', '35.520172 semanas', '35.520148 semanas', 'Difieren en 0.00002 semanas (menos de 2 segundos); discrepancia relativa menor a 0.0001%.'),
        ('Fecha estimada', 'Fines de sept. / 1 oct. 2023', 'Fines de sept. / 1 oct. 2023', 'Ambos métodos conducen a la misma estimación temporal del hito.')
    ]
    for row in comp_items:
        r_cells = table_comp.add_row().cells
        for idx, val in enumerate(row):
            r_cells[idx].text = val
            set_cell_margins(r_cells[idx], top=50, bottom=50, left=70, right=70)
            p_c = r_cells[idx].paragraphs[0]
            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            for run in p_c.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(9.0)

    p_post_comp = doc.add_paragraph()
    p_post_comp.paragraph_format.space_before = Pt(8)
    p_post_comp.paragraph_format.space_after = Pt(12)

    # 3.4 Diferenciación
    add_custom_heading(doc, '3.4 Diferenciación Numérica: Ritmo Semanal de Streams', level=2)
    p = doc.add_paragraph(
        'Para analizar la velocidad con la que se generaban las reproducciones a lo largo del año, '
        'se estimó la derivada primera dS/dt aplicando esquemas de diferencias finitas sobre los datos discretos '
        'con un paso regular de h = 1 semana, contrastándolos con la derivada de la función continua ajustada.\n\n'
        'Fórmulas aplicadas:\n'
        '• Diferencia hacia adelante (error O(h)):   v_adelante(ti) = [ S(ti+1) - S(ti) ] / h\n'
        '• Diferencia hacia atrás (error O(h)):      v_atras(ti)    = [ S(ti) - S(ti-1) ] / h\n'
        '• Diferencia centrada (error O(h²)):        v_centrada(ti) = [ S(ti+1) - S(ti-1) ] / (2h)\n\n'
        'La siguiente tabla presenta una selección representativa de semanas a lo largo del año, '
        'incluyendo las semanas 24 a 27 que corresponden al auge de viralización en redes:'
    )
    p.paragraph_format.space_after = Pt(6)

    table_diff = doc.add_table(rows=1, cols=5)
    table_diff.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_header(table_diff, ['Semana (t)', 'Dif. Adelante O(h)', 'Dif. Atrás O(h)', 'Dif. Centrada O(h²)', "Derivada del modelo S'(t)"])

    # 11 filas representativas de salida.txt (incluye semanas 24-27)
    diff_data = [
        (0, '1.445', '---', '---', '1.081'),
        (1, '1.417', '1.445', '1.431', '1.233'),
        (10, '2.149', '2.565', '2.357', '2.369'),
        (20, '3.093', '3.024', '3.058', '3.154'),
        (24, '3.563', '3.084', '3.324', '3.326'),
        (25, '4.171', '3.563', '3.867', '3.357'),
        (26, '3.508', '4.171', '3.840', '3.383'),
        (27, '3.800', '3.508', '3.654', '3.403'),
        (30, '3.507', '3.613', '3.560', '3.435'),
        (35, '3.136', '3.254', '3.195', '3.387'),
        (46, '---', '2.812', '---', '2.838')
    ]
    for row in diff_data:
        r_cells = table_diff.add_row().cells
        for idx, val in enumerate(row):
            r_cells[idx].text = str(val)
            set_cell_margins(r_cells[idx], top=35, bottom=35, left=70, right=70)
            p_c = r_cells[idx].paragraphs[0]
            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p_c.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(8.5)

    doc.add_page_break()

    # 3.5 Localización del Pico de Demanda
    add_custom_heading(doc, '3.5 Localización del Pico de Demanda y Punto de Inflexión', level=2)
    p_diff_analysis = doc.add_paragraph(
        'El análisis diferencial permite contrastar la predicción teórica del modelo frente al comportamiento empírico de la demanda:\n\n'
        '• Según el modelo analítico: El ritmo máximo se produce en el punto de inflexión de la curva cúbica, '
        'donde la derivada segunda se anula (S\'\'(t) = 0):\n'
        '  S\'\'(t) = 6·a·t + 2·b = 0  →  t_pico = -b / (3a)\n'
        '  t_pico = -0.076977 / [ 3 · (-0.000839) ] = 30.59 semanas (fines de agosto de 2023), '
        'con un ritmo de 3.436 millones de streams por semana.\n\n'
        '• En los datos reales observados: El pico efectivo semanal se registró en la semana 26 (cierre del 27/07/2023), '
        'con 4.171 millones de streams en esa única semana. '
        'Esta fecha coincide con la explosión del trend de TikTok de julio de 2023 (Chilango, 12/07/2023).\n\n'
        '• Comparación: El ajuste polinómico cúbico, al ser una curva global y suave, suaviza el pico de la serie temporal: '
        'lo desplaza unas 4 semanas hacia adelante (semana 30.6 frente a semana 26) y lo atenúa (3.436 M/sem frente a los 4.171 M/sem observados).'
    )
    p_diff_analysis.paragraph_format.space_after = Pt(10)

    img3_path = os.path.join(base_dir, 'grafico_3_derivada_tasa_viralidad.png')
    if os.path.exists(img3_path):
        doc.add_picture(img3_path, width=Inches(6.0))
        p_caption3 = doc.add_paragraph(
            'Figura 3: Ritmo de streams semanales calculado a partir de los datos y comparado con la derivada '
            "del modelo S'(t), visualizando el efecto de suavizado y el pico de demanda."
        )
        p_caption3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_caption3.runs[0].font.italic = True
        p_caption3.runs[0].font.size = Pt(9.5)
        p_caption3.runs[0].font.color.rgb = RGBColor.from_string('595959')

    doc.add_page_break()

    # 3.6 Generalización a otras canciones
    add_custom_heading(doc, '3.6 Generalización a otras canciones', level=2)
    p_gen = doc.add_paragraph(
        'A fin de responder al requerimiento de la cátedra respecto a que la metodología sirva como una herramienta '
        'generalizable de ingeniería, el script de cálculo se estructuró de forma completamente modular. Mediante la función '
        'analizar_cancion(nombre, csv, meta), el sistema es capaz de procesar cualquier serie temporal histórica de streams '
        'semanales obtenida de los charts oficiales (kworb.net). Incorporar una nueva canción únicamente requiere agregar el '
        'archivo CSV en la carpeta datos/ y registrar una línea con su nombre y meta en la lista del script.\n\n'
        'Para evaluar el alcance y los límites del enfoque numérico, se contrastó el caso de "Rosa Pastel" (resurgimiento '
        'gradual de catálogo impulsado por redes) frente a dos estrenos comerciales masivos en Spotify México: '
        '"Ella Baila Sola" (Eslabón Armado y Peso Pluma, 2023) y "Tití Me Preguntó" (Bad Bunny, 2022). '
        'Los resultados comparativos obtenidos se resumen en la siguiente tabla:'
    )
    p_gen.paragraph_format.space_after = Pt(6)

    # Tabla comparativa de canciones (compacta)
    table_gen = doc.add_table(rows=1, cols=10)
    table_gen.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_gen = [
        'Canción', 'Semanas (desde)', 'Total M', 'R²', 'Sy/x M',
        'Hito 100 M (semana, Newton)', 'Iter. bis./Newton', 'Pico modelo', 'Pico datos', 'Diagnóstico'
    ]
    col_widths_gen = [
        Inches(1.2), Inches(0.8), Inches(0.45), Inches(0.55), Inches(0.45),
        Inches(0.85), Inches(0.55), Inches(0.75), Inches(0.75), Inches(0.5)
    ]
    format_table_header(table_gen.rows[0], headers_gen, col_widths=col_widths_gen)

    gen_rows = [
        ('Rosa Pastel (Belanova)', '47 (26/01/2023)', '132.9', '0.999533', '0.927', '35.52 (≈1/10/2023)', '15 / 3', 'semana 30.59', 'semana 26, 4.171 M', 'aplica'),
        ('Ella Baila Sola (Eslabón Armado y Peso Pluma)', '52 (23/03/2023, estreno)', '409.6', '0.996265', '6.656', '3.55 (≈16/04/2023)', '19 / 3', 'no detecta (a = +0.005926)', 'semana 5, 26.140 M', 'no aplica'),
        ('Tití Me Preguntó (Bad Bunny)', '52 (12/05/2022, estreno)', '298.3', '0.999692', '1.596', '9.87 (≈20/07/2022)', '17 / 3', 'no detecta (a = +0.000279)', 'semana 6, 9.860 M', 'no aplica')
    ]

    for row in gen_rows:
        r_cells = table_gen.add_row().cells
        for idx, val in enumerate(row):
            r_cells[idx].text = val
            set_cell_margins(r_cells[idx], top=30, bottom=30, left=40, right=40)
            p_c = r_cells[idx].paragraphs[0]
            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            for run in p_c.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(7.5)
                if idx == 9:
                    run.font.bold = True

    p_post_gen = doc.add_paragraph()
    p_post_gen.paragraph_format.space_after = Pt(8)

    img4_path = os.path.join(base_dir, 'grafico_4_comparacion_canciones.png')
    if os.path.exists(img4_path):
        doc.add_picture(img4_path, width=Inches(5.2))
        p_caption4 = doc.add_paragraph(
            'Figura 4: Streams semanales medidos y derivada del modelo S\'(t) '
            'para las tres canciones analizadas. Se observa cómo la cúbica ajusta con alto R² pero genera una derivada '
            'parabólica cóncava hacia arriba en los estrenos (a > 0), provocando un repunte irreal hacia el final del año.'
        )
        p_caption4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_caption4.runs[0].font.italic = True
        p_caption4.runs[0].font.size = Pt(9.5)
        p_caption4.runs[0].font.color.rgb = RGBColor.from_string('595959')

    p_ideas = doc.add_paragraph(
        'Del análisis sistemático de la tabla comparativa y la Figura 4 se desprenden las siguientes conclusiones y principios clave:\n\n'
        '1. Regla de validación matemática del pico: El ritmo de reproducciones está dado por la derivada primera S\'(t) = 3a·t² + 2b·t + c, '
        'que corresponde a una parábola. El punto de inflexión del modelo continuo se ubica donde S\'\'(t) = 6a·t + 2b = 0, es decir, '
        'en t = -b/(3a). Este punto es un MÁXIMO local del ritmo de streams únicamente si la parábola abre hacia abajo, lo que exige '
        'estrictamente que a < 0 y que el valor t caiga dentro del intervalo de semanas observadas. Si a > 0, la parábola abre hacia arriba '
        'y el punto t = -b/(3a) representa un MÍNIMO del ritmo de streams; por ende, en este caso la función cúbica resulta '
        'matemáticamente incapaz de modelar el pico de la serie.\n\n'
        '2. Resurgimiento gradual (Rosa Pastel): "Rosa Pastel" describe un fenómeno de resurgimiento gradual: sube sostenidamente '
        'durante varios meses hasta alcanzar un pico a mediados de 2023 y luego decae paulatinamente. La regresión cúbica obtiene '
        'a = -0.000839 < 0, por lo que encuentra de forma consistente el pico en la semana 30.59. El diagnóstico es que el modelo aplica.\n\n'
        '3. Dinámica de estrenos y falacia del R² alto: Los estrenos comerciales ("Ella Baila Sola" y "Tití Me Preguntó") arrancan '
        'directamente en o muy cerca de su pico histórico debido a la expectativa del lanzamiento, y a partir de allí experimentan '
        'un decaimiento sostenido. Al ajustar un polinomio cúbico a estos perfiles, el modelo obtiene coeficientes principales positivos '
        '(a = +0.005926 y a = +0.000279). En consecuencia, la derivada cuadrática vuelve a subir de manera pronunciada e irreal hacia '
        'el final del período analizado (comportamiento claramente visible en el gráfico 4 para Ella Baila Sola). A pesar de esta '
        'incoherencia física evidente, el coeficiente de determinación R² se mantiene altísimo (0.996265 y 0.999692). '
        'Esto evidencia un principio esencial de la práctica de ingeniería: un R² alto no garantiza que el modelo sirva para todo ni '
        'que represente adecuadamente la dinámica física real.\n\n'
        '4. Universalidad de los componentes generales: Aunque la cúbica no sea idónea para predecir el pico en estrenos, '
        'las demás herramientas numéricas implementadas funcionan de forma universal para todas las canciones: la búsqueda de '
        'raíces para determinar cuándo se alcanzaron los 100 millones de streams convergió dentro de la tolerancia fijada en los tres casos '
        '(Bisección en 15 a 19 iteraciones; Newton-Raphson en exactamente 3 iteraciones), y el cálculo de derivadas discretas '
        'por diferencias finitas localizó certeramente el pico real de los datos empíricos.\n\n'
        '5. Detección automática del intervalo en Tití Me Preguntó: En los datos reales acumulados de Tití Me Preguntó, el cruce '
        'de los 100 millones ocurre entre las semanas 10 y 11 (interpolación lineal en t = 10.04 semanas), pero la función del modelo '
        'cúbico cruza dicho umbral entre las semanas 9 y 10 (con raíz en t* = 9.87 semanas). El algoritmo programado detecta '
        'automáticamente el intervalo de cambio de signo sobre la función del modelo f(t) = S(t) - 100 y utiliza dicho intervalo para '
        'inicializar Bisección y fijar el punto de partida de Newton-Raphson. Este desfase responde al mismo efecto ya analizado: '
        'la regresión por mínimos cuadrados minimiza los residuos globales pero no pasa exactamente por los puntos observados.\n\n'
        '6. Valor de ingeniería y líneas futuras: El mayor valor de la herramienta desarrollada como proyecto de ingeniería radica en su '
        'reutilización y en su capacidad de autodiagnóstico: ante cualquier serie de demanda, calcula metas acumuladas y comprueba '
        'automáticamente la validez del modelo para estimar el pico. Además, el software avisa explícitamente cuando no aplica ("no aplica"), '
        'evitando emitir estimaciones falsas o carentes de sustento. Como mejora y trabajo futuro para canciones de estreno, '
        'se plantea incorporar modelos basados en decaimiento exponencial con linealización logarítmica (abordados en el apunte de ajuste de curvas).'
    )
    p_ideas.paragraph_format.space_after = Pt(12)

    doc.add_page_break()

    # 3.7 Limitaciones
    add_custom_heading(doc, '3.7 Limitaciones del Modelo Numérico', level=2)
    p_lim = doc.add_paragraph(
        'El análisis numérico realizado presenta una serie de limitaciones técnicas y metodológicas '
        'que deben considerarse al interpretar los resultados:\n\n'
        '1. La cúbica no pasa por los puntos: El ajuste por mínimos cuadrados minimiza la suma de residuos cuadráticos globales, '
        'pero no garantiza que la curva pase por los puntos observados. Por este motivo, la raíz del modelo para los 100 millones '
        '(t* = 35.52 semanas en Rosa Pastel) difiere en aproximadamente 2.75 días respecto a la interpolación lineal directa entre '
        'las semanas 35 y 36 (t = 35.13 semanas). Esta discrepancia es inherente al compromiso entre simplicidad analítica y precisión local.\n\n'
        '2. Suavizado del pico de demanda: Al ajustar un único polinomio cúbico a lo largo de la serie temporal, el modelo atenúa '
        'los cambios abruptos de pendiente. En Rosa Pastel, el pico real de la semana 26 (4.171 M streams) es desplazado por el modelo '
        'hacia la semana 30.6 y atenuado a 3.436 M streams/semana.\n\n'
        '3. Tipología de curvas admisibles y dinámica de estrenos: La regresión cúbica solo es capaz de modelar trayectorias que '
        'presenten un único pico interior de ritmo (aquel donde a < 0, con etapa de aceleración previa e inflexión posterior). '
        'En canciones de estreno comercial (como Ella Baila Sola o Tití Me Preguntó), donde el consumo máximo ocurre inmediatamente tras '
        'el lanzamiento y luego decae de forma sostenida, la cúbica genera a > 0 y su derivada exhibe un rebote ficticio al final. '
        'Para modelar adecuadamente los estrenos se requiere otro tipo de modelo matemático, como un decaimiento exponencial con linealización.\n\n'
        '4. Alcance de los datos: Las cifras empleadas provienen exclusivamente de los charts semanales del Top 200 de Spotify México (kworb.net). '
        'No contemplan las reproducciones en otras plataformas masivas de streaming (como YouTube o Apple Music), '
        'ni el consumo en otros países de habla hispana donde el fenómeno también se replicó, '
        'ni las escuchas por debajo del umbral del Top 200.\n\n'
        '5. Imposibilidad de extrapolación fuera del rango observado: El modelo cúbico es estrictamente descriptivo para el intervalo relevado. '
        'Debido a que el coeficiente de mayor orden en Rosa Pastel es negativo (a = -0.000839), evaluar la función fuera de 2023 '
        'conduciría a un decaimiento monótono hacia -∞, lo cual carece de sentido físico para un valor de reproducciones acumuladas.'
    )
    p_lim.paragraph_format.space_after = Pt(14)

    # -------------------------------------------------------------
    # 4. CONCLUSIONES
    # -------------------------------------------------------------
    add_custom_heading(doc, '4. CONCLUSIONES Y DISCUSIÓN ACADÉMICA', level=1)
    p_conc = doc.add_paragraph(
        'A partir de los cálculos realizados y el análisis de los resultados obtenidos, se extraen las siguientes conclusiones:\n\n'
        '1. Ajuste de Curvas: La regresión polinómica cúbica ofreció una aproximación muy representativa de la acumulación anual '
        'de streams en Spotify México para Rosa Pastel, alcanzando un coeficiente de determinación R² = 0.9995 y un error estándar '
        'Sy/x = 0.927 M. El modelo describe con claridad las etapas de crecimiento acelerado e inflexión hacia una etapa más estable.\n\n'
        '2. Desempeño Comparativo de Búsqueda de Raíces: Ambos métodos numéricos permitieron ubicar el hito de los 100 millones '
        'de reproducciones en la semana 35.52 (fines de septiembre / 1 de octubre de 2023), con una diferencia entre ambos de solo 0.00002 semanas. '
        'Sin embargo, Newton-Raphson demostró ser notablemente más veloz que Bisección (3 iteraciones frente a 15) '
        'gracias a su convergencia cuadrática, confirmando lo anticipado por la teoría.\n\n'
        '3. Control y Verificación: La comparación entre el modelo cúbico y la interpolación lineal directa entre las semanas 35 y 36 '
        'arrojó una diferencia de apenas 2.75 días. Este resultado valida la coherencia práctica del modelo continuo frente a los datos tabulados.\n\n'
        '4. Análisis de Derivadas y Pico: El cálculo de derivadas por diferencias finitas permitió constatar que el mayor ritmo de consumo '
        'ocurrió en la semana 26 (fines de julio de 2023, con 4.171 M streams), coincidiendo con la repercusión del trend de TikTok. '
        'Se verificó además que el modelo cúbico tiende a suavizar este pico, desplazándolo temporalmente unas 4 semanas.\n\n'
        '5. Utilidad en Ingeniería: El ejercicio evidenció cómo las herramientas clásicas de métodos numéricos permiten convertir '
        'un conjunto de datos discretos de telemetría en información continua utilizable para la toma de decisiones, '
        'como la planificación de recursos computacionales y el dimensionamiento de servidores de streaming ante variaciones de demanda.\n\n'
        '6. Generalización y Criterio de Aplicabilidad en Ingeniería: Al extender el método a otras canciones ("Ella Baila Sola" y '
        '"Tití Me Preguntó"), se constató que mientras la búsqueda de raíces para metas acumuladas y el cálculo de derivadas discretas '
        'resultan universales y altamente eficientes (Newton convergió siempre en 3 iteraciones), la regresión cúbica no resulta aplicable '
        'para predecir el pico en estrenos comerciales sin aceleración previa (a > 0). Esto demostró que un R² sumamente elevado '
        '(> 0.996) no garantiza la validez física del modelo. El valor de ingeniería de la herramienta radica en su modularidad, '
        'reutilización y capacidad de autodiagnóstico para notificar cuándo un modelo no aplica en lugar de arrojar resultados falsos, '
        'señalando la conveniencia de integrar modelos alternativos (como decaimiento exponencial con linealización).'
    )
    p_conc.paragraph_format.space_after = Pt(14)

    # -------------------------------------------------------------
    # 5. BIBLIOGRAFÍA Y DECLARACIÓN DE USO DE IA
    # -------------------------------------------------------------
    add_custom_heading(doc, '5. BIBLIOGRAFÍA Y DECLARACIÓN DE USO DE IA', level=1)
    p_bib = doc.add_paragraph(
        '1. Chapra, S. C., & Canale, R. P. (2015). Métodos Numéricos para Ingenieros (7ma ed.). McGraw-Hill Education.\n'
        '2. Arnaudo, C. (2026). Material de Cátedra y Apuntes Teórico-Prácticos: Raíces de Ecuaciones, Ajuste de Curvas y Diferenciación Numérica. Facultad de Ingeniería, Universidad Católica de Córdoba.\n'
        '3. Burden, R. L., & Faires, J. D. (2011). Análisis Numérico (9na ed.). Cengage Learning.\n'
        '4. kworb.net. (2026). Spotify Chart History – Belanova "Rosa Pastel" (Track 6Z0ybnsUBhbZ9ZjPW64eoF). '
        'Disponible en: https://kworb.net/spotify/track/6Z0ybnsUBhbZ9ZjPW64eoF.html (consultado el 22/10/2026).\n'
        '5. kworb.net. (2026). Spotify Chart History – Eslabón Armado y Peso Pluma "Ella Baila Sola" (Track 3qQbCzHBycnDpGskqOWY0E). '
        'Disponible en: https://kworb.net/spotify/track/3qQbCzHBycnDpGskqOWY0E.html (consultado el 27/10/2026).\n'
        '6. kworb.net. (2026). Spotify Chart History – Bad Bunny "Tití Me Preguntó" (Track 1IHWl5LamUGEuP4ozKQSXZ). '
        'Disponible en: https://kworb.net/spotify/track/1IHWl5LamUGEuP4ozKQSXZ.html (consultado el 27/10/2026).\n'
        '7. Chilango. (2023). "Rosa Pastel, la triste tendencia de TikTok que musicaliza sueños frustrados". '
        'Disponible en: https://www.chilango.com/agenda/otros/rosa-pastel-tiktok-tendencia/ (publicado el 12 de julio de 2023).\n\n'
        'DECLARACIÓN SOBRE EL USO DE HERRAMIENTAS DE INTELIGENCIA ARTIFICIAL:\n'
        'En el desarrollo de este trabajo se utilizaron herramientas de inteligencia artificial (Google Antigravity/Gemini y Claude de Anthropic) '
        'como soporte para estructurar y redactar el informe, generar gráficos y revisar el código de cálculo. '
        'Todos los cálculos numéricos, datos, tablas de iteraciones y conclusiones fueron verificados y analizados críticamente por los alumnos autores.'
    )
    p_bib.paragraph_format.space_after = Pt(8)

    doc_path = os.path.join(base_dir, 'Informe_Proyecto_Metodos_Numericos_Rosa_Pastel.docx')
    doc.save(doc_path)
    print(f'[OK] Documento Word guardado exitosamente en: {doc_path}')


if __name__ == '__main__':
    main()
