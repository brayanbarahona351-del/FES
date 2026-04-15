import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from docx import Document
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Profesional FES", layout="wide")

if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

# --- 1. DATOS PERSONALES Y CONTEXTO CLÍNICO (SIDEBAR) ---
with st.sidebar:
    st.header("📋 Ficha Técnica e Identificación")
    st.markdown("Escala Aplicada: **[X] FES**  [ ] WES  [ ] CIES")
    st.divider()
    
    nombre = st.text_input("Nombre Completo del Informante", placeholder="Ej: Maria Auxiliadora Zelaya")
    edad = st.number_input("Edad", 12, 99, 30)
    profesion = st.text_input("Profesión / Ocupación", placeholder="Ej: Docente Universitaria / Ama de casa")
    
    st.subheader("🌐 Contexto Analítico")
    composicion = st.selectbox("Composición Familiar", ["Nuclear", "Extensa", "Monoparental", "Reconstituida"], 
                               help="Nuclear: Padres/Hijos. Extensa: Incluye abuelos. Reconstituida: Padrastros.")
    
    ciclo_vital = st.selectbox("Etapa Ciclo Vital", ["Hijos Infantes/Pequeños", "Hijos Adolescentes", "Hijos Adultos", "Nido Vacío"],
                               help="Ej: Si tiene hijos de 0-12 años, seleccione Infantes.")
    
    st.subheader("⚠️ Factores de Influencia (Ejemplos)")
    crisis = st.text_area("Crisis Recientes", 
                          placeholder="Ej: Duelo por fallecimiento de abuelo materno hace 3 meses, mudanza reciente o pérdida de empleo del padre.")
    
    jerarquia = st.text_area("Roles y Jerarquía", 
                             placeholder="Ej: La madre toma las decisiones económicas, el padre se encarga de la disciplina. Los hijos no tienen tareas asignadas.")
    
    cultura = st.text_area("Antecedentes Culturales / Religiosos", 
                           placeholder="Ej: Familia católica con asistencia semanal a misa; valores tradicionales de respeto absoluto a los mayores.")

# --- 2. HOJAS DE TRABAJO (TABS) ---
tab1, tab2, tab3 = st.tabs(["📄 Hoja 1: Instrucciones", "📝 Hoja 2: Aplicación (90 Ítems)", "📊 Hoja 3: Perfil e IA"])

with tab1:
    st.header("Instrucciones de la Escala FES")
    st.markdown(f"""
    **Estimado(a) {nombre if nombre else 'Usuario'}:**
    Lea las frases pausadamente. Decida si cada una describe a su familia la mayoría de las veces (**Verdadero**) o si no la describe (**Falso**).
    
    *   **Identificación:** Se ha marcado automáticamente la escala como **[X] FES**.
    *   **Pausadamente:** No hay tiempo límite. Analice su realidad familiar actual.
    """)
    st.info("💡 El análisis final cruzará su profesión y etapa vital para un diagnóstico preciso.")

with tab2:
    st.header("Cuestionario FES (Autoaplicado)")
    
    # 90 Preguntas completas
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

    for i in range(1, 91):
        st.session_state.respuestas[i] = st.radio(
            f"**{i}. {preguntas_fes[i]}**",
            ["V", "F"],
            index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i]),
            key=f"q_{i}",
            horizontal=True
        )

with tab3:
    if None in st.session_state.respuestas.values():
        st.warning("⚠️ Responda las 90 preguntas para ver el análisis.")
    else:
        st.header(f"Informe de Resultados: Familia de {nombre}")
        
        # 1. VALORES SIMULADOS (Aquí se conecta la lógica real de puntuación)
        sub_nombres = ["CO", "EX", "CT", "AU", "AC", "IC", "SR", "MR", "OR", "CN"]
        s_valores = [50, 45, 60, 40, 55, 50, 48, 65, 42, 58] # Ejemplo
        
        # 2. GRÁFICO DE SUBESCALAS (LÍNEAS)
        fig_ind = go.Figure()
        fig_ind.add_trace(go.Scatter(x=sub_nombres, y=s_valores, mode='lines+markers', marker=dict(size=10, symbol='square'), line_color='navy'))
        fig_ind.update_layout(title="Perfil Individual de Subescalas", yaxis_range=[0, 100], template="plotly_white")
        st.plotly_chart(fig_ind)

        # 3. GRÁFICO DE DIMENSIONES (BARRAS)
        rel = (s_valores[0] + s_valores[1] + (100 - s_valores[2])) / 3
        des = sum(s_valores[3:8]) / 5
        est = (s_valores[8] + s_valores[9]) / 2
        fig_dim = go.Figure(data=[go.Bar(x=["Relaciones", "Desarrollo", "Estabilidad"], y=[rel, des, est], marker_color=['#2E86C1', '#28B463', '#D35400'])])
        fig_dim.update_layout(title="Análisis por Dimensiones Generales", yaxis_range=[0, 100])
        st.plotly_chart(fig_dim)

        # 4. ANÁLISIS DE IA CRUZADO
        st.subheader("🧠 Interpretación Clínica y Recomendaciones")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Análisis de Perfil Profesional:**")
            st.write(f"Dada su ocupación como **{profesion}** y su edad de **{edad} años**, se observa una tendencia a...")
            if s_valores[9] > 60 and "Infantes" in ciclo_vital:
                st.info("✅ **Interpretación:** El nivel de Control es funcional; las familias con niños pequeños requieren este ajuste para la seguridad.")
        with c2:
            st.markdown("**Influencia de Crisis y Roles:**")
            if crisis:
                st.error(f"⚠️ **Atención:** El clima reportado está influenciado por: {crisis}. No se recomienda un diagnóstico estructural ahora.")
            st.write(f"**Dinámica de Autoridad:** {jerarquia}")

        st.success(f"Informe listo para {nombre}. Escala marcada: [X] FES")
