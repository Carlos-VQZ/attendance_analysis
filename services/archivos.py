import pandas as pd
from typing import Optional
from utils.validacion import es_nombre_valido, limpiar_dataframe

class ArchivosService:
    @staticmethod
    def cargar_archivo_excel(archivo) -> Optional[pd.DataFrame]:
        """Carga y limpia un archivo Excel de asistencia"""
        try:
            df = pd.read_excel(archivo, sheet_name=0, header=2)
            df = limpiar_dataframe(df)
            return df
        except Exception as e:
            raise ValueError(f"Error al cargar archivo: {str(e)}")

    @staticmethod
    def validar_archivos_cargados(*archivos) -> bool:
        """Verifica que todos los archivos requeridos estén cargados"""
        return all(archivo is not None for archivo in archivos)