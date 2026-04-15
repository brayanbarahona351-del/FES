import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import plotly.graph_objects as go

# --- FUNCIÓN: GENERAR WORD PROFESIONAL ---
def generar_word_fes(datos_paciente, pd_res, s_scores, analisis_ia):
    doc = Document()
    
    # ESTILO DE TÍTULO
    titulo = doc.add_heading('INFORME CLÍNICO: ESCALA FES', 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # HOJA 1: DATOS GENERALES
    doc.add_heading('1. Datos de Identificación', level=1)
    for clave, valor in datos_paciente.items():
        p = doc.add_paragraph()
        p.add_run(f"{clave}: ").bold = True
        p.add_run(str(valor))

    doc.add_page_break() # SALTO DE PÁGINA

    # HOJA 2: CUADROS ESTADÍSTICOS (RÉPLICA EXCEL)
    doc.add_heading('2. Resultados Cuantitativos', level=1)
    tabla = doc.add_table(rows=1, cols=3)
    tabla.style = 'Table Grid'
    hdr_cells = tabla.rows[0].cells
    hdr_cells[0].text = 'Subescala'
    hdr_cells[1].text = 'Puntaje Directo (PD)'
    hdr_cells[2].text = 'Puntaje Típico (S)'

    for sub, pd_v in pd_res.items():
        row_cells = tabla.add_row().cells
        row_cells[0].text = sub
        row_cells[1].text = str(pd_v)
        row_cells[2].text = str(s_scores[sub])

    doc.add_page_break() # SALTO DE PÁGINA

    # HOJA 3: ANÁLISIS DE IA Y RECOMENDACIONES
    doc.add_heading('3. Interpretación y Recomendaciones (IA)', level=1)
    
    for item in analisis_ia:
        doc.add_heading(item['Area'], level=2)
        p_causas = doc.add_paragraph()
        p_causas.add_run("Posibles Causas: ").bold = True
        p_causas.add_run(item['Causas'])
        
        p_rec = doc.add_paragraph()
        p_rec.add_run("Recomendaciones Terapéuticas: ").bold = True
        p_rec.add_run(item['Recomendaciones'])

    # Guardar en buffer
    target = BytesIO()
    doc.save(target)
    target.seek(0)
    return target

# --- LÓGICA DE LA IA (Reglas de Experto) ---
def obtener_analisis_ia(s_scores):
    analisis = []
    # Ejemplo Dimensión Relaciones
    if s_scores['Cohesión (CO)'] < 40:
        analisis.append({
            "Area": "Dimensión de Relaciones",
            "Causas": "Se observa un distanciamiento emocional significativo. Los miembros podrían estar funcionando como islas independientes sin apoyo mutuo.",
            "Recomendaciones": "Implementar rituales de conexión diaria y terapia de familia centrada en la afectividad."
        })
    # Ejemplo Dimensión Estabilidad
    if s_scores['Control (CN)'] > 60:
        analisis.append({
            "Area": "Dimensión de Estabilidad",
            "Causas": "El exceso de reglas rígidas está sofocando la autonomía de los miembros, generando un clima de tensión.",
            "Recomendaciones": "Flexibilizar normas y permitir la participación de los hijos en la toma de decisiones familiares."
        })
    
    if not analisis:
        analisis.append({
            "Area": "General",
            "Causas": "El clima familiar se encuentra dentro de parámetros funcionales.",
            "Recomendaciones": "Continuar fortaleciendo los canales de comunicación asertiva."
        })
    return analisis

# --- INTERFAZ STREAMLIT (RESULTADOS FINALES) ---
if st.session_state.pagina_actual == 7:
    # ... (Cálculos de PD y S previos) ...
    
    # Preparamos datos para la IA
    resultados_ia = obtener_analisis_ia(s_scores)
    datos_paciente = {"Familia": familia, "Informante": informante, "Edad": edad}

    st.header("🏁 Evaluación Finalizada")
    
    # BOTÓN DE DESCARGA WORD
    doc_word = generar_word_fes(datos_paciente, pd_res, s_scores, resultados_ia)
    
    st.download_button(
        label="📥 Descargar Informe en Word (.docx)",
        data=doc_word,
        file_name=f"Informe_FES_{familia}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    st.info("El documento descargado contiene 3 hojas: 1) Datos, 2) Cuadros estadísticos y 3) Análisis con recomendaciones.")
