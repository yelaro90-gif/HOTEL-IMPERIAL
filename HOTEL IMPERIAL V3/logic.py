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

# --- AJUSTE EN CARGA DE FOLIOS (Para que solo salgan ABIERTOS) ---
def cargar_folios_activos():
    conexion = conectar()
    if not conexion: return []
    try:
        cur = conexion.cursor()
        # Filtro estricto: solo ABIERTO
        cur.execute("SELECT id_folio, nombre_responsable FROM folios WHERE estado = 'ABIERTO' ORDER BY id_folio DESC")
        return cur.fetchall()
    except Exception as e:
        print(f"Error al cargar folios: {e}")
        return []
    finally:
        conexion.close()

# --- NUEVA FUNCIÓN: CERRAR FOLIO COMPLETO ---
def cerrar_folio_y_salida(num_hab, id_folio):
    """Libera la habitación y cierra el folio para que no aparezca más en listas."""
    conexion = conectar()
    if not conexion: return False
    try:
        cur = conexion.cursor()
        
        # 1. Liberar la habitación actual
        cur.execute("UPDATE reservas SET estado = 'FINALIZADA' WHERE habitacion = %s AND estado = 'OCUPADA'", (num_hab,))
        cur.execute("UPDATE habitaciones SET estado_aseo = 'LIMPIEZA' WHERE nro_habitacion = %s", (num_hab,))
        
        # 2. Cerrar el Folio (Ya no saldrá en los ComboBox)
        cur.execute("UPDATE folios SET estado = 'CERRADO' WHERE id_folio = %s", (id_folio,))
        
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al cerrar folio: {e}")
        conexion.rollback()
        return False
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
# --- FUNCIONES PARA CONSULTAR OCUPACIÓN ACTUAL ---

def obtener_detalles_huesped_actual(num_hab):
    conexion = conectar()
    if not conexion: return None
    try:
        cur = conexion.cursor()
        sql = """
            SELECT r.nombre_huesped, r.identificacion, r.celular, r.procedencia, 
                   r.fecha_entrada, r.fecha_salida, r.valor_reserva, r.forma_pago, r.estado,
                   r.id_folio_vinculado, f.nombre_responsable
            FROM reservas r
            LEFT JOIN folios f ON r.id_folio_vinculado = f.id_folio
            WHERE r.habitacion = %s AND r.estado IN ('OCUPADA', 'RESERVADA')
            ORDER BY r.id_reserva DESC LIMIT 1
        """
        cur.execute(sql, (num_hab,))
        res = cur.fetchone()
        
        if res:
            return {
                'nombre': res[0],
                'identificacion': res[1],
                'celular': res[2],
                'procedencia': res[3],
                'f_entrada': res[4],
                'f_salida': res[5] if res[5] else "N/A",
                'v_reserva': res[6], # <--- Este es tu TOTAL PROVISIONAL
                'forma_pago': res[7],
                'estado_reserva': res[8],
                'id_folio': res[9],
                'responsable_folio': res[10]
            }
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conexion.close()
def liberar_habitacion(num_hab):
    """
    Finaliza la estancia (Check-out). 
    Cambia el estado de la reserva a 'FINALIZADA' y la hab a 'LIMPIEZA' (o LIMPIA).
    """
    conexion = conectar()
    if not conexion: return False
    try:
        cur = conexion.cursor()
        
        # 1. Finalizar la reserva activa
        sql_res = "UPDATE reservas SET estado = 'FINALIZADA' WHERE habitacion = %s AND estado = 'OCUPADA'"
        cur.execute(sql_res, (num_hab,))
        
        # 2. Poner la habitación en LIMPIEZA (siguiendo tu lógica de estados)
        sql_hab = "UPDATE habitaciones SET estado_aseo = 'LIMPIEZA' WHERE nro_habitacion = %s"
        cur.execute(sql_hab, (num_hab,))
        
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al liberar habitación: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()
def registrar_tercero(datos):
    """Inserta los datos del formulario en la tabla terceros"""
    conexion = conectar() # Tu función de conexión
    if not conexion: return False
    try:
        cur = conexion.cursor()
        query = """
            INSERT INTO terceros (nombres, tipo_id, identificacion, direccion, 
                                 telefono, correo, rol_principal, cargo_especialidad)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            datos['nombres'], datos['tipo_id'], datos['id'], 
            datos['direccion'], datos['telefono'], datos['correo'], 
            datos['rol'], datos['cargo']
        )
        cur.execute(query, valores)
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error en BD: {e}")
        return False
    finally:
        conexion.close()    
def guardar_cuenta_bancaria(id_tercero, numero, tipo, descripcion):
    conexion = conectar()
    if not conexion: return False
    try:
        cur = conexion.cursor()
        # Añadimos el campo estado con valor True por defecto
        query = """
            INSERT INTO cuentas_bancarias (id_tercero, numero_cuenta, tipo_cuenta, descripcion, estado)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (id_tercero, numero, tipo, descripcion, True))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error logic.guardar_cuenta_bancaria: {e}")
        return False
    finally:
        conexion.close()
def obtener_id_tercero_por_identificacion(identificacion):
    conexion = conectar()
    if not conexion: return None
    try:
        cur = conexion.cursor()
        cur.execute("SELECT id_tercero FROM terceros WHERE identificacion = %s", (identificacion,))
        resultado = cur.fetchone()
        return resultado[0] if resultado else None
    finally:
        conexion.close()       
def cambiar_estado_cuenta(id_cuenta, nuevo_estado):
    """
    Cambia el estado de una cuenta (True para activa, False para inactiva)
    """
    conexion = conectar()
    if not conexion: return False
    try:
        cur = conexion.cursor()
        # Usamos un UPDATE para no borrar el registro, solo ocultarlo
        cur.execute("UPDATE cuentas_bancarias SET estado = %s WHERE id_cuenta = %s", 
                    (nuevo_estado, id_cuenta))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error logic.cambiar_estado_cuenta: {e}")
        return False
    finally:
        conexion.close()
def obtener_personal_aseo():
    conexion = conectar()
    if not conexion: return []
    try:
        cur = conexion.cursor()
        # Filtramos por el cargo que definimos ayer
        query = "SELECT id_tercero, nombres FROM terceros WHERE cargo_especialidad = 'ASEO' AND estado = True"
        cur.execute(query)
        return cur.fetchall() # Devuelve lista de tuplas [(id, nombre), ...]
    finally:
        conexion.close()
# --- GESTIÓN DE HISTORIAL DE ASEO Y ESTADOS ---

def iniciar_limpieza(num_hab, id_empleado):
    """Registra el inicio del aseo y vincula al empleado"""
    conexion = conectar()
    if not conexion: return False
    try:
        cur = conexion.cursor()
        # 1. Obtener el id_habitacion interno usando el nro_habitacion
        cur.execute("SELECT id_habitacion FROM habitaciones WHERE nro_habitacion = %s", (num_hab,))
        res = cur.fetchone()
        if not res: return False
        id_hab_interno = res[0]

        # 2. Insertar en el historial (Usando los nombres de tu nueva tabla)
        query_h = """
            INSERT INTO historial_aseo (id_habitacion, id_empleado, fecha_inicio, estado_final)
            VALUES (%s, %s, CURRENT_TIMESTAMP, 'EN PROCESO')
        """
        cur.execute(query_h, (id_hab_interno, id_empleado))
        
        # 3. Actualizar el estado de la habitación a 'LIMPIEZA'
        cur.execute("UPDATE habitaciones SET estado_aseo = 'LIMPIEZA' WHERE nro_habitacion = %s", (num_hab,))
        
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error logic.iniciar_limpieza: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()

def finalizar_limpieza(num_hab):
    """Cierra el historial y pone la habitación como LIMPIA (Dorado)"""
    conexion = conectar()
    if not conexion: return False
    try:
        cur = conexion.cursor()
        # 1. Obtener ID interno
        cur.execute("SELECT id_habitacion FROM habitaciones WHERE nro_habitacion = %s", (num_hab,))
        id_hab_interno = cur.fetchone()[0]

        # 2. Finalizar el registro en historial_aseo
        query_f = """
            UPDATE historial_aseo 
            SET fecha_fin = CURRENT_TIMESTAMP, estado_final = 'TERMINADA'
            WHERE id_habitacion = %s AND estado_final = 'EN PROCESO'
        """
        cur.execute(query_f, (id_hab_interno,))
        
        # 3. Cambiar a estado LIMPIA
        cur.execute("UPDATE habitaciones SET estado_aseo = 'LIMPIA' WHERE nro_habitacion = %s", (num_hab,))
        
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error logic.finalizar_limpieza: {e}")
        return False
    finally:
        conexion.close()

def obtener_aseo_en_progreso(num_hab):
    """Verifica si una habitación está siendo limpiada actualmente"""
    conexion = conectar()
    if not conexion: return None
    try:
        cur = conexion.cursor()
        query = """
            SELECT t.nombres 
            FROM historial_aseo h
            JOIN terceros t ON h.id_empleado = t.id_tercero
            JOIN habitaciones hab ON h.id_habitacion = hab.id_habitacion
            WHERE hab.nro_habitacion = %s AND h.estado_final = 'EN PROCESO'
        """
        cur.execute(query, (num_hab,))
        res = cur.fetchone()
        return res[0] if res else None
    finally:
        conexion.close()
# --- NUEVAS FUNCIONES DE ASEO ---

def obtener_aseo_en_progreso(num_hab):
    """Verifica si alguien está limpiando la habitación actualmente"""
    conexion = conectar()
    if not conexion: return None
    try:
        cur = conexion.cursor()
        query = """
            SELECT t.nombres 
            FROM historial_aseo h
            JOIN terceros t ON h.id_empleado = t.id_tercero
            JOIN habitaciones hab ON h.id_habitacion = hab.id_habitacion
            WHERE hab.nro_habitacion = %s AND h.estado_final = 'EN PROCESO'
        """
        cur.execute(query, (num_hab,))
        res = cur.fetchone()
        return res[0] if res else None
    finally:
        conexion.close()

def finalizar_limpieza(num_hab):
    """Cierra el historial y cambia estado a LIMPIA"""
    conexion = conectar()
    if not conexion: return False
    try:
        cur = conexion.cursor()
        # 1. Obtener ID interno de la hab
        cur.execute("SELECT id_habitacion FROM habitaciones WHERE nro_habitacion = %s", (num_hab,))
        id_int = cur.fetchone()[0]
        # 2. Finalizar historial
        cur.execute("UPDATE historial_aseo SET fecha_fin = CURRENT_TIMESTAMP, estado_final = 'TERMINADA' WHERE id_habitacion = %s AND estado_final = 'EN PROCESO'", (id_int,))
        # 3. Cambiar a LIMPIA
        cur.execute("UPDATE habitaciones SET estado_aseo = 'LIMPIA' WHERE nro_habitacion = %s", (num_hab,))
        conexion.commit()
        return True
    except:
        return False
    finally:
        conexion.close()