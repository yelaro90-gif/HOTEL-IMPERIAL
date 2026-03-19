from database import ejecutar_query
from database import conectar


def registrar_folio(nombre, identificacion):
    """
    Toma el nombre e ID y los manda a guardar.
    Usa fetch=False (por defecto) para que el motor haga COMMIT.
    """
    sql = "INSERT INTO cuentas_folios (nombre_responsable, identificacion) VALUES (%s, %s)"
    parametros = (nombre, identificacion)
    # Ejecutamos y devolvemos True si funcionó
    return ejecutar_query(sql, parametros)

def cargar_folios():
    """
    Pide todos los folios para mostrarlos en la lista.
    Usa fetch=True para que el motor devuelva los datos (FETCHALL).
    """
    sql = "SELECT id, nombre_responsable, identificacion FROM cuentas_folios ORDER BY id DESC"
    # Ejecutamos y devolvemos la lista de folios
    return ejecutar_query(sql, fetch=True)

def validar_login(usuario, clave):
    """
    Busca un usuario que coincida con el nombre y la contraseña.
    Devuelve los datos del usuario si existe, o None si no coinciden.
    """
    sql = "SELECT id, usuario, nombre_completo, rol FROM usuarios WHERE usuario = %s AND password = %s"
    parametros = (usuario, clave)
    
    # Usamos fetch=True porque queremos traer los datos del usuario logueado
    resultado = ejecutar_query(sql, parametros, fetch=True)
    
    # Si la lista tiene algo, significa que el usuario y clave son correctos
    if resultado and len(resultado) > 0:
        return resultado[0]  # Devolvemos la primera fila encontrada
    return None

def gestionar_turno(id_usuario, base_inicial=0):
    # 1. Buscar si ya hay un turno ABIERTO para este usuario
    sql_buscar = "SELECT id_turno FROM turnos WHERE id_usuario = %s AND estado = 'ABIERTO'"
    resultado = ejecutar_query(sql_buscar, (id_usuario,), fetch=True)
    
    if resultado:
        return resultado[0][0] # Retorna el ID si ya existe uno abierto
    
    # 2. Si no hay, crear uno nuevo con la base de caja
    sql_insertar = "INSERT INTO turnos (id_usuario, base_caja) VALUES (%s, %s)"
    parametros = (id_usuario, base_inicial)
    
    # Usamos una pequeña trampa para obtener el ID recién creado
    ejecutar_query(sql_insertar, parametros)
    
    # Buscamos el ID que acabamos de insertar
    res = ejecutar_query("SELECT MAX(id_turno) FROM turnos WHERE id_usuario = %s", (id_usuario,), fetch=True)
    return res[0][0]

def crear_folio_db(nombre, identificacion, id_turno_apertura):
    conexion = conectar()
    if not conexion: return False
    try:
        cursor = conexion.cursor()
        sql = """
            INSERT INTO folios (nombre_responsable, identificacion, id_turno_apertura, estado)
            VALUES (%s, %s, %s, 'ABIERTO')
        """
        cursor.execute(sql, (nombre, identificacion, id_turno_apertura))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conexion.close()

def obtener_folios_db():
    conexion = conectar()
    if not conexion: return []
    try:
        cursor = conexion.cursor()
        # Traemos solo los folios ABIERTOS para la gestión diaria
        cursor.execute("SELECT id_folio, nombre_responsable, identificacion, estado, fecha_apertura FROM folios WHERE estado = 'ABIERTO' ORDER BY id_folio DESC")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener folios: {e}")
        return []
    finally:
        conexion.close()

def obtener_todas_habitaciones():
    try:
        # Asegúrate de que conectar_db esté importado o definido en logic.py
        from database import conectar
        conn = conectar()
        cur = conn.cursor()
        # Traemos el número y el estado de aseo de la tabla que acabas de llenar
        cur.execute("SELECT nro_habitacion, estado_aseo FROM habitaciones ORDER BY nro_habitacion ASC")
        datos = cur.fetchall()
        cur.close()
        conn.close()
        return datos # Retorna una lista tipo [('101', 'LIMPIA'), ('102', 'SUCIA')...]
    except Exception as e:
        print(f"Error en logic: {e}")
        return []

# --- FUNCIÓN DE DETALLES CORREGIDA CON TUS COLUMNAS REALES ---

def obtener_detalles_habitacion(num_hab):
    """Consulta la base de datos Postgres con las columnas reales de tu tabla"""
    print(f"Buscando habitación {num_hab} en la base de datos...") 

    # Nombres de columnas según tu imagen de la tabla 'habitaciones'
    sql = "SELECT estado_general, tipo_vista, tipo_ventilacion FROM habitaciones WHERE nro_habitacion = %s"
    parametros = (num_hab,)
    
    try:
        resultado = ejecutar_query(sql, parametros, fetch=True)

        if resultado and len(resultado) > 0:
            fila = resultado[0]
            return {
                "tipo": str(fila[0]),       # estado_general (DISPONIBLE, etc)
                "vista": str(fila[1]),      # tipo_vista (CALLE, INTERIOR)
                "aire": str(fila[2])        # tipo_ventilacion (VENTILADOR, AIRE)
            }
        else:
            return {"tipo": "N/A", "vista": "N/A", "aire": "N/A"}
            
    except Exception as e:
        print(f"Error leyendo BD: {e}")
        return {"tipo": "Error BD", "vista": "Error BD", "aire": "Error BD"}

def obtener_datos_huesped(num_hab):
    """Retorna quién está en la habitación cuando está OCUPADA"""
    return {
        'nombre': 'Cliente Imperial',
        'doc': '12345678',
        'fecha_in': '2026-03-19',
        'fecha_out': 'Pendiente',
        'pago': 250000
    }

def obtener_estado_hab(num_hab):
    """Devuelve el estado actual de una habitación específica"""
    habitaciones = obtener_todas_habitaciones()
    for num, estado in habitaciones:
        if str(num) == str(num_hab):
            return estado
    return "LIMPIA"