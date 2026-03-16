import tkinter as tk
from formularios import VentanaLogin

if __name__ == "__main__":
    root = tk.Tk()
    # Iniciamos con la ventana de Login
    app = VentanaLogin(root)
    root.mainloop()