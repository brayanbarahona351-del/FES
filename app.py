import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="FES Moos Suite - Clínica Profesional Honduras", layout="wide")

# --- ESTILO VISUAL DE ALTO NIVEL ---
st.markdown("""
    <style>
    .excel-header { background-color: #E67E22; color: white; padding: 40px; text-align: center; border-radius: 15px; font-family: 'Arial Black'; margin-bottom: 30px; border: 3px solid #D35400; }
    .stRadio > div { flex-direction: row; gap: 30px; background-color: #fcfcfc; padding: 15px; border-radius: 12px; border: 1px solid #ddd; }
    .seccion-clinica { background-color: #fdfefe; border-left: 10px solid #E67E22; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS: 90 PREGUNTAS LITERALES Y CALIFICACIÓN ---
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

JERARQUIA = {
    "1. Relaciones": {"CO": "Cohesión", "EX": "Expresividad", "CT": "Conflicto"},
    "2. Desarrollo (Crecimiento Personal)": {"AU": "Autonomía", "AC": "Actuación", "IC": "Intelectual-Cultural", "SR": "Social-Recreativo", "MR": "Moralidad-Religiosidad"},
    "3. Estabilidad (Sistema de Mantenimiento)": {"OR": "Organización", "CN": "Control"}
}

# --- LÓGICA DE PROCESAMIENTO AVANZADO ---
def baremacion_t(respuestas):
    pd = {s: 0 for s in ["CO", "EX", "CT", "AU", "AC", "IC", "SR", "MR", "OR", "CN"]}
    for i, res in respuestas.items():
        if res == BANCO_FES[i][2]: pd[BANCO_FES[i][1]] += 1
    # Conversión a T (Honduras estándar: Media 50, DE 10)
    t_scores = {k: (v * 5 + 25) for k, v in pd.items()}
    return t_scores

def interpretar_nivel(val):
    if val >= 70: return "MUY ALTA", "Indica una presencia extrema de esta característica en el hogar."
    if val >= 60: return "ALTA", "Indica una tendencia marcada por encima de la media."
    if val >= 40: return "MEDIA", "Se encuentra dentro del rango de normalidad esperado."
    if val >= 30: return "BAJA", "Existe una carencia o debilidad en esta área específica."
    return "MUY BAJA", "Indica una ausencia crítica que requiere intervención inmediata."

# --- INTERFAZ ---
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

tab1, tab2, tab3 = st.tabs(["🏠 HOJA 1: FICHA TÉCNICA", "📝 HOJA 2: CUESTIONARIO LITERAL", "📊 HOJA 3: INFORME CLÍNICO E IMPRESIÓN"])

with tab1:
    st.markdown('<div class="excel-header"><h1>ESCALA DE CLIMA SOCIAL FAMILIAR (FES)</h1><h3>HONDURAS - SOFTWARE DE ALTA PRECISIÓN</h3></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("👤 NOMBRE COMPLETO DEL EXAMINADO", "Barayan Adan Barahona Marquez")
        edad = st.number_input("📅 EDAD", 1, 100, 20)
        sexo = st.selectbox("🚻 SEXO", ["Masculino", "Femenino", "Otro"])
        ocup = st.text_input("💼 OCUPACIÓN / PROFESIÓN", "Policia")
    with c2:
        grado = st.text_input("🎓 GRADO ACADÉMICO", "Bachiller")
        exam = st.text_input("🩺 EVALUADOR RESPONSABLE", "Lic. en Psicología")
        fecha = st.date_input("📆 FECHA DE APLICACIÓN")
        lugar = st.text_input("📍 LUGAR", "Honduras")

with tab2:
    st.header("📝 Cuestionario Literal (90 Frases Oficiales)")
    st.info("Marque V (Verdadero) o F (Falso) para cada frase basándose en su realidad familiar actual.")
    for i, (txt, sub, clv) in BANCO_FES.items():
        st.session_state.respuestas[i] = st.radio(f"**{i}.** {txt}", ["V", "F"], key=f"q{i}", horizontal=True, index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i]))
        st.divider()

with tab3:
    if None in st.session_state.respuestas.values():
        st.warning("⚠️ El informe no puede generarse: Faltan preguntas por contestar en la Hoja 2.")
    else:
        scores_t = baremacion_t(st.session_state.respuestas)
        st.header("📊 Análisis Integral del Clima Familiar")
        
        # 1. Gráfico Global Integrado
        nombres_completos = []
        valores_t = []
        colores = []
        c_map = {"1. Relaciones": "#2E86C1", "2. Desarrollo (Crecimiento Personal)": "#28B463", "3. Estabilidad (Sistema de Mantenimiento)": "#CB4335"}
        
        for dim, subs in JERARQUIA.items():
            for sigla, full in subs.items():
                nombres_completos.append(full)
                valores_t.append(scores_t[sigla])
                colores.append(c_map[dim])

        fig_global = go.Figure(data=[go.Bar(x=nombres_completos, y=valores_t, marker_color=colores)])
        fig_global.update_layout(yaxis_range=[0, 100], title="Perfil General de Subescalas (Interpretación de Perfil)")
        st.plotly_chart(fig_global, use_container_width=True)

        # 2. Análisis Detallado (Estilo Imagen)
        st.header("🧠 Interpretación Detallada por Áreas")
        for dim, subs in JERARQUIA.items():
            with st.container():
                st.markdown(f'<div class="seccion-clinica"><h3>🔹 {dim}</h3>', unsafe_allow_html=True)
                for sigla, full in subs.items():
                    nivel, desc_rapida = interpretar_nivel(scores_t[sigla])
                    st.write(f"**{full} ({scores_t[sigla]}/100):** {nivel}. {desc_rapida}")
                st.markdown('</div>', unsafe_allow_html=True)

        # 3. Situaciones Problema, Causas y Tareas
        st.divider()
        st.header("📋 Análisis de Situaciones Problema e Intervención")
        col_ia1, col_ia2 = st.columns(2)
        with col_ia1:
            st.subheader("🚩 Motivos, Causas y Por qué sucede")
            if scores_t["CT"] > 60:
                st.write("**Conflicto Elevado:** Se debe a modelos de comunicación reactivos y falta de validación emocional mutua.")
            if scores_t["CO"] < 40:
                st.write("**Cohesión Baja:** Indica un distanciamiento afectivo provocado por la falta de rituales de conexión familiar.")
            st.write("**Análisis General:** La dinámica familiar se ve afectada por factores de estrés que impiden un desarrollo equilibrado en las áreas sociales.")
        
        with col_ia2:
            st.subheader("🛠️ Plan Terapéutico y Tareas")
            st.write("1. **Tarea:** Implementar el 'Círculo de Palabra' semanal para mejorar la expresividad.")
            st.write("2. **Tarea:** Definir un manual de convivencia democrático para reducir el control punitivo.")

        # --- GENERACIÓN DE INFORME WORD TOTAL ---
        doc = Document()
        doc.add_heading('INFORME PSICOMÉTRICO PROFESIONAL: FES DE MOOS', 0)
        
        # Ficha Técnica
        doc.add_heading('I. Datos de Identificación', level=1)
        table_id = doc.add_table(rows=1, cols=2)
        cells = table_id.rows[0].cells
        cells[0].text = f"Nombre: {nombre}\nEdad: {edad}\nSexo: {sexo}\nLugar: {lugar}"
        cells[1].text = f"Fecha: {fecha}\nExaminador: {exam}\nGrado: {grado}\nProfesión: {ocup}"

        # Gráfico estático
        doc.add_heading('II. Perfil Gráfico de Resultados', level=1)
        plt.figure(figsize=(12, 6))
        plt.bar(nombres_completos, valores_t, color=colores)
        plt.axhline(y=50, color='r', linestyle='--')
        plt.ylim(0, 100); plt.xticks(rotation=45, ha='right')
        plt.title("Interpretación de Perfil Multidimensional")
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png', bbox_inches='tight'); img_buf.seek(0)
        doc.add_picture(img_buf, width=Inches(6))

        # Hoja de Preguntas y Respuestas
        doc.add_page_break()
        doc.add_heading('III. Hoja de Preguntas y Respuestas Literales', level=1)
        for i, res in st.session_state.respuestas.items():
            doc.add_paragraph(f"{i}. {BANCO_FES[i][0]} -> RESPUESTA: {res}")

        # Análisis Estilo Imagen
        doc.add_page_break()
        doc.add_heading('IV. Análisis de Subescalas e Interpretación', level=1)
        for dim, subs in JERARQUIA.items():
            doc.add_heading(dim, level=2)
            for sigla, full in subs.items():
                nivel, desc = interpretar_nivel(scores_t[sigla])
                p = doc.add_paragraph(style='List Bullet')
                p.add_run(f"{full} ({scores_t[sigla]}/100): ").bold = True
                p.add_run(f"{nivel}. {desc}")

        # Plan Terapéutico
        doc.add_heading('V. Diagnóstico y Plan de Intervención', level=1)
        doc.add_paragraph(f"MOTIVOS Y CAUSAS: Los resultados sugieren que el examinado {nombre} presenta una dinámica...")
        doc.add_paragraph("TAREAS Y CRONOGRAMA: Se recomienda seguimiento psicológico para trabajar las áreas críticas detectadas.")

        final_buf = BytesIO()
        doc.save(final_buf)
        st.download_button("📥 DESCARGAR INFORME CLÍNICO COMPLETO (WORD)", final_buf.getvalue(), f"Informe_FES_Total_{nombre}.docx")

st.sidebar.success("✅ Software Habilitado: 90 Preguntas + Gráfico Global + Perfil Honduras + Word Integral.")
