"""
SECOP AI - Sistema Profesional de Consultas
Plataforma de Inteligencia Artificial para Contratación Pública
"""

import streamlit as st
import requests
import time
from datetime import datetime
import re
import pandas as pd
import os

# ============================================
# CONFIGURACIÓN
# ============================================
API_URL = "http://localhost:5001"

# Credenciales de acceso (hardcoded)
CREDENTIALS = {
    "admin": "secop2024",
    "usuario": "demo123",
    "invitado": "guest2024"
}

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================
st.set_page_config(
    page_title="SECOP AI - Sistema de Consultas",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================
# ESTILOS CSS PROFESIONALES
# ============================================
st.markdown("""
    <style>
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilos generales */
    .main {
        background: white;
    }
    
    /* Login container */
    .login-container {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        max-width: 450px;
        margin: 2rem auto;
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Header profesional */
    .professional-header {
        text-align: center;
        padding: 2rem 0;
        color: white;
    }
    
    .professional-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: black;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .professional-header p {
        font-size: 1.1rem;
        opacity: 0.95;
        color: black;
    }
    
    /* Mensajes de chat */
    .user-message {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 5px 18px;
        margin: 1rem 0;
        margin-left: 20%;
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
    }
    
    .bot-message {
        background: #f8f9fa;
        color: #2c3e50;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 18px 5px;
        margin: 1rem 0;
        margin-right: 20%;
        border-left: 4px solid #34495e;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Credentials box */
    .credentials-box {
        background: #f8f9fa;
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        font-family: 'Courier New', monospace;
    }
    
    .credential-item {
        background: white;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        font-size: 0.95rem;
    }
    
    /* Botones */
    .stButton>button {
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(52, 73, 94, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(52, 73, 94, 0.5);
        background: linear-gradient(135deg, #2c3e50 0%, #1a252f 100%);
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        transition: all 0.3s;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Logo container */
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .logo-text {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# INICIALIZAR SESSION STATE
# ============================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'username' not in st.session_state:
    st.session_state.username = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'model_trained' not in st.session_state:
    st.session_state.model_trained = False

if 'show_confidence' not in st.session_state:
    st.session_state.show_confidence = False

if 'selected_mode' not in st.session_state:
    st.session_state.selected_mode = None  # 'chatbot' o 'buscador'

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def format_markdown_response(text):
    """Convierte markdown simple a HTML con estilos bonitos"""
    import html
    
    # Escapar HTML primero
    text = html.escape(text)
    
    # Convertir negritas **texto** a <strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #2c3e50;">\1</strong>', text)
    
    # Convertir viñetas - texto
    lines = text.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        # Detectar viñetas
        if stripped.startswith('- '):
            if not in_list:
                formatted_lines.append('<ul style="margin: 0.5rem 0; padding-left: 1.5rem;">')
                in_list = True
            content = stripped[2:]  # Quitar "- "
            formatted_lines.append(f'<li style="margin: 0.3rem 0; line-height: 1.6;">{content}</li>')
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            
            # Párrafos normales
            if stripped:
                formatted_lines.append(f'<p style="margin: 0.5rem 0; line-height: 1.6;">{line}</p>')
            else:
                formatted_lines.append('<br>')
    
    if in_list:
        formatted_lines.append('</ul>')
    
    return ''.join(formatted_lines)

# ============================================
# FUNCIONES DE API
# ============================================

def check_backend_health():
    """Verifica si el backend está activo"""
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def send_chat_message(message):
    """Envía un mensaje al chatbot"""
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={"message": message},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def train_model():
    """Llama al endpoint de entrenamiento"""
    try:
        response = requests.post(f"{API_URL}/api/train", timeout=300)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "message": "Error en el servidor"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

# ============================================
# FUNCIÓN DE LOGIN
# ============================================

def login_page():
    """Página de login profesional"""
    
    # Header
    st.markdown("""
        <div class="professional-header">
            <div class="logo-text">🏛️</div>
            <h1>GovAI</h1>
            <p>Sistema Inteligente de Consultas sobre Contratación Pública</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Container de login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:        
        st.markdown("### 🔐 Iniciar Sesión")
        st.markdown("Ingresa tus credenciales para acceder al sistema")
        
        # Mostrar credenciales disponibles
        with st.expander("📋 Ver Credenciales de Acceso", expanded=True):
            st.markdown("""
                <div class="credentials-box">
                    <p style="text-align: center; font-weight: bold; margin-bottom: 1rem; color: #667eea;">
                        Credenciales Disponibles
                    </p>
            """, unsafe_allow_html=True)
            
            for username, password in CREDENTIALS.items():
                st.markdown(f"""
                    <div class="credential-item">
                        <strong>Usuario:</strong> {username}<br>
                        <strong>Contraseña:</strong> {password}
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.info("💡 Copia y pega las credenciales en los campos de abajo")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Formulario de login
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
            
            submit = st.form_submit_button("Ingresar al Sistema")
            
            if submit:
                if username in CREDENTIALS and CREDENTIALS[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"✅ ¡Bienvenido, {username}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
            <div style="text-align: center; color: black; margin-top: 2rem; opacity: 0.8;">
                <p>🔒 Sistema Seguro | Powered by AI</p>
            </div>
        """, unsafe_allow_html=True)

# ============================================
# FUNCIÓN DE SELECCIÓN DE MODO
# ============================================

def mode_selection_page():
    """Página para seleccionar entre Chatbot y Buscador"""
    
    st.markdown("""
        <div class="professional-header" style="text-align: center; margin-bottom: 3rem;">
            <h1 style="font-size: 2.5rem; margin: 0;">Bienvenido, {}</h1>
            <p style="font-size: 1rem; margin-top: 0.5rem;">Selecciona el modo que deseas usar</p>
        </div>
    """.format(st.session_state.username), unsafe_allow_html=True)
    
    # Dos botones grandes
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        
        # Botón Chatbot
        if st.button("GovAI Chatbot", key="btn_chatbot", use_container_width=True):
            st.session_state.selected_mode = 'chatbot'
            st.rerun()
        
        st.markdown("""
            <p style="text-align: center; color: #666; margin: 0.5rem 0 2rem 0;">
                Conversa con GovAI sobre contratación pública
            </p>
        """, unsafe_allow_html=True)
        
        # Botón Buscador
        if st.button("Buscador SECOP", key="btn_buscador", use_container_width=True):
            st.session_state.selected_mode = 'buscador'
            st.rerun()
        
        st.markdown("""
            <p style="text-align: center; color: #666; margin: 0.5rem 0;">
                Busca y consulta documentos PDF directamente
            </p>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Botón de cerrar sesión
        if st.button("Cerrar Sesión", key="logout_mode_selection"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.selected_mode = None
            st.session_state.chat_history = []
            st.rerun()

# ============================================
# FUNCIÓN DE CHAT
# ============================================

def chat_page():
    """Página principal del chat"""
    
    # Navbar profesional con botón incluido
    st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
            padding: 1rem 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="
                    background: white;
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.2rem;
                ">👤</div>
                <div style="display: flex; flex-direction: column;">
                    <div style="color: white; font-weight: 600; font-size: 1rem;">{st.session_state.username}</div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="color: #bdc3c7; font-size: 0.85rem;">Usuario activo</span>
                    </div>
                </div>
            </div>
            <div style="color: white; font-size: 0.9rem;">
                <button onclick="window.location.reload();" style="
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 4px 10px;
                    font-size: 0.8rem;
                    cursor: pointer;
                ">
                Cerrar Sesión
                </button>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Botón para volver a selección de modo
    col1, col2, col3 = st.columns([2, 4, 2])
    with col2:
        if st.button("Volver", key="back_to_mode_chat"):
            st.session_state.selected_mode = None
            st.rerun()
    
    # Título principal
    st.markdown("""
        <div class="professional-header">
            <h1 style="font-size: 2rem; margin: 0;">GovAI Chatbot</h1>
            <p style="font-size: 0.9rem; margin: 0;">Asistente Inteligente de Contratación Pública</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Verificar estado del backend silenciosamente
    health = check_backend_health()
    if health and health.get('model_trained'):
        st.session_state.model_trained = True
    else:
        st.session_state.model_trained = False
    
    
    # Historial de chat
    if st.session_state.chat_history:
        for idx, entry in enumerate(st.session_state.chat_history):
            # Mensaje del usuario
            st.markdown(f"""
                <div class="user-message">
                    <strong>Tú:</strong><br>
                    {entry['message']}
                </div>
            """, unsafe_allow_html=True)
            
            # Respuesta del bot
            confidence = entry.get('confidence', 0)
            confidence_emoji = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.4 else "🔴"
            
            # Mostrar confianza si está habilitado
            confidence_text = ""
            if st.session_state.show_confidence:
                confidence_text = f" <span style='font-size: 0.85rem; color: #666;'>(Confianza: {confidence:.1%})</span>"
            
            # Efecto de escritura solo en la última respuesta
            response_text = entry['response']
            
            # Formatear con markdown bonito
            formatted_response = format_markdown_response(response_text)
            
            if idx == len(st.session_state.chat_history) - 1 and 'typing_complete' not in entry:
                # Simular escritura progresiva
                placeholder = st.empty()
                full_text = response_text
                displayed_text = ""
                
                for i in range(0, len(full_text), 3):  # Mostrar 3 caracteres a la vez
                    displayed_text = full_text[:i+3]
                    formatted_display = format_markdown_response(displayed_text)
                    placeholder.markdown(f"""
                        <div class="bot-message">
                            <strong>GovAI</strong> {confidence_emoji}{confidence_text}<br><br>
                            {formatted_display}<span style='opacity: 0.5;'>▋</span>
                        </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.01)  # Pequeña pausa entre caracteres
                
                # Marcar como completado
                entry['typing_complete'] = True
                placeholder.markdown(f"""
                    <div class="bot-message">
                        <strong>GovAI</strong> {confidence_emoji}{confidence_text}<br><br>
                        {formatted_response}
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Mostrar respuesta completa directamente
                st.markdown(f"""
                    <div class="bot-message">
                        <strong>GovAI</strong> {confidence_emoji}{confidence_text}<br><br>
                        {formatted_response}
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #666;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">💬</div>
                <h3>¡Bienvenido al Asistente SECOP!</h3>
                <p>Soy tu asistente especializado en normativa de contratación pública.</p>
                <p style="margin-top: 1rem;">
                    <strong>Puedes preguntarme sobre:</strong><br>
                    📜 Leyes y decretos<br>
                    📋 Procedimientos de contratación<br>
                    ⚖️ Normativas específicas<br>
                    🔍 Cualquier duda sobre SECOP
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.model_trained:
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Escribe tu consulta aquí...",
                placeholder="Ejemplo: ¿Qué dice la Ley 80 de 1993 sobre contratos públicos?",
                key="user_message_input"
            )
            
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                submit = st.form_submit_button("Enviar", use_container_width=True)
            
            if submit and user_input.strip():
                with st.spinner("🤔 Analizando tu pregunta..."):
                    response = send_chat_message(user_input)
                    
                    if response:
                        st.session_state.chat_history.append({
                            "message": user_input,
                            "response": response['response'],
                            "confidence": response.get('confidence', 0),
                            "timestamp": response.get('timestamp', datetime.now().isoformat())
                        })
                        st.rerun()
                    else:
                        st.error("❌ Error al procesar el mensaje. Verifica la conexión con el backend.")
            elif submit:
                st.warning("⚠️ Por favor escribe un mensaje")
    else:
        st.warning("⚠️ El modelo debe estar entrenado para hacer consultas")

# ============================================
# FUNCIÓN DE BUSCADOR
# ============================================

def buscador_page():
    """Página del buscador de documentos PDF y entidades"""
    
    # Navbar profesional
    st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #2c3e50 0%, #34495e 100%);
            padding: 1rem 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        ">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="
                    background: white;
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.2rem;
                ">👤</div>
                <div style="display: flex; flex-direction: column;">
                    <div style="color: white; font-weight: 600; font-size: 1rem;">{st.session_state.username}</div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="color: #bdc3c7; font-size: 0.85rem;">Modo: Buscador</span>
                    </div>
                </div>
            </div>
            <div style="color: white; font-size: 0.9rem;">
                <button onclick="window.location.reload();" style="
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 4px 10px;
                    font-size: 0.8rem;
                    cursor: pointer;
                ">
                Cerrar Sesión
                </button>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Título principal
    st.markdown("""
        <div class="professional-header">
            <h1 style="font-size: 2rem; margin: 0;">🔍 Buscador SECOP</h1>
            <p style="font-size: 0.9rem; margin: 0;">Consulta documentos y entidades del sistema SECOP</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs para documentos y entidades
    tab1, tab2 = st.tabs(["📄 Documentos", "🏢 Entidades"])
    
    # ============================================
    # TAB 1: DOCUMENTOS
    # ============================================
    with tab1:
        st.markdown("### Buscar Documentos PDF")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Obtener lista de documentos del backend
        try:
            response = requests.get(f"{API_URL}/api/documents", timeout=5)
            if response.status_code == 200:
                documents = response.json()
                
                if documents:
                    st.markdown("""
                        <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                            <p style="margin: 0; color: #2c3e50;">
                                <strong>📚 Documentos disponibles:</strong> {} archivos
                            </p>
                        </div>
                    """.format(len(documents)), unsafe_allow_html=True)
                    
                    # Mostrar cada documento
                    for idx, doc in enumerate(documents):
                        with st.expander(f"📄 {doc['title']}", expanded=False):
                            st.markdown(f"""
                                <div style="background: white; padding: 1rem; border-radius: 8px;">
                                    <p style="color: #666; line-height: 1.6;">
                                        {doc['preview']}
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Botón para ver documento completo (placeholder por ahora)
                            if st.button(f"Ver documento completo", key=f"view_doc_{idx}"):
                                st.info("🔜 Funcionalidad de visualización de PDF en desarrollo")
                else:
                    st.warning("⚠️ No hay documentos disponibles")
            else:
                st.error("❌ Error al obtener documentos del backend")
        except Exception as e:
            st.error(f"❌ Error de conexión: {str(e)}")
    
    # ============================================
    # TAB 2: ENTIDADES
    # ============================================
    with tab2:
        st.markdown("### Buscar Entidades SECOP")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Leer CSV de entidades
        csv_path = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "secop", "secop_sintetico_258.csv")
        
        try:
            # Leer el CSV
            df_entidades = pd.read_csv(csv_path)
            
            # Inicializar estado de paginación si no existe
            if 'entidades_page' not in st.session_state:
                st.session_state.entidades_page = 0
            
            # Configuración de paginación
            items_per_page = 10
            total_items = len(df_entidades)
            total_pages = (total_items - 1) // items_per_page + 1
            
            # Calcular índices para la página actual
            start_idx = st.session_state.entidades_page * items_per_page
            end_idx = min(start_idx + items_per_page, total_items)
            
            # Mostrar datos de la página actual
            df_page = df_entidades.iloc[start_idx:end_idx]
            
            # Mostrar tabla con estilo
            st.dataframe(
                df_page,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "NIT": st.column_config.TextColumn(
                        "NIT",
                        width="medium",
                    ),
                    "nombre": st.column_config.TextColumn(
                        "Nombre",
                        width="large",
                    ),
                    "usuarios": st.column_config.NumberColumn(
                        "Usuarios",
                        width="small",
                    ),
                }
            )

            # Controles de paginación
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Estilos CSS específicos para los botones de paginación
            st.markdown("""
                <style>
                    /* Estilos para botones de paginación */
                    div[data-testid="column"] button[kind="secondary"] {
                        font-size: 0.75rem !important;
                        padding: 0.25rem 0.5rem !important;
                        height: auto !important;
                        min-height: 2rem !important;
                    }
                    div[data-testid="column"] button[kind="secondary"] p {
                        font-size: 0.75rem !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("Primera", disabled=(st.session_state.entidades_page == 0), key="btn_primera"):
                    st.session_state.entidades_page = 0
                    st.rerun()
            
            with col2:
                if st.button("Anterior", disabled=(st.session_state.entidades_page == 0), key="btn_anterior"):
                    st.session_state.entidades_page -= 1
                    st.rerun()
            
            with col3:
                st.markdown(f"""
                    <div style="text-align: center; padding: 0.5rem;">
                        <strong>Página {st.session_state.entidades_page + 1} de {total_pages}</strong>
                        <br>
                        <span style="color: #666; font-size: 0.9rem;">
                            Mostrando {start_idx + 1}-{end_idx} de {total_items}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                if st.button("Siguiente", disabled=(st.session_state.entidades_page >= total_pages - 1), key="btn_siguiente"):
                    st.session_state.entidades_page += 1
                    st.rerun()
            
            with col5:
                if st.button("Última", disabled=(st.session_state.entidades_page >= total_pages - 1), key="btn_ultima"):
                    st.session_state.entidades_page = total_pages - 1
                    st.rerun()
                    
        except FileNotFoundError:
            st.error("❌ No se encontró el archivo de entidades")
        except Exception as e:
            st.error(f"❌ Error al cargar entidades: {str(e)}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botón para volver a selección de modo
    col1, col2, col3 = st.columns([2, 4, 2])
    with col2:
        if st.button("Volver", key="back_to_mode"):
            st.session_state.selected_mode = None
            st.rerun()

# ============================================
# LÓGICA PRINCIPAL
# ============================================

if not st.session_state.authenticated:
    login_page()
elif st.session_state.selected_mode is None:
    mode_selection_page()
elif st.session_state.selected_mode == 'chatbot':
    chat_page()
elif st.session_state.selected_mode == 'buscador':
    buscador_page()