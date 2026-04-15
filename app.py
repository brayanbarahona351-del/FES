import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from docx import Document
from io import BytesIO

# --- 1. CONFIGURACIÓN DE PÁGINA Y SESIÓN ---
st.set_page_config(page_title="Evaluación Profesional FES", layout="wide")

if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

# --- 2. HOJA DE DATOS PERSONALES Y CONTEXTO ---
with st.sidebar:
    st.header("📋 Ficha de Identificación")
    st.markdown("Marque la escala aplicada: **[X] FES** [ ] WES [ ] CIES [ ] CES")
    
    nombre = st.text_input("Apellidos de la Familia / Paciente")
    composicion = st.selectbox("Composición Familiar", ["Nuclear", "Extensa", "Monoparental", "Reconstituida", "Otra"])
    ciclo_vital = st.selectbox("Ciclo Vital", ["Hijos pequeños", "Adolescentes", "Hijos adultos", "Nido vacío", "Adultos mayores"])
    estrato = st.selectbox("Nivel Socioeconómico", ["Bajo", "Medio-Bajo", "Medio", "Alto"])
    crisis = st.text_area("Situaciones de crisis actuales (Duelos, mudanzas, etc.)")
    roles = st.text_area("Roles y Jerarquías (¿Quién manda?, ¿Cómo se dividen las tareas?)")
    cultura = st.text_area("Antecedentes Culturales / Religiosos")

# --- 3. PESTAÑAS DE TRABAJO (Hojas de Excel) ---
tab1, tab2, tab3 = st.tabs(["📄 Instrucciones", "📝 Aplicación", "📊 Resultados & Perfil Individual"])

with tab1:
    st.subheader("Instrucciones de la Prueba")
    st.write("Se debe llenar pausadamente. Piense en su familia tal como es en la actualidad.")
    st.info("Esta escala evalúa tres dimensiones: Relaciones, Desarrollo y Estabilidad.")

with tab2:
    st.header("Cuestionario FES")
    # (Aquí van los radios de los 90 ítems igual que en el código anterior)
    # Por brevedad, simulamos la respuesta final:
    if st.button("Finalizar Aplicación"):
        st.session_state.finalizado = True

with tab3:
    # --- CÁLCULO Y GRÁFICOS ---
    # Simulación de puntajes directos (PD) y típicos (S)
    subescalas = ["CO", "EX", "CT", "AU", "AC", "IC", "SR", "MR", "OR", "CN"]
    s_scores = {s: 50 for s in subescalas} # Aquí iría tu lógica de cálculo real

    # Agrupación por Dimensiones
    dimensiones = {
        "Relaciones": (s_scores["CO"] + s_scores["EX"] + (100 - s_scores["CT"])) / 3,
        "Desarrollo": (s_scores["AU"] + s_scores["AC"] + s_scores["IC"] + s_scores["SR"] + s_scores["MR"]) / 5,
        "Estabilidad": (s_scores["OR"] + s_scores["CN"]) / 2
    }

    # GRÁFICO 1: Perfil Individual de Subescalas
    fig_sub = go.Figure(data=go.Scatter(x=subescalas, y=list(s_scores.values()), mode='lines+markers', name="Subescalas"))
    fig_sub.update_layout(title="Perfil Individual FES (10 Subescalas)", yaxis_range=[0, 100])
    st.plotly_chart(fig_sub)

    # GRÁFICO 2: Perfil por Dimensiones
    fig_dim = go.Figure(data=go.Bar(x=list(dimensiones.keys()), y=list(dimensiones.values()), marker_color='teal'))
    fig_dim.update_layout(title="Interpretación por Dimensiones", yaxis_range=[0, 100])
    st.plotly_chart(fig_dim)

    # --- ANÁLISIS CUALITATIVO CRUZADO (IA) ---
    st.subheader("🧠 Interpretación Contextualizada (IA)")
    
    contexto = f"Familia {composicion} con {ciclo_vital}."
    if s_scores["CN"] > 60 and ciclo_vital == "Hijos pequeños":
        st.write(f"**Análisis:** El alto control detectado es coherente con la etapa de {ciclo_vital}, donde la supervisión es necesaria.")
    else:
        st.write(f"**Análisis:** Se observa una configuración familiar que debe evaluarse bajo el prisma de {crisis if crisis else 'su estabilidad actual'}.")

    st.write(f"**Roles:** {roles}")
