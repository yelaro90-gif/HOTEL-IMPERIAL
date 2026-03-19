from database import ejecutar_query
from database import conectar
from datetime import datetime, date

# --- FUNCIONES DE FOLIOS * ---

def registrar_folio(nombre, identificacion, id_turno_apertura, tipo="CONTADO"):
    """
    Crea un folio vinculado al turno actual y define si es Crédito o Contado.
    Retorna el ID del folio recién creado para vincularlo a la reserva.
    """
    conexion = conectar()
    if not conexion: return False
    try:
        cur = conexion.cursor()
        # Usamos la tabla 'folios' con las columnas de estado y tipo_cuenta
        sql = """
            INSERT INTO folios (nombre_responsable, identificacion, id_turno_apertura, estado, tipo_cuenta)
            VALUES (%s, %s, %s, 'ABIERTO', %s) RETURNING id_folio
        """
        cur.execute(sql, (nombre, identificacion, id_turno_apertura, tipo))
        id_nuevo = cur.fetchone()[0]
        conexion.commit()
        return id_nuevo # Devolvemos el ID para que la reserva sepa a qué folio pegarse
    except Exception as e:
        print(f"Error al registrar folio: {e}")
        return False
    finally:
        conexion.close()

def cargar_folios_activos():
    conexion = conectar()
    if not conexion: return []
    try:
        cur = conexion.cursor()
        cur.execute("SELECT id_folio, nombre_responsable FROM folios WHERE estado = 'ABIERTO' ORDER BY id_folio DESC")
        return cur.fetchall()
    except Exception as e:
        print(f"Error al cargar folios: {e}")
        return []
    finally:
        conexion.close()

# --- ACCESO Y SEGURIDAD (Ajustado para tu formularios.py) ---

def validar_login(usuario, clave):
    """Ajustado a tus columnas reales: id, usuario, password, nombre_completo *"""
    conexion = conectar()
    if not conexion: return None
    try:
        cur = conexion.cursor()
        # Nombres exactos de tu imagen
        sql = "SELECT id, usuario, nombre_completo FROM usuarios WHERE usuario = %s AND password = %s"
        
        # .strip() para evitar espacios invisibles
        cur.execute(sql, (usuario.strip(), clave.strip())) 
        resultado = cur.fetchone()
        
        # resultado será algo como (1, 'admin', 'Robinson Administrador')
        return resultado 
    except Exception as e:
        print(f"Error en consulta login: {e}")
        return None
    finally:
        conexion.close()

def gestionar_turno(id_usuario, base_inicial=0):
    sql_buscar = "SELECT id_turno FROM turnos WHERE id_usuario = %s AND estado = 'ABIERTO'"
    resultado = ejecutar_query(sql_buscar, (id_usuario,), fetch=True)
    
    if resultado:
        return resultado[0][0]
    
    sql_insertar = "INSERT INTO turnos (id_usuario, base_caja, estado) VALUES (%s, %s, 'ABIERTO')"
    parametros = (id_usuario, base_inicial)
    ejecutar_query(sql_insertar, parametros)
    
    res = ejecutar_query("SELECT MAX(id_turno) FROM turnos WHERE id_usuario = %s", (id_usuario,), fetch=True)
    return res[0][0]

# --- GESTIÓN DE HABITACIONES Y ESTADOS * ---

def obtener_todas_habitaciones():
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT nro_habitacion, estado_aseo FROM habitaciones ORDER BY nro_habitacion ASC")
        datos = cur.fetchall()
        cur.close()
        conn.close()
        return datos
    except Exception as e:
        print(f"Error en logic: {e}")
        return []

def obtener_estado_hab(num_hab):
    habitaciones = obtener_todas_habitaciones()
    for num, estado in habitaciones:
        if str(num) == str(num_hab):
            return estado
    return "LIMPIA"

def obtener_detalles_habitacion(num_hab):
    sql = "SELECT estado_general, tipo_vista, tipo_ventilacion FROM habitaciones WHERE nro_habitacion = %s"
    parametros = (num_hab,)
    try:
        resultado = ejecutar_query(sql, parametros, fetch=True)
        if resultado and len(resultado) > 0:
            fila = resultado[0]
            return {
                "tipo": str(fila[0]),
                "vista": str(fila[1]),
                "aire": str(fila[2])
            }
        return {"tipo": "N/A", "vista": "N/A", "aire": "N/A"}
    except:
        return {"tipo": "Error", "vista": "Error", "aire": "Error"}

# --- LÓGICA DE RESERVAS Y CHECK-IN (Final con Validación) ---

def realizar_checkin_completo(datos):
    conexion = conectar()
    if not conexion: return False
    cur = conexion.cursor()
    
    try:
        # AÑADIDO: VALIDACIÓN DE DISPONIBILIDAD (Evita que reserven la misma hab en mismas fechas)
        sql_val = """
            SELECT id_reserva FROM reservas 
            WHERE habitacion = %s AND estado NOT IN ('CANCELADA', 'FINALIZADA')
            AND ((%s BETWEEN fecha_entrada AND fecha_salida) 
                 OR (%s BETWEEN fecha_entrada AND fecha_salida))
        """
        cur.execute(sql_val, (datos['nro_hab'], datos['f_entrada'], datos['f_salida']))
        if cur.fetchone() and datos['f_salida'].strip() != "":
            return "CRUCE"

        # 1. GESTIÓN AUTOMÁTICA DE FOLIO *
        id_folio_final = None
        if not datos.get('id_folio') or datos.get('id_folio') == "NUEVO FOLIO":
            sql_folio = """
                INSERT INTO folios (nombre_responsable, identificacion, estado, tipo_cuenta) 
                VALUES (%s, %s, 'ABIERTO', %s) RETURNING id_folio
            """
            tipo = "CREDITO" if datos['forma_pago'] == "CREDITO" else "CONTADO"
            cur.execute(sql_folio, (datos['nombre'], datos['identificacion'], tipo))
            id_folio_final = cur.fetchone()[0]
        else:
            id_folio_final = datos['id_folio'].split(" - ")[0]

        # 2. DETERMINAR ESTADO
        hoy = date.today().strftime('%Y-%m-%d')
        estado_hab = "OCUPADA" if datos['f_entrada'] == hoy else "RESERVADA"

        # 3. INSERTAR EN TABLA RESERVAS (19 campos) *
        sql_reserva = """
            INSERT INTO reservas (
                habitacion, nombre_huesped, identificacion, email, celular, procedencia,
                fecha_entrada, fecha_salida, valor_reserva, forma_pago, tipo_reserva,
                id_usuario, id_turno_registro, id_folio_vinculado, estado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        f_salida = datos['f_salida'] if datos['f_salida'] and datos['f_salida'].strip() != "" else None

        valores = (
            datos['nro_hab'], datos['nombre'], datos['identificacion'], datos['email'],
            datos['celular'], datos['procedencia'], datos['f_entrada'], f_salida,
            datos['v_reserva'], datos['forma_pago'], datos['tipo_reserva'],
            datos['id_usuario'], datos['id_turno'], id_folio_final, estado_hab
        )
        cur.execute(sql_reserva, valores)

        # 4. ACTUALIZAR HABITACIÓN
        cur.execute("UPDATE habitaciones SET estado_aseo = %s WHERE nro_habitacion = %s", 
                    (estado_hab, datos['nro_hab']))

        conexion.commit()
        return True
    except Exception as e:
        print(f"Error en logic: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()