import streamlit as st
import pandas as pd
import io
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Sistema de Reportes de Asistencias",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # API KEY DE GROQ
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # CSS personalizado optimizado
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

    # Sidebar para cargar archivos
    with st.sidebar:
        st.header("📁 Cargar Archivos Excel")
        st.markdown("---")
        
        archivo_horas = st.file_uploader(
            "📋 Reporte de Horas Trabajadas",
            type=['xlsx', 'xls'],
            key="horas",
            help="Archivo: Reporte Quincenal de Asistencias - horas trabajadas.xlsx"
        )
        
        archivo_diferencia = st.file_uploader(
            "📊 Reporte de Diferencias",
            type=['xlsx', 'xls'],
            key="diferencia",
            help="Archivo: Reporte Quincenal de Asistencias - diferencia.xlsx"
        )
        
        archivo_retardos = st.file_uploader(
            "⏰ Reporte de Retardos",
            type=['xlsx', 'xls'],
            key="retardos",
            help="Archivo: Reporte Quincenal de Asistencias - retardos.xlsx"
        )
        
        archivo_tiempo_extra = st.file_uploader(
            "⏱️ Reporte de Tiempo Extra",
            type=['xlsx', 'xls'],
            key="tiempo_extra",
            help="Archivo: Reporte Quincenal de Asistencias - tiempo extra.xlsx"
        )
        
        st.markdown("---")
        st.markdown("### 🤖 Chat IA Disponible")
        if GROQ_API_KEY and GROQ_API_KEY != "tu_api_key_aqui":
            st.success("✅ IA configurada y lista")
        else:
            st.warning("⚠️ Configura tu API Key en el código")

    def cargar_y_limpiar(archivo):
        try:
            df = pd.read_excel(archivo, sheet_name=0, header=2)
            df = df[df['Nombre'].notna()].reset_index(drop=True)

            def es_nombre_valido(nombre):
                nombre_str = str(nombre).strip()
                if len(nombre_str) < 3 or nombre_str.isdigit():
                    return False
                numeros_y_simbolos = sum(1 for c in nombre_str if c.isdigit() or c in ':-.,;')
                letras = sum(1 for c in nombre_str if c.isalpha())
                if letras == 0 or numeros_y_simbolos > letras:
                    return False
                patrones_invalidos = ['página', ':', '--', ';;', '..']
                if any(pat in nombre_str.lower() for pat in patrones_invalidos):
                    return False
                return True

            ultima_fila_valida = -1
            for i, fila in df.iterrows():
                if es_nombre_valido(fila['Nombre']):
                    ultima_fila_valida = i
                else:
                    break

            if ultima_fila_valida != -1:
                df = df.iloc[:ultima_fila_valida + 1].reset_index(drop=True)
            else:
                df = df.iloc[0:0]

            df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
            st.sidebar.success(f"✅ Archivo procesado: {len(df)} empleados encontrados")
            return df

        except Exception as e:
            st.error(f"Error al cargar archivo: {str(e)}")
            return None

    def tiempo_a_minutos(tiempo_str):
        if pd.isna(tiempo_str) or tiempo_str in ['F', 'N/L', 'J']:
            return 0
        try:
            tiempo_str = str(tiempo_str).strip()
            es_negativo = tiempo_str.startswith('-')
            if es_negativo:
                tiempo_str = tiempo_str[1:]
            horas, minutos = map(int, tiempo_str.split(':'))
            total = horas * 60 + minutos
            return -total if es_negativo else total
        except:
            return 0

    def contar_dias_trabajados(fila):
        return sum(1 for col in fila.index if str(col).isdigit() and pd.notna(fila[col]) and ':' in str(fila[col]) and fila[col] not in ['F', 'N/L', 'J'])

    def contar_dias_descanso(fila):
        return sum(1 for col in fila.index if str(col).isdigit() and fila[col] == 'N/L')

    def contar_registro_mal(fila):
        return sum(1 for col in fila.index if str(col).isdigit() and pd.notna(fila[col]) and fila[col] not in ['F', 'N/L', 'J'] and tiempo_a_minutos(fila[col]) <= -120)

    def contar_retardos(fila):
        return sum(1 for col in fila.index if str(col).isdigit() and pd.notna(fila[col]) and fila[col] not in ['F', 'N/L', 'J'] and tiempo_a_minutos(fila[col]) >= 10)

    def consultar_groq(pregunta, datos_contexto, api_key):
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        contexto = f"""
        Eres un analista de recursos humanos especializado en reportes de asistencias. 
        Tienes acceso a los siguientes datos de un reporte de asistencias:

        RESUMEN DE DATOS:
        - Total de empleados: {len(datos_contexto)}
        - Total días trabajados: {datos_contexto['Días Trabajados'].sum()}
        - Total faltas: {datos_contexto['Faltas'].sum()}
        - Total retardos: {datos_contexto['Retardos'].sum()}
        - Total registros mal: {datos_contexto['Registro Mal'].sum()}

        DATOS DETALLADOS:
        {datos_contexto.to_string()}

        INSTRUCCIONES:
        - Responde siempre en español
        - Sé específico y usa los datos proporcionados
        - Si mencionas empleados específicos, usa sus nombres reales de los datos
        - Proporciona insights útiles para recursos humanos
        - Si te preguntan por estadísticas, calcula y presenta los resultados claramente
        - Puedes sugerir acciones correctivas basadas en los datos
        """
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "messages": [
                {"role": "system", "content": contexto},
                {"role": "user", "content": pregunta}
            ],
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.7,
            "max_completion_tokens": 1024,
            "top_p": 1,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            return f"Error al conectar con Groq: {str(e)}"
        except Exception as e:
            return f"Error inesperado: {str(e)}"

    # Estado de los archivos
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if archivo_horas:
            st.markdown('<p class="status-ok">✅ Horas Trabajadas</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ Horas Trabajadas</p>', unsafe_allow_html=True)
    
    with col2:
        if archivo_diferencia:
            st.markdown('<p class="status-ok">✅ Diferencias</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ Diferencias</p>', unsafe_allow_html=True)
    
    with col3:
        if archivo_retardos:
            st.markdown('<p class="status-ok">✅ Retardos</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ Retardos</p>', unsafe_allow_html=True)
    
    with col4:
        if archivo_tiempo_extra:
            st.markdown('<p class="status-ok">✅ Tiempo Extra</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ Tiempo Extra</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Procesar archivos cuando todos estén cargados
    if all([archivo_horas, archivo_diferencia, archivo_retardos, archivo_tiempo_extra]):
        
        with st.spinner('Procesando archivos... Por favor espera'):
            df_horas = cargar_y_limpiar(archivo_horas)
            df_diferencia = cargar_y_limpiar(archivo_diferencia)
            df_retardos = cargar_y_limpiar(archivo_retardos)
            df_tiempo_extra = cargar_y_limpiar(archivo_tiempo_extra)

            if all(df is not None for df in [df_horas, df_diferencia, df_retardos, df_tiempo_extra]):
                
                # Usar df_horas como base principal (todos los empleados deben estar aquí)
                reporte_data = []
                
                # Iterar sobre cada empleado en df_horas
                for i in range(len(df_horas)):
                    nombre = df_horas.iloc[i]['Nombre']
                    fila_horas = df_horas.iloc[i]
                    
                    # Buscar la fila correspondiente en cada DataFrame
                    # Si no existe, crear una fila vacía con valores por defecto
                    
                    # Buscar en df_diferencia
                    fila_diferencia = None
                    for j in range(len(df_diferencia)):
                        if df_diferencia.iloc[j]['Nombre'] == nombre:
                            fila_diferencia = df_diferencia.iloc[j]
                            break
                    
                    # Buscar en df_retardos
                    fila_retardos = None
                    for j in range(len(df_retardos)):
                        if df_retardos.iloc[j]['Nombre'] == nombre:
                            fila_retardos = df_retardos.iloc[j]
                            break
                    
                    # Buscar en df_tiempo_extra
                    fila_tiempo_extra = None
                    for j in range(len(df_tiempo_extra)):
                        if df_tiempo_extra.iloc[j]['Nombre'] == nombre:
                            fila_tiempo_extra = df_tiempo_extra.iloc[j]
                            break
                    
                    # Extraer datos de df_horas (siempre existe)
                    horas_trabajadas = fila_horas.get('Total de\nHoras') or fila_horas.get('Total de Horas') or 'N/A'
                    dias_trabajados = contar_dias_trabajados(fila_horas)
                    dias_descanso = contar_dias_descanso(fila_horas)
                    dias_falta = fila_horas.get('Faltas', 0) or 0
                    
                    # Extraer datos de df_diferencia (si existe)
                    if fila_diferencia is not None:
                        dias_registro_mal = contar_registro_mal(fila_diferencia)
                        diferencia_total = fila_diferencia.get('Tiempo\nTotal') or fila_diferencia.get('Tiempo Total') or 'N/A'
                    else:
                        dias_registro_mal = 0
                        diferencia_total = '00:00'
                    
                    # Extraer datos de df_retardos (si existe)
                    if fila_retardos is not None:
                        dias_con_retardo = contar_retardos(fila_retardos)
                    else:
                        dias_con_retardo = 0
                    
                    # Extraer datos de df_tiempo_extra (si existe)
                    if fila_tiempo_extra is not None:
                        tiempo_extra = fila_tiempo_extra.get('Tiempo\nTotal') or fila_tiempo_extra.get('Tiempo Total') or 'N/A'
                    else:
                        tiempo_extra = '00:00'
                    
                    reporte_data.append({
                        'Nombre': nombre,
                        'Horas Trabajadas': horas_trabajadas,
                        'Días Trabajados': dias_trabajados,
                        'Días Descanso': dias_descanso,
                        'Faltas': dias_falta,
                        'Registro Mal': dias_registro_mal,
                        'Retardos': dias_con_retardo,
                        'Diferencia Total': diferencia_total,
                        'Tiempo Extra': tiempo_extra
                    })

                df_reporte = pd.DataFrame(reporte_data)

                # Mostrar métricas generales
                st.subheader("📈 Resumen General")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Total Empleados", len(df_reporte))
                
                with col2:
                    total_dias_trabajados = df_reporte['Días Trabajados'].sum()
                    st.metric("Total Días Trabajados", total_dias_trabajados)
                
                with col3:
                    total_faltas = df_reporte['Faltas'].sum()
                    st.metric("Total Faltas", total_faltas)
                
                with col4:
                    total_retardos = df_reporte['Retardos'].sum()
                    st.metric("Total Retardos", total_retardos)
                
                with col5:
                    total_registro_mal = df_reporte['Registro Mal'].sum()
                    st.metric("Registros Mal", total_registro_mal)

                st.markdown("---")

                # Mostrar tabla del reporte
                st.subheader("📋 Reporte Detallado de Asistencias")
                
                col1, col2 = st.columns(2)
                with col1:
                    filtro_nombre = st.text_input("🔍 Buscar por nombre:", placeholder="Escribe el nombre del empleado...")
                
                with col2:
                    mostrar_todos = st.checkbox("Mostrar todos los empleados", value=True)

                df_filtrado = df_reporte.copy()
                if filtro_nombre and not mostrar_todos:
                    df_filtrado = df_filtrado[df_filtrado['Nombre'].str.contains(filtro_nombre, case=False, na=False)]

                st.dataframe(
                    df_filtrado,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Nombre": st.column_config.TextColumn("Nombre", width="medium"),
                        "Horas Trabajadas": st.column_config.TextColumn("Horas", width="small"),
                        "Días Trabajados": st.column_config.NumberColumn("D.Trab", width="small"),
                        "Días Descanso": st.column_config.NumberColumn("D.Desc", width="small"),
                        "Faltas": st.column_config.NumberColumn("Faltas", width="small"),
                        "Registro Mal": st.column_config.NumberColumn("R.Mal", width="small"),
                        "Retardos": st.column_config.NumberColumn("Retardos", width="small"),
                        "Diferencia Total": st.column_config.TextColumn("Dif.Total", width="small"),
                        "Tiempo Extra": st.column_config.TextColumn("T.Extra", width="small")
                    }
                )

                # Diagnóstico de datos para debug
                with st.expander("🔍 Diagnóstico de Datos (Debug)"):
                    st.write("**Empleados por reporte:**")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.write(f"**Horas:** {len(df_horas)} empleados")
                        st.write("Nombres:")
                        for nombre in df_horas['Nombre'].tolist()[:5]:
                            st.write(f"- {nombre}")
                        if len(df_horas) > 5:
                            st.write(f"... y {len(df_horas) - 5} más")
                    
                    with col2:
                        st.write(f"**Diferencia:** {len(df_diferencia)} empleados")
                        st.write("Nombres:")
                        for nombre in df_diferencia['Nombre'].tolist()[:5]:
                            st.write(f"- {nombre}")
                        if len(df_diferencia) > 5:
                            st.write(f"... y {len(df_diferencia) - 5} más")
                    
                    with col3:
                        st.write(f"**Retardos:** {len(df_retardos)} empleados")
                        st.write("Nombres:")
                        for nombre in df_retardos['Nombre'].tolist()[:5]:
                            st.write(f"- {nombre}")
                        if len(df_retardos) > 5:
                            st.write(f"... y {len(df_retardos) - 5} más")
                    
                    with col4:
                        st.write(f"**Tiempo Extra:** {len(df_tiempo_extra)} empleados")
                        st.write("Nombres:")
                        for nombre in df_tiempo_extra['Nombre'].tolist()[:5]:
                            st.write(f"- {nombre}")
                        if len(df_tiempo_extra) > 5:
                            st.write(f"... y {len(df_tiempo_extra) - 5} más")
                    
                    # Mostrar empleados que no aparecen en algunos reportes
                    empleados_horas = set(df_horas['Nombre'].tolist())
                    empleados_diferencia = set(df_diferencia['Nombre'].tolist())
                    empleados_retardos = set(df_retardos['Nombre'].tolist())
                    empleados_tiempo_extra = set(df_tiempo_extra['Nombre'].tolist())
                    
                    st.write("**Empleados que faltan en cada reporte:**")
                    
                    faltantes_diferencia = empleados_horas - empleados_diferencia
                    faltantes_retardos = empleados_horas - empleados_retardos
                    faltantes_tiempo_extra = empleados_horas - empleados_tiempo_extra
                    
                    if faltantes_diferencia:
                        st.write(f"**No están en Diferencia:** {', '.join(list(faltantes_diferencia)[:3])}")
                    if faltantes_retardos:
                        st.write(f"**No están en Retardos:** {', '.join(list(faltantes_retardos)[:3])}")
                    if faltantes_tiempo_extra:
                        st.write(f"**No están en Tiempo Extra:** {', '.join(list(faltantes_tiempo_extra)[:3])}")

                # Botón para descargar reporte
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col2:
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

                # Vista previa de archivos cargados
                with st.expander("👀 Vista previa de archivos cargados"):
                    tab1, tab2, tab3, tab4 = st.tabs(["Horas", "Diferencias", "Retardos", "Tiempo Extra"])
                    
                    with tab1:
                        st.dataframe(df_horas, use_container_width=True)
                    with tab2:
                        st.dataframe(df_diferencia, use_container_width=True)
                    with tab3:
                        st.dataframe(df_retardos, use_container_width=True)
                    with tab4:
                        st.dataframe(df_tiempo_extra, use_container_width=True)

                # Chat de análisis con IA
                st.markdown("---")
                
                if GROQ_API_KEY and GROQ_API_KEY != "tu_api_key_aqui":
                    st.markdown("""
                    <div class="chat-header">
                        🤖 Asistente de Análisis de RH
                        <br><small>Haz preguntas sobre tus datos de asistencias</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                    
                    if "chat_history" not in st.session_state:
                        st.session_state.chat_history = []
                    
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
                    
                    st.markdown("#### 🚀 Análisis rápido:")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("📊 Resumen General", use_container_width=True):
                            pregunta = "Dame un resumen general del reporte de asistencias con los principales hallazgos y estadísticas importantes"
                            st.session_state.chat_history.append(("user", pregunta))
                            with st.spinner("🔍 Analizando datos..."):
                                respuesta = consultar_groq(pregunta, df_reporte, GROQ_API_KEY)
                                st.session_state.chat_history.append(("assistant", respuesta))
                            st.rerun()
                    
                    with col2:
                        if st.button("⚠️ Alertas Críticas", use_container_width=True):
                            pregunta = "Identifica empleados con problemas críticos de asistencia, puntualidad o registro. Dame nombres específicos y qué acciones recomiendas"
                            st.session_state.chat_history.append(("user", pregunta))
                            with st.spinner("🔍 Identificando problemas..."):
                                respuesta = consultar_groq(pregunta, df_reporte, GROQ_API_KEY)
                                st.session_state.chat_history.append(("assistant", respuesta))
                            st.rerun()
                    
                    with col3:
                        if st.button("🏆 Top Performers", use_container_width=True):
                            pregunta = "¿Cuáles son los empleados con mejor desempeño en asistencia y puntualidad? Dame un ranking de los top 5"
                            st.session_state.chat_history.append(("user", pregunta))
                            with st.spinner("🔍 Evaluando desempeño..."):
                                respuesta = consultar_groq(pregunta, df_reporte, GROQ_API_KEY)
                                st.session_state.chat_history.append(("assistant", respuesta))
                            st.rerun()
                    
                    with col4:
                        if st.button("📈 Métricas Clave", use_container_width=True):
                            pregunta = "Calcula y presenta las métricas más importantes: promedios, porcentajes, tendencias y comparaciones entre empleados"
                            st.session_state.chat_history.append(("user", pregunta))
                            with st.spinner("🔍 Calculando métricas..."):
                                respuesta = consultar_groq(pregunta, df_reporte, GROQ_API_KEY)
                                st.session_state.chat_history.append(("assistant", respuesta))
                            st.rerun()
                    
                    if st.session_state.chat_history:
                        st.markdown("#### 💬 Conversación:")
                        for i, (role, message) in enumerate(st.session_state.chat_history):
                            if role == "user":
                                st.markdown(f"""
                                <div class="chat-message-user">
                                    <strong>🧑‍💼 Tu pregunta:</strong><br>{message}
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="chat-message-ai">
                                    <strong>🤖 Análisis:</strong><br>{message}
                                </div>
                                """, unsafe_allow_html=True)
                    
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
                                    respuesta = consultar_groq(nueva_pregunta, df_reporte, GROQ_API_KEY)
                                    st.session_state.chat_history.append(("assistant", respuesta))
                                st.rerun()
                    
                    if st.session_state.chat_history:
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            if st.button("🗑️ Limpiar Chat", use_container_width=True):
                                st.session_state.chat_history = []
                                st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                else:
                    st.markdown("""
                    <div class="chat-container">
                        <div class="chat-header">
                            🔧 Configuración Requerida
                        </div>
                        <div style="padding: 2rem; text-align: center;">
                            <h3>🔑 API Key de Groq Requerida</h3>
                            <p>Para usar el chat de análisis, necesitas configurar tu API Key de Groq en el código.</p>
                            
                            <h4>🚀 Pasos para configurar:</h4>
                            <div style="text-align: left; max-width: 600px; margin: 0 auto;">
                                <ol>
                                    <li>Ve a <a href="https://console.groq.com" target="_blank">console.groq.com</a></li>
                                    <li>Regístrate o inicia sesión</li>
                                    <li>Crea una nueva API Key</li>
                                    <li>Reemplaza "tu_api_key_aqui" en el código con tu API Key real</li>
                                    <li>Reinicia la aplicación</li>
                                </ol>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    else:
        st.info("👆 Por favor, carga los 4 archivos Excel requeridos en la barra lateral para generar el reporte.")
        
        st.markdown("""
        ### 📋 Instrucciones:
        
        1. **Configura tu API Key**: Cambia "tu_api_key_aqui" en el código por tu API Key real de Groq
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

if __name__ == "__main__":
    main()