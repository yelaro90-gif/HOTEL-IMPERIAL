# config.py

# 1. Configuración de la Base de Datos
DB_CONFIG = {
    "host": "127.0.0.1",
    "database": "hotel_imperial",
    "user": "postgres",
    "password": "Confiestaseguridad",
    "port": "5432"
}

# 2. Configuración Visual (Colores)
DORADO = "#C5A059"
NEGRO_FONDO = "#1A1A1A"
NEGRO_LATERAL = "#121212"
BLANCO_HUESO = "#F5F5F5"

# 3. Estados de las habitaciones
COLORES_ESTADO = {
    "Disponible": DORADO, 
    "Ocupado": "#E74C3C", 
    "Limpieza": "#F39C12", 
    "Inactiva": "#5D6D7E"
}