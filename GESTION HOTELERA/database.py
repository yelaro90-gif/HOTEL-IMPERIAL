# database.py
import psycopg2
from config import DB_CONFIG

def ejecutar_query(query, params=None, fetch=False):
    """Ejecuta una consulta SQL y retorna resultados si se solicita."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        curr = conn.cursor()
        curr.execute(query, params)
        res = curr.fetchall() if fetch else None
        conn.commit()
        curr.close()
        conn.close()
        return res
    except Exception as e:
        print(f"Error en base de datos: {e}")
        return None

def obtener_habitaciones():
    """Trae la lista de habitaciones para dibujar el mapa."""
    return ejecutar_query("SELECT numero, tipo, estado, estado_mantenimiento FROM habitaciones ORDER BY numero", fetch=True)

def buscar_tercero_por_id(identificacion):
    """Busca si una persona ya existe en la tabla de terceros."""
    query = """SELECT nombres, apellidos, direccion, correo, telefono, ocupacion, procedencia 
               FROM terceros WHERE identificacion = %s"""
    res = ejecutar_query(query, (identificacion,), fetch=True)
    return res[0] if res else None