from database import ejecutar_query

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