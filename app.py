import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import plotly.graph_objects as go
import math

# --- 1. INICIALIZACIÓN DE SESIÓN (Evita el AttributeError) ---
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 0
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}
if 'datos_familia' not in st.session_state:
    st.session_state.datos_familia = {}

# --- 2. CLAVES DE CORRECCIÓN (Pág. 8 del PDF) ---
# He configurado las subescalas con la lógica de V/F del manual
CLAVES = {
    "Cohesión (CO)": {"V": [1, 11, 21, 31, 41, 51, 61, 71, 81], "F": []},
    "Expresividad (EX)": {"V": [2, 12, 32, 42, 52, 62, 72, 82], "F": [22]},
    "Conflicto (CT)": {"V": [3, 23, 43, 53, 73], "F": [13, 33, 63, 83]},
    "Autonomía (AU)": {"V": [4, 14, 24, 34, 44, 54, 64, 74], "F": [84]},
    "Actuación (AC)": {"V": [5, 15, 25, 35, 45, 55, 65, 75, 85], "F": []},
    "Intelectual (IC)": {"V": [6, 16, 26, 36, 46, 56, 66, 76, 86], "F": []},
    "Social-Rec (SR)": {"V": [7, 17, 27, 37, 47, 57, 67, 77], "F": [87]},
    "Moralidad (MR)": {"V": [8, 28, 38, 48, 58, 68, 78, 88], "F": [18]},
    "Organización (OR)": {"V": [9, 19, 29, 39, 49, 59, 69, 79, 89], "F": []},
    "Control (CN)": {"V": [10, 30, 40, 50, 60, 70, 80], "F": [20, 90]}
}

# --- 3. FUNCIONES DE ANÁLISIS E INFORME ---
def obtener_analisis_ia(s_scores):
    analisis = []
    # Lógica de ejemplo para la IA
    if s_scores["Cohesión (CO)"] < 40:
        analisis.append({"Area": "COHESIÓN", "Causas": "Desvinculación afectiva y falta de apoyo mutuo percibido.", "Rec": "Fomentar espacios compartidos no estructurados."})
    if s_scores["Conflicto (CT)"] > 60:
        analisis.append({"Area": "CONFLICTO", "Causas": "Baja tolerancia a la frustración y comunicación agresiva.", "Rec": "Entrenamiento en resolución de problemas y comunicación asertiva."})
    return analisis

def generar_word(datos, pd_res, s_scores, analisis_ia):
    doc = Document()
    doc.add_heading('INFORME PSICOLÓGICO - ESCALA FES', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # HOJA 1: Datos
    doc.add_heading('1. Datos Generales', level=1)
    for k, v in datos.items(): doc.add_paragraph(f"{k}: {v}")
    doc.add_page_break()
    
    # HOJA 2: Cuadros Excel
    doc.add_heading('2. Cuadros de Resultados', level=1)
    tabla = doc.add_table(rows=1, cols=3)
    tabla.style = 'Table Grid'
    for i, h in enumerate(['Subescala', 'PD', 'S']): tabla.rows[0].cells[i].text = h
    for sub, pd_v in pd_res.items():
        row = tabla.add_row().cells
        row[0].text, row[1].text, row[2].text = sub, str(pd_v), str(s_scores[sub])
    doc.add_page_break()
    
    # HOJA 3: IA
    doc.add_heading('3. Análisis Experto y Recomendaciones', level=1)
    for a in analisis_ia:
        doc.add_heading(a['Area'], level=2)
        doc.add_paragraph(f"Causas: {a['Causas']}")
        doc.add_paragraph(f"Recomendaciones: {a['Rec']}")
    
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- 4. INTERFAZ ---
st.title("🏠 Software FES: Clima Social Familiar")

with st.sidebar:
    st.header("📋 Datos")
    nombre = st.text_input("Familia / Paciente")
    if st.button("🗑️ Reiniciar"):
        st.session_state.pagina_actual = 0
        st.session_state.respuestas = {i: None for i in range(1, 91)}
        st.rerun()

# FLUJO DE PÁGINAS
if st.session_state.pagina_actual == 0:
    st.info("Lea las instrucciones del manual y presione comenzar.")
    if st.button("Comenzar Autoaplicación"):
        st.session_state.pagina_actual = 1
        st.rerun()

elif 1 <= st.session_state.pagina_actual <= 6:
    step = 15
    idx_inicio = (st.session_state.pagina_actual - 1) * step + 1
    st.subheader(f"Preguntas {idx_inicio} a {idx_inicio + step - 1}")
    
    for i in range(idx_inicio, idx_inicio + step):
        if i > 90: break
        st.session_state.respuestas[i] = st.radio(f"{i}. Pregunta {i}", ["V", "F"], 
            index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i]), key=f"r{i}")

    col1, col2 = st.columns(2)
    if col1.button("Atrás") and st.session_state.pagina_actual > 1:
        st.session_state.pagina_actual -= 1
        st.rerun()
    if col2.button("Siguiente"):
        st.session_state.pagina_actual += 1
        st.rerun()

elif st.session_state.pagina_actual > 6:
    st.header("📊 Resultados Finales")
    
    # Cálculo
    pd_final = {}
    for sub, c in CLAVES.items():
        v = sum(1 for x in c["V"] if st.session_state.respuestas[x] == "V")
        f = sum(1 for x in c["F"] if st.session_state.respuestas[x] == "F")
        pd_final[sub] = v + f
    
    s_scores = {k: (v * 4) + 25 for k, v in pd_final.items()} # Simulación baremo
    analisis = obtener_analisis_ia(s_scores)
    
    # Descarga
    file_word = generar_word({"Paciente": nombre}, pd_final, s_scores, analisis)
    st.download_button("📥 Descargar Reporte en Word", file_word, "Informe_FES.docx")
    
    # Gráfico
    fig = go.Figure(data=go.Scatter(x=list(s_scores.keys()), y=list(s_scores.values()), mode='lines+markers'))
    st.plotly_chart(fig)
