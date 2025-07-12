import streamlit as st
import pandas as pd
from datetime import datetime
import io
from models.reporte import ReporteConsolidado
from services.archivos import ArchivosService
from services.reporte import ReporteService
from services.chat_ia import ChatIAService
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def configurar_pagina():
    """Configuración inicial de la página Streamlit"""
    st.set_page_config(
        page_title="Sistema de Reportes de Asistencias",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizado
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .upload-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .status-ok {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .chat-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .chat-message-user {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        margin-left: 2rem;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
        font-weight: 500;
    }
    .chat-message-ai {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #2c3e50;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        margin-right: 2rem;
        box-shadow: 0 4px 15px rgba(168, 237, 234, 0.3);
        font-weight: 500;
        line-height: 1.6;
    }
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px 15px 0 0;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .quick-buttons {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    .example-questions {
        background: rgba(255,255,255,0.8);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .stButton > button {
        border-radius: 25px !important;
        border: none !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    .stTextInput > div > div > input {
        border-radius: 25px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 0.75rem 1.5rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>📊 Sistema de Reportes de Asistencias</h1>
        <p>Sube tus archivos Excel y genera reportes automáticamente</p>
    </div>
    """, unsafe_allow_html=True)

def cargar_archivos_sidebar(archivos_service: ArchivosService) -> tuple:
    """Muestra los uploaders en el sidebar y devuelve los archivos cargados y la API key"""
    with st.sidebar:
        st.header("📁 Cargar Archivos Excel")
        st.markdown("---")
        
        archivos = {
            'horas': st.file_uploader(
                "📋 Reporte de Horas Trabajadas",
                type=['xlsx', 'xls'],
                key="horas",
                help="Archivo: Reporte Quincenal de Asistencias - horas trabajadas.xlsx"
            ),
            'diferencia': st.file_uploader(
                "📊 Reporte de Diferencias",
                type=['xlsx', 'xls'],
                key="diferencia",
                help="Archivo: Reporte Quincenal de Asistencias - diferencia.xlsx"
            ),
            'retardos': st.file_uploader(
                "⏰ Reporte de Retardos",
                type=['xlsx', 'xls'],
                key="retardos",
                help="Archivo: Reporte Quincenal de Asistencias - retardos.xlsx"
            ),
            'tiempo_extra': st.file_uploader(
                "⏱️ Reporte de Tiempo Extra",
                type=['xlsx', 'xls'],
                key="tiempo_extra",
                help="Archivo: Reporte Quincenal de Asistencias - tiempo extra.xlsx"
            )
        }
        
        st.markdown("---")
        st.markdown("### 🤖 Chat IA Disponible")
        api_key_usuario = st.text_input("🔑 Ingresa tu API Key de Groq:", type="password")

        if api_key_usuario:
            st.success("✅ API Key ingresada correctamente")
        else:
            st.warning("⚠️ Debes ingresar tu API Key para usar el análisis con IA")
    
    return archivos, api_key_usuario

def mostrar_estado_archivos(archivos: dict):
    """Muestra el estado de los archivos cargados"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if archivos['horas']:
            st.markdown('<p class="status-ok">✅ Horas Trabajadas</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ Horas Trabajadas</p>', unsafe_allow_html=True)
    
    with col2:
        if archivos['diferencia']:
            st.markdown('<p class="status-ok">✅ Diferencias</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ Diferencias</p>', unsafe_allow_html=True)
    
    with col3:
        if archivos['retardos']:
            st.markdown('<p class="status-ok">✅ Retardos</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ Retardos</p>', unsafe_allow_html=True)
    
    with col4:
        if archivos['tiempo_extra']:
            st.markdown('<p class="status-ok">✅ Tiempo Extra</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ Tiempo Extra</p>', unsafe_allow_html=True)
    
    st.markdown("---")

def mostrar_reporte(reporte: ReporteConsolidado):
    """Muestra el reporte consolidado en la interfaz"""
    # Convertir el modelo a DataFrame para mostrar
    df_reporte = pd.DataFrame([vars(e) for e in reporte.empleados])
    
    # Mostrar métricas generales
    st.subheader("📈 Resumen General")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Empleados", len(reporte.empleados))
    
    with col2:
        st.metric("Total Días Trabajados", reporte.total_dias_trabajados)
    
    with col3:
        st.metric("Total Faltas", reporte.total_faltas)
    
    with col4:
        st.metric("Total Retardos", reporte.total_retardos)
    
    with col5:
        st.metric("Registros Mal", reporte.total_registro_mal)

    st.markdown("---")

    # Mostrar tabla del reporte
    st.subheader("📋 Reporte Detallado de Asistencias")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_nombre = st.text_input("🔍 Buscar por nombre:", placeholder="Escribe el nombre del empleado...")
    
    with col2:
        mostrar_todos = st.checkbox("Mostrar todos los empleados", value=True)

    # Aplicar filtros
    df_filtrado = df_reporte.copy()
    if filtro_nombre and not mostrar_todos:
        df_filtrado = df_filtrado[df_filtrado['nombre'].str.contains(filtro_nombre, case=False, na=False)]

    # Mostrar tabla
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True,
        column_config={
            "nombre": st.column_config.TextColumn("Nombre", width="medium"),
            "horas_trabajadas": st.column_config.TextColumn("Horas", width="small"),
            "dias_trabajados": st.column_config.NumberColumn("D.Trab", width="small"),
            "dias_descanso": st.column_config.NumberColumn("D.Desc", width="small"),
            "faltas": st.column_config.NumberColumn("Faltas", width="small"),
            "registro_mal": st.column_config.NumberColumn("R.Mal", width="small"),
            "retardos": st.column_config.NumberColumn("Retardos", width="small"),
            "diferencia_total": st.column_config.TextColumn("Dif.Total", width="small"),
            "tiempo_extra": st.column_config.TextColumn("T.Extra", width="small")
        }
    )

    # Botón para descargar reporte
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        # Crear archivo Excel para descarga
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_reporte.to_excel(writer, sheet_name='Reporte_Asistencias', index=False)
        
        st.download_button(
            label="📥 Descargar Reporte Excel",
            data=output.getvalue(),
            file_name=f"reporte_asistencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

def mostrar_mensaje_chat(role: str, message):
    """Muestra mensajes del chat con formato mejorado"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message-user">
            <strong>🧑‍💼 Tu pregunta:</strong><br>{message}
        </div>
        """, unsafe_allow_html=True)
    else:
        if isinstance(message, dict) and message.get('tipo') == 'ia_analysis':
            # Respuesta de IA estructurada
            st.markdown(f"""
            <div class="chat-message-ai">
                <strong>🤖 Análisis realizado:</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar código en expander
            with st.expander("💻 Ver consulta ejecutada", expanded=False):
                st.code(message['codigo'], language='python')
            
            # Mostrar texto si existe
            if message['texto'] and message['texto'].strip():
                texto_limpio = message['texto'].strip()
                lineas = texto_limpio.split('\n')
                
                texto_descriptivo = []
                datos_tabulares = []
                
                for linea in lineas:
                    linea = linea.strip()
                    if linea and not any(word in linea for word in ['Nombre', 'Faltas', 'Retardos', 'Horas']):
                        texto_descriptivo.append(linea)
                    elif linea:
                        datos_tabulares.append(linea)
                
                if texto_descriptivo:
                    texto_final = '\n'.join(texto_descriptivo)
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); 
                               padding: 1.5rem; border-radius: 15px; margin: 0.5rem 0;
                               border-left: 4px solid #667eea; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <strong style="color: #1565c0;">📝 Análisis:</strong><br>
                        <div style="color: #2c3e50; font-size: 1rem; line-height: 1.6; margin-top: 0.5rem;">
                            {texto_final.replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Mostrar DataFrame si existe
            if message['dataframe'] is not None and not message['dataframe'].empty:
                st.markdown("**📊 Resultado:**")
                st.dataframe(
                    message['dataframe'], 
                    use_container_width=True,
                    hide_index=True
                )
        else:
            # Respuesta de IA simple (texto)
            st.markdown(f"""
            <div class="chat-message-ai">
                <strong>🤖 Respuesta:</strong><br>{message}
            </div>
            """, unsafe_allow_html=True)

def mostrar_chat_ia(chat_ia_service: ChatIAService, reporte: ReporteConsolidado):
    """Muestra la interfaz del chat de IA"""
    # Convertir el modelo a DataFrame para el chat
    df_reporte = pd.DataFrame([vars(e) for e in reporte.empleados])
    
    st.markdown("---")
    
    # Header del chat
    st.markdown("""
    <div class="chat-header">
        🤖 Asistente de Análisis de RH
        <br><small>Haz preguntas sobre tus datos de asistencias</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Contenedor del chat
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Inicializar historial de chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Ejemplos de preguntas en cards
    st.markdown("""
    <div class="example-questions">
        <h4>💡 Preguntas que puedes hacer:</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
                • ¿Quién tiene más retardos?<br>
                • ¿Cuál es el promedio de faltas?<br>
                • ¿Qué empleados trabajan más horas extra?<br>
                • Identifica problemas de asistencia
            </div>
            <div>
                • ¿Cuál es el patrón de ausentismo?<br>
                • Recomienda acciones correctivas<br>
                • Haz un análisis de productividad<br>
                • Compara rendimiento de empleados
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botones de preguntas rápidas
    st.markdown("#### 🚀 Análisis rápido:")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Resumen General", use_container_width=True):
            pregunta = "Dame un resumen general del reporte de asistencias con los principales hallazgos y estadísticas importantes"
            st.session_state.chat_history.append(("user", pregunta))
            with st.spinner("🔍 Analizando datos..."):
                respuesta = chat_ia_service.generar_consulta_ia(pregunta, df_reporte)
                st.session_state.chat_history.append(("assistant", {
                    'tipo': 'ia_analysis',
                    'codigo': respuesta[2],
                    'texto': respuesta[0],
                    'dataframe': respuesta[1]
                }))
            st.rerun()
    
    with col2:
        if st.button("⚠️ Alertas Críticas", use_container_width=True):
            pregunta = "Identifica empleados con problemas críticos de asistencia, puntualidad o registro. Dame nombres específicos y qué acciones recomiendas"
            st.session_state.chat_history.append(("user", pregunta))
            with st.spinner("🔍 Identificando problemas..."):
                respuesta = chat_ia_service.generar_consulta_ia(pregunta, df_reporte)
                st.session_state.chat_history.append(("assistant", {
                    'tipo': 'ia_analysis',
                    'codigo': respuesta[2],
                    'texto': respuesta[0],
                    'dataframe': respuesta[1]
                }))
            st.rerun()
    
    with col3:
        if st.button("🏆 Top Performers", use_container_width=True):
            pregunta = "¿Cuáles son los empleados con mejor desempeño en asistencia y puntualidad? Dame un ranking de los top 5"
            st.session_state.chat_history.append(("user", pregunta))
            with st.spinner("🔍 Evaluando desempeño..."):
                respuesta = chat_ia_service.generar_consulta_ia(pregunta, df_reporte)
                st.session_state.chat_history.append(("assistant", {
                    'tipo': 'ia_analysis',
                    'codigo': respuesta[2],
                    'texto': respuesta[0],
                    'dataframe': respuesta[1]
                }))
            st.rerun()
    
    with col4:
        if st.button("📈 Métricas Clave", use_container_width=True):
            pregunta = "Calcula y presenta las métricas más importantes: promedios, porcentajes, tendencias y comparaciones entre empleados"
            st.session_state.chat_history.append(("user", pregunta))
            with st.spinner("🔍 Calculando métricas..."):
                respuesta = chat_ia_service.generar_consulta_ia(pregunta, df_reporte)
                st.session_state.chat_history.append(("assistant", {
                    'tipo': 'ia_analysis',
                    'codigo': respuesta[2],
                    'texto': respuesta[0],
                    'dataframe': respuesta[1]
                }))
            st.rerun()
    
    # Mostrar historial de chat
    for i, (role, message) in enumerate(st.session_state.chat_history):
        mostrar_mensaje_chat(role, message)
    
    # Input para nueva pregunta
    st.markdown("#### ✍️ Haz tu pregunta personalizada:")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        nueva_pregunta = st.text_input(
            "",
            placeholder="💭 Ej: ¿Cuáles son los empleados con más retardos y qué patrones observas?",
            key="nueva_pregunta",
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("🚀 Analizar", use_container_width=True, type="primary"):
            if nueva_pregunta.strip():
                st.session_state.chat_history.append(("user", nueva_pregunta))
                with st.spinner("🤖 Generando análisis..."):
                    respuesta = chat_ia_service.generar_consulta_ia(nueva_pregunta, df_reporte)
                    st.session_state.chat_history.append(("assistant", {
                        'tipo': 'ia_analysis',
                        'codigo': respuesta[2],
                        'texto': respuesta[0],
                        'dataframe': respuesta[1]
                    }))
                st.rerun()
    
    # Botones de acción
    if st.session_state.chat_history:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Limpiar Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def mostrar_instrucciones():
    """Muestra instrucciones cuando no hay archivos cargados"""
    st.info("👆 Por favor, carga los 4 archivos Excel requeridos en la barra lateral para generar el reporte.")
    
    st.markdown("""
    ### 📋 Instrucciones:
    
    1. **Ingresa tu API Key**: Usa la barra lateral para ingresar tu API Key de Groq
    2. **Carga los archivos**: Usa la barra lateral para subir los 4 archivos Excel requeridos
    3. **Archivos necesarios**:
       - 📋 Reporte de Horas Trabajadas
       - 📊 Reporte de Diferencias  
       - ⏰ Reporte de Retardos
       - ⏱️ Reporte de Tiempo Extra
    4. **Procesamiento automático**: Una vez cargados todos los archivos, el reporte se generará automáticamente
    5. **Análisis con IA**: Usa el chat rediseñado para hacer preguntas sobre los datos
    6. **Descarga**: Podrás descargar el reporte final en formato Excel
    """)

def main():
    # Configuración inicial de la página
    configurar_pagina()
    
    # Inicializar servicios
    archivos_service = ArchivosService()
    reporte_service = ReporteService()
    
    # Cargar archivos desde sidebar y obtener API key
    archivos, api_key_usuario = cargar_archivos_sidebar(archivos_service)
    
    # Inicializar chat IA service con la API key
    chat_ia_service = ChatIAService(api_key=api_key_usuario) if api_key_usuario else None
    
    # Mostrar estado de los archivos
    mostrar_estado_archivos(archivos)
    
    # Procesar si todos los archivos están cargados
    if archivos_service.validar_archivos_cargados(*archivos.values()):
        with st.spinner('Procesando archivos...'):
            try:
                # Cargar y procesar archivos
                df_horas = archivos_service.cargar_archivo_excel(archivos['horas'])
                df_diferencia = archivos_service.cargar_archivo_excel(archivos['diferencia'])
                df_retardos = archivos_service.cargar_archivo_excel(archivos['retardos'])
                df_tiempo_extra = archivos_service.cargar_archivo_excel(archivos['tiempo_extra'])
                
                if all(df is not None for df in [df_horas, df_diferencia, df_retardos, df_tiempo_extra]):
                    # Generar reporte consolidado
                    reporte = reporte_service.generar_reporte_consolidado(
                        df_horas, df_diferencia, df_retardos, df_tiempo_extra
                    )
                    
                    # Mostrar reporte
                    mostrar_reporte(reporte)
                    
                    # Mostrar chat IA si está configurado
                    if chat_ia_service and api_key_usuario:
                        mostrar_chat_ia(chat_ia_service, reporte)
                    else:
                        st.warning("ℹ️ Ingresa tu API Key de Groq en la barra lateral para habilitar el chat de análisis")
                    
                    st.success("✅ Procesamiento completado exitosamente")
                else:
                    st.error("❌ Error al procesar uno o más archivos. Verifica que los archivos sean válidos.")
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")
    else:
        mostrar_instrucciones()

if __name__ == "__main__":
    main()