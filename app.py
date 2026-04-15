import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Software Profesional FES", layout="wide")

if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

# --- FUNCIÓN: GENERAR WORD POR HOJAS ---
def generar_word_fes(datos, pd_res, s_res, analisis_ia):
    doc = Document()
    # HOJA 1: CARÁTULA
    t = doc.add_heading('INFORME PSICOPROFESIONAL FES', 0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_heading('1. Datos Contextuales', level=1)
    for k, v in datos.items():
        doc.add_paragraph(f"{k}: {v}")
    doc.add_page_break()

    # HOJA 2: RESULTADOS Y GRÁFICOS
    doc.add_heading('2. Perfil de Resultados', level=1)
    tabla = doc.add_table(rows=1, cols=3); tabla.style = 'Table Grid'
    hdr = tabla.rows[0].cells
    hdr[0].text, hdr[1].text, hdr[2].text = 'Escala', 'PD', 'S'
    for s, v in pd_res.items():
        row = tabla.add_row().cells
        row[0].text, row[1].text, row[2].text = s, str(v), str(s_res[s])
    doc.add_page_break()

    # HOJA 3: ANÁLISIS IA
    doc.add_heading('3. Interpretación Clínica y Recomendaciones', level=1)
    for area in analisis_ia:
        doc.add_heading(area['titulo'], level=2)
        doc.add_paragraph(area['contenido'])
    
    buf = BytesIO(); doc.save(buf); buf.seek(0)
    return buf

# --- SIDEBAR: DATOS PERSONALES Y CONTEXTO ---
with st.sidebar:
    st.header("📋 Ficha Técnica")
    st.markdown("**Escala Aplicada: [X] FES** [ ] WES [ ] CIES")
    nombre = st.text_input("Nombre Completo", "Barayan Adan Barahona Marquez")
    edad = st.number_input("Edad", 12, 99, 32)
    profesion = st.text_input("Profesión", "Policia")
    
    st.subheader("🌐 Contexto Familiar Relevante")
    composicion = st.selectbox("Composición", ["Nuclear", "Extensa", "Reconstituida"])
    ciclo_vital = st.selectbox("Ciclo Vital", ["Hijos pequeños", "Hijos adolescentes", "Adultos"])
    crisis = st.text_area("Crisis actual (Ej: Alcoholismo del padre)", "mi padre sufre de alcoholismo")
    jerarquia = st.text_area("Roles y Autoridad", "mi madre ama de casa, mi padre gastos, yo ayudo")
    cultura = st.text_area("Antecedentes Culturales", "Valores tradicionales, respeto a la autoridad")

# --- PESTAÑAS (HOJAS) ---
tab1, tab2, tab3, tab4 = st.tabs(["📄 Instrucciones", "📝 Aplicación", "📊 Gráficos", "🧠 Análisis e Impresión"])

with tab1:
    st.header("Instrucciones de la Prueba")
    st.write(f"Estimado **{nombre}**, lea pausadamente las instrucciones:")
    st.markdown("""
    - Responda **V** o **F** pensando en su familia tal como es en la actualidad.
    - No hay respuestas correctas, solo perfiles de su realidad.
    - **Llene pausadamente** cada ítem para que los resultados sean precisos.
    """)

with tab2:
    st.header("Cuestionario FES (90 Ítems)")
    preguntas = {1: "En mi familia nos ayudamos y apoyamos realmente unos a otros", 2: "Los miembros guardan sentimientos para sí mismos", 3: "En nuestra familia discutimos mucho"} # (Completar con las 90 anteriores)
    for i in range(1, 91):
        txt = preguntas.get(i, f"Frase número {i} del manual FES.")
        st.session_state.respuestas[i] = st.radio(f"{i}. {txt}", ["V", "F"], key=f"q{i}", horizontal=True, index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i]))

with tab3:
    st.header("Visualización de Resultados")
    sub_n = ["CO", "EX", "CT", "AU", "AC", "IC", "SR", "MR", "OR", "CN"]
    s_v = {s: 50 for s in sub_n} # Simulación
    
    # Gráfico 1: Subescalas
    fig1 = go.Figure(data=go.Scatter(x=sub_n, y=list(s_v.values()), mode='lines+markers', marker_symbol='square'))
    fig1.update_layout(title="Perfil de 10 Subescalas", yaxis_range=[0, 100])
    st.plotly_chart(fig_ind := fig1)

    # Gráfico 2: Dimensiones
    dim_v = [55, 45, 60] # Relaciones, Desarrollo, Estabilidad
    fig2 = go.Figure(data=[go.Bar(x=["Relaciones", "Desarrollo", "Estabilidad"], y=dim_v)])
    fig2.update_layout(title="Interpretación por Dimensiones", yaxis_range=[0, 100])
    st.plotly_chart(fig2)

with tab4:
    st.header("🧠 Análisis de IA y Reporte Profesional")
    
    # Lógica de Análisis Cruzado (Contextual)
    analisis = [
        {"titulo": "Análisis General y por Áreas", "contenido": f"El informante {nombre}, de ocupación {profesion}, presenta un clima familiar marcado por la crisis reactiva de {crisis}."},
        {"titulo": "Recomendaciones Terapéuticas", "contenido": "Se sugiere terapia familiar sistémica enfocada en la jerarquía y el manejo de la crisis de alcoholismo reportada."}
    ]
    
    for a in analisis:
        st.subheader(a['titulo'])
        st.write(a['contenido'])

    word_file = generar_word_fes({"Nombre": nombre, "Profesión": profesion, "Crisis": crisis}, s_v, s_v, analisis)
    st.download_button("📥 DESCARGAR INFORME COMPLETO (HOJAS SEPARADAS)", word_file, f"Reporte_FES_{nombre}.docx")

st.success(f"Informe listo para {nombre}. Escala marcada: [X] FES")
