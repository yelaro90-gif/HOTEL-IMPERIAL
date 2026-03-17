import customtkinter as ctk
from formularios import VentanaLogin

if __name__ == "__main__":
    # Configuramos el estilo visual del Hotel Imperial
    ctk.set_appearance_mode("dark")
    
    # Creamos la base para el Login
    root = ctk.CTk() 
    
    # Iniciamos con la ventana de Login
    app = VentanaLogin(root)
    
    # Mantenemos la aplicación activa
    root.mainloop()