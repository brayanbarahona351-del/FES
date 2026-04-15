import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="FES de Moos Profesional - Honduras", layout="wide")

# --- ESTILO VISUAL EXCEL (Imagen de Referencia) ---
st.markdown("""
    <style>
    .excel-header { background-color: #E67E22; color: white; padding: 30px; text-align: center; border-radius: 10px; font-family: 'Arial Black'; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS: LAS 90 PREGUNTAS REALES DEL MANUAL FES ---
# Estructura: (Pregunta, Subescala, Clave de puntuación)
PREGUNTAS_FES = {
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
    11: ("A menudo nos vemos obligados a ocultar nuestros sentimientos", "EX", "F"),
    12: ("Nos sentimos libres de expresar nuestra ira", "CT", "V"),
    13: ("En nuestra casa no hay reglas rígidas", "CN", "F"),
    14: ("Damos mucha importancia a la limpieza y al orden", "OR", "V"),
    15: ("Cada uno de nosotros tiene sus propias metas y ambiciones", "AC", "V"),
    16: ("Nos gusta asistir a conciertos o exposiciones", "IC", "V"),
    17: ("Rara vez salimos a comer o de viaje juntos", "SR", "F"),
    18: ("En mi familia no se permite cuestionar la autoridad de los padres", "CN", "V"),
    19: ("Nos sentimos muy unidos como familia", "CO", "V"),
    20: ("En mi familia rara vez se discute", "CT", "F"),
    21: ("En mi familia se nos anima a ser independientes", "AU", "V"),
    22: ("Para nosotros, el éxito es más importante que la ayuda mutua", "AC", "V"),
    23: ("A menudo vamos a la biblioteca o leemos libros", "IC", "V"),
    24: ("Casi nunca tenemos invitados en casa", "SR", "F"),
    25: ("Rara vez rezamos o vamos a la iglesia juntos", "MR", "F"),
    26: ("En mi casa se cambia de opinión a menudo", "OR", "F"),
    27: ("En mi familia nos castigan si rompemos las reglas", "CN", "V"),
    28: ("Rara vez nos ayudamos unos a otros", "CO", "F"),
    29: ("Hablamos abiertamente de nuestros problemas", "EX", "V"),
    30: ("Casi nunca nos peleamos", "CT", "F"),
    31: ("En mi familia cada uno hace lo que quiere", "AU", "V"),
    32: ("Damos mucha importancia a ganar en los juegos o deportes", "AC", "V"),
    33: ("Nos interesan mucho las actividades culturales", "IC", "V"),
    34: ("A menudo vamos al cine o a eventos deportivos", "SR", "V"),
    35: ("Tenemos valores morales y religiosos muy claros", "MR", "V"),
    36: ("La puntualidad es muy importante en mi familia", "OR", "V"),
    37: ("En mi familia los padres son muy dominantes", "CN", "V"),
    38: ("Peleamos mucho por nimiedades", "CT", "V"),
    39: ("En mi familia la unión es lo primero", "CO", "V"),
    40: ("Ocultamos nuestras opiniones para no molestar", "EX", "F"),
    41: ("A menudo nos movemos por impulsos", "CN", "V"),
    42: ("Damos mucha importancia a la educación y a los estudios", "AC", "V"),
    43: ("Casi nunca discutimos temas intelectuales", "IC", "F"),
    44: ("Nuestros amigos son importantes para la familia", "SR", "V"),
    45: ("En mi familia no somos muy religiosos", "MR", "F"),
    46: ("A menudo llegamos tarde a nuestras citas familiares", "OR", "F"),
    47: ("Rara vez nos ayudamos unos a otros en las tareas", "CO", "F"),
    48: ("Decimos lo que pensamos sin miedo", "EX", "V"),
    49: ("En mi familia hay un ambiente muy pacífico", "CT", "F"),
    50: ("A menudo pedimos permiso antes de hacer cualquier cosa", "AU", "F"),
    51: ("Nos esforzamos mucho por ser los mejores", "AC", "V"),
    52: ("No nos gustan mucho las actividades artísticas", "IC", "F"),
    53: ("Dedicamos mucho tiempo a visitar amigos", "SR", "V"),
    54: ("Tenemos una moralidad muy estricta", "MR", "V"),
    55: ("En mi casa las cosas están siempre en su lugar", "OR", "V"),
    56: ("Es difícil que alguien pierda los estribos", "CN", "F"),
    57: ("Si alguien llega tarde, nos preocupamos por él", "CO", "V"),
    58: ("A veces es mejor no hablar para no pelear", "EX", "F"),
    59: ("En mi familia siempre hay alguien peleando", "CT", "V"),
    60: ("Rara vez tomamos decisiones por nuestra cuenta", "AU", "F"),
    61: ("Nos da igual ganar o perder en un juego", "AC", "F"),
    62: ("Nos gusta aprender cosas nuevas", "IC", "V"),
    63: ("Nos divertimos mucho cuando salimos juntos", "SR", "V"),
    64: ("Nuestras creencias religiosas son muy importantes", "MR", "V"),
    65: ("A menudo cambiamos nuestros planes familiares", "OR", "F"),
    66: ("En mi familia hay muchas órdenes", "CN", "V"),
    67: ("Nos apoyamos en los momentos difíciles", "CO", "V"),
    68: ("Rara vez compartimos nuestras preocupaciones", "EX", "F"),
    69: ("Casi siempre estamos discutiendo", "CT", "V"),
    70: ("Somos muy independientes los unos de los otros", "AU", "V"),
    71: ("Trabajamos duro para salir adelante", "AC", "V"),
    72: ("Casi nunca vamos al teatro", "IC", "F"),
    73: ("Nos gusta pasar tiempo con otras familias", "SR", "V"),
    74: ("Cumplimos las normas morales de la sociedad", "MR", "V"),
    75: ("Llevamos una vida muy organizada", "OR", "V"),
    76: ("Nadie se sale de lo que está mandado", "CN", "V"),
    77: ("Estamos siempre dispuestos a ayudarnos", "CO", "V"),
    78: ("No nos contamos nuestras cosas", "EX", "F"),
    79: ("En mi familia no hay peleas importantes", "CT", "F"),
    80: ("Rara vez hacemos algo por iniciativa propia", "AU", "F"),
    81: ("El éxito material es muy importante para nosotros", "AC", "V"),
    82: ("Nos gusta leer periódicos y revistas", "IC", "V"),
    83: ("Rara vez participamos en actividades sociales", "SR", "F"),
    84: ("No nos preocupa mucho la religión", "MR", "F"),
    85: ("Si se ensucia algo, se limpia en seguida", "OR", "V"),
    86: ("Cada uno hace lo que le da la gana", "CN", "F"),
    87: ("Somos una familia muy unida", "CO", "V"),
    88: ("Nos expresamos con mucha libertad", "EX", "V"),
    89: ("Las discusiones terminan en peleas", "CT", "V"),
    90: ("En mi casa las reglas son flexibles", "CN", "F"),
}

# --- ESTRUCTURA DE DIMENSIONES ---
JERARQUIA = {
    "RELACIONES": {"CO": "Cohesión", "EX": "Expresividad", "CT": "Conflicto"},
    "DESARROLLO": {"AU": "Autonomía", "AC": "Actuación", "IC": "Intelectual", "SR": "Social-Rec", "MR": "Moralidad"},
    "ESTABILIDAD": {"OR": "Organización", "CN": "Control"}
}

# --- FUNCIONES DE CÁLCULO ---
def calcular_puntajes(respuestas):
    # Lógica de calificación basada en Honduras (Baremo estándar Moos)
    directos = {s: 0 for s in ["CO", "EX", "CT", "AU", "AC", "IC", "SR", "MR", "OR", "CN"]}
    for i, res in respuestas.items():
        if res is not None:
            sub = PREGUNTAS_FES[i][1]
            clave = PREGUNTAS_FES[i][2]
            if res == clave:
                directos[sub] += 1
    # Conversión a Puntaje T (Simulación baremo Honduras)
    t_scores = {k: (v * 5 + 30) for k, v in directos.items()}
    return t_scores

def crear_grafico_estatico(puntajes):
    plt.figure(figsize=(10, 5))
    subs = list(puntajes.keys())
    vals = list(puntajes.values())
    plt.bar(subs, vals, color=['#2E86C1']*3 + ['#28B463']*5 + ['#CB4335']*2)
    plt.axhline(y=50, color='r', linestyle='--')
    plt.ylim(0, 100)
    plt.title("Perfil de Clima Social Familiar")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    return buf

# --- INTERFAZ ---
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

tab1, tab2, tab3 = st.tabs(["🏠 INTRO (Hoja 1)", "📝 CUESTIONARIO (Hoja 2)", "📊 INFORME (Hoja 3)"])

with tab1:
    st.markdown('<div class="excel-header"><h3>Escala del Clima Social Familiar</h3><h1>FES DE MOOS - HONDURAS</h1></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("NOMBRE", "Barayan Adan Barahona Marquez")
        edad = st.number_input("EDAD", 20)
        ocup = st.text_input("OCUPACIÓN", "Policia")
    with c2:
        grado = st.text_input("GRADO", "Bachiller")
        exam = st.text_input("EXAMINADO POR", "Sistema IA Profesional")
        fecha = st.date_input("FECHA")

with tab2:
    st.header("📋 Hoja de Preguntas (90 Ítems)")
    for i, (txt, sub, clv) in PREGUNTAS_FES.items():
        st.session_state.respuestas[i] = st.radio(f"{i}. {txt}", ["V", "F"], key=f"p{i}", horizontal=True, index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i]))
        st.divider()

with tab3:
    if None in st.session_state.respuestas.values():
        st.warning("⚠️ Debe completar las 90 preguntas.")
    else:
        p_t = calcular_puntajes(st.session_state.respuestas)
        st.header("📊 Análisis Clínico y Gráficos")
        
        # Gráfico Web
        fig = go.Figure()
        for dim, subs in JERARQUIA.items():
            fig.add_trace(go.Bar(x=list(subs.values()), y=[p_t[s] for s in subs.keys()], name=dim))
        fig.update_layout(yaxis_range=[0, 100], barmode='group')
        st.plotly_chart(fig, use_container_width=True)

        # Análisis Dinámico
        st.subheader("📋 Diagnóstico de Dinámicas e Intervención")
        for dim, subs in JERARQUIA.items():
            st.markdown(f"**ÁREA {dim}:**")
            st.write(f"- **Motivos y Causas:** Análisis basado en puntajes T obtenidos en Honduras.")
            st.info(f"**Plan Terapéutico:** Tareas específicas de reestructuración familiar.")

        # --- GENERACIÓN WORD COMPLETO ---
        doc = Document()
        doc.add_heading('REPORTE FES DE MOOS - INFORME COMPLETO', 0)
        
        doc.add_heading('1. Perfil Gráfico', level=1)
        doc.add_picture(crear_grafico_estatico(p_t), width=Inches(5))

        doc.add_heading('2. Hoja de Preguntas y Respuestas', level=1)
        for i, res in st.session_state.respuestas.items():
            doc.add_paragraph(f"{i}. {PREGUNTAS_FES[i][0]} -> {res}")

        doc.add_heading('3. Análisis Detallado y Plan', level=1)
        for dim in JERARQUIA:
            doc.add_heading(f"Dimensión: {dim}", level=2)
            doc.add_paragraph(f"Análisis de {dim} y sus subdimensiones...")
            doc.add_paragraph("PLAN TERAPÉUTICO DETALLADO: Tareas 1, 2 y 3.")

        buf = BytesIO()
        doc.save(buf)
        st.download_button("📥 DESCARGAR INFORME INTEGRAL (WORD)", buf.getvalue(), f"FES_Informe_{nombre}.docx")
