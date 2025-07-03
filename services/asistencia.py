import pandas as pd
from typing import List, Dict
from utils.tiempo import tiempo_a_minutos
from models.asistencia import DatosAsistencia, ReporteAsistencia

class AsistenciaService:
    @staticmethod
    def contar_dias_trabajados(fila: pd.Series) -> int:
        """Cuenta días trabajados en una fila del DataFrame"""
        return sum(1 for col in fila.index 
                  if str(col).isdigit() 
                  and pd.notna(fila[col]) 
                  and ':' in str(fila[col]) 
                  and fila[col] not in ['F', 'N/L', 'J'])

    @staticmethod
    def contar_dias_descanso(fila: pd.Series) -> int:
        """Cuenta días de descanso en una fila del DataFrame"""
        return sum(1 for col in fila.index 
                  if str(col).isdigit() 
                  and fila[col] == 'N/L')

    @staticmethod
    def contar_registro_mal(fila: pd.Series) -> int:
        """Cuenta registros mal hechos (diferencia <= -120 minutos)"""
        return sum(1 for col in fila.index 
                  if str(col).isdigit() 
                  and pd.notna(fila[col]) 
                  and fila[col] not in ['F', 'N/L', 'J'] 
                  and tiempo_a_minutos(fila[col]) <= -120)

    @staticmethod
    def contar_retardos(fila: pd.Series) -> int:
        """Cuenta retardos (diferencia >= 10 minutos)"""
        return sum(1 for col in fila.index 
                  if str(col).isdigit() 
                  and pd.notna(fila[col]) 
                  and fila[col] not in ['F', 'N/L', 'J'] 
                  and tiempo_a_minutos(fila[col]) >= 10)