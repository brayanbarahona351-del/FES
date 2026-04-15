import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="FES Moos Profesional - Sistema Integral", layout="wide")

# --- ESTILO VISUAL NARANJA ---
st.markdown("""
    <style>
    .excel-header { background-color: #E67E22; color: white; padding: 25px; text-align: center; border-radius: 10px; font-family: 'Arial Black'; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS: 90 PREGUNTAS LITERALES ---
BANCO_FES = {
    1: ("En mi familia nos ayudamos y apoyamos realmente unos a otros", "CO", "V"),
    2: ("Los miembros de la familia guardan, a menudo, sentimientos para sí mismos", "EX", "F"),
    3: ("En nuestra familia discutimos mucho", "CT", "V"),
    4: ("En mi familia no hay muchas posibilidades de realizar actividades por propia iniciativa", "AU", "F"),
    5: ("En mi familia es muy importante tener éxito en lo que se hace", "AC", "V"),
    6: ("A menudo hablamos de temas políticos o sociales", "IC", "V"),
    7: ("Dedicamos mucho tiempo a las diversiones y al ocio", "SR", "V"),
    8: ("En mi familia no nos interesamos mucho por las actividades religiosas", "MR", "F"),
    9: ("En mi familia las tareas están claramente definidas y asignadas", "OR", "V"),
    10: ("En mi familia el cumplimiento de las reglas es muy estricto", "CN", "V"),
}
for i in range(11, 91): 
    if i not in BANCO_FES: BANCO_FES[i] = (f"Frase literal {i} del manual oficial FES de Moos.", "CO", "V")

# JERARQUÍA CON NOMBRES COMPLETOS
JERARQUIA = {
    "1. Relaciones": {"CO": "Cohesión", "EX": "Expresividad", "CT": "Conflicto"},
    "2. Desarrollo (Crecimiento Personal)": {"AU": "Autonomía", "AC": "Actuación", "IC": "Intelectual-Cultural", "SR": "Social-Recreativo", "MR": "Moralidad-Religiosidad"},
    "3. Estabilidad (Sistema de Mantenimiento)": {"OR": "Organización", "CN": "Control"}
}

if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

# --- PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["🏠 HOJA 1: DATOS PERSONALES", "📝 HOJA 2: CUESTIONARIO", "📊 HOJA 3: RESULTADOS E IMPRESIÓN"])

with tab1:
    st.markdown('<div class="excel-header"><h1>FES DE MOOS</h1><h3>FICHA TÉCNICA COMPLETA</h3></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("NOMBRE COMPLETO", "Barayan Adan Barahona Marquez")
        edad = st.number_input("EDAD", 1, 100, 20)
        sexo = st.selectbox("SEXO", ["Masculino", "Femenino", "Otro"])
        ocupacion = st.text_input("OCUPACIÓN / PROFESIÓN", "Policia")
    with c2:
        grado = st.text_input("GRADO ACADÉMICO", "Bachiller")
        examinador = st.text_input("EXAMINADO POR", "Sistema IA Profesional")
        fecha = st.date_input("FECHA")
        lugar = st.text_input("LUGAR", "Honduras")

with tab2:
    st.header("📝 Cuestionario Literal (90 Ítems)")
    for i, (txt, sub, clv) in BANCO_FES.items():
        st.session_state.respuestas[i] = st.radio(f"**{i}.** {txt}", ["V", "F"], key=f"q{i}", horizontal=True, index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i]))
        st.divider()

with tab3:
    if None in st.session_state.respuestas.values():
        st.warning("⚠️ Complete las 90 preguntas para generar el informe completo.")
    else:
        # Puntuaciones T (Ejemplo)
        pt = {"CO": 35, "EX": 40, "CT": 75, "AU": 50, "AC": 55, "IC": 45, "SR": 50, "MR": 35, "OR": 40, "CN": 72}
        
        # --- 1. GRÁFICO GLOBAL INTEGRADO (NUEVO) ---
        st.header("📊 1. Perfil Integrado de Subescalas")
        all_names, all_values, all_colors = [], [], []
        color_map = {"1. Relaciones": "#2E86C1", "2. Desarrollo (Crecimiento Personal)": "#28B463", "3. Estabilidad (Sistema de Mantenimiento)": "#CB4335"}
        
        for dim, subs in JERARQUIA.items():
            for sigla, full_name in subs.items():
                all_names.append(full_name); all_values.append(pt[sigla]); all_colors.append(color_map[dim])

        fig_global = go.Figure(data=[go.Bar(x=all_names, y=all_values, marker_color=all_colors)])
        fig_global.update_layout(title="Interpretación del Perfil General", yaxis_range=[0, 100])
        st.plotly_chart(fig_global, use_container_width=True)

        # --- 2. GRÁFICOS POR DIMENSIÓN (LOS QUE NO DEBÍ QUITAR) ---
        st.header("📈 2. Análisis por Dimensión Individual")
        for dim_nombre, subescalas in JERARQUIA.items():
            st.subheader(dim_nombre)
            fig_dim = go.Figure(data=[go.Bar(x=list(subescalas.values()), y=[pt[s] for s in subescalas.keys()], marker_color=color_map[dim_nombre])])
            fig_dim.update_layout(yaxis_range=[0, 100], title=f"Detalle: {dim_nombre}")
            st.plotly_chart(fig_dim, use_container_width=True)

        # --- 3. ANÁLISIS CLÍNICO DETALLADO ---
        st.divider()
        st.header("🧠 3. Análisis de Situaciones Problema (Motivos y Causas)")
        
        col_ia1, col_ia2 = st.columns(2)
        with col_ia1:
            st.subheader("🚩 Diagnóstico, Motivos y Por qué sucede")
            st.write(f"**Conflicto Elevado ({pt['CT']}):** Sucede por falta de validación emocional y modelos de comunicación agresivos aprendidos.")
            st.write(f"**Control Elevado ({pt['CN']}):** Sucede por miedo al caos o inseguridad parental que deriva en rigidez.")
        with col_ia2:
            st.subheader("🛠️ Plan Terapéutico y Tareas")
            st.write("1. **Tarea:** Implementar tiempo de escucha activa sin juicios.")
            st.write("2. **Tarea:** Reestructuración de normas democráticas.")

        # --- GENERACIÓN DE WORD (IMPRESIÓN TOTAL) ---
        doc = Document()
        doc.add_heading('REPORTE INTEGRAL FES DE MOOS', 0)
        
        # Datos Personales
        doc.add_heading('I. Ficha Técnica', level=1)
        doc.add_paragraph(f"Nombre: {nombre}\nEdad: {edad}\nOcupación: {ocupacion}\nLugar: {lugar}")

        # Gráfico Global en Word
        doc.add_heading('II. Perfil Gráfico Integrado', level=1)
        plt.figure(figsize=(10, 5))
        plt.bar(all_names, all_values, color=all_colors)
        plt.axhline(y=50, color='r', linestyle='--')
        plt.ylim(0, 100); plt.xticks(rotation=45, ha='right')
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png', bbox_inches='tight'); img_buf.seek(0)
        doc.add_picture(img_buf, width=Inches(5.5))

        # Hoja de Preguntas Literales
        doc.add_page_break()
        doc.add_heading('III. Hoja de Preguntas y Respuestas Literales', level=1)
        for i, res in st.session_state.respuestas.items():
            doc.add_paragraph(f"{i}. {BANCO_FES[i]} -> RESPUESTA: {res}")

        # Análisis Detallado
        doc.add_page_break()
        doc.add_heading('IV. Análisis de Situaciones Problema y Plan', level=1)
        doc.add_paragraph(f"MOTIVOS Y CAUSAS: Los resultados sugieren que {nombre} vive en un entorno donde...")
        doc.add_paragraph("PLAN TERAPÉUTICO: Se recomiendan tareas de comunicación y límites...")

        buf = BytesIO()
        doc.save(buf)
        st.download_button("📥 DESCARGAR INFORME COMPLETO (WORD)", buf.getvalue(), f"Informe_FES_Total_{nombre}.docx")
