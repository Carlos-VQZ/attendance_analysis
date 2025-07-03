from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ReporteConsolidado:
    datos: List[Dict[str, Any]]
    metricas_generales: Dict[str, Any]
    dataframe: Any  # pandas DataFrame