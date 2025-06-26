import streamlit as st
import pandas as pd
import numpy as np
import io
import requests
import json
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

    load_dotenv()  # Carga las variables del archivo .env

    # API KEY DE GROQ
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
 

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
    
    /* Estilos del chat mejorados */
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
        if GROQ_API_KEY != "tu_api_key_aqui":
            st.success("✅ IA configurada y lista")
        else:
            st.warning("⚠️ Configura tu API Key en el código")

    def cargar_y_limpiar(archivo):
        try:
            # Cargar el archivo sin eliminar columnas todavía
            df = pd.read_excel(archivo, sheet_name=0, header=2)

            # Filtrar filas donde el campo 'Nombre' no sea nulo
            df = df[df['Nombre'].notna()].reset_index(drop=True)

            # Función para validar si es un nombre real
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

            # Encontrar la última fila válida con nombre
            ultima_fila_valida = -1
            for i, fila in df.iterrows():
                if es_nombre_valido(fila['Nombre']):
                    ultima_fila_valida = i
                else:
                    break

            # Cortar solo hasta la última fila válida
            if ultima_fila_valida != -1:
                df = df.iloc[:ultima_fila_valida + 1].reset_index(drop=True)
            else:
                df = df.iloc[0:0]

            # Eliminar columnas sin nombre claro
            df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

            st.sidebar.success(f"✅ Archivo procesado: {len(df)} empleados encontrados")
            return df

        except Exception as e:
            st.error(f"Error al cargar archivo: {str(e)}")
            return None

    # Función para convertir HH:MM a minutos
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

    # Funciones de conteo
    def contar_dias_trabajados(fila):
        return sum(1 for col in fila.index if str(col).isdigit() and pd.notna(fila[col]) and ':' in str(fila[col]) and fila[col] not in ['F', 'N/L', 'J'])

    def contar_dias_descanso(fila):
        return sum(1 for col in fila.index if str(col).isdigit() and fila[col] == 'N/L')

    def contar_registro_mal(fila):
        return sum(1 for col in fila.index if str(col).isdigit() and pd.notna(fila[col]) and fila[col] not in ['F', 'N/L', 'J'] and tiempo_a_minutos(fila[col]) <= -120)

    def contar_retardos(fila):
        return sum(1 for col in fila.index if str(col).isdigit() and pd.notna(fila[col]) and fila[col] not in ['F', 'N/L', 'J'] and tiempo_a_minutos(fila[col]) >= 10)
   

    # Funcion para obtener info del dataframe 
    def obtener_info_dataframe(df):
        """Obtiene información detallada del DataFrame - VERSIÓN CORREGIDA"""
        from io import StringIO
        import sys
        
        # Capturar info() correctamente
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        
        # CORRECCIÓN: Ahora sí ejecuta df.info()
        df.info()
        
        sys.stdout = old_stdout
        info_str = buffer.getvalue()
        
        # Obtener dtypes
        dtypes_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            unique_count = df[col].nunique()
            sample_values = df[col].dropna().head(3).tolist()
            dtypes_info.append(f"  {col}: {dtype} (únicos: {unique_count}, ejemplos: {sample_values})")
        
        return info_str, "\n".join(dtypes_info)

    # Función para generar consulta con IA 
    def generar_consulta_con_ia(pregunta, df_reporte, api_key):
        """Genera consulta con IA - VERSIÓN MEJORADA"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Obtener información del DataFrame
        info_str, dtypes_detail = obtener_info_dataframe(df_reporte)
        
        # Obtener describe solo para columnas numéricas
        describe_str = ""
        try:
            numeric_cols = df_reporte.select_dtypes(include=['int64', 'float64']).columns.tolist()
            if numeric_cols:
                describe_str = str(df_reporte[numeric_cols].describe())
        except:
            describe_str = "No hay columnas numéricas para describir"
        
        # CONTEXTO MEJORADO CON MEJOR MANEJO DE TIEMPOS
        contexto = f"""
    Eres un experto en pandas y análisis de datos de RH. Genera SOLO código Python ejecutable para responder preguntas sobre el DataFrame 'df_reporte'.

    INFORMACIÓN DEL DATAFRAME:
    Filas: {len(df_reporte)}
    Columnas: {list(df_reporte.columns)}

    TIPOS DE DATOS:
    {df_reporte.dtypes.to_string()}

    MUESTRA DE DATOS:
    {df_reporte.head(2).to_string()}

    ESTADÍSTICAS (solo columnas numéricas):
    {describe_str}

    FUNCIONES AUXILIARES DISPONIBLES:
    1. convertir_tiempo_a_minutos(tiempo_str) - Convierte "HH:MM" a minutos
    2. convertir_tiempo_a_horas_decimales(tiempo_str) - Convierte "HH:MM" a horas decimales
    3. obtener_empleado_max_tiempo_extra() - Obtiene empleado con más tiempo extra
    4. obtener_empleado_max_horas_trabajadas() - Obtiene empleado con más horas trabajadas
    5. obtener_top_empleados_por_columna(columna, n=5, orden='desc') - Top N empleados por columna

    REGLAS IMPORTANTES:
    1. USA SOLO el DataFrame 'df_reporte'
    2. SIEMPRE termina con print() del resultado
    3. SIEMPRE verifica que las columnas existan antes de usarlas
    4. Para columnas de tiempo (formato HH:MM), usa las funciones auxiliares
    5. Para rankings, usa .head(5) o .tail(5)
    6. Para preguntas sobre tiempo extra o horas trabajadas, usa las funciones auxiliares

    EJEMPLOS DE CÓDIGO CORRECTO:

    Para tiempo extra:
    ```python
    resultado = obtener_empleado_max_tiempo_extra()
    print(resultado)
    ```

    Para top retardos:
    ```python
    if 'Retardos' in df_reporte.columns:
        print("Top 5 empleados con más retardos:")
        print(df_reporte.nlargest(5, 'Retardos')[['Nombre', 'Retardos']])
    else:
        print("La columna 'Retardos' no existe")
    ```

    Para análisis de horas trabajadas:
    ```python
    if 'Horas Trabajadas' in df_reporte.columns:
        # Crear columna temporal con minutos
        df_temp = df_reporte.copy()
        df_temp['Horas_Minutos'] = df_temp['Horas Trabajadas'].apply(convertir_tiempo_a_minutos)
        
        print("Top 5 empleados con más horas trabajadas:")
        top_horas = df_temp.nlargest(5, 'Horas_Minutos')[['Nombre', 'Horas Trabajadas']]
        print(top_horas)
    else:
        print("La columna 'Horas Trabajadas' no existe")
    ```

    IMPORTANTE: Para columnas con formato de tiempo (HH:MM), SIEMPRE usa las funciones auxiliares para convertir antes de hacer comparaciones o cálculos.

    GENERA SOLO CÓDIGO PYTHON, SIN EXPLICACIONES.
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
            "temperature": 0.3,  # Reducir temperatura para más consistencia
            "max_completion_tokens": 512,
            "top_p": 1,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            codigo = response.json()['choices'][0]['message']['content']
            # Limpiar el código de markdown si existe
            codigo = codigo.replace('```python', '').replace('```', '').strip()
            return codigo
        except Exception as e:
            return f"Error al generar consulta: {str(e)}"

    def ejecutar_consulta_mejorada(codigo, df_reporte):
        """Ejecuta código pandas y captura tanto texto como DataFrames"""
        try:
            from io import StringIO
            import sys
            
            # Variables para capturar resultados
            resultado_texto = ""
            resultado_df = None
            
            # Funciones auxiliares para análisis
            def convertir_tiempo_a_minutos(tiempo_str):
                """Convierte formato HH:MM a minutos de forma segura"""
                try:
                    if pd.isna(tiempo_str) or str(tiempo_str).strip() in ['N/A', '', '0:00', '00:00']:
                        return 0
                    tiempo_str = str(tiempo_str).strip()
                    if ':' not in tiempo_str:
                        return 0
                    partes = tiempo_str.split(':')
                    if len(partes) != 2:
                        return 0
                    horas, minutos = int(partes[0]), int(partes[1])
                    return horas * 60 + minutos
                except:
                    return 0
            
            def convertir_tiempo_a_horas_decimales(tiempo_str):
                """Convierte formato HH:MM a horas decimales"""
                try:
                    if pd.isna(tiempo_str) or str(tiempo_str).strip() in ['N/A', '', '0:00', '00:00']:
                        return 0.0
                    tiempo_str = str(tiempo_str).strip()
                    if ':' not in tiempo_str:
                        return 0.0
                    partes = tiempo_str.split(':')
                    if len(partes) != 2:
                        return 0.0
                    horas, minutos = int(partes[0]), int(partes[1])
                    return horas + minutos / 60.0
                except:
                    return 0.0
            
            def obtener_empleado_max_tiempo_extra():
                """Encuentra el empleado con más tiempo extra"""
                try:
                    if 'Tiempo Extra' not in df_reporte.columns:
                        return "La columna 'Tiempo Extra' no existe"
                    
                    # Crear una copia del dataframe para trabajar
                    df_temp = df_reporte.copy()
                    df_temp['Tiempo_Extra_Minutos'] = df_temp['Tiempo Extra'].apply(convertir_tiempo_a_minutos)
                    
                    # Encontrar el máximo
                    max_idx = df_temp['Tiempo_Extra_Minutos'].idxmax()
                    max_empleado = df_temp.loc[max_idx]
                    
                    return f"Empleado con más tiempo extra: {max_empleado['Nombre']} ({max_empleado['Tiempo Extra']})"
                except Exception as e:
                    return f"Error al calcular tiempo extra: {str(e)}"
            
            def obtener_empleado_max_horas_trabajadas():
                """Encuentra el empleado con más horas trabajadas"""
                try:
                    if 'Horas Trabajadas' not in df_reporte.columns:
                        return "La columna 'Horas Trabajadas' no existe"
                    
                    # Crear una copia del dataframe para trabajar
                    df_temp = df_reporte.copy()
                    df_temp['Horas_Trabajadas_Minutos'] = df_temp['Horas Trabajadas'].apply(convertir_tiempo_a_minutos)
                    
                    # Encontrar el máximo
                    max_idx = df_temp['Horas_Trabajadas_Minutos'].idxmax()
                    max_empleado = df_temp.loc[max_idx]
                    
                    return f"Empleado con más horas trabajadas: {max_empleado['Nombre']} ({max_empleado['Horas Trabajadas']})"
                except Exception as e:
                    return f"Error al calcular horas trabajadas: {str(e)}"
            
            def obtener_top_empleados_por_columna(columna, n=5, orden='desc'):
                """Obtiene top N empleados por una columna específica"""
                try:
                    if columna not in df_reporte.columns:
                        return f"La columna '{columna}' no existe"
                    
                    df_temp = df_reporte.copy()
                    
                    # Si es una columna de tiempo, convertir a minutos
                    if 'Tiempo' in columna or 'Horas' in columna:
                        df_temp[f'{columna}_Minutos'] = df_temp[columna].apply(convertir_tiempo_a_minutos)
                        columna_ordenar = f'{columna}_Minutos'
                    else:
                        columna_ordenar = columna
                    
                    # Ordenar
                    if orden == 'desc':
                        df_resultado = df_temp.nlargest(n, columna_ordenar)
                    else:
                        df_resultado = df_temp.nsmallest(n, columna_ordenar)
                    
                    return df_resultado[['Nombre', columna]]
                except Exception as e:
                    return f"Error al obtener top empleados: {str(e)}"
            
            # Contexto seguro con funciones auxiliares y tipos básicos
            contexto_seguro = {
                'df_reporte': df_reporte,
                'pd': pd,
                'np': np,
                'int': int,  # ← AÑADIDO: Incluir int en el contexto
                'float': float,
                'str': str,
                'len': len,
                'max': max,
                'min': min,
                'sum': sum,
                'abs': abs,
                'round': round,
                'range': range,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'sorted': sorted,
                'enumerate': enumerate,
                'zip': zip,
                'convertir_tiempo_a_minutos': convertir_tiempo_a_minutos,
                'convertir_tiempo_a_horas_decimales': convertir_tiempo_a_horas_decimales,
                'obtener_empleado_max_tiempo_extra': obtener_empleado_max_tiempo_extra,
                'obtener_empleado_max_horas_trabajadas': obtener_empleado_max_horas_trabajadas,
                'obtener_top_empleados_por_columna': obtener_top_empleados_por_columna,
            }
            
            # Función print personalizada para capturar texto
            output_buffer = StringIO()
            def custom_print(*args, **kwargs):
                print(*args, file=output_buffer, **kwargs)
            
            contexto_seguro['print'] = custom_print
            
            # Ejecutar código
            exec(codigo, {"__builtins__": {}}, contexto_seguro)
            
            # Obtener resultado de texto
            resultado_texto = output_buffer.getvalue()
            
            # Intentar extraer DataFrame del resultado si es posible
            try:
                # Si el código contiene operaciones que devuelven DataFrames
                lines = codigo.strip().split('\n')
                last_line = lines[-1].strip()
                
                # Si la última línea es un print de un DataFrame slice
                if 'print(' in last_line and '[' in last_line and ']' in last_line:
                    # Ejecutar solo la parte del DataFrame sin el print
                    df_part = last_line.replace('print(', '').rstrip(')')
                    resultado_df = eval(df_part, {"__builtins__": {}}, contexto_seguro)
                    
                    if isinstance(resultado_df, pd.DataFrame) and not resultado_df.empty:
                        # Limpiar el texto del resultado ya que lo mostraremos como tabla
                        lines_text = resultado_texto.strip().split('\n')
                        # Mantener solo las líneas que no sean la tabla
                        clean_lines = []
                        skip_table = False
                        for line in lines_text:
                            if 'Nombre' in line and any(col in line for col in ['Faltas', 'Retardos', 'Horas']):
                                skip_table = True
                                continue
                            if skip_table and (line.strip() == '' or not any(c.isalnum() for c in line)):
                                skip_table = False
                                continue
                            if not skip_table:
                                clean_lines.append(line)
                        
                        resultado_texto = '\n'.join(clean_lines)
            except:
                pass
                
            return resultado_texto, resultado_df
            
        except Exception as e:
            return f"Error al ejecutar consulta: {str(e)}", None


    # Función principal de análisis 
    def analizar_con_ia(pregunta, df_reporte, api_key):
        """Función mejorada para análisis con IA con mejor presentación"""
        
        # Generar código
        codigo = generar_consulta_con_ia(pregunta, df_reporte, api_key)
        
        if codigo.startswith("Error"):
            return codigo
        
        # Ejecutar código y capturar tanto texto como DataFrames
        resultado_texto, resultado_df = ejecutar_consulta_mejorada(codigo, df_reporte)
        
        # Formatear respuesta con mejor presentación
        return resultado_texto, resultado_df, codigo

    def procesar_respuesta_ia(pregunta, df_reporte, api_key):
        """Procesa la respuesta de IA y la formatea para Streamlit"""
        resultado_texto, resultado_df, codigo = analizar_con_ia(pregunta, df_reporte, api_key)
        
        # Crear respuesta formateada
        respuesta_formateada = {
            'tipo': 'ia_analysis',
            'codigo': codigo,
            'texto': resultado_texto,
            'dataframe': resultado_df
        }
        
        return respuesta_formateada

    def mostrar_mensaje_chat(role, message):
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
                    # Limpiar texto y dividir en líneas
                    texto_limpio = message['texto'].strip()
                    lineas = texto_limpio.split('\n')
                    
                    # Separar líneas que son texto descriptivo de las que parecen datos tabulares
                    texto_descriptivo = []
                    datos_tabulares = []
                    
                    for linea in lineas:
                        linea = linea.strip()
                        if linea and not any(word in linea for word in ['Nombre', 'Faltas', 'Retardos', 'Horas']):
                            texto_descriptivo.append(linea)
                        elif linea:
                            datos_tabulares.append(linea)
                    
                    # Mostrar solo texto descriptivo si existe
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
            # Cargar DataFrames
            df_horas = cargar_y_limpiar(archivo_horas)
            df_diferencia = cargar_y_limpiar(archivo_diferencia)
            df_retardos = cargar_y_limpiar(archivo_retardos)
            df_tiempo_extra = cargar_y_limpiar(archivo_tiempo_extra)

            if all(df is not None for df in [df_horas, df_diferencia, df_retardos, df_tiempo_extra]):
                
                # Generar reporte
                reporte_data = []
                
                for i in range(len(df_horas)):
                    nombre = df_horas.iloc[i]['Nombre']
                    fila_horas = df_horas.iloc[i]
                    fila_diferencia = df_diferencia.iloc[i]
                    fila_retardos = df_retardos.iloc[i]
                    fila_tiempo_extra = df_tiempo_extra.iloc[i]
                    
                    horas_trabajadas = fila_horas.get('Total de\nHoras') or fila_horas.get('Total de Horas') or 'N/A'
                    dias_trabajados = contar_dias_trabajados(fila_horas)
                    dias_descanso = contar_dias_descanso(fila_horas)
                    dias_falta = fila_horas.get('Faltas', 0) or 0
                    dias_registro_mal = contar_registro_mal(fila_diferencia)
                    dias_con_retardo = contar_retardos(fila_retardos)
                    diferencia_total = fila_diferencia.get('Tiempo\nTotal') or fila_diferencia.get('Tiempo Total') or 'N/A'
                    tiempo_extra = fila_tiempo_extra.get('Tiempo\nTotal') or fila_tiempo_extra.get('Tiempo Total') or 'N/A'
                    
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

                # Crear DataFrame del reporte
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
                
                # Filtros
                col1, col2 = st.columns(2)
                with col1:
                    filtro_nombre = st.text_input("🔍 Buscar por nombre:", placeholder="Escribe el nombre del empleado...")
                
                with col2:
                    mostrar_todos = st.checkbox("Mostrar todos los empleados", value=True)

                # Aplicar filtros
                df_filtrado = df_reporte.copy()
                if filtro_nombre and not mostrar_todos:
                    df_filtrado = df_filtrado[df_filtrado['Nombre'].str.contains(filtro_nombre, case=False, na=False)]

                # Mostrar tabla
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

                # Mostrar vista previa de los archivos cargados
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

                # Chat de análisis con IA - Nuevo diseño
                st.markdown("---")
                
                if GROQ_API_KEY != "tu_api_key_aqui":
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
                    
                    # Botones de preguntas rápidas con nuevo diseño
                    st.markdown("#### 🚀 Análisis rápido:")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("📊 Resumen General", use_container_width=True):
                            pregunta = "Dame un resumen general del reporte de asistencias con los principales hallazgos y estadísticas importantes"
                            st.session_state.chat_history.append(("user", pregunta))
                            with st.spinner("🔍 Analizando datos..."):
                                respuesta = procesar_respuesta_ia(pregunta, df_reporte, GROQ_API_KEY)
                                st.session_state.chat_history.append(("assistant", respuesta))
                            st.rerun()
                    
                    with col2:
                        if st.button("⚠️ Alertas Críticas", use_container_width=True):
                            pregunta = "Identifica empleados con problemas críticos de asistencia, puntualidad o registro. Dame nombres específicos y qué acciones recomiendas"
                            st.session_state.chat_history.append(("user", pregunta))
                            with st.spinner("🔍 Identificando problemas..."):
                                respuesta = procesar_respuesta_ia(pregunta, df_reporte, GROQ_API_KEY)
                                st.session_state.chat_history.append(("assistant", respuesta))
                            st.rerun()
                    
                    with col3:
                        if st.button("🏆 Top Performers", use_container_width=True):
                            pregunta = "¿Cuáles son los empleados con mejor desempeño en asistencia y puntualidad? Dame un ranking de los top 5"
                            st.session_state.chat_history.append(("user", pregunta))
                            with st.spinner("🔍 Evaluando desempeño..."):
                                respuesta = procesar_respuesta_ia(pregunta, df_reporte, GROQ_API_KEY)
                                st.session_state.chat_history.append(("assistant", respuesta))
                            st.rerun()
                    
                    with col4:
                        if st.button("📈 Métricas Clave", use_container_width=True):
                            pregunta = "Calcula y presenta las métricas más importantes: promedios, porcentajes, tendencias y comparaciones entre empleados"
                            st.session_state.chat_history.append(("user", pregunta))
                            with st.spinner("🔍 Calculando métricas..."):
                                respuesta = procesar_respuesta_ia(pregunta, df_reporte, GROQ_API_KEY)
                                st.session_state.chat_history.append(("assistant", respuesta))
                            st.rerun()
                    
                    # Mostrar historial de chat con nuevo diseño
                    for i, (role, message) in enumerate(st.session_state.chat_history):
                        mostrar_mensaje_chat(role, message)  # ← REEMPLAZAR TODO EL BLOQUE CON ESTA LÍNEA
                                        
                    # Input para nueva pregunta con diseño mejorado
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
                                    respuesta = procesar_respuesta_ia(nueva_pregunta, df_reporte, GROQ_API_KEY)
                                    st.session_state.chat_history.append(("assistant", respuesta))
                                st.rerun()
                    
                    # Botones de acción
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
                st.error("❌ Error al procesar uno o más archivos. Verifica que los archivos sean válidos.")

    else:
        st.info("👆 Por favor, carga los 4 archivos Excel requeridos en la barra lateral para generar el reporte.")
        
        # Instrucciones actualizadas
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