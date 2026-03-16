import tkinter as tk
from tkinter import messagebox,simpledialog
from tkinter import ttk # Necesario para la tabla (Treeview)
from logic import validar_login
from logic import gestionar_turno
from logic import obtener_folios_db
from logic import crear_folio_db


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
        
        # Limpiar placeholders
        user_f = "" if u == "Usuario" else u
        pass_f = "" if c == "Contraseña" else c

        datos_usuario = validar_login(user_f, pass_f)
        if datos_usuario:
            id_usuario = datos_usuario[0]
            base = simpledialog.askfloat("Caja", "Base inicial:", initialvalue=0)
            
            if base is not None:
                id_turno = gestionar_turno(id_usuario, base)
                sesion = {"id_usuario": id_usuario, "nombre": datos_usuario[2], "id_turno": id_turno}
                

                # 3. Ocultamos la de login (o la destruimos)
                self.root.withdraw()
                # Creamos la principal como una ventana nueva
                nueva_ventana = tk.Toplevel() 
                VentanaPrincipal(nueva_ventana, sesion)

            else:
                messagebox.showwarning("Cancelado", "Debe ingresar una base para iniciar.")
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")


# --- 3. VENTANA PRINCIPAL (Centro de Mando) ---
class VentanaPrincipal:
    def __init__(self, root, sesion):
        self.root = root
        self.sesion = sesion # Aquí vive el id_turno para usarlo después
        self.root.title("Hotel Imperial - Menú Principal")
        self.root.geometry("800x500")
        self.root.configure(bg="black")

        # Barra de estado superior (Dorada)
        self.barra_estado = tk.Frame(self.root, bg="#D4AF37", height=30)
        self.barra_estado.pack(fill="x")
        
        info = f"USUARIO: {self.sesion['nombre']}  |  TURNO ACTIVO: {self.sesion['id_turno']}"
        tk.Label(self.barra_estado, text=info, bg="#D4AF37", fg="black", 
                 font=("Arial", 9, "bold")).pack(side="left", padx=20)

        # Contenedor de botones
        self.menu_frame = tk.Frame(self.root, bg="black")
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.menu_frame, text="PANEL DE CONTROL", bg="black", fg="#D4AF37", 
                 font=("Garamond", 24, "bold")).pack(pady=30)
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
        # Botones elegantes
        btn_estilo = {"bg": "#D4AF37", "fg": "black", "font": ("Arial", 11, "bold"), 
                      "width": 30, "bd": 0, "cursor": "hand2", "pady": 10}

        tk.Button(self.menu_frame, text="GESTIÓN DE RESERVAS / FOLIOS", **btn_estilo,
                  command=self.abrir_reservas).pack(pady=10)
        
        tk.Button(self.menu_frame, text="CIERRE DE CAJA", **btn_estilo).pack(pady=10)

    def abrir_reservas(self):        
        # Creamos la ventana de reservas y le pasamos el ID del turno de la sesión
        ventana_res = tk.Toplevel(self.root)
        VentanaReservas(ventana_res, self.sesion['id_turno'])


class VentanaReservas:
    def __init__(self, root, id_turno):
        self.root = root
        self.id_turno = id_turno
        self.root.title("Gestión de Folios - Hotel Imperial")
        self.root.geometry("900x600")
        self.root.configure(bg="black")

        # --- FORMULARIO SUPERIOR ---
        frame_form = tk.Frame(self.root, bg="black")
        frame_form.pack(pady=20)

        # Nombre con texto interno
        self.ent_nombre = tk.Entry(frame_form, bg="#1a1a1a", fg="gray", insertbackground="#D4AF37",
                                   highlightthickness=1, highlightbackground="#D4AF37", font=("Arial", 12), width=30)
        self.ent_nombre.insert(0, "Nombre del Huésped")
        self.ent_nombre.pack(side="left", padx=10)

        # ID con texto interno
        self.ent_id = tk.Entry(frame_form, bg="#1a1a1a", fg="gray", insertbackground="#D4AF37",
                               highlightthickness=1, highlightbackground="#D4AF37", font=("Arial", 12), width=20)
        self.ent_id.insert(0, "Identificación")
        self.ent_id.pack(side="left", padx=10)

        # Botón Guardar
        btn_guardar = tk.Button(frame_form, text="ABRIR FOLIO", bg="#D4AF37", fg="black", 
                                font=("Arial", 10, "bold"), command=self.guardar_folio)
        btn_guardar.pack(side="left", padx=10)

        # --- TABLA DE FOLIOS (Treeview) ---
        self.crear_tabla()
        self.cargar_datos()

    def crear_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1a1a1a", foreground="white", fieldbackground="#1a1a1a", rowheight=25)
        style.map("Treeview", background=[('selected', '#D4AF37')], foreground=[('selected', 'black')])

        self.tabla = ttk.Treeview(self.root, columns=("ID", "Nombre", "ID Cliente", "Estado", "Fecha"), show='headings')
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Nombre", text="Huésped")
        self.tabla.heading("ID Cliente", text="Identificación")
        self.tabla.heading("Estado", text="Estado")
        self.tabla.heading("Fecha", text="Fecha Apertura")
        
        self.tabla.pack(pady=20, padx=20, fill="both", expand=True)

    def cargar_datos(self):
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        # Traer de la DB
        for fila in obtener_folios_db():
            self.tabla.insert("", "end", values=fila)

    def guardar_folio(self):
        nom = self.ent_nombre.get()
        ident = self.ent_id.get()
        
        if nom == "Nombre del Huésped" or ident == "Identificación":
            messagebox.showwarning("Atención", "Complete los datos")
            return

        # Llamamos a la función de guardado que hicimos antes
        if crear_folio_db(nom, ident, self.id_turno):
            messagebox.showinfo("Éxito", "Folio creado")
            self.cargar_datos() # Refresca la tabla automáticamente       