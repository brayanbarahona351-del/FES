import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# --- CONFIGURACIÓN DE LA SUITE CLÍNICA ---
st.set_page_config(page_title="FES de Moos - Suite Profesional Honduras", layout="wide")

# --- ESTILO VISUAL PROFESIONAL ---
st.markdown("""
    <style>
    .header-style { background-color: #E67E22; color: white; padding: 30px; text-align: center; border-radius: 15px; font-family: 'Arial Black'; margin-bottom: 25px; }
    .card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 8px solid #E67E22; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS: 90 PREGUNTAS LITERALES DEL MANUAL ---
# (Texto, Subescala, Clave de puntuación)
BANCO_PREGUNTAS = {
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

# --- ESTRUCTURA DE DIMENSIONES Y DESCRIPCIONES (ESTILO IMAGEN) ---
JERARQUIA = {
    "1. Relaciones": {
        "CO": ("Cohesión", "Grado en que los miembros están unidos y se apoyan."),
        "EX": ("Expresividad", "Grado en que se permite y anima a actuar libremente y a expresar sentimientos."),
        "CT": ("Conflicto", "Grado de expresión abierta de ira y agresividad.")
    },
    "2. Desarrollo (Crecimiento personal)": {
        "AU": ("Autonomía", "Independencia de los miembros para tomar sus propias decisiones."),
        "AC": ("Actuación", "Importancia que se da al éxito y a la competitividad."),
        "IC": ("Intelectual-Cultural", "Interés por actividades culturales, políticas e intelectuales."),
        "SR": ("Social-Recreativo", "Participación en actividades de ocio y sociales fuera de casa."),
        "MR": ("Moralidad-Religiosidad", "Importancia de los valores éticos y religiosos.")
    },
    "3. Estabilidad (Sistema de mantenimiento)": {
        "OR": ("Organización", "Importancia del orden y la planificación en las tareas domésticas."),
        "CN": ("Control", "Grado en que la dirección de la vida familiar se atiene a reglas fijas.")
    }
}

# --- LÓGICA DE CALIFICACIÓN Y ANÁLISIS ---
def calcular_resultados(respuestas):
    directos = {s: 0 for s in ["CO", "EX", "CT", "AU", "AC", "IC", "SR", "MR", "OR", "CN"]}
    for i, res in respuestas.items():
        if res == BANCO_PREGUNTAS[i]: directos[BANCO_PREGUNTAS[i]] += 1
    # Baremación T (Media 50)
    t_scores = {k: (v * 5 + 30) for k, v in directos.items()}
    return t_scores

def nivel_cualitativo(val):
    if val >= 70: return "Muy Alta"
    if val >= 60: return "Alta"
    if val >= 40: return "Media"
    if val >= 30: return "Baja"
    return "Muy Baja"

# --- INTERFAZ ---
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

tab1, tab2, tab3 = st.tabs(["🏠 DATOS PERSONALES", "📝 CUESTIONARIO LITERAL", "📊 INFORME INTEGRAL"])

with tab1:
    st.markdown('<div class="header-style"><h1>FES DE MOOS</h1><h3>Sistema de Evaluación Familiar Honduras</h3></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("👤 NOMBRE COMPLETO", "Barayan Adan Barahona Marquez")
        edad = st.number_input("📅 EDAD", 1, 100, 20)
        sexo = st.selectbox("🚻 SEXO", ["Masculino", "Femenino", "Otro"])
        ocupacion = st.text_input("💼 PROFESIÓN", "Policia")
    with c2:
        grado = st.text_input("🎓 GRADO", "Bachiller")
        examinador = st.text_input("🩺 EXAMINADOR", "Lic. en Psicología")
        fecha = st.date_input("📆 FECHA")
        lugar = st.text_input("📍 LUGAR", "Honduras")

with tab2:
    st.header("📝 Aplicación: 90 Frases Literales")
    for i, (txt, sub, clv) in BANCO_PREGUNTAS.items():
        st.session_state.respuestas[i] = st.radio(f"**{i}.** {txt}", ["V", "F"], key=f"q{i}", horizontal=True, index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i]))
        st.divider()

with tab3:
    if None in st.session_state.respuestas.values():
        st.warning("⚠️ Complete las 90 preguntas para generar el informe completo.")
    else:
        scores = calcular_resultados(st.session_state.respuestas)
        
        # --- GRÁFICO GLOBAL INTEGRADO ---
        st.header("📊 Perfil General de Subescalas")
        names, vals, colors = [], [], []
        color_map = {"1. Relaciones": "#2E86C1", "2. Desarrollo (Crecimiento personal)": "#28B463", "3. Estabilidad (Sistema de mantenimiento)": "#CB4335"}
        
        for dim, subs in JERARQUIA.items():
            for sigla, (name, d) in subs.items():
                names.append(name); vals.append(scores[sigla]); colors.append(color_map[dim])

        fig_global = go.Figure(data=[go.Bar(x=names, y=vals, marker_color=colors)])
        fig_global.update_layout(yaxis_range=, title="Interpretación del Perfil General")
        st.plotly_chart(fig_global, use_container_width=True)

        # --- ANÁLISIS DETALLADO (ESTILO IMAGEN) ---
        st.header("🧠 Resumen de Puntuaciones e Interpretación")
        for dim, subs in JERARQUIA.items():
            with st.container():
                st.markdown(f"### 🔹 {dim}")
                for sigla, (n_full, desc) in subs.items():
                    niv = nivel_cualitativo(scores[sigla])
                    st.write(f"**{n_full} ({scores[sigla]}/100):** {niv}. {desc}")

        # --- MOTIVOS, CAUSAS Y PLAN ---
        st.divider()
        st.header("📋 Análisis de Situaciones Problema y Plan")
        c_a, c_b = st.columns(2)
        with c_a:
            st.subheader("🚩 Motivos y Causas")
            if scores["CT"] > 60:
                st.write("**Conflictividad Alta:** Sucede debido a fallas en la regulación emocional y modelos de resolución de problemas basados en la confrontación.")
            if scores["CN"] > 60:
                st.write("**Control Rígido:** Sucede por una necesidad parental de predictibilidad ante el miedo al desorden o conductas disruptivas.")
        with c_b:
            st.subheader("🛠️ Plan Terapéutico")
            st.write("1. **Tarea:** Cenas familiares sin dispositivos para elevar la Cohesión.")
            st.write("2. **Tarea:** Entrenamiento en resolución asertiva de conflictos.")

        # --- GENERACIÓN DE WORD (IMPRESIÓN COMPLETA) ---
        doc = Document()
        doc.add_heading('REPORTE CLÍNICO INTEGRAL - FES DE MOOS', 0)
        
        # 1. Ficha Técnica
        doc.add_heading('I. Datos del Examinado', level=1)
        doc.add_paragraph(f"Nombre: {nombre}\nEdad: {edad}\nLugar: {lugar}\nEvaluador: {examinador}")

        # 2. Gráfico
        plt.figure(figsize=(12, 6))
        plt.bar(names, vals, color=colors)
        plt.xticks(rotation=45, ha='right'); plt.ylim(0, 100); plt.axhline(y=50, color='r', ls='--')
        plt.title("Perfil Gráfico de Subescalas")
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png', bbox_inches='tight'); img_buf.seek(0)
        doc.add_picture(img_buf, width=Inches(6))

        # 3. Hoja de Preguntas y Respuestas
        doc.add_page_break()
        doc.add_heading('II. Hoja de Preguntas y Respuestas Literales', level=1)
        for i, r in st.session_state.respuestas.items():
            doc.add_paragraph(f"{i}. {BANCO_PREGUNTAS[i]} -> RESPUESTA: {r}")

        # 4. Análisis Estilo Imagen
        doc.add_page_break()
        doc.add_heading('III. Resumen de Puntuaciones e Interpretación', level=1)
        for dim, subs in JERARQUIA.items():
            doc.add_heading(dim, level=2)
            for sigla, (n_full, desc) in subs.items():
                niv = nivel_cualitativo(scores[sigla])
                p = doc.add_paragraph(style='List Bullet')
                p.add_run(f"{n_full}: ").bold = True
                p.add_run(f"{niv}. {desc} (Puntaje T: {scores[sigla]})")

        # 5. Análisis Clínico y Plan
        doc.add_heading('IV. Diagnóstico, Causas y Plan Terapéutico', level=1)
        doc.add_paragraph(f"Motivos y Causas: Se identifica una dinámica familiar donde los puntajes indican...")
        doc.add_paragraph("Tareas sugeridas: Reestructuración de roles y fomento de la expresividad.")

        out = BytesIO()
        doc.save(out)
        st.download_button("📥 DESCARGAR INFORME COMPLETO (WORD)", out.getvalue(), f"Informe_FES_{nombre}.docx")
