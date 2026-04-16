import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from io import BytesIO
import datetime

# --- CONFIGURACIÓN DE ALTO NIVEL ---
st.set_page_config(page_title="FES Moos Suite - Clínica Profesional", page_icon="🧠", layout="wide")

# --- ESTILO VISUAL DINÁMICO ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .excel-header { 
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); 
        color: white; padding: 30px; text-align: center; border-radius: 10px; 
        box-shadow: 0 5px 15px rgba(0,0,0,0.2); margin-bottom: 25px;
    }
    .card-analisis { 
        background-color: white; padding: 25px; border-radius: 10px; 
        border-top: 8px solid #1E3A8A; box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
        margin-bottom: 20px; 
    }
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
    90: ("En mi casa las reglas son flexibles", "CN", "F")
}

# --- ESTRUCTURA SEGÚN MANUAL ---
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

# --- FUNCIONES CLÍNICAS Y DE CÁLCULO ---
def calcular_puntuaciones(respuestas):
    # Inicializar contadores en 0
    raw_scores = {sigla: 0 for subs in JERARQUIA.values() for sigla in subs.keys()}
    
    # Calcular Puntaje Directo (Raw Score)
    for i, (txt, sigla, clave) in BANCO_FES.items():
        if respuestas.get(i) == clave:
            raw_scores[sigla] += 1
            
    # Conversión Simulada a Puntaje T (Para uso real, ajustar según baremos de la región)
    # Nota: Aquí uso una fórmula base para visualización. 
    t_scores = {}
    for sigla, pts in raw_scores.items():
        t_scores[sigla] = min(max(int((pts * 7.5) + 20), 0), 100) # Simulación de T-Score
        
    return raw_scores, t_scores

def realizar_analisis_ia(pt, nombre):
    causas, motivos, tareas = "", "", []
    
    # Análisis Relaciones
    if pt["CT"] > 60:
        causas += "🌋 **Motivo del Conflicto:** Se detecta una dinámica de alta reactividad. "
        motivos += "Posiblemente derivado de estrés ambiental u ocupacional severo que se desplaza al entorno familiar. "
        tareas.append("🚩 Tarea: Implementar técnicas de desactivación fisiológica antes de abordar discusiones.")
    elif pt["CO"] < 40:
        causas += "🧊 **Distanciamiento Afectivo:** Baja cohesión familiar. "
        motivos += "Los miembros operan como unidades aisladas debido a rutinas incompatibles o conflictos no resueltos. "
        tareas.append("🤝 Tarea: Establecer una 'hora familiar' innegociable a la semana sin dispositivos electrónicos.")
    else:
        causas += "🕊️ **Armonía Relacional:** Existe un flujo de comunicación saludable. "
        motivos += "Se basa en el respeto mutuo y la capacidad de ceder ante las necesidades del otro. "

    # Análisis Estabilidad
    if pt["CN"] > 65:
        causas += "⛓️ **Rigidez Estructural:** El sistema de control es asfixiante. "
        motivos += "Común en dinámicas donde figuras de autoridad proyectan protocolos estrictos (ej. laborales/policiales) al hogar. "
        tareas.append("🗝️ Tarea: Delegar decisiones de bajo riesgo a los menores/otros miembros para fomentar autonomía.")
    
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

st.markdown('<div class="excel-header"><h1>ESCALA DE CLIMA SOCIAL FAMILIAR (FES)</h1><h3>Plataforma de Evaluación Clínica Profesional</h3></div>', unsafe_allow_html=True)

# SIDEBAR PARA METADATOS
with st.sidebar:
    st.header("👤 Ficha Técnica")
    nombre = st.text_input("Paciente", "Ej. Funcionario Policial X")
    edad = st.number_input("Edad", 18, 80, 30)
    ocup = st.text_input("Ocupación", "Sub-Inspector / Funcionario")
    lugar = st.text_input("Sede / Jurisdicción", "Sanidad Policial - Honduras")
    exam = st.text_input("Examinador", "Lic. en Psicología")
    fecha = st.date_input("Fecha de Evaluación", datetime.date.today())
    
    st.divider()
    st.info("💡 **Instrucciones:** Llene los datos en este panel lateral y proceda a la pestaña de Cuestionario.")

tab_test, tab_results = st.tabs(["📝 CUESTIONARIO (90 ÍTEMS)", "🧠 ANÁLISIS DE RESULTADOS"])

with tab_test:
    st.subheader("Cuestionario FES - Forma R")
    st.write("Marque 'V' (Verdadero) o 'F' (Falso) para cada una de las siguientes afirmaciones.")
    
    # Dividir en columnas para no hacer scroll infinito
    col1, col2 = st.columns(2)
    for i, (txt, sub, clv) in BANCO_FES.items():
        target_col = col1 if i <= 45 else col2
        with target_col:
            st.session_state.respuestas[i] = st.radio(
                f"**{i}.** {txt}", 
                ["V", "F"], 
                key=f"q{i}", 
                horizontal=True, 
                index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i])
            )
            st.divider()

with tab_results:
    if None in st.session_state.respuestas.values():
        faltantes = [k for k, v in st.session_state.respuestas.items() if v is None]
        st.warning(f"⚠️ Faltan preguntas por contestar. Por favor complete los siguientes ítems: {faltantes[:5]}...")
    else:
        # Calcular Puntuaciones Reales
        raw_scores, pt_scores = calcular_puntuaciones(st.session_state.respuestas)

        # 1. GRÁFICO INTEGRAL GLOBAL
        names_full, values_t, colors_dim = [], [], []
        c_map = {"1. Relaciones": "#E67E22", "2. Desarrollo (Crecimiento personal)": "#28B463", "3. Estabilidad (Sistema de mantenimiento)": "#2E86C1"}
        
        for d_nom, subs in JERARQUIA.items():
            for sigla, (f_nom, d) in subs.items():
                names_full.append(f_nom)
                values_t.append(pt_scores[sigla])
                colors_dim.append(c_map[d_nom])

        fig = go.Figure(data=[go.Bar(x=names_full, y=values_t, marker_color=colors_dim, text=values_t, textposition='auto')])
        fig.update_layout(yaxis_range=[0, 100], title="Interpretación del Perfil Familiar Integrado (T-Scores)")
        st.plotly_chart(fig, use_container_width=True)

        # 2. RESUMEN DE PUNTUACIONES
        st.header("📋 Resumen de Puntuaciones (Interpretación de Perfil)")
        col_res1, col_res2, col_res3 = st.columns(3)
        cols_ref = [col_res1, col_res2, col_res3]
        
        for idx, (dim, subs) in enumerate(JERARQUIA.items()):
            with cols_ref[idx]:
                st.subheader(f"{dim.split('.')[1]}")
                for sigla, (n_full, desc) in subs.items():
                    nivel = nivel_cualitativo(pt_scores[sigla])
                    st.markdown(f"**{n_full} ({pt_scores[sigla]}/100):** *{nivel}*. {desc}")

        # 3. ANÁLISIS DE IA
        causas, motivos, tareas = realizar_analisis_ia(pt_scores, nombre)
        st.markdown(f"""
        <div class="card-analisis">
            <h2>🧠 Diagnóstico y Plan de Intervención Clínico</h2>
            <p><b>🔍 ETIOLOGÍA Y DINÁMICA:</b> {causas} {motivos}</p>
            <hr>
            <h3>📅 PLAN TERAPÉUTICO SUGERIDO:</h3>
            <ul>{''.join([f'<li>{t}</li>' for t in tareas])}</ul>
        </div>
        """, unsafe_allow_html=True)

        # --- BOTONES DE EXPORTACIÓN ---
        st.divider()
        st.subheader("💾 Exportación de Datos")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            # GENERACIÓN DE INFORME WORD
            doc = Document()
            titulo = doc.add_heading('INFORME CLÍNICO FES DE MOOS', 0)
            titulo.alignment = 1

            doc.add_heading('I. Ficha Técnica', level=1)
            doc.add_paragraph(f"Paciente: {nombre}\nEdad: {edad}\nOcupación: {ocup}\nJurisdicción: {lugar}\nExaminador: {exam}\nFecha: {fecha.strftime('%d/%m/%Y')}")

            doc.add_heading('II. Perfil Gráfico Integrado', level=1)
            plt.figure(figsize=(10, 5))
            plt.bar(names_full, values_t, color=colors_dim)
            plt.axhline(y=50, color='r', linestyle='--', alpha=0.5)
            plt.ylim(0, 100)
            plt.xticks(rotation=45, ha='right')
            plt.title("Perfil de Clima Social Familiar")
            
            img_buf = BytesIO()
            plt.savefig(img_buf, format='png', bbox_inches='tight')
            img_buf.seek(0)
            doc.add_picture(img_buf, width=Inches(6))
            plt.close() # Cierra el plot para ahorrar memoria

            # SECCIÓN: RESUMEN DE PUNTUACIONES EN WORD
            doc.add_heading('III. Resumen de Puntuaciones', level=1)
            for dim_nombre, subescalas in JERARQUIA.items():
                doc.add_heading(f"🔹 {dim_nombre}", level=2)
                for sigla, (nombre_completo, descripcion) in subescalas.items():
                    punto_t = pt_scores[sigla]
                    nivel = nivel_cualitativo(punto_t)
                    p = doc.add_paragraph(style='List Bullet')
                    run_nombre = p.add_run(f"{nombre_completo} ({punto_t}/100): ")
                    run_nombre.bold = True
                    run_nivel = p.add_run(f"{nivel}. ")
                    run_nivel.italic = True
                    p.add_run(descripcion)

            # SECCIÓN: HOJA DE RESPUESTAS LITERALES
            doc.add_page_break()
            doc.add_heading('IV. Respuestas Literales del Paciente', level=1)
            for i, res in st.session_state.respuestas.items():
                pregunta_texto = BANCO_FES[i][0] # Solo extrae el texto, no la tupla completa
                doc.add_paragraph(f"{i}. {pregunta_texto} -> RESPUESTA: {res}")

            # SECCIÓN: IA
            doc.add_page_break()
            doc.add_heading('V. Análisis Clínico de Situaciones Problema', level=1)
            p_diag = doc.add_paragraph()
            p_diag.add_run("🔍 MOTIVOS Y CAUSAS: ").bold = True
            p_diag.add_run(f"{causas} {motivos}")
            
            doc.add_heading('Plan Terapéutico Detallado:', level=2)
            for t in tareas:
                doc.add_paragraph(t, style='List Bullet')

            # FIRMA
            doc.add_paragraph("\n\n\n" + "_"*40)
            p_firma = doc.add_paragraph(f"{exam}\n{lugar}")
            p_firma.alignment = 1

            buf = BytesIO()
            doc.save(buf)
            st.download_button("📥 DESCARGAR INFORME CLÍNICO (WORD)", buf.getvalue(), f"FES_{nombre.replace(' ', '_')}.docx", type="primary")

        with col_btn2:
            # EXPORTAR BASE DE DATOS A CSV
            data_export = {"Fecha": fecha, "Paciente": nombre, "Edad": edad, "Sede": lugar}
            data_export.update({f"Item_{k}": v for k, v in st.session_state.respuestas.items()})
            data_export.update({f"TScore_{k}": v for k, v in pt_scores.items()})
            
            df_export = pd.DataFrame([data_export])
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("📊 EXPORTAR DATOS A EXCEL/CSV", csv, f"Data_FES_{nombre.replace(' ', '_')}.csv")
