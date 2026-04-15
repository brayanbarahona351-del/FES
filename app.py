import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="FES Moos Profesional - Sistema Integral", layout="wide")

# --- ESTILO VISUAL ---
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

# JERARQUÍA CON NOMBRES COMPLETOS (Para los gráficos)
JERARQUIA = {
    "1. Relaciones": {"CO": "Cohesión", "EX": "Expresividad", "CT": "Conflicto"},
    "2. Desarrollo (Crecimiento Personal)": {"AU": "Autonomía", "AC": "Actuación", "IC": "Intelectual-Cultural", "SR": "Social-Recreativo", "MR": "Moralidad-Religiosidad"},
    "3. Estabilidad (Sistema de Mantenimiento)": {"OR": "Organización", "CN": "Control"}
}

if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: "V" for i in range(1, 91)} # Simulación para ver gráficos

# --- INTERFAZ ---
tab1, tab2, tab3 = st.tabs(["🏠 DATOS PERSONALES", "📝 CUESTIONARIO", "📊 INFORME INTEGRAL E INTERPRETACIÓN"])

with tab1:
    st.markdown('<div class="excel-header"><h1>FES DE MOOS</h1><h3>FICHA TÉCNICA DEL EXAMINADO</h3></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("👤 NOMBRE COMPLETO", "Barayan Adan Barahona Marquez")
        edad = st.number_input("📅 EDAD", 1, 100, 20)
        sexo = st.selectbox("🚻 SEXO", ["Masculino", "Femenino", "Otro"])
        ocupacion = st.text_input("💼 OCUPACIÓN / PROFESIÓN", "Policia")
    with c2:
        grado = st.text_input("🎓 GRADO ACADÉMICO", "Bachiller")
        examinador = st.text_input("🩺 EXAMINADO POR", "Sistema IA Profesional")
        fecha = st.date_input("FECHA DE EVALUACIÓN")
        lugar = st.text_input("📍 LUGAR", "Honduras")

with tab2:
    st.header("📝 Cuestionario Literal")
    for i, (txt, sub, clv) in BANCO_FES.items():
        st.session_state.respuestas[i] = st.radio(f"**{i}.** {txt}", ["V", "F"], key=f"q{i}", horizontal=True)

with tab3:
    # Puntajes T (Simulados para el análisis de perfil)
    pt = {"CO": 35, "EX": 40, "CT": 75, "AU": 50, "AC": 55, "IC": 45, "SR": 50, "MR": 35, "OR": 40, "CN": 72}
    
    st.header("📊 1. Perfil Integrado Global")
    
    # --- GRÁFICO INTEGRAL (REQUERIMIENTO NUEVO) ---
    all_names = []
    all_values = []
    all_colors = []
    color_map = {"1. Relaciones": "#2E86C1", "2. Desarrollo (Crecimiento Personal)": "#28B463", "3. Estabilidad (Sistema de Mantenimiento)": "#CB4335"}
    
    for dim, subs in JERARQUIA.items():
        for sigla, full_name in subs.items():
            all_names.append(full_name)
            all_values.append(pt[sigla])
            all_colors.append(color_map[dim])

    fig_global = go.Figure(data=[go.Bar(x=all_names, y=all_values, marker_color=all_colors)])
    fig_global.update_layout(title="Interpretación de Perfil General (Dimensiones Integradas)", yaxis_range=[0, 100], xaxis_tickangle=-45)
    st.plotly_chart(fig_global, use_container_width=True)

    st.divider()
    
    # --- ANÁLISIS DETALLADO CON EJEMPLOS DE "POR QUÉ SUCEDE" ---
    st.header("🧠 2. Análisis Clínico de Situaciones Problema")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🚩 Diagnóstico y Motivos")
        if pt["CT"] > 60:
            st.error("**Área Crítica: Conflictividad Elevada**")
            st.write("**¿Por qué sucede esto? (Ejemplos):**")
            st.write("*   **Falta de Validación:** Los miembros sienten que sus opiniones no cuentan, lo que genera frustración que estalla en gritos.")
            st.write("*   **Modelos Aprendidos:** Se utiliza la discusión como única forma de obtener atención o resolver diferencias.")
            st.write("*   **Estrés Externo:** Presiones económicas o laborales que se descargan en el núcleo familiar.")
        
        if pt["CN"] > 65:
            st.warning("**Área Crítica: Control Autoritario**")
            st.write("**¿Por qué sucede esto? (Ejemplos):**")
            st.write("*   **Miedo al Caos:** Los padres temen perder el respeto de los hijos y compensan con reglas extremas.")
            st.write("*   **Inseguridad:** Necesidad de predecir cada movimiento para sentirse seguros en el ambiente hogareño.")

    with col_b:
        st.subheader("🛠️ Plan Terapéutico y Tareas")
        st.success("**Estrategia de Intervención**")
        st.write("1. **Tarea de Roles:** Intercambio de responsabilidades durante un fin de semana para fomentar empatía.")
        st.write("2. **Tarea de Comunicación:** Implementar el 'Semáforo de la Ira' para identificar cuándo retirarse de una discusión.")

    # --- GENERACIÓN DE WORD CON TODO ---
    doc = Document()
    doc.add_heading('REPORTE PROFESIONAL FES DE MOOS', 0)
    doc.add_heading(f'Paciente: {nombre} | Fecha: {fecha}', level=1)

    # Gráfico Global en el Word
    doc.add_heading('I. Gráfico de Perfil Integrado', level=2)
    plt.figure(figsize=(12, 6))
    plt.bar(all_names, all_values, color=all_colors)
    plt.xticks(rotation=45, ha='right')
    plt.axhline(y=50, color='red', linestyle='--')
    plt.ylim(0, 100)
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight'); img_buf.seek(0)
    doc.add_picture(img_buf, width=Inches(6))

    # Análisis de situaciones problema en el Word
    doc.add_heading('II. Interpretación de Situaciones Problema', level=2)
    doc.add_paragraph(f"Se analizan las causas raíz de los puntajes críticos. Por ejemplo, la elevación en Control puede deberse a modelos de crianza rígidos o miedos parentales...")

    final_buf = BytesIO()
    doc.save(final_buf)
    st.download_button("📥 DESCARGAR INFORME WORD COMPLETO", final_buf.getvalue(), f"Informe_FES_Final_{nombre}.docx")
