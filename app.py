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

# --- 1. FUNCIÓN: GENERAR WORD CON SALTOS DE PÁGINA (CORREGIDA) ---
def generar_word_profesional(datos, pd_res, s_res, analisis_ia):
    doc = Document()
    
    # HOJA 1: DATOS DE IDENTIFICACIÓN
    titulo = doc.add_heading('INFORME CLÍNICO: ESCALA FES', 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_heading('1. Datos de Identificación y Contexto', level=1)
    for k, v in datos.items():
        p = doc.add_paragraph()
        p.add_run(f"{k}: ").bold = True
        p.add_run(str(v))
    
    doc.add_page_break() # SALTO A HOJA 2

    # HOJA 2: RESULTADOS ESTADÍSTICOS
    doc.add_heading('2. Resultados Cuantitativos', level=1)
    tabla = doc.add_table(rows=1, cols=3)
    tabla.style = 'Table Grid'
    
    # Acceso corregido a las celdas del encabezado
    hdr_cells = tabla.rows[0].cells
    hdr_cells[0].text = 'Subescala'
    hdr_cells[1].text = 'PD (Directo)'
    hdr_cells[2].text = 'S (Típico)'
    
    for sub, valor_pd in pd_res.items():
        row_cells = tabla.add_row().cells
        row_cells[0].text = str(sub)
        row_cells[1].text = str(valor_pd)
        row_cells[2].text = str(s_res[sub])
    
    doc.add_page_break() # SALTO A HOJA 3

    # HOJA 3: ANÁLISIS DE IA Y RECOMENDACIONES
    doc.add_heading('3. Interpretación Clínica y Recomendaciones', level=1)
    for item in analisis_ia:
        doc.add_heading(item['titulo'], level=2)
        doc.add_paragraph(item['contenido'])

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- 2. SIDEBAR: DATOS PARA EL ANÁLISIS ---
with st.sidebar:
    st.header("📋 Ficha Técnica")
    st.markdown("Escala Aplicada: **[X] FES**")
    nombre = st.text_input("Nombre Completo", value="Barayan Adan Barahona Marquez")
    edad = st.number_input("Edad", 12, 99, 32)
    profesion = st.text_input("Profesión", value="Policia")
    
    st.subheader("🌐 Variables de Contexto")
    composicion = st.selectbox("Composición", ["Nuclear", "Extensa", "Monoparental", "Reconstituida"])
    ciclo_vital = st.selectbox("Etapa Ciclo Vital", ["Infantes", "Adolescentes", "Adultos", "Nido Vacío"])
    crisis = st.text_area("Influencia de Crisis", value="mi padre sufre de alcoholismo", 
                          help="Ejemplo: fallecimiento, desempleo o adicciones.")
    jerarquia = st.text_area("Dinámica de Autoridad", value="mi madre ama de casa, mi padre se encarga de los gastos",
                             help="Ejemplo: roles y toma de decisiones.")

# --- 3. PESTAÑAS (HOJAS DE TRABAJO) ---
tab1, tab2, tab3 = st.tabs(["📄 Instrucciones", "📝 Aplicación (90 Ítems)", "📊 Informe e Impresión"])

with tab1:
    st.header("Instrucciones Oficiales FES")
    st.write(f"Estimado **{nombre}**, responda V (Verdadero) o F (Falso) a cada frase.")

with tab2:
    st.header("Cuestionario Autoaplicado")
    # Diccionario de preguntas abreviado para el ejemplo (debes poner las 90)
    for i in range(1, 91):
        st.session_state.respuestas[i] = st.radio(f"**{i}.** Frase del manual FES...", 
                                                 ["V", "F"], key=f"q{i}", horizontal=True,
                                                 index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i]))

with tab3:
    if None in st.session_state.respuestas.values():
        st.warning("⚠️ Complete las 90 preguntas para generar el reporte de impresión.")
    else:
        # LÓGICA DE CALIFICACIÓN (Ejemplo simulado)
        sub_nombres = ["CO", "EX", "CT", "AU", "AC", "IC", "SR", "MR", "OR", "CN"]
        pd_simulado = {s: 5 for s in sub_nombres}
        s_simulado = {s: 50 for s in sub_nombres}
        
        # ANÁLISIS DE IA PERSONALIZADO
        analisis_ia = [
            {"titulo": "Análisis de Perfil Profesional", 
             "contenido": f"Dada su ocupación como {profesion} y su edad de {edad} años, se observa una percepción del clima familiar marcada por la estructura y el cumplimiento de normas."},
            {"titulo": "Influencia de Crisis y Roles", 
             "contenido": f"Atención: El clima reportado está influenciado por: {crisis}. Se observa una dinámica donde: {jerarquia}."},
            {"titulo": "Recomendaciones Terapéuticas", 
             "contenido": "Se sugiere trabajar en la expresión de afectos y flexibilizar el control para mejorar la cohesión familiar."}
        ]

        # BOTÓN DE IMPRESIÓN (WORD)
        datos_informe = {"Nombre": nombre, "Edad": edad, "Profesión": profesion, "Contexto": composicion}
        doc_word = generar_word_profesional(datos_informe, pd_simulado, s_simulado, analisis_ia)
        
        st.download_button(
            label="📥 DESCARGAR INFORME PARA IMPRIMIR (WORD)",
            data=doc_word,
            file_name=f"Informe_FES_{nombre}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # GRÁFICO DE PERFIL
        fig = go.Figure(data=go.Scatter(x=sub_nombres, y=list(s_simulado.values()), mode='lines+markers', name="Perfil Individual"))
        fig.update_layout(title="Perfil de Subescalas FES", yaxis_range=)
        st.plotly_chart(fig)
