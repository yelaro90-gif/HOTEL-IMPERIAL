from logic import validar_login

# Prueba 1: Datos correctos
user = validar_login("admin", "1234")
if user:
    print(f"¡Bienvenido {user[2]}! Tu rol es: {user[3]}")
else:
    print("Usuario o clave incorrectos.")

# Prueba 2: Datos incorrectos
error = validar_login("admin", "clave_falsa")
if not error:
    print("La validación de error también funciona correctamente.")