import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

# --- CONFIGURACIÓN ESTILO EXCEL (FONDO NARANJA) ---
st.markdown("""
    <style>
    .excel-header {
        background-color: #E67E22;
        color: white;
        padding: 40px;
        text-align: center;
        border-radius: 10px;
        font-family: 'Arial Black', Gadget, sans-serif;
    }
    .main { background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTRUCTURA TÉCNICA FES DE MOOS ---
# Definición de la jerarquía: Dimensión -> Subdimensiones
JERARQUIA_FES = {
    "RELACIONES": {
        "Sub": ["Cohesión (CO)", "Expresividad (EX)", "Conflicto (CT)"],
        "Color": "#2E86C1",
        "Dinamica": "Mide el grado de comunicación y apoyo libre entre los miembros contra la expresión de ira."
    },
    "DESARROLLO": {
        "Sub": ["Autonomía (AU)", "Actuación (AC)", "Intelectual (IC)", "Social-Rec (SR)", "Moralidad (MR)"],
        "Color": "#28B463",
        "Dinamica": "Evalúa los procesos de crecimiento personal fomentados por el grupo familiar."
    },
    "ESTABILIDAD": {
        "Sub": ["Organización (OR)", "Control (CN)"],
        "Color": "#CB4335",
        "Dinamica": "Analiza la estructura, reglas y jerarquías que rigen la convivencia."
    }
}

# --- INTERFAZ TIPO EXCEL (Imagen de referencia) ---
st.markdown('<div class="excel-header"><h3>Escala del Clima Social Familiar</h3><h1>FES DE MOOS</h1></div>', unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("NOMBRE", "Barayan Adan Barahona Marquez")
        edad = st.number_input("EDAD", 0, 100, 20)
        ocupacion = st.text_input("OCUPACION", "Policia")
    with col2:
        grado = st.text_input("GRADO", "Bachiller")
        examinado = st.text_input("EXAMINADO POR", "Sistema Automático")
        fecha = st.date_input("FECHA")

# --- LÓGICA DE RESULTADOS (Simulada para el ejemplo) ---
# En un caso real, aquí iría la suma de los "V" y "F" del cuestionario
puntajes_s = {
    "Cohesión (CO)": 65, "Expresividad (EX)": 40, "Conflicto (CT)": 75,
    "Autonomía (AU)": 55, "Actuación (AC)": 60, "Intelectual (IC)": 45, "Social-Rec (SR)": 50, "Moralidad (MR)": 30,
    "Organización (OR)": 35, "Control (CN)": 70
}

# --- PESTAÑA DE ANÁLISIS Y GRÁFICOS ---
st.divider()
st.header("📊 Análisis de Dimensiones y Subdimensiones")

# 1. GRÁFICO INTEGRADO (Todas las dimensiones unidas)
st.subheader("I. Perfil General Integrado")
fig_global = go.Figure()
for dim, info in JERARQUIA_FES.items():
    valores = [puntajes_s[s] for s in info["Sub"]]
    fig_global.add_trace(go.Bar(x=info["Sub"], y=valores, name=dim, marker_color=info["Color"]))

fig_global.update_layout(barmode='group', yaxis_range=[0, 100], title="Comparativa de Subescalas por Dimensión")
st.plotly_chart(fig_global, use_container_width=True)

# 2. GRÁFICOS POR DIMENSIÓN Y ANÁLISIS DE DINÁMICA
st.subheader("II. Análisis Profundo de la Dinámica Familiar")

for dim, info in JERARQUIA_FES.items():
    with st.expander(f"VER DIMENSIÓN: {dim}", expanded=True):
        c1, c2 = st.columns([1, 2])
        
        with c1:
            # Gráfico pequeño por dimensión
            fig_dim = go.Figure(go.Scatterpolar(
                r=[puntajes_s[s] for s in info["Sub"]],
                theta=info["Sub"],
                fill='toself',
                marker_color=info["Color"]
            ))
            fig_dim.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
            st.plotly_chart(fig_dim, use_container_width=True)
        
        with c2:
            st.markdown(f"**Definición:** {info['Dinamica']}")
            # Lógica de análisis dinámico
            st.markdown("**Interpretación de la Dinámica:**")
            
            # Ejemplo de lógica para Dimensión Relaciones
            if dim == "RELACIONES":
                if puntajes_s["Conflicto (CT)"] > 60 and puntajes_s["Cohesión (CO)"] < 40:
                    st.error("🚨 Dinámica de ALTO RIESGO: Se observa una familia con fuertes tensiones internas y escaso apoyo emocional.")
                else:
                    st.info("Dinámica Estable: Los niveles de conflicto y unión están dentro de los parámetros esperados.")
            
            # Ejemplo de lógica para Estabilidad
            if dim == "ESTABILIDAD":
                if puntajes_s["Control (CN)"] > 65 and puntajes_s["Organización (OR)"] < 40:
                    st.warning("⚠️ Dinámica de CONTROL CAÓTICO: Existen muchas reglas impuestas pero falta orden en la ejecución diaria.")

# --- BOTÓN DE MODIFICACIÓN DE INSTRUCCIONES ---
st.sidebar.info("Este programa ahora vincula cada subescala a su dimensión correspondiente según el manual de Moos.")
