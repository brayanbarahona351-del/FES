import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Evaluación Clima Familiar (FES)", layout="centered")

# --- ESTILOS TIPO CLÍNICO (Inspirado en tu última app) ---
st.markdown("""
    <style>
    .stRadio > div { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; }
    .stProgress > div > div > div > div { background-color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- CONTROL DE SESIÓN ---
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}
    st.session_state.pagina_actual = 0

# --- DATA: CLAVES DE CORRECCIÓN (Pág. 8 del PDF) ---
CLAVES = {
    "Cohesión (CO)": {"V": [1, 11, 21, 31, 41, 51, 61, 71, 81], "F": []},
    "Expresividad (EX)": {"V": [2, 12, 32, 42, 52, 62, 72, 82], "F": [22]},
    "Conflicto (CT)": {"V": [3, 23, 43, 53, 73], "F": [13, 33, 63, 83]},
    "Autonomía (AU)": {"V": [4, 14, 24, 34, 44, 54, 64, 74], "F": [84]},
    "Actuación (AC)": {"V": [5, 15, 25, 35, 45, 65, 75, 85], "F": [55]},
    "Int.-Cultural (IC)": {"V": [6, 16, 26, 56, 66, 76, 86], "F": [36, 46]},
    "Social-Rec. (SR)": {"V": [7, 17, 27, 37, 47, 77], "F": [57, 67, 87]},
    "Moral.-Relig. (MR)": {"V": [8, 28, 38, 48, 58, 78, 88], "F": [18, 68]},
    "Organización (OR)": {"V": [9, 19, 29, 39, 49, 59, 69, 79, 89], "F": []},
    "Control (CN)": {"V": [10, 30, 40, 50, 80, 90], "F": [20, 60, 70]}
}

# --- TEXTOS DEL CUESTIONARIO (Pág. 1-4 del PDF) ---
PREGUNTAS = {
    1: "En mi familia nos ayudamos y apoyamos realmente unos a otros",
    2: "Los miembros de la familia guardan, a menudo, sentimientos para sí mismos",
    3: "En nuestra familia discutimos mucho",
    4: "En general ningún miembro de la familia decide por su cuenta",
    5: "Creemos que es importante ser los mejores en cualquier cosa que hagamos",
    6: "A menudo hablamos de temas políticos o sociales",
    7: "Pasamos en casa la mayor parte de nuestro tiempo libre",
    8: "Asistimos con bastante regularidad a los cultos de la Iglesia, templo, etc.",
    9: "Las actividades de nuestra familia se planifican cuidadosamente",
    10: "En mi familia tenemos reuniones obligatorias muy pocas veces",
    # NOTA: Aquí debes completar los 90 textos del manual.
}
# Relleno automático para demostración
for i in range(11, 91): 
    if i not in PREGUNTAS: PREGUNTAS[i] = f"Frase número {i} del manual FES (Consultar PDF)."

# --- INTERFAZ DE USUARIO ---
st.title("🏠 Escala de Clima Social Familiar (FES)")

with st.sidebar:
    st.header("👤 Perfil del Evaluado")
    nombre = st.text_input("Apellidos de la Familia / Nombre")
    edad = st.number_input("Edad del informante", 12, 90, 25)
    sexo = st.selectbox("Sexo", ["Masculino", "Femenino"])
    
    st.divider()
    respondidas = sum(1 for v in st.session_state.respuestas.values() if v is not None)
    st.progress(respondidas / 90)
    st.write(f"Progreso: {respondidas}/90 ítems")
    if st.button("🔄 Reiniciar"): 
        st.session_state.respuestas = {i: None for i in range(1, 91)}
        st.rerun()

# --- PÁGINA 0: INSTRUCCIONES (Pág. 1 del Manual) ---
if st.session_state.pagina_actual == 0:
    st.header("📖 Instrucciones")
    st.markdown(f"""> **Bienvenido(a), {nombre if nombre else 'Usuario'}.**
    A continuación encontrará una serie de frases sobre su familia. 
    Debe decidir si la frase es **Verdadera (V)** o **Falsa (F)** pensando en lo que sucede la mayoría de las veces.
    - No hay respuestas correctas o incorrectas.
    - Trate de responder a todas las frases.""")
    if st.button("Comenzar Evaluación"):
        st.session_state.pagina_actual = 1
        st.rerun()

# --- CUESTIONARIO PAGINADO (Réplica de tu lógica anterior) ---
elif 1 <= st.session_state.pagina_actual <= 6:
    ITEMS_PAG = 15
    inicio = (st.session_state.pagina_actual - 1) * ITEMS_PAG + 1
    fin = inicio + ITEMS_PAG

    st.subheader(f"Parte {st.session_state.pagina_actual} de 6")
    
    for i in range(inicio, fin):
        if i > 90: break
        st.session_state.respuestas[i] = st.radio(
            f"**{i}. {PREGUNTAS[i]}**", 
            ["Verdadero", "Falso"], 
            index=None if st.session_state.respuestas[i] is None else ["Verdadero", "Falso"].index(st.session_state.respuestas[i]),
            key=f"item_{i}",
            horizontal=True
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Anterior"):
            st.session_state.pagina_actual -= 1
            st.rerun()
    with col2:
        if st.session_state.pagina_actual < 6:
            if st.button("Siguiente ➡️"): st.session_state.pagina_actual += 1; st.rerun()
        else:
            if st.button("📊 GENERAR RESULTADOS"):
                st.session_state.pagina_actual = 7
                st.rerun()

# --- PÁGINA FINAL: RESULTADOS (Réplica de Cuadros Excel y Gráficas) ---
elif st.session_state.pagina_actual == 7:
    st.header("📈 Informe de Resultados")
    
    # 1. Cálculo de Puntajes Directos (PD)
    pd_res = {}
    for sub, val in CLAVES.items():
        score = sum(1 for i in val["V"] if st.session_state.respuestas[i] == "Verdadero")
        score += sum(1 for i in val["F"] if st.session_state.respuestas[i] == "Falso")
        pd_res[sub] = score

    # 2. Simulación de Conversión a Puntajes S (Baremos Pág. 10)
    # Aquí se programaría la tabla exacta del PDF
    def convertir_a_s(pd): return (pd * 5) + 20 # Ejemplo de fórmula de baremo

    s_scores = {k: convertir_a_s(v) for k, v in pd_res.items()}

    # 3. CUADRO DE RESULTADOS (Réplica Excel)
    df_res = pd.DataFrame({
        "Subescala": pd_res.keys(),
        "Puntaje Directo (PD)": pd_res.values(),
        "Puntaje Típico (S)": s_scores.values()
    })
    st.table(df_res)

    # 4. GRÁFICA DE PERFIL (Réplica Gráfico Excel)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(pd_res.keys()), 
        y=list(s_scores.values()),
        mode='lines+markers',
        line=dict(color='#007bff', width=3),
        marker=dict(size=10)
    ))
    fig.update_layout(title="Perfil de Clima Social Familiar", yaxis_range=[0, 100], grid=dict(rows=1, columns=1))
    st.plotly_chart(fig)

    st.balloons()
