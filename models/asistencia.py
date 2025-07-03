from dataclasses import dataclass
from typing import Optional

@dataclass
class DatosAsistencia:
    nombre: str
    horas_trabajadas: str
    dias_trabajados: int
    dias_descanso: int
    faltas: int
    registro_mal: int
    retardos: int
    diferencia_total: str
    tiempo_extra: str

@dataclass
class ReporteAsistencia:
    empleados: list[DatosAsistencia]
    total_dias_trabajados: int
    total_faltas: int
    total_retardos: int
    total_registro_mal: int