import requests
from typing import Dict, Optional, Tuple, Any
import pandas as pd
import numpy as np
from io import StringIO
import sys
from utils.config import Config


class ChatIAService:
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def generar_consulta_ia(
        self, 
        pregunta: str, 
        df_reporte: pd.DataFrame
    ) -> Tuple[Optional[str], Optional[pd.DataFrame], Optional[str]]:
        """Genera y ejecuta una consulta de IA sobre el DataFrame"""
        if not self.api_key or self.api_key == "tu_api_key_aqui":
            return "API Key no configurada", None, None
            
        codigo = self._generar_codigo_ia(pregunta, df_reporte)
        if isinstance(codigo, tuple):  # Si hay error
            return codigo[0], None, None
            
        resultado_texto, resultado_df = self._ejecutar_codigo(codigo, df_reporte)
        return resultado_texto, resultado_df, codigo
    
    def _generar_codigo_ia(self, pregunta: str, df_reporte: pd.DataFrame) -> str:
        """Genera código Python para responder la pregunta usando IA"""
        url = self.api_url
        
        # Obtener información del DataFrame
        info_str, dtypes_detail = self._obtener_info_dataframe(df_reporte)
        
        # Obtener describe solo para columnas numéricas
        describe_str = ""
        try:
            numeric_cols = df_reporte.select_dtypes(include=['int64', 'float64']).columns.tolist()
            if numeric_cols:
                describe_str = str(df_reporte[numeric_cols].describe())
        except:
            describe_str = "No hay columnas numéricas para describir"
        
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

Para retardos:
```python
if 'Retardos' in df_reporte.columns:
    print("Top 5 empleados con más retardos:")
    print(df_reporte.nlargest(5, 'Retardos')[['Nombre', 'Retardos']])
else:
    print("La columna 'Retardos' no existe")
```

Para horas trabajadas:
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
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "messages": [
                {"role": "system", "content": contexto},
                {"role": "user", "content": pregunta}
            ],
            "model": "llama3-70b-8192",
            "temperature": 0.3,
            "max_tokens": 1024,
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

    def _ejecutar_codigo(self, codigo: str, df_reporte: pd.DataFrame) -> Tuple[str, Optional[pd.DataFrame]]:
        """Ejecuta código pandas y captura tanto texto como DataFrames"""
        try:
            # Variables para capturar resultados
            resultado_texto = ""
            resultado_df = None
            
            # Contexto seguro con funciones auxiliares
            contexto_seguro = {
                'df_reporte': df_reporte,
                'pd': pd,
                'np': np,
                'convertir_tiempo_a_minutos': self._convertir_tiempo_a_minutos,
                'convertir_tiempo_a_horas_decimales': self._convertir_tiempo_a_horas_decimales,
                'obtener_empleado_max_tiempo_extra': lambda: self._obtener_empleado_max_columna(df_reporte, 'Tiempo Extra'),
                'obtener_empleado_max_horas_trabajadas': lambda: self._obtener_empleado_max_columna(df_reporte, 'Horas Trabajadas'),
                'obtener_top_empleados_por_columna': lambda columna, n=5, orden='desc': self._obtener_top_empleados_por_columna(df_reporte, columna, n, orden),
                '__builtins__': {
                    'print': self._custom_print,
                    'int': int,
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
                    'zip': zip
                }
            }
            
            # Buffer para capturar output
            self._output_buffer = StringIO()
            
            # Ejecutar código
            exec(codigo, contexto_seguro)
            
            # Obtener resultado de texto
            resultado_texto = self._output_buffer.getvalue()
            
            # Intentar extraer DataFrame del resultado si es posible
            if 'print(' in codigo:
                # Si el último comando fue un print, verificar si contenía un DataFrame
                last_line = codigo.strip().split('\n')[-1]
                if 'print(' in last_line and '[' in last_line and ']' in last_line:
                    try:
                        # Extraer la expresión antes del print
                        expr = last_line.split('print(')[1].rsplit(')', 1)[0]
                        resultado_df = eval(expr, contexto_seguro)
                        if isinstance(resultado_df, pd.DataFrame):
                            # Limpiar el texto del resultado si mostramos el DataFrame aparte
                            resultado_texto = resultado_texto.replace(str(resultado_df), '').strip()
                    except:
                        pass
                
            return resultado_texto, resultado_df if isinstance(resultado_df, pd.DataFrame) else None
            
        except Exception as e:
            return f"Error al ejecutar consulta: {str(e)}", None

    # Funciones auxiliares para el contexto de ejecución
    def _custom_print(self, *args, **kwargs):
        """Función print personalizada para capturar output"""
        print(*args, file=self._output_buffer, **kwargs)

    def _convertir_tiempo_a_minutos(self, tiempo_str) -> int:
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

    def _convertir_tiempo_a_horas_decimales(self, tiempo_str) -> float:
        """Convierte formato HH:MM a horas decimales"""
        minutos = self._convertir_tiempo_a_minutos(tiempo_str)
        return minutos / 60.0

    def _obtener_empleado_max_columna(self, df: pd.DataFrame, columna: str) -> str:
        """Obtiene el empleado con máximo valor en una columna"""
        try:
            if columna not in df.columns:
                return f"La columna '{columna}' no existe"
            
            if 'Tiempo' in columna or 'Horas' in columna:
                df_temp = df.copy()
                df_temp['temp_minutos'] = df_temp[columna].apply(self._convertir_tiempo_a_minutos)
                max_idx = df_temp['temp_minutos'].idxmax()
            else:
                max_idx = df[columna].idxmax()
            
            max_empleado = df.loc[max_idx]
            return f"Empleado con máximo {columna}: {max_empleado['Nombre']} ({max_empleado[columna]})"
        except Exception as e:
            return f"Error al calcular máximo {columna}: {str(e)}"

    def _obtener_top_empleados_por_columna(self, df: pd.DataFrame, columna: str, n: int = 5, orden: str = 'desc') -> pd.DataFrame:
        """Obtiene top N empleados por una columna específica"""
        try:
            if columna not in df.columns:
                return f"La columna '{columna}' no existe"
            
            df_temp = df.copy()
            
            # Si es una columna de tiempo, convertir a minutos
            if 'Tiempo' in columna or 'Horas' in columna:
                df_temp[f'{columna}_Minutos'] = df_temp[columna].apply(self._convertir_tiempo_a_minutos)
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

    def _obtener_info_dataframe(self, df: pd.DataFrame) -> Tuple[str, str]:
        """Obtiene información detallada del DataFrame"""
        # Capturar info()
        old_stdout = sys.stdout
        sys.stdout = buffer = StringIO()
        df.info(buf=buffer, verbose=True)
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