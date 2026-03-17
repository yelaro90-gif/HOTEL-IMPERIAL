import tkinter as tk
import customtkinter as ctk 
from tkinter import messagebox, simpledialog, ttk 
import logic 
from menu_superior import ToolbarPrincipal 

# --- 1. COMPONENTE DE LA PUERTA ---
class PuertaHabitacion(ctk.CTkFrame):
    def __init__(self, master, num_hab, estado='LIMPIA', comando=None):
        super().__init__(master, width=140, height=170, corner_radius=12, border_color="#D4AF37", border_width=2)
        self.num_hab = num_hab
        self.comando = comando
        
        colores = {
            'LIMPIA': '#2E7D32', 'OCUPADA': '#C62828', 
            'TEMPORAL': '#6A1B9A', 'RESERVADA': '#1565C0', 
            'SUCIA': '#EF6C00', 'INACTIVA': '#333333'
        }
        
        self.configure(fg_color=colores.get(estado, '#2E7D32'))
        
        ctk.CTkLabel(self, text=num_hab, font=("Arial", 28, "bold"), text_color="white").pack(pady=(25, 0))
        ctk.CTkLabel(self, text=estado, font=("Arial", 11, "bold"), text_color="#FFD700").pack(pady=10)

        self.bind("<Button-1>", lambda e: self.comando(self.num_hab))
        for widget in self.winfo_children():
            widget.bind("<Button-1>", lambda e: self.comando(self.num_hab))

# --- 2. VENTANA LOGIN ---
class VentanaLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Imperial - Acceso")
        self.root.geometry("350x450")
        self.root.configure(bg="black") 

        self.frame = tk.Frame(self.root, bg="black", padx=30, pady=30, highlightbackground="#D4AF37", highlightthickness=2)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.frame, text="HOTEL IMPERIAL", bg="black", fg="#D4AF37", font=("Garamond", 18, "bold")).pack(pady=(0, 30))
        
        self.txt_usuario = tk.Entry(self.frame, font=("Arial", 12), bg="#1a1a1a", fg="gray", insertbackground="#D4AF37", bd=0, highlightthickness=1, highlightbackground="#D4AF37")
        self.txt_usuario.insert(0, "Usuario")
        self.txt_usuario.pack(fill="x", pady=10, ipady=7)

        self.txt_clave = tk.Entry(self.frame, font=("Arial", 12), bg="#1a1a1a", fg="gray", insertbackground="#D4AF37", bd=0, highlightthickness=1, highlightbackground="#D4AF37")
        self.txt_clave.insert(0, "Contraseña")
        self.txt_clave.pack(fill="x", pady=10, ipady=7)

        tk.Button(self.frame, text="ENTRAR", bg="#D4AF37", fg="black", font=("Arial", 10, "bold"), command=self.intentar_entrar).pack(fill="x", pady=30, ipady=10)

    def intentar_entrar(self):
        u = self.txt_usuario.get()
        c = self.txt_clave.get()
        datos_usuario = logic.validar_login(u, c)
        
        if datos_usuario:
            id_usuario = datos_usuario[0]
            base = simpledialog.askfloat("Caja", "Base inicial:", initialvalue=0)
            if base is not None:
                id_turno = logic.gestionar_turno(id_usuario, base)
                sesion = {"id_usuario": id_usuario, "nombre": datos_usuario[2], "id_turno": id_turno}
                
                self.root.destroy() # Cerramos login
                app_mapa = VentanaPrincipal(sesion=sesion) # Lanzamos mapa
                app_mapa.mainloop()
        else:
            messagebox.showerror("Error", "Datos incorrectos")

# --- 3. VENTANA PRINCIPAL (EL MAPA) ---
class VentanaPrincipal(ctk.CTk):
    def __init__(self, sesion=None):
        super().__init__()
        self.sesion = sesion
        self.title("HOTEL IMPERIAL V3")
        self.geometry("1100x700")
        self.configure(fg_color="black")

        # Barra Superior
        self.menu = ToolbarPrincipal(self, usuario_nom=self.sesion['nombre'], turno_id=self.sesion['id_turno'])
        self.menu.pack(side="top", fill="x")

        # Contenedor de Puertas
        self.area_puertas = ctk.CTkScrollableFrame(self, fg_color="black", label_text="MAPA DE HABITACIONES", label_text_color="#FFD700")
        self.area_puertas.pack(fill="both", expand=True, padx=20, pady=20)

        self.dibujar_puertas()

    def dibujar_puertas(self):
        habitaciones_datos = logic.obtener_todas_habitaciones()
        for widget in self.area_puertas.winfo_children():
            widget.destroy()

        col, fila = 0, 0
        for num, estado in habitaciones_datos:
            puerta = PuertaHabitacion(self.area_puertas, num, estado, self.gestionar_clic_puerta)
            puerta.grid(row=fila, column=col, padx=15, pady=15)
            col += 1
            if col > 3: col = 0; fila += 1

    def gestionar_clic_puerta(self, num_hab):
        estado = logic.obtener_estado_hab(num_hab)
        if estado == 'LIMPIA':
            VentanaNuevaReserva(self, num_hab, self.sesion)
        else:
            messagebox.showinfo("Aviso", f"Habitación {num_hab} en estado: {estado}")

# --- 4. VENTANA DE RESERVA ---
class VentanaNuevaReserva(ctk.CTkToplevel):
    def __init__(self, master, num_hab, sesion):
        super().__init__(master)
        self.num_hab = num_hab
        self.sesion = sesion
        self.title(f"Registro Habitación {self.num_hab}")
        self.geometry("400x500")
        self.configure(fg_color="black")
        self.grab_set()

        ctk.CTkLabel(self, text=f"HABITACIÓN {self.num_hab}", font=("Arial", 20, "bold"), text_color="#D4AF37").pack(pady=20)
        self.entry_nom = ctk.CTkEntry(self, placeholder_text="NOMBRE DEL HUÉSPED", width=300)
        self.entry_nom.pack(pady=10)
        
        ctk.CTkButton(self, text="GUARDAR", fg_color="#D4AF37", text_color="black", command=self.destroy).pack(pady=20)