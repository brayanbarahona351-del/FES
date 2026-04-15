import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from docx import Document
from docx.shared import Pt
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="FES de Moos - IA Clínica", layout="wide")

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .excel-header { background-color: #E67E22; color: white; padding: 25px; text-align: center; border-radius: 10px; font-family: 'Arial Black'; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS TÉCNICA ---
JERARQUIA = {
    "RELACIONES": {"CO": "Cohesión", "EX": "Expresividad", "CT": "Conflicto"},
    "DESARROLLO": {"AU": "Autonomía", "AC": "Actuación", "IC": "Intelectual", "SR": "Social-Rec", "MR": "Moralidad"},
    "ESTABILIDAD": {"OR": "Organización", "CN": "Control"}
}

# --- LÓGICA DE ANÁLISIS DETALLADO (IA) ---
def realizar_analisis_profundo(puntajes):
    analisis = {}
    
    # Análisis Relaciones
    if puntajes["CT"] > 60:
        analisis["RELACIONES"] = {
            "diagnostico": "Dinámica de Alta Tensión",
            "causas": "Dificultad en la gestión de la ira y falta de canales de comunicación asertiva.",
            "soluciones": "Entrenamiento en resolución de conflictos y escucha activa.",
            "plan": ["Tarea 1: Implementar la técnica del 'Tiempo Fuera'.", "Tarea 2: Sesiones de expresión emocional controlada."]
        }
    else:
        analisis["RELACIONES"] = {"diagnostico": "Equilibrio Relacional", "causas": "Respeto mutuo.", "soluciones": "Mantenimiento.", "plan": ["Tarea: Cena sin móviles."]}

    # Análisis Estabilidad
    if puntajes["CN"] > 65 and puntajes["OR"] < 40:
        analisis["ESTABILIDAD"] = {
            "diagnostico": "Control Autoritario Rígido pero Desorganizado",
            "causas": "Liderazgo basado en el miedo sin una estructura de rutinas clara.",
            "soluciones": "Creación de un sistema de responsabilidades compartidas.",
            "plan": ["Tarea 1: Calendario visual de tareas.", "Tarea 2: Delegar decisiones menores."]
        }
    else:
        analisis["ESTABILIDAD"] = {"diagnostico": "Estructura Saludable", "causas": "Normas claras.", "soluciones": "Fomento de autonomía.", "plan": ["Tarea: Revisión mensual de reglas."]}

    return analisis

# --- GENERADOR DE WORD ---
def generar_word_profesional(datos, puntajes, analisis):
    doc = Document()
    doc.add_heading('REPORTE CLÍNICO DETALLADO: FES DE MOOS', 0)

    doc.add_heading('I. Identificación', level=1)
    for k, v in datos.items():
        doc.add_paragraph(f"{k}: {v}")

    doc.add_heading('II. Análisis por Dimensión y Subescalas', level=1)
    for dim, info in analisis.items():
        doc.add_heading(f"Dimensión: {dim}", level=2)
        doc.add_paragraph(f"Diagnóstico: {info['diagnostico']}").bold = True
        doc.add_paragraph(f"Causas y Motivos: {info['causas']}")
        doc.add_paragraph(f"Soluciones Propuestas: {info['soluciones']}")
        
        doc.add_heading("Plan Terapéutico y Tareas:", level=3)
        for tarea in info['plan']:
            doc.add_paragraph(tarea, style='List Bullet')

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- INTERFAZ ---
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: "V" for i in range(1, 91)}

tab1, tab2, tab3 = st.tabs(["🏠 INTRO", "📝 CUESTIONARIO", "📊 RESULTADOS"])

with tab1:
    st.markdown('<div class="excel-header"><h1>FES DE MOOS</h1><h3>Sistema Profesional de Análisis Familiar</h3></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("NOMBRE", "Barayan Adan Barahona Marquez")
        edad = st.number_input("EDAD", 20)
        ocup = st.text_input("OCUPACIÓN", "Policia")
    with c2:
        grado = st.text_input("GRADO", "Bachiller")
        exam = st.text_input("EXAMINADO POR", "Sistema IA")
        fecha = st.date_input("FECHA")

with tab3:
    # PUNTAJES CORREGIDOS (Simulación)
    p_s = {"CO": 35, "EX": 40, "CT": 75, "AU": 50, "AC": 45, "IC": 40, "SR": 50, "MR": 30, "OR": 35, "CN": 70}
    
    informe_ia = realizar_analisis_profundo(p_s)
    
    st.header("Análisis de Resultados")
    
    # GRÁFICO GLOBAL - CORRECCIÓN DE ERROR yaxis_range
    fig = go.Figure()
    colors = {"RELACIONES": "#2E86C1", "DESARROLLO": "#28B463", "ESTABILIDAD": "#CB4335"}
    for dim, subs in JERARQUIA.items():
        fig.add_trace(go.Bar(x=list(subs.values()), y=[p_s[s] for s in subs.keys()], name=dim, marker_color=colors[dim]))
    
    # VALOR ASIGNADO A yaxis_range PARA EVITAR SYNTAX ERROR
    fig.update_layout(title="Perfil de Subescalas Integradas", barmode='group', yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

    # BOTÓN DE IMPRESIÓN WORD
    st.divider()
    datos_id = {"Nombre": nombre, "Edad": edad, "Ocupación": ocup, "Grado": grado, "Fecha": fecha}
    word_file = generar_word_profesional(datos_id, p_s, informe_ia)
    
    st.download_button(
        label="📥 DESCARGAR INFORME WORD (ANÁLISIS + CAUSAS + PLAN)",
        data=word_file,
        file_name=f"Informe_FES_{nombre}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
