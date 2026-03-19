import tkinter as tk
import customtkinter as ctk 
from tkinter import messagebox, simpledialog, ttk 
import logic 
from menu_superior import ToolbarPrincipal 

# --- 1. COMPONENTE DE LA PUERTA ---
class PuertaHabitacion(ctk.CTkFrame):
    # AÑADIDO: color_borde="gray" para recibir el color desde dibujar_puertas
    def __init__(self, master, num_hab, estado='LIMPIA', comando=None, hover_comando=None, color_borde="#D4AF37"):
        super().__init__(master, width=140, height=180, fg_color="transparent")
        self.num_hab = num_hab
        self.estado = estado
        self.comando = comando
        self.hover_comando = hover_comando
        self.pack_propagate(False)

        # Número arriba (Usa el color dorado o el que venga del sistema)
        self.lbl_num = ctk.CTkLabel(self, text=num_hab, font=("Arial", 20, "bold"), text_color="#D4AF37")
        self.lbl_num.pack(pady=(10, 5))

        # La Puerta (Icono que se agranda) *
        # Usamos color_borde para que la puerta brille según su estado (Azul, Rojo, etc.)
        colores = {'LIMPIA': '#2E7D32', 'OCUPADA': '#C62828', 'SUCIA': '#EF6C00'}
        
        self.puerta_visual = ctk.CTkFrame(
            self, width=80, height=110, corner_radius=8, 
            fg_color=colores.get(estado, '#333333'), 
            border_width=3, 
            border_color=color_borde # <-- AQUÍ USAMOS EL COLOR QUE FALLABA
        )
        self.puerta_visual.pack(pady=5)
        self.puerta_visual.pack_propagate(False)

        # Estado abajo
        self.lbl_est = ctk.CTkLabel(self, text=estado, font=("Arial", 10), text_color="white")
        self.lbl_est.pack()

        # Eventos (Aseguramos que el click funcione en todos los elementos)
        self.puerta_visual.bind("<Enter>", self._agrandar)
        self.puerta_visual.bind("<Leave>", self._encoger)
        self.puerta_visual.bind("<Button-1>", lambda e: self.comando(self.num_hab))
        
        # Opcional: Que el número también sea clickeable
        self.lbl_num.bind("<Button-1>", lambda e: self.comando(self.num_hab))

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
        u = self.txt_usuario.get()
        c = self.txt_clave.get()
        
        if u == "Usuario" or c == "Contraseña":
            messagebox.showwarning("Atención", "Ingrese credenciales")
            return

        datos_usuario = logic.validar_login(u, c)
        
        if datos_usuario:
            # datos_usuario[0] es el ID (1)
            # datos_usuario[2] es 'Robinson Administrador'
            id_usuario = datos_usuario[0]
            nombre_real = datos_usuario[2]
            
            base = simpledialog.askfloat("Caja", f"Bienvenido {nombre_real}\nBase inicial:", initialvalue=0)
            
            if base is not None:
                id_turno = logic.gestionar_turno(id_usuario, base)
                # Guardamos para el mapa y las reservas
                self.root.sesion_exitosa = {
                    "id_usuario": id_usuario, 
                    "nombre": nombre_real, 
                    "id_turno": id_turno
                }
                self.root.withdraw() 
                self.root.quit()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
# --- 3. VENTANA PRINCIPAL (EL MAPA) ---
class VentanaPrincipal(ctk.CTk):
    
    # 1. ÚNICO AGREGADO: Diccionario de colores para los 6 estados
    COLORES_ESTADOS = {
        "LIMPIA": "#D4AF37",       # Dorado
        "OCUPADA": "#FF0000",      # Rojo
        "LIMPIEZA": "#FFFF00",     # Amarillo
        "RESERVADA": "#0000FF",    # Azul
        "TEMPORAL": "#800080",     # Morado
        "INHABILITADA": "#424242"  # Gris
    }

    def __init__(self, sesion=None):
        
        super().__init__()
        self.sesion = sesion
        self.title("HOTEL IMPERIAL V3")
        self.geometry("1200x750")
        self.configure(fg_color="black")

        # 1. Barra Superior (Toolbar)
        self.menu = ToolbarPrincipal(self, usuario_nom=self.sesion['nombre'], turno_id=self.sesion['id_turno'])
        self.menu.pack(side="top", fill="x")

        # --- CONTENEDOR PRINCIPAL ---
        self.contenedor_maestro = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_maestro.pack(fill="both", expand=True)

        # 2. PANEL IZQUIERDO: DETALLES
        self.panel_detalles = ctk.CTkFrame(self.contenedor_maestro, width=280, corner_radius=0, 
                                           fg_color="#1a1a1a", border_width=1, border_color="#D4AF37")
        self.panel_detalles.pack(side="left", fill="y", padx=(0, 5))
        self.panel_detalles.pack_propagate(False)

        ctk.CTkLabel(self.panel_detalles, text="DETALLES DE HABITACIÓN", 
                     font=("Garamond", 18, "bold"), text_color="#D4AF37").pack(pady=20)

        self.lbl_info_tecnica = ctk.CTkLabel(self.panel_detalles, text="Pase el mouse por\nuna puerta para ver info", 
                                             font=("Arial", 13), text_color="gray", justify="left")
        self.lbl_info_tecnica.pack(pady=30, padx=20)

        # --- 2. ÚNICO AGREGADO: Cuadro para Reservas Anticipadas ---
        ctk.CTkLabel(self.panel_detalles, text="RESERVAS PRÓXIMAS", 
                     font=("Garamond", 15, "bold"), text_color="#0000FF").pack(pady=(10, 0))
        
        self.txt_reservas_prox = ctk.CTkTextbox(self.panel_detalles, height=180, fg_color="#0d0d0d", 
                                                border_color="#0000FF", border_width=1, font=("Arial", 11))
        self.txt_reservas_prox.pack(padx=15, pady=10, fill="x")

        # 3. CONTENEDOR DERECHO: MAPA DE PUERTAS
        self.area_puertas = ctk.CTkScrollableFrame(self.contenedor_maestro, fg_color="black", 
                                                   label_text="MAPA DE HABITACIONES", label_text_color="#FFD700")
        self.area_puertas.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.dibujar_puertas()

    def actualizar_panel_izquierdo(self, num_hab):
        """Función que se activa con el HOVER de la puerta"""
        datos = logic.obtener_detalles_habitacion(num_hab)
        estado = logic.obtener_estado_hab(num_hab)
        
        # Colores de fondo del panel según estado
        colores = {'LIMPIA': '#1B4D3E', 'OCUPADA': '#4D1B1B', 'LIMPIEZA': '#4D331B', 'RESERVADA': '#1B1B4D'}
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
            # 3. ÚNICO AGREGADO: Color de borde según el diccionario
            color_borde = self.COLORES_ESTADOS.get(estado, "#D4AF37")

            puerta = PuertaHabitacion(
                self.area_puertas, 
                num, 
                estado, 
                comando=self.gestionar_clic_puerta,
                hover_comando=self.actualizar_panel_izquierdo,
                color_borde=color_borde # Para que la puerta sepa de qué color ser
            )
            puerta.grid(row=fila, column=col, padx=15, pady=15)
            
            col += 1
            if col > 3: 
                col = 0
                fila += 1

    def gestionar_clic_puerta(self, num_hab):
        """Lógica de decisión al hacer CLIC real"""
        estado = logic.obtener_estado_hab(num_hab)
        
        # MANTENEMOS TUS NOMBRES ORIGINALES
        if estado in ['LIMPIA', 'DISPONIBLE', 'RESERVADA']:
            # Usamos TU clase original para que no aparezca el error amarillo
            VentanaNuevaReserva(self, num_hab, self.sesion)
            
        elif estado == 'OCUPADA':
            # Usamos TU clase original
            VentanaDetalleHuesped(self, num_hab)
            
        elif estado == 'INHABILITADA':
            messagebox.showwarning("Bloqueo", f"La habitación {num_hab} se encuentra fuera de servicio.")
            
        else:
            # Caso Sucia/Mantenimiento/Limpieza
            messagebox.showinfo("Mantenimiento", f"La habitación {num_hab} requiere limpieza.")
# --- 4. VENTANA DE RESERVA ---
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
import logic


import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import messagebox

class VentanaNuevaReserva(ctk.CTkToplevel):
    def __init__(self, master, num_hab, sesion):
        super().__init__(master)
        self.num_hab = num_hab
        self.sesion = sesion
        
        self.title(f"Registro Habitación {self.num_hab}")
        self.geometry("900x750") 
        self.configure(fg_color="black")
        self.grab_set()

        # --- TÍTULO ---
        ctk.CTkLabel(self, text=f"REGISTRO HABITACIÓN {self.num_hab}", 
                     font=("Garamond", 28, "bold"), text_color="#D4AF37").pack(pady=15)

        # --- SECCIÓN 1: DATOS HUÉSPED ---
        self._etiqueta(self, "DATOS DEL HUÉSPED")
        
        self.frame_huesped = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_huesped.pack(fill="x", padx=20)
        self.frame_huesped.columnconfigure((0, 1), weight=1)

        # Usamos exactamente tus variables originales
        self.entry_nom = self._campo_grid(self.frame_huesped, "NOMBRE COMPLETO", 0, 0)
        self.entry_doc = self._campo_grid(self.frame_huesped, "IDENTIFICACIÓN", 0, 1)
        self.entry_cel = self._campo_grid(self.frame_huesped, "CELULAR", 1, 0)
        self.entry_email = self._campo_grid(self.frame_huesped, "EMAIL (OPCIONAL)", 1, 1)
        self.entry_proc = self._campo_grid(self.frame_huesped, "PROCEDENCIA", 2, 0, colspan=2)

        # Línea dorada divisoria
        ctk.CTkFrame(self, height=2, fg_color="#D4AF37").pack(fill="x", padx=40, pady=15)

        # --- SECCIÓN 2: DETALLES DE RESERVA Y PAGO ---
        self._etiqueta(self, "DETALLES DE RESERVA Y PAGO")

        self.frame_reserva = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_reserva.pack(fill="x", padx=20)
        self.frame_reserva.columnconfigure((0, 1), weight=1)

        # Calendarios (Manteniendo funcionalidad original)
        self.cal_entrada = self._calendario_grid(self.frame_reserva, "📅 FECHA ENTRADA", 0, 0)
        self.cal_salida = self._calendario_grid(self.frame_reserva, "📅 FECHA SALIDA (OPCIONAL)", 0, 1)

        # Combos y Valor Total
        import logic # Asegúrate que logic esté accesible
        folios_db = logic.cargar_folios_activos()
        opciones_f = [f"{f[0]} - {f[1]}" for f in folios_db]
        
        self.combo_folio = self._selector_grid(self.frame_reserva, "📁 VINCULAR A FOLIO", ["NUEVO FOLIO"] + opciones_f, 1, 0)
        self.entry_valor = self._campo_grid(self.frame_reserva, "💵 VALOR TOTAL RESERVA", 1, 1)

        # Fila final de selectores (3 columnas)
        self.frame_combos = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_combos.pack(fill="x", padx=20, pady=10)
        self.frame_combos.columnconfigure((0, 1, 2), weight=1)

        self.combo_pago = self._selector_grid(self.frame_combos, "💳 PAGO", ["EFECTIVO", "CREDITO", "TRANSFERENCIA"], 0, 0)
        self.combo_tipo_res = self._selector_grid(self.frame_combos, "🔘 TIPO", ["INMEDIATA", "ANTICIPADA", "TEMPORAL"], 0, 1)
        self.combo_estado = self._selector_grid(self.frame_combos, "✅ ESTADO", ["ACTIVA", "ANULADA"], 0, 2)

        # --- BOTÓN GUARDAR (CENTRADITO) ---
        self.btn_guardar = ctk.CTkButton(self, text="CONFIRMAR Y GUARDAR ✓", 
                                        fg_color="#D4AF37", text_color="black",
                                        font=("Arial", 16, "bold"), height=50, width=400,
                                        command=self.ejecutar_guardado)
        self.btn_guardar.pack(pady=25)

    # --- MÉTODOS DE SOPORTE (Mantienen tu lógica de diseño) ---
    def _campo_grid(self, parent, p_text, row, col, colspan=1):
        e = ctk.CTkEntry(parent, placeholder_text=p_text, height=35, 
                         border_color="#D4AF37", fg_color="#1A1A1A")
        e.grid(row=row, column=col, columnspan=colspan, padx=10, pady=8, sticky="ew")
        return e

    def _selector_grid(self, parent, titulo, valores, row, col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(f, text=titulo, font=("Arial", 10, "bold"), text_color="#D4AF37").pack(anchor="w")
        c = ctk.CTkComboBox(f, values=valores, border_color="#D4AF37", fg_color="#1A1A1A", button_color="#D4AF37")
        c.pack(fill="x")
        return c

    def _calendario_grid(self, parent, titulo, row, col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(f, text=titulo, font=("Arial", 10, "bold"), text_color="#D4AF37").pack(anchor="w")
        cal = DateEntry(f, background='#D4AF37', date_pattern='yyyy-mm-dd')
        cal.pack(fill="x", ipady=3)
        return cal

    def _etiqueta(self, parent, texto):
        ctk.CTkLabel(parent, text=texto, font=("Arial", 12, "bold"), text_color="#D4AF37").pack(pady=5)

    def ejecutar_guardado(self):
        # Esta es TU LOGICA ORIGINAL intacta
        datos = {
            'nro_hab': self.num_hab,
            'nombre': self.entry_nom.get().upper(),
            'identificacion': self.entry_doc.get(),
            'celular': self.entry_cel.get(),
            'email': self.entry_email.get() or "N/A",
            'procedencia': self.entry_proc.get() or "N/A",
            'f_entrada': self.cal_entrada.get(),
            'f_salida': self.cal_salida.get(),
            'v_reserva': self.entry_valor.get(),
            'forma_pago': self.combo_pago.get(),
            'tipo_reserva': self.combo_tipo_res.get(),
            'estado_reserva': self.combo_estado.get(),
            'folio_seleccionado': self.combo_folio.get() if "NUEVO" not in self.combo_folio.get() else None,
            'id_usuario': self.sesion['id_usuario'],
            'id_turno': self.sesion['id_turno']
        }
        
        import logic
        if logic.realizar_checkin_completo(datos):
            messagebox.showinfo("Éxito", "Registro guardado.")
            self.master.dibujar_puertas()
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo guardar.")

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
            
class VentanaCheckInMinimal(ctk.CTkToplevel):
    def __init__(self, master, num_hab, sesion, callback_refresh):
        super().__init__(master)
        self.title(f"Check-In Hab. {num_hab}")
        self.geometry("450x700") # Más alta para acomodar los campos
        self.configure(fg_color="black")
        
        self.num_hab = num_hab
        self.sesion = sesion
        self.callback_refresh = callback_refresh
        self.grab_set()

        # --- ESTILO ---
        dorado = "#D4AF37"
        negro_claro = "#1a1a1a"
        font_titulo = ("Garamond", 22, "bold")
        font_entrada = ("Arial", 12)
        font_boton = ("Arial", 13, "bold")

        # --- TÍTULO ---
        ctk.CTkLabel(self, text=f"REGISTRO HABITACIÓN {num_hab}", font=font_titulo, text_color=dorado).pack(pady=(25, 35))

        # --- CONTENEDOR DE CAMPOS (Con sangría lateral) ---
        self.frame_campos = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_campos.pack(padx=30, fill="both", expand=True)

        # Helper para crear entradas consistentes
        def crear_entrada(placeholder, width=350, height=45):
            entry = ctk.CTkEntry(self.frame_campos, 
                                 placeholder_text=placeholder, 
                                 font=font_entrada,
                                 width=width, 
                                 height=height, 
                                 border_color=dorado, 
                                 fg_color=negro_claro, 
                                 text_color="white")
            entry.pack(pady=10)
            return entry

        # 1. DATOS PERSONALES [huesped, identificacion, celular]
        self.ent_nombre = crear_entrada("Nombre Completo del Huésped")
        self.ent_doc = crear_entrada("Número de Identificación")
        self.ent_celular = crear_entrada("Celular de Contacto (Opcional)")

        # Separador visual sutil
        ctk.CTkFrame(self.frame_campos, height=1, fg_color="#333333").pack(fill="x", pady=15)

        # 2. DATOS DE ESTANCIA [fecha_salida]
        # Por ahora simple, lo ideal sería un DatePicker, pero usemos placeholder por ahora.
        self.ent_salida = crear_entrada("Fecha de Salida Estimada (YYYY-MM-DD)")

        # 3. DATOS FINANCIEROS [valor_reserva, adelanto]
        self.ent_valor_total = crear_entrada("Valor Total de la Reserva ($)")
        
        # Este dato va a la tabla de 'pagos' o al folio, pero es crucial en el Check-In
        self.ent_adelanto = crear_entrada("Monto de Adelanto / Pago Inicial ($)")

        # --- BOTÓN DE CONFIRMACIÓN ---
        self.btn_confirmar = ctk.CTkButton(self, 
                                           text="CONFIRMAR E INGRESAR", 
                                           font=font_boton,
                                           fg_color=dorado, 
                                           text_color="black", 
                                           hover_color="#B8860B",
                                           height=50, 
                                           width=280, 
                                           command=self.procesar_checkin)
        self.btn_confirmar.pack(pady=40)

    def procesar_checkin(self):
        # Captura básica de datos
        datos = {
            'nro_hab': self.num_hab,
            'nombre': self.ent_nombre.get(),
            'identificacion': self.ent_doc.get(),
            'celular': self.ent_celular.get(),
            'f_salida': self.ent_salida.get(),
            'v_total': self.ent_valor_total.get(),
            'adelanto': self.ent_adelanto.get() or "0", # Manejo de adelanto
            'id_usuario': self.sesion['id_usuario'],
            'id_turno': self.sesion['id_turno']
        }

        # Validación rápida
        if not datos['nombre'] or not datos['identificacion'] or not datos['v_total']:
            messagebox.showwarning("Atención", "Por favor, complete al menos: Nombre, Identificación y Valor Total.")
            return

        # --- Conexión con LOGIC ---
        # Pasamos el diccionario completo para que logic lo inserte en reservas, folios y pagos.
        exito = logic.realizar_checkin_completo(datos)

        if exito:
            messagebox.showinfo("¡Éxito!", f"Check-In de Hab. {self.num_hab} realizado correctamente.\nSe ha creado el folio.")
            self.callback_refresh() # Refresca el mapa (cambia a ROJO)
            self.destroy() # Cierra la ventana
        else:
            messagebox.showerror("Error", "Hubo un problema al guardar la reserva. Revise la base de datos.")