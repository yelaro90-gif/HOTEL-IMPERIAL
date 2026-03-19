import tkinter as tk
import customtkinter as ctk 
from tkinter import messagebox, simpledialog, ttk 
import logic 
from menu_superior import ToolbarPrincipal 

# --- 1. COMPONENTE DE LA PUERTA ---
class PuertaHabitacion(ctk.CTkFrame):
    def __init__(self, master, num_hab, estado='LIMPIA', comando=None, hover_comando=None):
        super().__init__(master, width=140, height=180, fg_color="transparent")
        self.num_hab = num_hab
        self.estado = estado
        self.comando = comando
        self.hover_comando = hover_comando
        self.pack_propagate(False)

        # Número arriba
        self.lbl_num = ctk.CTkLabel(self, text=num_hab, font=("Arial", 20, "bold"), text_color="#D4AF37")
        self.lbl_num.pack(pady=(10, 5))

        # La Puerta (Icono que se agranda)
        colores = {'LIMPIA': '#2E7D32', 'OCUPADA': '#C62828', 'SUCIA': '#EF6C00'}
        self.puerta_visual = ctk.CTkFrame(self, width=80, height=110, corner_radius=8, 
                                          fg_color=colores.get(estado, '#333333'), 
                                          border_width=2, border_color="#D4AF37")
        self.puerta_visual.pack(pady=5)
        self.puerta_visual.pack_propagate(False)

        # Estado abajo
        self.lbl_est = ctk.CTkLabel(self, text=estado, font=("Arial", 10), text_color="white")
        self.lbl_est.pack()

        # Eventos
        self.puerta_visual.bind("<Enter>", self._agrandar)
        self.puerta_visual.bind("<Leave>", self._encoger)
        self.puerta_visual.bind("<Button-1>", lambda e: self.comando(self.num_hab))

    def _agrandar(self, event):
        self.puerta_visual.configure(width=95, height=125)
        if self.hover_comando:
            try:
                self.hover_comando(self.num_hab)
            except Exception as e:
                print(f"Error en hover: {e}")

    def _encoger(self, event):
        self.puerta_visual.configure(width=80, height=110)
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
        
        # --- INPUT USUARIO ---
        self.txt_usuario = tk.Entry(self.frame, font=("Arial", 12), bg="#1a1a1a", fg="gray", 
                                    insertbackground="#D4AF37", bd=0, highlightthickness=1, highlightbackground="#D4AF37")
        self.txt_usuario.insert(0, "Usuario")
        self.txt_usuario.pack(fill="x", pady=10, ipady=7)
        
        # Eventos para limpiar el texto
        self.txt_usuario.bind('<FocusIn>', lambda e: self.on_entry_click(self.txt_usuario, "Usuario"))
        self.txt_usuario.bind('<FocusOut>', lambda e: self.on_focusout(self.txt_usuario, "Usuario"))

        # --- INPUT CLAVE ---
        self.txt_clave = tk.Entry(self.frame, font=("Arial", 12), bg="#1a1a1a", fg="gray", 
                                  insertbackground="#D4AF37", bd=0, highlightthickness=1, highlightbackground="#D4AF37")
        self.txt_clave.insert(0, "Contraseña")
        self.txt_clave.pack(fill="x", pady=10, ipady=7)
        
        # Eventos para limpiar el texto y ocultar la clave
        self.txt_clave.bind('<FocusIn>', lambda e: self.on_entry_click(self.txt_clave, "Contraseña"))
        self.txt_clave.bind('<FocusOut>', lambda e: self.on_focusout(self.txt_clave, "Contraseña"))

        tk.Button(self.frame, text="ENTRAR", bg="#D4AF37", fg="black", font=("Arial", 10, "bold"), 
                  cursor="hand2", command=self.intentar_entrar).pack(fill="x", pady=30, ipady=10)

    # --- FUNCIONES PARA EL TEXTO DINÁMICO ---
    def on_entry_click(self, entry, placeholder):
        """Borra el texto cuando el usuario hace clic"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.insert(0, '')
            entry.config(fg='white') # Cambia a blanco al escribir
            if placeholder == "Contraseña":
                entry.config(show="*") # Oculta los caracteres solo si es la clave

    def on_focusout(self, entry, placeholder):
        """Pone el texto de nuevo si el usuario deja el campo vacío"""
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.config(fg='gray')
            if placeholder == "Contraseña":
                entry.config(show="") # Muestra la palabra "Contraseña" de nuevo

    def intentar_entrar(self):
        # ... (Tu lógica de validación se mantiene igual) ...
        u = self.txt_usuario.get()
        c = self.txt_clave.get()
        
        # Evitar que mande la palabra "Usuario" o "Contraseña" como datos reales
        if u == "Usuario" or c == "Contraseña":
            messagebox.showwarning("Atención", "Por favor ingrese sus credenciales")
            return

        datos_usuario = logic.validar_login(u, c)
        if datos_usuario:
            id_usuario = datos_usuario[0]
            base = simpledialog.askfloat("Caja", "Base inicial:", initialvalue=0)
            if base is not None:
                id_turno = logic.gestionar_turno(id_usuario, base)
                self.root.sesion_exitosa = {"id_usuario": id_usuario, "nombre": datos_usuario[2], "id_turno": id_turno}
                self.root.withdraw() 
                self.root.quit()
        else:
            messagebox.showerror("Error", "Datos incorrectos")
# --- 3. VENTANA PRINCIPAL (EL MAPA) ---
class VentanaPrincipal(ctk.CTk):
    def __init__(self, sesion=None):
        super().__init__()
        self.sesion = sesion
        self.title("HOTEL IMPERIAL V3")
        self.geometry("1200x750")
        self.configure(fg_color="black")

        # 1. Barra Superior (Toolbar)
        self.menu = ToolbarPrincipal(self, usuario_nom=self.sesion['nombre'], turno_id=self.sesion['id_turno'])
        self.menu.pack(side="top", fill="x")

        # --- CONTENEDOR PRINCIPAL (Para separar Panel de Mapa) ---
        self.contenedor_maestro = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_maestro.pack(fill="both", expand=True)

        # 2. PANEL IZQUIERDO: DETALLES (Fijo a la izquierda)
        self.panel_detalles = ctk.CTkFrame(self.contenedor_maestro, width=280, corner_radius=0, 
                                           fg_color="#1a1a1a", border_width=1, border_color="#D4AF37")
        self.panel_detalles.pack(side="left", fill="y", padx=(0, 5))
        self.panel_detalles.pack_propagate(False) # Evita que se encoja

        ctk.CTkLabel(self.panel_detalles, text="DETALLES DE HABITACIÓN", 
                     font=("Garamond", 18, "bold"), text_color="#D4AF37").pack(pady=20)

        # Etiqueta dinámica para la información técnica
        self.lbl_info_tecnica = ctk.CTkLabel(self.panel_detalles, text="Pase el mouse por\nuna puerta para ver info", 
                                             font=("Arial", 13), text_color="gray", justify="left")
        self.lbl_info_tecnica.pack(pady=50, padx=20)

        # 3. CONTENEDOR DERECHO: MAPA DE PUERTAS (Scrollable)
        self.area_puertas = ctk.CTkScrollableFrame(self.contenedor_maestro, fg_color="black", 
                                                   label_text="MAPA DE HABITACIONES", label_text_color="#FFD700")
        self.area_puertas.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.dibujar_puertas()

    def actualizar_panel_izquierdo(self, num_hab):
        """Función que se activa con el HOVER de la puerta"""
        # Obtenemos datos técnicos y estado
        datos = logic.obtener_detalles_habitacion(num_hab)
        estado = logic.obtener_estado_hab(num_hab)
        
        # Colores según estado para el fondo del panel
        colores = {'LIMPIA': '#1B4D3E', 'OCUPADA': '#4D1B1B', 'SUCIA': '#4D331B'}
        nuevo_color = colores.get(estado, '#1a1a1a')
        
        self.panel_detalles.configure(fg_color=nuevo_color)
        
        texto_detalle = (
            f"HABITACIÓN: {num_hab}\n\n"
            f"ESTADO: {estado}\n"
            f"TIPO: {datos.get('tipo', 'N/A')}\n"
            f"VISTA: {datos.get('vista', 'N/A')}\n"
            f"VENTILACIÓN: {datos.get('aire', 'N/A')}"
        )
        self.lbl_info_tecnica.configure(text=texto_detalle, text_color="white", font=("Arial", 14, "bold"))

    def dibujar_puertas(self):
        """Renderiza las puertas en la cuadrícula"""
        habitaciones_datos = logic.obtener_todas_habitaciones()
        for widget in self.area_puertas.winfo_children():
            widget.destroy()

        col, fila = 0, 0
        for num, estado in habitaciones_datos:
            # Pasamos tanto la función de CLIC como la de HOVER
            puerta = PuertaHabitacion(
                self.area_puertas, 
                num, 
                estado, 
                comando=self.gestionar_clic_puerta,
                hover_comando=self.actualizar_panel_izquierdo # Conecta el movimiento del mouse
            )
            puerta.grid(row=fila, column=col, padx=15, pady=15)
            
            col += 1
            if col > 3: # 4 columnas por fila
                col = 0
                fila += 1

    def gestionar_clic_puerta(self, num_hab):
        """Lógica de decisión al hacer CLIC real"""
        estado = logic.obtener_estado_hab(num_hab)
        
        if estado in ['LIMPIA', 'DISPONIBLE']:
            # Caso disponible -> Registro
            VentanaNuevaReserva(self, num_hab, self.sesion)
        elif estado == 'OCUPADA':
            # Caso ocupada -> Ver Huésped
            VentanaDetalleHuesped(self, num_hab)
        else:
            # Caso Sucia/Mantenimiento
            messagebox.showinfo("Mantenimiento", f"La habitación {num_hab} requiere limpieza.")
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
# --- 5. VENTANA DETALLE HUÉSPED ---
class VentanaDetalleHuesped(ctk.CTkToplevel):
    def __init__(self, master, num_hab):
        super().__init__(master)
        self.title(f"Información Habitación {num_hab}")
        self.geometry("500x400")
        self.configure(fg_color="black")
        self.grab_set() # Bloquea la ventana de atrás hasta cerrar esta

        # Título dorado
        ctk.CTkLabel(self, text=f"DETALLES DE OCUPACIÓN - HAB {num_hab}", 
                     font=("Garamond", 18, "bold"), text_color="#D4AF37").pack(pady=20)

        # Contenedor para la "Tabla"
        self.frame_tabla = ctk.CTkFrame(self, fg_color="#1a1a1a", border_color="#D4AF37", border_width=1)
        self.pack_propagate(False)
        self.frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        # Traemos los datos de la persona desde logic
        datos = logic.obtener_datos_huesped(num_hab) # Debes crear esta función en logic.py

        # Filas de la tabla (Etiqueta: Valor)
        campos = [
            ("NOMBRE:", datos.get('nombre', 'N/A')),
            ("DOCUMENTO:", datos.get('doc', 'N/A')),
            ("INGRESO:", datos.get('fecha_in', 'N/A')),
            ("SALIDA:", datos.get('fecha_out', 'N/A')),
            ("TOTAL PAGO:", f"${datos.get('pago', 0)}")
        ]

        for i, (label, valor) in enumerate(campos):
            f = ctk.CTkFrame(self.frame_tabla, fg_color="transparent")
            f.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(f, text=label, font=("Arial", 12, "bold"), text_color="#D4AF37", width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=valor, font=("Arial", 12), text_color="white").pack(side="left")

        # Botones de acción
        ctk.CTkButton(self, text="CERRAR CUENTA", fg_color="#C62828", text_color="white", 
                      command=lambda: self.finalizar_estadia(num_hab)).pack(side="left", padx=50, pady=20)
        ctk.CTkButton(self, text="VOLVER", fg_color="#333333", command=self.destroy).pack(side="right", padx=50, pady=20)

    def finalizar_estadia(self, num):
        if messagebox.askyesno("Confirmar", f"¿Desea liberar la habitación {num}?"):
            logic.cambiar_estado_hab(num, 'SUCIA')
            self.master.dibujar_puertas() # Refresca el mapa
            self.destroy()       