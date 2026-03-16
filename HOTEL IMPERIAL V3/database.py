import psycopg2
from config import DB_CONFIG

def conectar():
    try:
        # Los asteriscos ** pasan todo el diccionario de config automáticamente
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_client_encoding('UTF8')
        return conn
    except Exception as e:
        print(f"Error al conectar: {e}")
        return None

def ejecutar_query(query, params=None, fetch=False):
    conexion = conectar()
    if conexion:
        try:
            cur = conexion.cursor()
            cur.execute(query, params)
            
            # Si queremos leer datos (SELECT), fetch es True
            if fetch:
                resultado = cur.fetchall()
            else:
                # Si queremos guardar datos (INSERT), hacemos commit
                conexion.commit()
                resultado = True
                
            cur.close()
            conexion.close()
            return resultado
        except Exception as e:
            print(f"Error en la consulta: {e}")
            return None
    return None