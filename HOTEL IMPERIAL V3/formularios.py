import tkinter as tk
from tkinter import messagebox
from logic import validar_login

# --- 1. VENTANA DE LOGIN (Negro y Dorado) ---
class VentanaLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Imperial - Acceso")
        self.root.geometry("350x450")
        self.root.configure(bg="black") 
        self.root.resizable(False, False)

        # Contenedor central con borde dorado
        self.frame = tk.Frame(self.root, bg="black", padx=30, pady=30, 
                              highlightbackground="#D4AF37", highlightthickness=2)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.frame, text="HOTEL IMPERIAL", bg="black", fg="#D4AF37", 
                 font=("Garamond", 18, "bold")).pack(pady=(0, 30))
        
        # --- Campo Usuario con Placeholder ---
        self.txt_usuario = tk.Entry(self.frame, font=("Arial", 12), bg="#1a1a1a", fg="gray",
                                    insertbackground="#D4AF37", bd=0, highlightthickness=1, 
                                    highlightbackground="#D4AF37")
        self.txt_usuario.insert(0, "Usuario")
        self.txt_usuario.bind("<FocusIn>", lambda e: self.limpiar_placeholder(self.txt_usuario, "Usuario"))
        self.txt_usuario.bind("<FocusOut>", lambda e: self.poner_placeholder(self.txt_usuario, "Usuario"))
        self.txt_usuario.pack(fill="x", pady=10, ipady=7)

        # --- Campo Clave con Placeholder ---
        self.txt_clave = tk.Entry(self.frame, font=("Arial", 12), bg="#1a1a1a", fg="gray",
                                  insertbackground="#D4AF37", bd=0, highlightthickness=1, 
                                  highlightbackground="#D4AF37")
        self.txt_clave.insert(0, "Contraseña")
        self.txt_clave.bind("<FocusIn>", lambda e: self.limpiar_placeholder(self.txt_clave, "Contraseña", ocultar=True))
        self.txt_clave.bind("<FocusOut>", lambda e: self.poner_placeholder(self.txt_clave, "Contraseña", ocultar=True))
        self.txt_clave.pack(fill="x", pady=10, ipady=7)

        # Botón Dorado
        btn_entrar = tk.Button(self.frame, text="ENTRAR", bg="#D4AF37", fg="black", 
                               font=("Arial", 10, "bold"), bd=0, cursor="hand2",
                               activebackground="#B8860B", command=self.intentar_entrar)
        btn_entrar.pack(fill="x", pady=30, ipady=10)

    def limpiar_placeholder(self, entry, texto, ocultar=False):
        if entry.get() == texto:
            entry.delete(0, tk.END)
            entry.config(fg="white")
            if ocultar: entry.config(show="*")

    def poner_placeholder(self, entry, texto, ocultar=False):
        if not entry.get():
            entry.insert(0, texto)
            entry.config(fg="gray")
            if ocultar: entry.config(show="")

    def intentar_entrar(self):
        u = self.txt_usuario.get()
        c = self.txt_clave.get()
        
        # Limpieza de placeholders para la lógica
        user_final = "" if u == "Usuario" else u
        pass_final = "" if c == "Contraseña" else c

        datos_usuario = validar_login(user_final, pass_final)
        
        if datos_usuario:
            messagebox.showinfo("Éxito", f"Acceso concedido: {datos_usuario[2]}\n¡Bienvenido al sistema!")
            # Por ahora no abrimos ninguna otra ventana, solo confirmamos el acceso
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")