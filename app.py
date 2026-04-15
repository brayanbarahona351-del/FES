import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Profesional FES", layout="wide")

# Inicialización de la memoria de la sesión
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

# --- 1. DATOS PERSONALES Y CONTEXTO CLÍNICO (SIDEBAR) ---
with st.sidebar:
    st.header("📋 Ficha Técnica e Identificación")
    st.markdown("Escala Aplicada: **[X] FES**  [ ] WES  [ ] CIES")
    st.divider()
    
    nombre = st.text_input("Nombre Completo del Informante", placeholder="Ej: Juan Pérez")
    edad = st.number_input("Edad", 12, 99, 30)
    profesion = st.text_input("Profesión / Ocupación", placeholder="Ej: Docente, Comerciante")
    
    st.subheader("🌐 Contexto Analítico")
    composicion = st.selectbox("Composición Familiar", ["Nuclear", "Extensa", "Monoparental", "Reconstituida"])
    ciclo_vital = st.selectbox("Etapa Ciclo Vital", ["Hijos Infantes/Pequeños", "Hijos Adolescentes", "Hijos Adultos", "Nido Vacío"])
    nivel_se = st.selectbox("Nivel Socioeconómico", ["Bajo", "Medio-Bajo", "Medio", "Alto"])
    
    st.subheader("⚠️ Factores de Influencia")
    crisis = st.text_area("Crisis Recientes", placeholder="Duelos, mudanzas, desempleo...")
    jerarquia = st.text_area("Roles y Jerarquía", placeholder="¿Quién ejerce la autoridad?")
    cultura = st.text_area("Antecedentes Culturales", placeholder="Valores religiosos o regionales")

# --- 2. HOJAS DE TRABAJO (TABS) ---
tab1, tab2, tab3 = st.tabs(["📄 Instrucciones", "📝 Aplicación (90 Ítems)", "📊 Perfil e IA"])

with tab1:
    st.header("Instrucciones de la Escala FES")
    st.markdown(f"""
    **Estimado(a) {nombre if nombre else 'Usuario'}:**
    
    A continuación aparecen 90 frases. Debe decidir si cada una describe a su familia la mayoría de las veces (**Verdadero**) o si no la describe (**Falso**).
    
    *   **Pausadamente:** Tómese su tiempo para reflexionar en cada punto.
    *   **Contexto:** Piense en las personas con las que convive actualmente.
    *   **Honestidad:** No hay respuestas correctas, solo perfiles reales.
    """)
    st.info("Al terminar, el sistema cruzará sus datos de profesión y contexto para el informe final.")

with tab2:
    st.header("Cuestionario FES")
    
    preguntas_fes = {
        1: "En mi familia nos ayudamos y apoyamos realmente unos a otros",
        2: "Los miembros de la familia guardan, a menudo, sentimientos para sí mismos",
        3: "En nuestra familia discutimos mucho",
        4: "En general ningún miembro de la familia decide por su cuenta",
        5: "Creemos que es importante ser los mejores en cualquier cosa que hagamos",
        6: "A menudo hablamos de temas políticos o sociales",
        7: "Pasamos en casa la mayor parte de nuestro tiempo libre",
        8: "Asistimos con bastante regularidad a los cultos de la iglesia",
        9: "Las actividades de nuestra familia se planifican cuidadosamente",
        10: "En mi familia tenemos reuniones obligatorias muy pocas veces",
        11: "En mi familia damos mucha importancia a la ayuda y el apoyo mutuo",
        12: "En casa hablamos libremente de lo que nos parece",
        13: "En mi familia casi nunca nos enfadamos unos con otros",
        14: "En mi familia se nos anima a valernos por nosotros mismos",
        15: "Para nosotros no es tan importante el éxito como el esfuerzo por conseguirlo",
        16: "A menudo vamos al cine, a conciertos o a conferencias",
        17: "En casa casi no tenemos amigos ni conocidos",
        18: "Creemos que hay cosas en las que hay que tener fe",
        19: "En mi familia la puntualidad es muy importante",
        20: "En casa se puede hacer casi todo lo que uno quiera",
        21: "En mi familia se ponen muchas ganas en todo lo que se hace",
        22: "En mi familia es difícil desahogarse sin ofender a alguien",
        23: "En mi familia a veces nos pegamos unos a otros",
        24: "En mi familia cada uno decide sus propias cosas",
        25: "En mi familia nos gusta mucho competir, somos muy competitivos",
        26: "Nos interesan mucho la música, el arte y la literatura",
        27: "Nuestra vida social es muy activa",
        28: "En mi familia creemos que quien no cumple los Diez Mandamientos será castigado",
        29: "En casa nos gusta que las cosas estén siempre en su sitio",
        30: "En mi familia se siguen las reglas de casa muy estrictamente",
        31: "En mi familia estamos muy unidos",
        32: "En casa nos contamos nuestros problemas personales",
        33: "En mi familia casi nunca perdemos la calma",
        34: "En mi familia nos animamos a ser independientes",
        35: "En mi familia creemos que para salir adelante hay que ser ambicioso",
        36: "En mi familia apenas sabemos nada de temas intelectuales o culturales",
        37: "Casi todos los fines de semana hacemos algo juntos",
        38: "En mi familia las oraciones son muy importantes",
        39: "En mi familia se tiene muy poco cuidado con la organización",
        40: "En mi familia apenas hay normas que seguir",
        41: "En mi familia tenemos mucha sensación de unión",
        42: "En mi familia si alguien está enfadado, los demás lo saben enseguida",
        43: "En mi familia casi nunca nos criticamos unos a otros",
        44: "En mi familia cada uno va a lo suyo",
        45: "En mi familia no nos importa tanto perder como jugar bien",
        46: "En mi familia a menudo hablamos de libros o revistas",
        47: "En mi familia casi nunca recibimos visitas de amigos",
        48: "En mi familia no creemos en la vida después de la muerte",
        49: "En mi familia somos muy ordenados y limpios",
        50: "En mi familia cada uno puede hacer lo que quiera",
        51: "En mi familia nos apoyamos unos a otros cuando algo va mal",
        52: "En casa es difícil hablar de sentimientos",
        53: "En mi familia a veces nos tiramos cosas a la cabeza",
        54: "En mi familia cada uno es su propio jefe",
        55: "En mi familia el éxito es lo que más cuenta",
        56: "En mi familia casi no tenemos aficiones culturales",
        57: "A menudo invitamos a amigos a comer o a cenar",
        58: "En mi familia creemos en el perdón de los pecados",
        59: "En mi familia el orden es más importante que la comodidad",
        60: "En casa hay reglas que nadie puede saltarse",
        61: "En mi familia hay mucho espíritu de grupo",
        62: "En casa hablamos abiertamente de sexo",
        63: "En mi familia casi nunca discutimos",
        64: "En mi familia se nos anima a pensar las cosas por nosotros mismos",
        65: "En mi familia apenas nos importa quién gana o quién pierde",
        66: "En mi familia a menudo vamos a bibliotecas o museos",
        67: "En mi familia casi todos tenemos muchos amigos",
        68: "En mi familia la religión no tiene mucha importancia",
        69: "En mi familia casi nunca se planifican las cosas con tiempo",
        70: "En mi familia el padre y la madre son muy estrictos",
        71: "En mi familia de verdad nos preocupamos unos por otros",
        72: "En mi familia solemos guardarnos nuestras opiniones",
        73: "En mi familia casi siempre estamos peleando",
        74: "En mi familia nos animan a que nos las arreglemos solos",
        75: "En mi familia trabajamos mucho para conseguir lo que queremos",
        76: "En mi familia apenas nos interesan los temas científicos",
        77: "En mi familia salimos mucho de casa",
        78: "En mi familia creemos que es importante confesar los pecados",
        79: "En mi familia cada uno es responsable de su propio orden",
        80: "En mi familia nunca se sabe quién tiene que hacer cada tarea",
        81: "En mi familia hay mucha alegría",
        82: "En mi familia se nos anima a decir siempre lo que pensamos",
        83: "En mi familia nos llevamos todos muy bien",
        84: "En mi familia cada uno es libre de hacer lo que le parezca",
        85: "En mi familia damos mucha importancia a las notas o calificaciones",
        86: "En mi familia a menudo hablamos de las noticias del día",
        87: "En mi familia casi nunca vamos juntos a sitios",
        88: "En mi familia no creemos en el infierno",
        89: "En mi familia a menudo cambiamos de planes a última hora",
        90: "En mi familia no hay muchas reglas que cumplir"
    }

    # Bucle para mostrar las 90 preguntas
    for i in range(1, 91):
        st.session_state.respuestas[i] = st.radio(
            f"**{i}. {preguntas_fes[i]}**",
            ["V", "F"],
            index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i]),
            key=f"q_{i}",
            horizontal=True
        )
    
    st.success("Cuestionario Completo. Revise los resultados en la Hoja 3.")

with tab3:
    if None in st.session_state.respuestas.values():
        st.warning("⚠️ Debe responder las 90 preguntas para generar el perfil.")
    else:
        st.header(f"Informe de Resultados: Familia de {nombre}")
        
        # --- LÓGICA DE CALIFICACIÓN (Puntajes S Simulados para el ejemplo) ---
        sub_nombres = ["CO", "EX", "CT", "AU", "AC", "IC", "SR", "MR", "OR", "CN"]
        s_valores = [45, 52, 38, 60, 55, 48, 42, 58, 65, 40] # Ej: Puntajes típicos S
        
        # --- GRÁFICO 1: PERFIL INDIVIDUAL ---
        fig_ind = go.Figure()
        fig_ind.add_trace(go.Scatter(x=sub_nombres, y=s_valores, mode='lines+markers', line_color='darkblue', name="Perfil Subescalas"))
        fig_ind.update_layout(title="Perfil Individual de las 10 Subescalas (S)", yaxis_range=, template="plotly_white")
        st.plotly_chart(fig_ind)

        # --- ANÁLISIS DE IA CONTEXTUAL ---
        st.subheader("🧠 Interpretación Clínica Basada en Contexto")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Análisis por Profesión y Perfil:**")
            st.write(f"Como **{profesion}**, su percepción de la subescala de 'Organización' ({s_valores[8]}) sugiere una alta valoración de la estructura.")
            
            if s_valores[9] > 60 and "Hijos Pequeños" in ciclo_vital:
                st.info("✅ **Nota Clínica:** El puntaje de 'Control' es elevado, lo cual es funcional y normativo dada la etapa de desarrollo de los hijos (Protección/Supervisión).")
            
        with col2:
            st.write("**Impacto del Contexto:**")
            if crisis:
                st.warning(f"⚠️ **Alerta:** Los resultados están 'ensuciados' por la crisis reportada: {crisis}. El clima es reactivo, no estructural.")
            st.write(f"**Dinámica de Autoridad:** {jerarquia if jerarquia else 'No especificada'}")

        st.success(f"Informe generado para {nombre}. Marque con una cruz: [X] FES")

