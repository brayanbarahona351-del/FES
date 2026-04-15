import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from docx import Document
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema FES Profesional", layout="wide")

# Inicialización de sesión
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

# --- 1. DATOS PERSONALES Y CONTEXTO (SIDEBAR) ---
with st.sidebar:
    st.header("📋 Ficha Técnica e Identificación")
    st.markdown("Escala Aplicada: **[X] FES**  [ ] WES  [ ] CIES  [ ] CES")
    st.divider()
    
    # Datos básicos
    nombre = st.text_input("Nombre Completo del Informante")
    edad = st.number_input("Edad", 12, 99, 25)
    profesion = st.text_input("Profesión / Ocupación")
    
    st.subheader("🌐 Contexto Demográfico y Familiar")
    
    composicion = st.selectbox("Composición Familiar", 
        ["Nuclear (Padres e hijos)", "Extensa (Incluye abuelos/tíos)", "Monoparental (Un solo padre)", "Reconstituida (Padrastros/Madastras)"],
        help="Ejemplo: Nuclear si solo viven padres e hijos.")
    
    ciclo_vital = st.selectbox("Etapa del Ciclo Vital", 
        ["Hijos Pequeños (0-12 años)", "Hijos Adolescentes", "Hijos Adultos", "Nido Vacío / Adultos Mayores"],
        help="Crucial para analizar Autonomía y Control.")
    
    nivel_se = st.selectbox("Nivel Socioeconómico y Educativo", 
        ["Bajo (Básica)", "Medio (Secundaria/Técnica)", "Alto (Universitaria/Posgrado)"],
        help="Influye en las escalas Intelectual-Cultural y Actuación.")
    
    crisis = st.text_area("Situaciones de Crisis / Eventos Recientes", 
        placeholder="Ejemplo: Duelo reciente (6 meses), mudanza, pérdida de empleo, enfermedad crónica en un miembro.")
    
    jerarquia = st.text_area("Roles y Jerarquías", 
        placeholder="Ejemplo: La madre ejerce la autoridad económica, el padre la disciplina; tareas divididas equitativamente.")
    
    cultura = st.text_area("Antecedentes Culturales / Religiosos", 
        placeholder="Ejemplo: Familia con fuertes valores religiosos católicos; tradición de cena dominical obligatoria.")

# --- 2. ESTRUCTURA DE PESTAÑAS (HOJAS) ---
tab1, tab2, tab3 = st.tabs(["📄 Hoja 1: Instrucciones", "📝 Hoja 2: Aplicación (Preguntas)", "📊 Hoja 3: Resultados e IA"])

with tab1:
    st.header("Instrucciones de la Escala FES")
    st.markdown(f"""
    **Estimado(a) {nombre if nombre else 'evaluado'}:**
    
    Lea las frases que aparecerán en la siguiente pestaña. Marque **Verdadero (V)** si la frase describe a su familia la mayoría de las veces, o **Falso (F)** si no es así. 
    
    *   Conteste pausadamente.
    *   No hay respuestas correctas ni incorrectas.
    *   **Importante:** Responda pensando en su familia *actual* y las personas con las que convive.
    """)

with tab2:
    st.header("Cuestionario Autoaplicado")
    st.info("Asegúrese de responder todas las preguntas para obtener el perfil.")
    
    # LISTA DE PREGUNTAS (Ejemplo de las primeras 10, completar hasta 90)
    preguntas_texto = {
        1: "En mi familia nos ayudamos y apoyamos realmente unos a otros.",
        2: "Los miembros de la familia guardan, a menudo, sentimientos para sí mismos.",
        3: "En nuestra familia discutimos mucho.",
        4: "En general ningún miembro de la familia decide por su cuenta.",
        5: "Creemos que es importante ser los mejores en cualquier cosa que hagamos.",
        6: "A menudo hablamos de temas políticos o sociales.",
        7: "Pasamos en casa la mayor parte de nuestro tiempo libre.",
        8: "Asistimos con bastante regularidad a los cultos de la iglesia.",
        9: "Las actividades de nuestra familia se planifican cuidadosamente.",
        10: "En mi familia tenemos reuniones obligatorias muy pocas veces."
    }
    
    # Renderizado de preguntas
    for i in range(1, 11): # Cambiar a 91 cuando tengas todos los textos
        st.session_state.respuestas[i] = st.radio(
            f"**{i}. {preguntas_texto.get(i, 'Frase del manual...')}**",
            ["V", "F"],
            index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i]),
            key=f"p_{i}",
            horizontal=True
        )
    
    if st.button("Finalizar y Procesar Perfil"):
        st.success("Respuestas guardadas. Pase a la Hoja 3.")

with tab3:
    st.header("Informe de Resultados y Análisis Contextual")
    
    # Simulación de puntajes para la gráfica
    sub_nombres = ["CO", "EX", "CT", "AU", "AC", "IC", "SR", "MR", "OR", "CN"]
    pd_valores = [7, 5, 3, 6, 8, 4, 5, 9, 6, 4] # Valores de ejemplo
    s_valores = [v * 5 + 20 for v in pd_valores] # Conversión ejemplo a S
    
    # --- GRÁFICO 1: PERFIL INDIVIDUAL (SUBESCALAS) ---
    fig_sub = go.Figure()
    fig_sub.add_trace(go.Scatter(x=sub_nombres, y=s_valores, mode='lines+markers', line=dict(color='blue', width=2), name="Perfil Subescalas"))
    fig_sub.update_layout(title="Perfil Individual FES (10 Subescalas)", yaxis_range=[0, 100], template="plotly_white")
    st.plotly_chart(fig_sub)
    
    # --- GRÁFICO 2: DIMENSIONES ---
    dim_nombres = ["Relaciones", "Desarrollo", "Estabilidad"]
    dim_valores = [55, 48, 62] # Ejemplo
    fig_dim = go.Figure(go.Bar(x=dim_nombres, y=dim_valores, marker_color=['#2E86C1', '#28B463', '#D35400']))
    fig_dim.update_layout(title="Interpretación por Dimensiones", yaxis_range=[0, 100])
    st.plotly_chart(fig_dim)

    # --- ANÁLISIS DE IA CRUZADO ---
    st.subheader("🧠 Análisis Interpretativo de la IA")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"**Análisis de Perfil:**")
        st.write(f"El informante ({nombre}), de profesión {profesion}, describe un clima familiar con...")
        if s_valores[9] > 60 and "Hijos Pequeños" in ciclo_vital:
            st.info("Nota Clínica: El puntaje alto en Control es normal debido a la etapa de Hijos Pequeños.")
    
    with col_b:
        st.write("**Factores de Riesgo/Protección:**")
        if crisis:
            st.warning(f"Atención: Los resultados están influenciados por: {crisis}")

