import pandas as pd

def es_nombre_valido(nombre) -> bool:
    """Valida si un string es un nombre válido"""
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

def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia un DataFrame de asistencias"""
    # Filtrar filas donde el campo 'Nombre' no sea nulo
    df = df[df['Nombre'].notna()].reset_index(drop=True)
    
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
    
    return df