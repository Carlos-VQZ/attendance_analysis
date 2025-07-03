import pandas as pd
from typing import Dict, List, Optional
from models.asistencia import DatosAsistencia, ReporteAsistencia
from .asistencia import AsistenciaService

class ReporteService:
    def __init__(self):
        self.asistencia_service = AsistenciaService()

    def generar_reporte_consolidado(
        self,
        df_horas: pd.DataFrame,
        df_diferencia: pd.DataFrame,
        df_retardos: pd.DataFrame,
        df_tiempo_extra: pd.DataFrame
    ) -> ReporteAsistencia:
        """Genera un reporte consolidado a partir de los DataFrames individuales"""
        # 1. Crear base con nombres
        df_base = df_horas[['Nombre']].copy()
        
        # 2. Procesar datos de horas
        datos_horas = self._procesar_horas(df_horas)
        df_datos_horas = pd.DataFrame(datos_horas)
        
        # 3. Procesar datos de diferencias
        datos_diferencias = self._procesar_diferencias(df_diferencia)
        df_datos_diferencias = pd.DataFrame(datos_diferencias)
        
        # 4. Procesar datos de retardos
        datos_retardos = self._procesar_retardos(df_retardos)
        df_datos_retardos = pd.DataFrame(datos_retardos)
        
        # 5. Procesar datos de tiempo extra
        datos_tiempo_extra = self._procesar_tiempo_extra(df_tiempo_extra)
        df_datos_tiempo_extra = pd.DataFrame(datos_tiempo_extra)
        
        # 6. Consolidar todos los datos
        df_reporte = self._consolidar_dataframes(
            df_datos_horas,
            df_datos_diferencias,
            df_datos_retardos,
            df_datos_tiempo_extra
        )
        
        # 7. Calcular métricas generales
        metricas = self._calcular_metricas_generales(df_reporte)
        
        # 8. Crear modelo de reporte
        empleados = [
            DatosAsistencia(
                nombre=row['Nombre'],
                horas_trabajadas=row['Horas Trabajadas'],
                dias_trabajados=row['Días Trabajados'],
                dias_descanso=row['Días Descanso'],
                faltas=row['Faltas'],
                registro_mal=row['Registro Mal'],
                retardos=row['Retardos'],
                diferencia_total=row['Diferencia Total'],
                tiempo_extra=row['Tiempo Extra']
            )
            for _, row in df_reporte.iterrows()
        ]
        
        return ReporteAsistencia(
            empleados=empleados,
            total_dias_trabajados=metricas['total_dias_trabajados'],
            total_faltas=metricas['total_faltas'],
            total_retardos=metricas['total_retardos'],
            total_registro_mal=metricas['total_registro_mal']
        )

    def _procesar_horas(self, df_horas: pd.DataFrame) -> List[Dict]:
        """Procesa el DataFrame de horas trabajadas"""
        datos = []
        for _, fila in df_horas.iterrows():
            datos.append({
                'Nombre': fila['Nombre'],
                'Horas Trabajadas': fila.get('Total de\nHoras') or fila.get('Total de Horas') or 'N/A',
                'Días Trabajados': self.asistencia_service.contar_dias_trabajados(fila),
                'Días Descanso': self.asistencia_service.contar_dias_descanso(fila),
                'Faltas': fila.get('Faltas', 0) or 0
            })
        return datos

    def _procesar_diferencias(self, df_diferencia: pd.DataFrame) -> List[Dict]:
        """Procesa el DataFrame de diferencias"""
        datos = []
        for _, fila in df_diferencia.iterrows():
            datos.append({
                'Nombre': fila['Nombre'],
                'Registro Mal': self.asistencia_service.contar_registro_mal(fila),
                'Diferencia Total': fila.get('Tiempo\nTotal') or fila.get('Tiempo Total') or 'N/A'
            })
        return datos

    def _procesar_retardos(self, df_retardos: pd.DataFrame) -> List[Dict]:
        """Procesa el DataFrame de retardos"""
        datos = []
        for _, fila in df_retardos.iterrows():
            datos.append({
                'Nombre': fila['Nombre'],
                'Retardos': self.asistencia_service.contar_retardos(fila)
            })
        return datos

    def _procesar_tiempo_extra(self, df_tiempo_extra: pd.DataFrame) -> List[Dict]:
        """Procesa el DataFrame de tiempo extra"""
        datos = []
        for _, fila in df_tiempo_extra.iterrows():
            datos.append({
                'Nombre': fila['Nombre'],
                'Tiempo Extra': fila.get('Tiempo\nTotal') or fila.get('Tiempo Total') or 'N/A'
            })
        return datos

    def _consolidar_dataframes(
        self,
        df_datos_horas: pd.DataFrame,
        df_datos_diferencias: pd.DataFrame,
        df_datos_retardos: pd.DataFrame,
        df_datos_tiempo_extra: pd.DataFrame
    ) -> pd.DataFrame:
        """Consolida todos los DataFrames en uno solo"""
        # Merge con horas como base
        df_reporte = df_datos_horas.copy()
        
        # Merge con diferencias (left join para conservar todos los empleados)
        df_reporte = df_reporte.merge(
            df_datos_diferencias, 
            on='Nombre', 
            how='left'
        )
        
        # Merge con retardos
        df_reporte = df_reporte.merge(
            df_datos_retardos, 
            on='Nombre', 
            how='left'
        )
        
        # Merge con tiempo extra
        df_reporte = df_reporte.merge(
            df_datos_tiempo_extra, 
            on='Nombre', 
            how='left'
        )
        
        # Llenar valores faltantes con valores por defecto
        df_reporte['Registro Mal'] = df_reporte['Registro Mal'].fillna(0).astype(int)
        df_reporte['Diferencia Total'] = df_reporte['Diferencia Total'].fillna('00:00')
        df_reporte['Retardos'] = df_reporte['Retardos'].fillna(0).astype(int)
        df_reporte['Tiempo Extra'] = df_reporte['Tiempo Extra'].fillna('00:00')
        
        # Reordenar columnas
        df_reporte = df_reporte[[
            'Nombre', 'Horas Trabajadas', 'Días Trabajados', 'Días Descanso', 
            'Faltas', 'Registro Mal', 'Retardos', 'Diferencia Total', 'Tiempo Extra'
        ]]
        
        return df_reporte

    def _calcular_metricas_generales(self, df_reporte: pd.DataFrame) -> Dict[str, int]:
        """Calcula las métricas generales del reporte"""
        return {
            'total_dias_trabajados': df_reporte['Días Trabajados'].sum(),
            'total_faltas': df_reporte['Faltas'].sum(),
            'total_retardos': df_reporte['Retardos'].sum(),
            'total_registro_mal': df_reporte['Registro Mal'].sum()
        }

    def obtener_dataframe_reporte(self, reporte: ReporteAsistencia) -> pd.DataFrame:
        """Convierte el modelo ReporteAsistencia a un DataFrame pandas"""
        return pd.DataFrame([vars(empleado) for empleado in reporte.empleados])