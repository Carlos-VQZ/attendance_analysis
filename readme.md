#  Sistema de Reportes de Asistencias

Una aplicación web desarrollada con Streamlit que automatiza el procesamiento y análisis de reportes de asistencias laborales, incluyendo un asistente de IA para análisis inteligente de datos de recursos humanos.

##  Características Principales

- **Procesamiento Automático**: Carga y procesa 4 tipos de archivos Excel de asistencias
- **Reporte Consolidado**: Genera un reporte unificado con métricas clave de cada empleado
- **Análisis con IA**: Chat inteligente powered by Groq para análisis de datos
- **Dashboard Interactivo**: Visualización de métricas generales y filtros personalizables
- **Descarga de Reportes**: Exporta reportes procesados a Excel

##  Tipos de Archivos Soportados

La aplicación procesa 4 archivos Excel específicos:

1. ** Reporte de Horas Trabajadas** (`horas_trabajadas.xlsx`)
2. ** Reporte de Diferencias** (`diferencias.xlsx`)
3. ** Reporte de Retardos** (`retardos.xlsx`)
4. ** Reporte de Tiempo Extra** (`tiempo_extra.xlsx`)

##  Instalación y Configuración

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### 1. Clonar o Descargar el Proyecto

```bash
# Si tienes Git instalado
git clone <url-del-repositorio>
cd sistema-reportes-asistencias

# O simplemente descarga el archivo .py
```

### 2. Instalar Dependencias

```bash
pip install streamlit pandas openpyxl xlsxwriter requests
```

### 3. Configurar API Key de Groq (Opcional pero Recomendado)

Para usar las funciones de análisis con IA:

1. Visita [console.groq.com](https://console.groq.com)
2. Regístrate o inicia sesión
3. Crea una nueva API Key
4. Edita el archivo y reemplaza:
   ```python
   GROQ_API_KEY = "api_key"
   ```
   Por:
   ```python
   GROQ_API_KEY = "tu_api_key"
   ```

## Cómo Ejecutar la Aplicación

## Configuración del entorno

Antes de ejecutar el proyecto, crea un archivo `.env` en la raíz con el siguiente contenido:

```bash
API_KEY=tu_api_key
```

### Ejecución Local

```bash
streamlit run main.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Ejecución en Servidor

```bash
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

## Guía de Uso

### 1. Cargar Archivos

1. Usa la **barra lateral izquierda** para cargar los 4 archivos Excel requeridos
2. Los archivos deben tener el formato estándar de reportes de asistencias
3. El sistema validará automáticamente la estructura de cada archivo

### 2. Visualizar Reporte

Una vez cargados todos los archivos:

- **Métricas Generales**: Ve el resumen en la parte superior
- **Tabla Detallada**: Revisa los datos de cada empleado
- **Filtros**: Busca empleados específicos o visualiza todos

### 3. Usar el Asistente de IA

Con la API Key configurada:

- **Preguntas Rápidas**: Usa los botones predefinidos para análisis comunes
- **Chat Personalizado**: Haz preguntas específicas sobre los datos
- **Análisis Inteligente**: Obtén insights, recomendaciones y métricas avanzadas

### 4. Descargar Resultados

- Usa el botón **"Descargar Reporte Excel"** para obtener el reporte consolidado
- El archivo incluye todos los datos procesados y calculados

##  Métricas Calculadas

La aplicación genera las siguientes métricas para cada empleado:

| Métrica | Descripción |
|---------|-------------|
| **Horas Trabajadas** | Total de horas laboradas en el período |
| **Días Trabajados** | Número de días con asistencia registrada |
| **Días Descanso** | Días programados de descanso (N/L) |
| **Faltas** | Días sin asistencia registrada |
| **Registro Mal** | Días con problemas en el registro de entrada/salida |
| **Retardos** | Número de llegadas tardías (≥10 minutos) |
| **Diferencia Total** | Diferencia acumulada de tiempo trabajado vs programado |
| **Tiempo Extra** | Total de horas extra trabajadas |

##  Funciones del Asistente de IA

### Análisis Disponibles

- **Resumen General**: Overview completo de métricas y hallazgos
- **Alertas Críticas**: Identificación de empleados con problemas
- **Top Performers**: Ranking de mejores empleados por asistencia
- **Métricas Clave**: Cálculos avanzados y comparaciones

### Preguntas Ejemplo

```
• ¿Quién tiene más retardos?
• ¿Cuál es el promedio de faltas por empleado?
• ¿Qué empleados trabajan más horas extra?
• Identifica patrones de ausentismo
• Recomienda acciones correctivas para empleados problemáticos
• Haz un análisis de productividad por departamento
```

## 🔧 Estructura del Código

```
sistema-reportes-asistencias/
│
├── main.py                 # Archivo principal de la aplicación
├── README.md              # Este archivo
└── requirements.txt       # Dependencias (opcional)
```

### Funciones Principales

- `main()`: Función principal de la aplicación
- `cargar_y_limpiar()`: Procesamiento y limpieza de archivos Excel
- `tiempo_a_minutos()`: Conversión de formato HH:MM a minutos
- `consultar_groq()`: Integración con API de Groq para análisis IA
- Funciones de conteo: `contar_dias_trabajados()`, `contar_retardos()`, etc.

## Dependencias

```
streamlit>=1.28.0
pandas>=1.5.0
openpyxl>=3.0.0
xlsxwriter>=3.0.0
requests>=2.28.0
```

## Personalización

### Configurar Diferentes Modelos de IA

Puedes cambiar el modelo de Groq editando:

```python
"model": "gemma2-9b-it",  # Cambia por otro modelo disponible
```

