# Imagen base oficial de Python
FROM python:3.11-slim

# Establecer directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install streamlit pandas openpyxl xlsxwriter requests python-dotenv

# Exponer el puerto por donde corre Streamlit
EXPOSE 8501

# Comando por defecto
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
