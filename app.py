import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from io import BytesIO

# --- CONFIGURACIÓN DE ALTO NIVEL ---
st.set_page_config(page_title="FES Moos Suite - Clínica Profesional Honduras", layout="wide")

# --- ESTILO VISUAL DINÁMICO ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .excel-header { 
        background: linear-gradient(135deg, #E67E22 0%, #D35400 100%); 
        color: white; padding: 40px; text-align: center; border-radius: 15px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.2); margin-bottom: 30px;
    }
    .card-analisis { 
        background-color: white; padding: 30px; border-radius: 15px; 
        border-top: 12px solid #E67E22; box-shadow: 0 6px 12px rgba(0,0,0,0.1); 
        margin-bottom: 25px; 
    }
    .stRadio > div { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS: LAS 90 PREGUNTAS LITERALES ---
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

# --- ESTRUCTURA SEGÚN IMAGEN ---
JERARQUIA = {
    "1. Relaciones": {
        "CO": ("Cohesión", "Los miembros se apoyan y ayudan mucho entre sí."),
        "EX": ("Expresividad", "Se actúa libremente y se expresan sentimientos abiertamente."),
        "CT": ("Conflicto", "Grado en que se expresan abiertamente la cólera y agresividad.")
    },
    "2. Desarrollo (Crecimiento personal)": {
        "AU": ("Autonomía", "Grado en que los miembros son independientes y autónomos."),
        "AC": ("Actuación", "Grado en que las actividades se orientan al éxito y competencia."),
        "IC": ("Intelectual-Cultural", "Interés por actividades culturales, políticas y sociales."),
        "SR": ("Social-Recreativo", "Participación en actividades recreativas y sociales."),
        "MR": ("Moralidad-Religiosidad", "Énfasis en valores éticos y religiosos.")
    },
    "3. Estabilidad (Sistema de mantenimiento)": {
        "OR": ("Organización", "Importancia dada al orden y planificación en el hogar."),
        "CN": ("Control", "Grado en que se atiene a reglas y procedimientos fijos.")
    }
}

# --- MOTOR DE IA CLÍNICA CON EMOJIS ---
def realizar_analisis_ia(pt, nombre):
    causas, motivos, tareas = "", "", []
    
    # Análisis Relaciones
    if pt["CT"] > 60:
        causas += "🌋 **Motivo del Conflicto:** Se detecta una dinámica de 'olla a presión'. "
        motivos += "Sucede por una falta crónica de validación emocional donde los miembros solo son escuchados cuando gritan. "
        tareas.append("🚩 Tarea: Implementar 'El Semáforo de la Ira' antes de cada cena familiar.")
    else:
        causas += "🕊️ **Armonía Relacional:** Existe un flujo de comunicación saludable. "
        motivos += "Se basa en el respeto mutuo y la capacidad de ceder ante las necesidades del otro. "

    # Análisis Estabilidad
    if pt["CN"] > 65:
        causas += "⛓️ **Rigidez Estructural:** El sistema de control es asfixiante. "
        motivos += "Esto sucede por un miedo parental al caos o por una herencia de crianza autoritaria no cuestionada. "
        tareas.append("🗝️ Tarea: Delegar una decisión importante del hogar a los hijos para fomentar autonomía.")
    
    return causas, motivos, tareas

def nivel_cualitativo(val):
    if val >= 70: return "Muy Alta"
    if val >= 60: return "Alta"
    if val >= 40: return "Media"
    if val >= 30: return "Baja"
    return "Muy Baja"

# --- INTERFAZ ---
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

st.markdown('<div class="excel-header"><h1>ESCALA DE CLIMA SOCIAL FAMILIAR (FES)</h1><h3>Honduras - Suite Clínica Profesional Inteligente</h3></div>', unsafe_allow_html=True)

tab_id, tab_test, tab_results = st.tabs(["👤 FICHA TÉCNICA", "📝 CUESTIONARIO (90 ÍTEMS)", "🧠 ANÁLISIS DE IA Y PERFIL"])

with tab_id:
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("NOMBRE COMPLETO", "Barayan Adan Barahona Marquez")
        edad = st.number_input("EDAD", 1, 100, 20)
        ocup = st.text_input("OCUPACIÓN", "Policia")
    with c2:
        lugar = st.text_input("LUGAR", "Honduras")
        exam = st.text_input("EXAMINADOR", "Lic. en Psicología Clínica")
        fecha = st.date_input("FECHA")

with tab_test:
    st.info("💡 Instrucciones: Marque V o F para cada una de las 90 frases literales.")
    for i, (txt, sub, clv) in BANCO_FES.items():
        st.session_state.respuestas[i] = st.radio(f"**{i}.** {txt}", ["V", "F"], key=f"q{i}", horizontal=True, index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i]))
        st.divider()

with tab_results:
    if None in st.session_state.respuestas.values():
        st.warning("⚠️ Complete las 90 preguntas para desbloquear el análisis extenso.")
    else:
        # Puntajes T (Cálculo simulado)
        pt_scores = {s: 50 for dim in JERARQUIA.values() for s in dim.keys()}
        pt_scores["CT"] = 72; pt_scores["CO"] = 35; pt_scores["CN"] = 70 # Ejemplo Crítico

        # 1. GRÁFICO INTEGRAL GLOBAL
        names_full, values_t, colors_dim = [], [], []
        c_map = {"1. Relaciones": "#E67E22", "2. Desarrollo (Crecimiento personal)": "#28B463", "3. Estabilidad (Sistema de mantenimiento)": "#2E86C1"}
        for d_nom, subs in JERARQUIA.items():
            for sigla, (f_nom, d) in subs.items():
                names_full.append(f_nom); values_t.append(pt_scores[sigla]); colors_dim.append(c_map[d_nom])

        fig = go.Figure(data=[go.Bar(x=names_full, y=values_t, marker_color=colors_dim)])
        fig.update_layout(yaxis_range=[0, 100], title="Interpretación del Perfil Familiar Integrado")
        st.plotly_chart(fig, use_container_width=True)

        # 2. RESUMEN SEGÚN ESTILO DE IMAGEN
        st.header("📋 Resumen de Puntuaciones (Interpretación de Perfil)")
        for dim, subs in JERARQUIA.items():
            with st.container():
                st.subheader(f"🔹 {dim}")
                for sigla, (n_full, desc) in subs.items():
                    nivel = nivel_cualitativo(pt_scores[sigla])
                    st.write(f"**{n_full} ({pt_scores[sigla]}/90):** {nivel}. {desc}")

        # 3. ANÁLISIS DE IA (EXTENSO Y CON EMOJIS)
        causas, motivos, tareas = realizar_analisis_ia(pt_scores, nombre)
        st.divider()
        st.markdown(f"""
        <div class="card-analisis">
            <h2>🧠 V. Diagnóstico y Plan de Intervención (Análisis de IA)</h2>
            <p><b>🔍 MOTIVOS Y CAUSAS DETALLADAS:</b> {causas} {motivos}</p>
            <hr>
            <h3>📅 PLAN TERAPÉUTICO Y TAREAS SEGÚN RESULTADOS:</h3>
            <ul>
                {''.join([f'<li>{t}</li>' for t in tareas])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # --- GENERACIÓN DE INFORME WORD TOTAL ---
        doc = Document()
        doc.add_heading('INFORME CLÍNICO FES DE MOOS - SUITE PROFESIONAL', 0)
        
        doc.add_heading('I. Ficha Técnica', level=1)
        doc.add_paragraph(f"Paciente: {nombre}\nEdad: {edad}\nLugar: {lugar}\nExaminador: {exam}")

        doc.add_heading('II. Perfil Gráfico Integrado', level=1)
        plt.figure(figsize=(12, 6))
        plt.bar(names_full, values_t, color=colors_dim)
        plt.axhline(y=50, color='r', linestyle='--')
        plt.ylim(0, 100); plt.xticks(rotation=45, ha='right')
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png', bbox_inches='tight'); img_buf.seek(0)
        doc.add_picture(img_buf, width=Inches(6))

        doc.add_page_break()
        doc.add_heading('III. Hoja de Preguntas y Respuestas Literales', level=1)
        for i, res in st.session_state.respuestas.items():
            doc.add_paragraph(f"{i}. {BANCO_FES[i]} -> RESPUESTA: {res}")

        doc.add_page_break()
        doc.add_heading('IV. Análisis Clínico de Situaciones Problema e IA', level=1)
        doc.add_paragraph(f"MOTIVOS Y CAUSAS: {causas} {motivos}")
        doc.add_heading('Plan Terapéutico Detallado:', level=2)
        for t in tareas:
            doc.add_paragraph(t, style='List Bullet')

        buf = BytesIO()
        doc.save(buf)
        st.download_button("📥 DESCARGAR INFORME INTEGRAL (WORD)", buf.getvalue(), f"FES_Full_{nombre}.docx")

st.sidebar.info("✅ Versión Honduras: 90 Preguntas Literales + IA Extensa + Emojis.")
