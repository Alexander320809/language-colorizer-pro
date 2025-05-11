# app_streamlit.py
import streamlit as st
import re
import json
import os
from functools import lru_cache
import pdfplumber

from youtube_transcript_api import YouTubeTranscriptApi
import requests
import tempfile

# ====================== CONFIGURACIÓN INICIAL ======================
# 2. Configuración de página INMEDIATAMENTE después de los imports
st.set_page_config(
    page_title="Language Colorizer Pro",
    layout="wide",
    page_icon="🎨"
)

PALABRAS_COLORES_JSON = "palabras_colores.json"

# ====================== CATEGORÍAS GRAMATICALES ======================
CATEGORIAS = {
    "verbos": "#00AA00",         # Verde
    "sustantivos": "purple",     # Morado
    "pronombres": "red",         # Rojo
    "articulos": "blue",         # Azul
    "conjunciones": "#8B4513",   # Marrón
    "adjetivos": "#FFC0CB",      # Rosado
    "adverbios": "#FFA500",      # Naranja
    "preposiciones": "#FFFF00"   # Amarillo
}

# ====================== DICCIONARIO BASE DE PALABRAS ======================
palabras_base = {
    "be": "#00AA00", "am": "#00AA00", "do": "#00AA00", "have": "#00AA00", "go": "#00AA00",
    "developed": "#00AA00", "remained": "#00AA00", "I": "red", "you": "red", "it": "red",
    "that": "red", "we": "red", "time": "purple", "thing": "purple", "people": "purple",
    "way": "purple", "day": "purple", "cat": "purple", "the": "blue", "a": "blue",
    "and": "#8B4513", "but": "#8B4513", "if": "#8B4513", "or": "#8B4513", "when": "#8B4513",
    "because": "#8B4513", "while": "#8B4513", "though": "#8B4513", "either": "#8B4513",
    "ll": "#8B4513", "whether": "#8B4513", "right": "#FFC0CB", "good": "#FFC0CB",
    "weird": "#FFC0CB", "local": "#FFC0CB", "awesome": "#FFC0CB", "deep": "#FFC0CB",
    "not": "#FFA500", "so": "#FFA500", "simply": "#FFA500", "to": "#FFFF00", "of": "#FFFF00"
}

# ====================== FUNCIONES DE GESTIÓN DE DATOS ======================
@st.cache_data
def cargar_palabras_colores():
    try:
        if os.path.exists(PALABRAS_COLORES_JSON) and os.path.getsize(PALABRAS_COLORES_JSON) > 0:
            with open(PALABRAS_COLORES_JSON, "r", encoding="utf-8") as f:
                return {**palabras_base, **json.load(f)}
        return palabras_base.copy()
    except Exception:
        return palabras_base.copy()

palabras_colores = cargar_palabras_colores()

def guardar_palabras_colores():
    try:
        with open(PALABRAS_COLORES_JSON, "w", encoding="utf-8") as f:
            json.dump(palabras_colores, f, indent=4)
        st.success("Diccionario guardado correctamente")
    except Exception as e:
        st.error(f"No se pudo guardar: {str(e)}")

# ====================== FUNCIONES DE PROCESAMIENTO ======================
@lru_cache(maxsize=1000)
def obtener_color(palabra):
    return palabras_colores.get(palabra.lower())

def limpiar_texto(texto):
    return "\n".join([re.sub(r'\s+', ' ', linea).strip() for linea in texto.splitlines()])

def aplicar_colores_html(texto):
    lineas = texto.split('\n')
    resultado = []
    for linea in lineas:
        if not linea.strip():
            resultado.append('<br>')
            continue
        palabras = re.findall(r"(\w+|\W+)", linea)
        linea_coloreada = []
        for segmento in palabras:
            if segmento.strip():
                palabra_limpia = re.sub(r'[^a-zA-Z\']', '', segmento.lower())
                color = obtener_color(palabra_limpia)
                if color:
                    base = re.sub(r'[^a-zA-Z\']', '', segmento)
                    resto = segmento[len(base):] if base else segmento
                    linea_coloreada.append(
                        f'<span style="border-bottom: 2px solid {color}">{base}</span>{resto}')
                else:
                    linea_coloreada.append(segmento)
            else:
                linea_coloreada.append(segmento)
        resultado.append(''.join(linea_coloreada))
    return '<br>'.join(resultado)

# ====================== FUNCIONES PARA ARCHIVOS ======================
def procesar_archivo(uploaded_file):
    try:
        if uploaded_file.name.endswith('.pdf'):
            with pdfplumber.open(uploaded_file) as pdf:
                return "\n".join([pagina.extract_text() or "" for pagina in pdf.pages if pagina.extract_text()])
        else:
            return uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"Error al procesar archivo: {str(e)}")
        return ""

# ====================== FUNCIONES PARA YOUTUBE ======================
def descargar_subtitulos_youtube(url):
    try:
        video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url).group(1)
        subtitles = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-GB', 'a.en'])
        return "\n".join([line['text'] for line in subtitles])
    except Exception as e:
        st.error(f"No se pudieron obtener subtítulos: {str(e)}")
        return ""

# ====================== CHAT CON IA ======================
class ChatAI:
    def __init__(self):
        self.idioma_respuesta = "ambos"
        self.base_url = "http://localhost:11434/api/generate"
        self.model = "llama3"

    def generar_respuesta(self, mensaje):
        try:
            prompt = mensaje
            if self.idioma_respuesta == "español":
                prompt += " (responde en español)"
            elif self.idioma_respuesta == "ambos":
                prompt += " (responde primero en inglés, luego en español)"
                
            response = requests.post(
                self.base_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            return response.json()["response"]
        except Exception as e:
            return f"Error: {str(e)}"

# ====================== INTERFAZ STREAMLIT ======================
def main():
    
    # CSS personalizado
    st.markdown("""
    <style>
        .texto-coloreado {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            white-space: pre-wrap;
        }
        .stTextArea textarea {
            min-height: 200px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar para configuración
    with st.sidebar:
        st.title("⚙️ Configuración")
        
        # Gestión del diccionario
        st.subheader("Diccionario de palabras")
        nueva_palabra = st.text_input("Nueva palabra")
        nueva_categoria = st.selectbox("Categoría", list(CATEGORIAS.keys()))
        
        if st.button("Agregar palabra"):
            if nueva_palabra and nueva_categoria:
                palabras_colores[nueva_palabra.lower()] = CATEGORIAS[nueva_categoria]
                guardar_palabras_colores()
                st.rerun()
        
        # Estadísticas
        st.subheader("📊 Estadísticas")
        for cat, color in CATEGORIAS.items():
            count = sum(1 for word, col in palabras_colores.items() if col.lower() == color.lower())
            st.markdown(f"<span style='color:{color}'>{cat.capitalize()}: {count}</span>", unsafe_allow_html=True)
        
        if st.button("Guardar diccionario"):
            guardar_palabras_colores()
    
    # Contenido principal
    st.title("🎨 Language Colorizer Pro")
    
    # Pestañas para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["Editor de Texto", "Chat con IA", "Configuración Avanzada"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cargar contenido")
            opcion = st.radio("Fuente:", ("Texto manual", "Archivo", "YouTube"))
            
            texto = ""
            if opcion == "Texto manual":
                texto = st.text_area("Escribe o pega tu texto aquí:", height=300)
            elif opcion == "Archivo":
                uploaded_file = st.file_uploader("Sube un archivo (TXT o PDF)", type=["txt", "pdf"])
                if uploaded_file:
                    texto = procesar_archivo(uploaded_file)
            elif opcion == "YouTube":
                url = st.text_input("URL de YouTube:")
                if url:
                    texto = descargar_subtitulos_youtube(url)
            
            if st.button("Procesar texto"):
                if texto:
                    st.session_state.texto_procesado = limpiar_texto(texto)
                else:
                    st.warning("Ingresa algún texto primero")
        
        with col2:
            st.subheader("Resultado coloreado")
            if "texto_procesado" in st.session_state:
                html_content = aplicar_colores_html(st.session_state.texto_procesado)
                st.markdown(f'<div class="texto-coloreado">{html_content}</div>', unsafe_allow_html=True)
                
                # Exportar a HTML
                html_full = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Documento Exportado</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
        .contenido {{ background-color: white; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="contenido">{html_content}</div>
</body>
</html>"""
                
                st.download_button(
                    label="Descargar como HTML",
                    data=html_full,
                    file_name="texto_coloreado.html",
                    mime="text/html"
                )
            else:
                st.info("Procesa algún texto para ver el resultado aquí")
    
    with tab2:
        st.subheader("💬 Chat Bilingüe con IA")
        
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
        
        # Mostrar historial de chat
        for msg in st.session_state.chat_messages:
            role = "user" if msg["role"] == "user" else "assistant"
            color = "#1a73e8" if role == "user" else "#0b8043"
            st.markdown(f"<span style='color:{color}; font-weight:bold'>{'Tú' if role == 'user' else 'IA'}:</span> {msg['content']}", unsafe_allow_html=True)
        
        # Configuración del chat
        idioma = st.radio("Idioma de respuesta:", ["Ambos", "Inglés", "Español"], horizontal=True)
        
        # Entrada de mensaje
        user_input = st.text_area("Escribe tu mensaje:", key="chat_input")
        
        if st.button("Enviar") and user_input:
            chatbot = ChatAI()
            chatbot.idioma_respuesta = idioma.lower()
            
            # Agregar mensaje del usuario
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            # Obtener respuesta
            respuesta = chatbot.generar_respuesta(user_input)
            
            # Agregar respuesta de la IA
            st.session_state.chat_messages.append({"role": "assistant", "content": respuesta})
            
            # Rerun para actualizar la vista
            st.rerun()
    
    with tab3:
        st.subheader("Configuración avanzada del diccionario")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_busqueda = st.text_input("Buscar palabra:")
        with col2:
            filtro_categoria = st.selectbox("Filtrar por categoría", ["Todas"] + list(CATEGORIAS.keys()))
        
        # Mostrar palabras del diccionario
        palabras_filtradas = []
        for palabra, color in palabras_colores.items():
            categoria = obtener_categoria_por_color(color)
            if (filtro_categoria == "Todas" or categoria == filtro_categoria) and \
               (not filtro_busqueda or filtro_busqueda.lower() in palabra.lower()):
                palabras_filtradas.append((palabra, categoria, color))
        
        # Tabla de palabras
        if palabras_filtradas:
            for palabra, categoria, color in sorted(palabras_filtradas, key=lambda x: x[0].lower()):
                cols = st.columns([4, 3, 2, 1])
                cols[0].markdown(f"**{palabra}**")
                cols[1].markdown(f"<span style='color:{color}'>{categoria}</span>", unsafe_allow_html=True)
                cols[2].markdown(f"`{color}`")
                if cols[3].button("❌", key=f"del_{palabra}"):
                    del palabras_colores[palabra]
                    guardar_palabras_colores()
                    st.rerun()
        else:
            st.info("No hay palabras que coincidan con los filtros")

def obtener_categoria_por_color(color):
    for cat, col in CATEGORIAS.items():
        if col.lower() == color.lower():
            return cat
    return "Desconocida"

if __name__ == "__main__":
    main()