import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Profesional FES", layout="wide")

# Inicialización de respuestas
if 'respuestas' not in st.session_state:
    st.session_state.respuestas = {i: None for i in range(1, 91)}

# --- 1. FUNCIÓN: GENERAR WORD CON SALTOS DE PÁGINA ---
def generar_word_profesional(datos, pd_res, s_res, analisis_ia):
    doc = Document()
    
    # HOJA 1: DATOS DE IDENTIFICACIÓN
    titulo = doc.add_heading('INFORME CLÍNICO: ESCALA FES', 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_heading('1. Datos de Identificación y Contexto', level=1)
    for k, v in datos.items():
        p = doc.add_paragraph()
        p.add_run(f"{k}: ").bold = True
        p.add_run(str(v))
    
    doc.add_page_break() 

    # HOJA 2: RESULTADOS ESTADÍSTICOS
    doc.add_heading('2. Resultados Cuantitativos', level=1)
    tabla = doc.add_table(rows=1, cols=3)
    tabla.style = 'Table Grid'
    
    hdr_cells = tabla.rows[0].cells
    hdr_cells[0].text = 'Subescala'
    hdr_cells[1].text = 'PD (Directo)'
    hdr_cells[2].text = 'S (Típico)'
    
    for sub, valor_pd in pd_res.items():
        row_cells = tabla.add_row().cells
        row_cells[0].text = str(sub)
        row_cells[1].text = str(valor_pd)
        row_cells[2].text = str(s_res[sub])
    
    doc.add_page_break() 

    # HOJA 3: ANÁLISIS DE IA Y RECOMENDACIONES
    doc.add_heading('3. Interpretación Clínica y Recomendaciones', level=1)
    for item in analisis_ia:
        doc.add_heading(item['titulo'], level=2)
        doc.add_paragraph(item['contenido'])

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# --- 2. SIDEBAR: FICHA TÉCNICA Y CONTEXTO ---
with st.sidebar:
    st.header("📋 Ficha Técnica")
    st.markdown("Escala Aplicada: **[X] FES**")
    nombre = st.text_input("Nombre Completo", value="Barayan Adan Barahona Marquez")
    edad = st.number_input("Edad", 12, 99, 32)
    profesion = st.text_input("Profesión", value="Policía")
    
    st.subheader("🌐 Contexto Analítico")
    composicion = st.selectbox("Composición", ["Nuclear", "Extensa", "Monoparental", "Reconstituida"])
    ciclo_vital = st.selectbox("Etapa Ciclo Vital", ["Infantes", "Adolescentes", "Adultos", "Nido Vacío"])
    crisis = st.text_area("Influencia de Crisis", value="mi padre sufre de alcoholismo")
    jerarquia = st.text_area("Dinámica de Autoridad", value="mi madre ama de casa, mi padre gastos, yo ayudo")

# --- 3. PESTAÑAS (HOJAS) ---
tab1, tab2, tab3 = st.tabs(["📄 Instrucciones", "📝 Aplicación (90 Ítems)", "📊 Informe e Impresión"])

with tab1:
    st.header("Instrucciones Oficiales FES")
    st.write(f"Estimado **{nombre}**, responda V (Verdadero) o F (Falso) pensando en su familia actual.")
    st.info("Pestaña 2: Cuestionario | Pestaña 3: Resultados e Impresión.")

with tab2:
    st.header("Cuestionario de 90 Ítems")
    
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
            key=f"item_{i}",
            horizontal=True,
            index=None if st.session_state.respuestas[i] is None else ["V", "F"].index(st.session_state.respuestas[i])
        )

with tab3:
    if None in st.session_state.respuestas.values():
        st.warning("⚠️ Debe responder las 90 preguntas para generar el informe completo.")
    else:
        # LÓGICA DE CALIFICACIÓN (Ejemplo simulado)
        sub_nombres = ["CO", "EX", "CT", "AU", "AC", "IC", "SR", "MR", "OR", "CN"]
        pd_val = {s: 5 for s in sub_nombres}
        s_val = {s: 50 for s in sub_nombres}
        
        # ANÁLISIS IA
        analisis_ia = [
            {"titulo": "Análisis de Perfil Profesional", 
             "contenido": f"Dada su ocupación como {profesion} y su edad de {edad} años, el perfil refleja una búsqueda de estructura y cumplimiento de normas propia de su entorno laboral."},
            {"titulo": "Influencia de Crisis y Roles", 
             "contenido": f"Atención: El clima está influenciado por: {crisis}. Dinámica reportada: {jerarquia}."},
            {"titulo": "Recomendaciones Terapéuticas", 
             "contenido": "Se sugiere trabajar en la flexibilización de roles y fortalecer la cohesión emocional para equilibrar la tensión por factores externos."}
        ]

        # BOTÓN DE IMPRESIÓN
        datos_informe = {"Nombre": nombre, "Edad": edad, "Profesión": profesion, "Crisis": crisis}
        doc_word = generar_word_profesional(datos_informe, pd_val, s_val, analisis_ia)
        
        st.download_button(label="📥 DESCARGAR INFORME EN WORD (HOJAS SEPARADAS)", 
                           data=doc_word, 
                           file_name=f"FES_{nombre}.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # GRÁFICO 1: SUBESCALAS
        fig1 = go.Figure(data=go.Scatter(x=sub_nombres, y=list(s_val.values()), mode='lines+markers', marker=dict(size=10, symbol='square'), line_color='navy'))
        fig1.update_layout(title="Perfil de Subescalas FES", yaxis_range=[20, 80], template="plotly_white")
        st.plotly_chart(fig1)

        # GRÁFICO 2: DIMENSIONES
        dim_val = [50, 50, 50] # Relaciones, Desarrollo, Estabilidad
        fig2 = go.Figure(data=[go.Bar(x=["Relaciones", "Desarrollo", "Estabilidad"], y=dim_val, marker_color='teal')])
        fig2.update_layout(title="Perfil por Dimensiones Generales", yaxis_range=[0, 100], template="plotly_white")
        st.plotly_chart(fig2)

        st.success(f"Informe listo para {nombre}. [X] Escala FES")
