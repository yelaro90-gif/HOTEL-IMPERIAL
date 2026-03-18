import customtkinter as ctk
# Importamos ambas clases para que no haya subrayados rojos
from formularios import VentanaLogin, VentanaPrincipal 

if __name__ == "__main__":
    # Configuramos el estilo visual del Hotel Imperial
    ctk.set_appearance_mode("dark")
    
    # 1. Creamos la base para el Login
    root = ctk.CTk() 
    
    # 2. Iniciamos con la ventana de Login
    app = VentanaLogin(root)
    
    # 3. Mantenemos el Login activo hasta que se valide el usuario
    root.mainloop()

    # --- AQUÍ EMPIEZA LA CONEXIÓN CON TU CÓDIGO DE GIT ---
    # Si el login fue exitoso y guardó la sesión en el root
    if hasattr(root, 'sesion_exitosa'):
        # Creamos la VentanaPrincipal con el mapa de habitaciones
        app_mapa = VentanaPrincipal(sesion=root.sesion_exitosa)
        
        # Función de seguridad para cerrar todo al final
        def cerrar_sistema_completo():
            app_mapa.destroy() # Cierra el mapa
            root.destroy()      # Cierra el login oculto
            
        # Configuramos la "X" del mapa para que cierre ambos procesos
        app_mapa.protocol("WM_DELETE_WINDOW", cerrar_sistema_completo)
        
        # Iniciamos el mapa
        app_mapa.mainloop()