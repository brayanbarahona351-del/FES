import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Profesional FES", layout="wide")

# Inicialización de respuestas
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

# --- FUNCIÓN: GENERAR WORD CON SALTOS DE PÁGINA ---
def generar_word_profesional(datos, pd_res, s_res, analisis_ia):
    doc = Document()
    
    # HOJA 1: CARÁTULA Y DATOS
    titulo = doc.add_heading('INFORME CLÍNICO: ESCALA FES', 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_heading('1. Datos de Identificación y Contexto', level=1)
    for k, v in datos.items():
        p = doc.add_paragraph()
        p.add_run(f"{k}: ").bold = True
        p.add_run(str(v))
    
    doc.add_page_break() # SALTO DE PÁGINA

    # HOJA 2: RESULTADOS CUANTITATIVOS (RÉPLICA EXCEL)
    doc.add_heading('2. Resultados Estadísticos', level=1)
    tabla = doc.add_table(rows=1, cols=3)
    tabla.style = 'Table Grid'
    hdr = tabla.rows.cells
    hdr.text, hdr.text, hdr.text = 'Subescala', 'PD (Directo)', 'S (Típico)'
    
    for sub, valor in pd_res.items():
        row = tabla.add_row().cells
        row.text, row.text, row.text = sub, str(valor), str(s_res[sub])
    
    doc.add_page_break() # SALTO DE PÁGINA

    # HOJA 3: ANÁLISIS DE IA Y RECOMENDACIONES
    doc.add_heading('3. Interpretación Clínica y Recomendaciones', level=1)
    for item in analisis_ia:
        doc.add_heading(item['titulo'], level=2)
        doc.add_paragraph(item['contenido'])

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- SIDEBAR (DATOS COMPLETOS) ---
with st.sidebar:
    st.header("📋 Ficha Técnica")
    st.markdown("Escala Aplicada: **[X] FES**")
    nombre = st.text_input("Nombre Completo", value="Barayan Adan Barahona Marquez")
    edad = st.number_input("Edad", 12, 99, 32)
    profesion = st.text_input("Profesión", value="Policia")
    
    st.subheader("🌐 Contexto")
    composicion = st.selectbox("Composición", ["Nuclear", "Extensa", "Monoparental", "Reconstituida"])
    ciclo_vital = st.selectbox("Ciclo Vital", ["Infantes", "Adolescentes", "Adultos", "Nido Vacío"])
    crisis = st.text_area("Crisis (Alcoholismo, etc.)", value="mi padre sufre de alcoholismo")
    jerarquia = st.text_area("Roles", value="madre ama de casa, padre gastos, yo ayudo")

# --- PESTAÑAS (TABS) ---
tab1, tab2, tab3 = st.tabs(["📄 Instrucciones", "📝 Aplicación", "📊 Informe e Impresión"])

with tab1:
    st.info("Lea pausadamente. Marque con una cruz mentalmente V o F. El sistema procesará el perfil individual.")

with tab2:
    st.header("Cuestionario (90 Ítems)")
    # (Bucle de 90 preguntas que ya tenemos...)
    for i in range(1, 91):
        st.session_state.respuestas[i] = st.radio(f"{i}. Pregunta...", ["V", "F"], key=f"f{i}", horizontal=True)

with tab3:
    if None in st.session_state.respuestas.values():
        st.warning("⚠️ Complete el test para imprimir.")
    else:
        # LÓGICA DE CALIFICACIÓN (Ejemplo)
        sub_nombres = ["CO", "EX", "CT", "AU", "AC", "IC", "SR", "MR", "OR", "CN"]
        s_scores = {s: 55 for s in sub_nombres} # Simulación
        
        # PREPARAR ANÁLISIS IA
        analisis_clinico = [
            {"titulo": "Análisis de Perfil Profesional", 
             "contenido": f"Dada su ocupación como {profesion} y su edad de {edad} años, se observa una estructura de control que busca compensar el caos externo."},
            {"titulo": "Influencia de Crisis", 
             "contenido": f"Atención: El clima está influenciado por la crisis de: {crisis}. No se recomienda diagnóstico estructural."},
            {"titulo": "Recomendaciones", 
             "contenido": "Se sugiere intervención en codependencia y establecimiento de límites claros en la jerarquía familiar."}
        ]

        # BOTÓN DE IMPRESIÓN WORD
        datos_doc = {"Nombre": nombre, "Edad": edad, "Profesión": profesion, "Crisis": crisis}
        archivo_word = generar_word_profesional(datos_doc, s_scores, s_scores, analisis_clinico)
        
        st.download_button(
            label="📥 DESCARGAR INFORME PARA IMPRIMIR (WORD)",
            data=archivo_word,
            file_name=f"Informe_FES_{nombre}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # GRÁFICOS
        fig = go.Figure(data=go.Scatter(x=sub_nombres, y=list(s_scores.values()), mode='lines+markers'))
        st.plotly_chart(fig)
