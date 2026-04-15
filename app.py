import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="FES de Moos - Sistema de Análisis Clínico", layout="wide")

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

# --- LÓGICA DE ANÁLISIS DE IA (Simulada para resultados detallados) ---
def analizar_dinamica_ia(puntajes):
    analisis = {}
    
    # Análisis de Relaciones
    if puntajes["CT"] > 60 and puntajes["CO"] < 40:
        analisis["REL"] = {
            "estado": "Crítico - Desunión Conflictiva",
            "causas": "Falta de canales de comunicación asertiva, luchas de poder internas y resentimientos no resueltos.",
            "soluciones": "Entrenamiento en comunicación no violenta y espacios de mediación familiar.",
            "tareas": ["Caja de agradecimientos semanal.", "Tiempo fuera positivo en discusiones."]
        }
    else:
        analisis["REL"] = {"estado": "Funcional", "causas": "Límites claros y apoyo mutuo.", "soluciones": "Mantener rituales de conexión.", "tareas": ["Cena familiar sin tecnología."]}
    
    # Análisis de Estabilidad
    if puntajes["CN"] > 65 and puntajes["OR"] < 40:
        analisis["EST"] = {
            "estado": "Riesgo - Control Autoritario Caótico",
            "causas": "Reglas impuestas por miedo sin una estructura organizativa real.",
            "soluciones": "Democratización de normas y creación de calendarios de tareas.",
            "tareas": ["Reunión de consejo familiar para revisar reglas.", "Panel visual de responsabilidades."]
        }
    else:
        analisis["EST"] = {"estado": "Estable", "causas": "Liderazgo equilibrado.", "soluciones": "Refuerzo de autonomía.", "tareas": ["Delegar una decisión importante a los hijos."]}

    return analisis

# --- FUNCIÓN PARA GENERAR REPORTE WORD CON GRÁFICOS ---
def generar_reporte_completo(datos, puntajes, analisis_ia):
    doc = Document()
    doc.add_heading('REPORTE CLÍNICO INTEGRAL: FES DE MOOS', 0)

    # 1. Datos de Identificación
    doc.add_heading('I. Datos Generales', level=1)
    for k, v in datos.items():
        doc.add_paragraph().add_run(f"{k}: ").bold = True
        doc.add_paragraph(str(v))

    # 2. Perfil de Resultados (Tabla Excel)
    doc.add_heading('II. Cuadro de Resultados por Subescala', level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    hdr = table.rows[0].cells
    hdr[0].text, hdr[1].text, hdr[2].text = 'Dimensión', 'Subescala', 'Puntaje T'
    
    for dim, subs in JERARQUIA.items():
        for sigla, nombre in subs.items():
            row = table.add_row().cells
            row[0].text, row[1].text, row[2].text = dim, nombre, str(puntajes[sigla])

    # 3. Análisis Clínico de la IA
    doc.add_heading('III. Análisis de Dinámicas, Causas y Soluciones', level=1)
    for dim, info in analisis_ia.items():
        doc.add_heading(f"Área: {dim}", level=2)
        doc.add_paragraph(f"**Estado:** {info['estado']}").bold = True
        doc.add_paragraph(f"**Causas y Motivos:** {info['causas']}")
        doc.add_paragraph(f"**Posibles Soluciones:** {info['soluciones']}")
        
        doc.add_heading("Plan Terapéutico (Tareas Detalladas):", level=3)
        for tarea in info['tareas']:
            doc.add_paragraph(f"- {tarea}", style='List Bullet')

    # Guardar documento
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFAZ STREAMLIT ---
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: "V" for i in range(1, 91)} # Simulación completa

tab_intro, tab_fes, tab_resultados = st.tabs(["🏠 INTRO", "📝 CUESTIONARIO", "📊 INFORME DETALLADO"])

with tab_intro:
    st.markdown('<div class="excel-header"><h1>FES DE MOOS</h1><h3>Análisis de Clima Social Familiar</h3></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("Nombre Completo", "Barayan Adan Barahona Marquez")
        edad = st.number_input("Edad", 0, 100, 20)
        ocup = st.text_input("Ocupación", "Policia")
    with c2:
        grado = st.text_input("Grado Académico", "Bachiller")
        exam = st.text_input("Evaluador", "Sistema IA Profesional")
        fecha = st.date_input("Fecha de Aplicación")

with tab_fes:
    st.header("Cuestionario Aplicado")
    st.info("Visualización de las 90 respuestas procesadas.")
    # Aquí iría el loop de preguntas ya mostrado anteriormente

with tab_resultados:
    # Simulamos puntajes para el análisis (Puntajes S de 20 a 80)
    puntajes_s = {"CO": 35, "EX": 40, "CT": 72, "AU": 50, "AC": 45, "IC": 40, "SR": 50, "MR": 30, "OR": 38, "CN": 70}
    
    analisis_clinico = analizar_dinamica_ia(puntajes_s)
    
    st.header("Análisis de Dimensiones y Perfil Familiar")
    
    # GRÁFICO 1: PERFIL INTEGRADO (DIMENSIONES + SUBDIMENSIONES)
    fig = go.Figure()
    colors = {"RELACIONES": "#2E86C1", "DESARROLLO": "#28B463", "ESTABILIDAD": "#CB4335"}
    for dim, subs in JERARQUIA.items():
        fig.add_trace(go.Bar(x=list(subs.values()), y=[puntajes_s[s] for s in subs.keys()], name=dim, marker_color=colors[dim]))
    
    fig.update_layout(title="Perfil de Subescalas Integradas", barmode='group', yaxis_range=)
    st.plotly_chart(fig, use_container_width=True)

    # MOSTRAR ANÁLISIS EN PANTALLA
    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🚩 Diagnóstico de Dinámicas")
        for dim, info in analisis_clinico.items():
            st.write(f"**{dim}:** {info['estado']}")
            st.caption(f"Motivos: {info['causas']}")

    with col_b:
        st.subheader("🛠️ Plan de Intervención")
        for dim, info in analisis_clinico.items():
            st.write(f"**Tareas sugeridas ({dim}):**")
            for t in info['tareas']:
                st.write(f"• {t}")

    # BOTÓN DE IMPRESIÓN WORD COMPLETO
    st.divider()
    datos_id = {"Nombre": nombre, "Edad": edad, "Ocupación": ocup, "Grado": grado, "Evaluador": exam, "Fecha": fecha}
    archivo_final = generar_reporte_completo(datos_id, puntajes_s, analisis_clinico)
    
    st.download_button(
        label="📥 DESCARGAR INFORME CLÍNICO COMPLETO (WORD)",
        data=archivo_final,
        file_name=f"Informe_FES_Profundo_{nombre}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

st.sidebar.success("Sistema configurado con Análisis Clínico, Causas, Soluciones y Plan Terapéutico.")
