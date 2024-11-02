








  load_dotenv()
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_server = os.getenv('DB_SERVER')
        db_name = os.getenv('DB_NAME')
        db_driver = os.getenv('DB_DRIVER')
        
        connection_url = f'mssql+pyodbc://{db_user}:{db_password}@{db_server}/{db_name}?driver={db_driver}&TrustServerCertificate=yes&Encrypt=no'
        self.engine = create_engine(connection_url)





# Ejemplo básico usando Python con Ollama
import pyodbc
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DBChat:
    def __init__(self):
        # Conexión a SQL Server usando variables de entorno
        connection_string = (
            f'DRIVER={os.getenv("DB_DRIVER")};'
            f'SERVER={os.getenv("DB_SERVER")};'
            f'DATABASE={os.getenv("DB_NAME")};'
            f'UID={os.getenv("DB_USER")};'
            f'PWD={os.getenv("DB_PASSWORD")}'
        )
        self.conn = pyodbc.connect(connection_string)
        
        # URL base de Ollama (asumiendo que se ejecuta localmente)
        self.ollama_url = "http://localhost:11434/api/generate"

    def procesar_pregunta(self, pregunta):
        # Preparar el prompt para Ollama con información adicional
        prompt = """Eres un asistente experto en SQL que aplica siempre las mejores practicas de sql,
         me ayudas a convertir preguntas en queries SQL para poder encontrar la respuesta en mi base de datos. 
         Respondes solo con la query SQL en texto plano, NADA MÁS, no uses markdown.
        
        No uses acentos en los querys
        
        Información de las tablas disponibles:
        
        1. Para preguntas sobre clientes, usa la tabla CATCTES que tiene los campos:
           - cod_cte: código del cliente
           - nom_cte: nombre del cliente
           - status: donde A=activo y B=Baja
           - cod_zona: código de la zona
        2. Para preguntas sobre proveedores, usa la tabla CATPROV que tiene los campos:
           - cod_prov: código del proveedor
           - nom_prov: nombre del proveedor
           - status: donde A=activo y B=Baja   
        3. Para preguntas sobre zonas, usa la tabla CATZONAS que tiene los campos:
           - cod_zona: código de la zona
           - nom_zona: nombre de la zona
           - Estatus: donde A=activo y B=Baja (ten en cuenta que este campo si tiene la letra "E" en la palabra "Estatus")      
        
        Solo devuelve el resultado de la consulta SQL, sin explicaciones adicionales. Un sólo query de sql compilable.
        Al final antes de compilar, asegurate de que la consulta SQL sea correcta y que no tenga ningún texto adicional luego del query que haria que 
        el query y falle.
                
        Pregunta: """ + pregunta

        #Si te preguntan sobre algún elemento activo debe ser algo como where status = 'A' para cualquier elemento de cualquiera de las tablas.
        #Para listar las tablas, usa: SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'
        #Solo devuelve la consulta SQL, sin explicaciones adicionales. Un sólo query de sql compilable.
        #Si te preguntan por una entidad contesta mencionando el nombre de la entidad
        # No devuelvas explicaciones adicionales.
        #Siempre que hagas inner joins y las tablas tengan alias cuando hagas referencia a los campos de las tablas, usa el alias de la tabla.



        # Llamada a Ollama
        response = requests.post(
            self.ollama_url,
            json={
                "model": "llama3.1:latest", # "llama3.2:latest", #llama3.1:latest
                "prompt": prompt,
                "stream": False
            }
        )
        
        # Agregar debugging para ver la estructura completa de la respuepythonsta
        print("Respuesta completa:", response.json())
        
        # Extraer la consulta SQL de la respuesta (modificado)p
        try:
            # Obtener la respuesta
            query = response.json().get('response', '')
            
            # Limpiar la consulta de TODOS los caracteres no deseados
            query = query.replace('```sql', '')
            query = query.replace('```', '')
            query = query.replace('`', '')
            query = query.strip()
            
            print(f"Consulta SQL limpia: {query}")  # Para ver la consulta después de limpiarla
            
            # Ejecutar consulta solo si no está vacía
            if query:
                df = pd.read_sql(query, self.conn)
                #return df
                return df.iloc[0,0]
            else:
                print("La consulta está vacía")
                return pd.DataFrame()
        except Exception as e:
            print(f"Error: {str(e)}")
            return pd.DataFrame()

# Ejemplo de uso
if __name__ == "__main__":
    chat = DBChat()
    #resultado = chat.procesar_pregunta("¿Cuáles son las tablas de la base de datos FABRICA_PASSA?")
    #resultado = chat.procesar_pregunta("¿Cuáles son los clientes activos?")
    # resultado = chat.procesar_pregunta("Cuántos clientes en total están activos?")
    # resultado = chat.procesar_pregunta("Cuántos proveedores en total están activos?")
    #resultado = chat.procesar_pregunta("Cuántos clientes activos hay de la zona culiacan?")
    resultado = chat.procesar_pregunta("Cuántos clientes activos hay de la zona culiacan que comienzan su nombre con la letra 'A'?")
    print(resultado)


