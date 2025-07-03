import pandas as pd

def tiempo_a_minutos(tiempo_str) -> int:
    """Convierte HH:MM a minutos"""
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

def tiempo_a_horas_decimales(tiempo_str) -> float:
    """Convierte HH:MM a horas decimales"""
    minutos = tiempo_a_minutos(tiempo_str)
    return minutos / 60.0