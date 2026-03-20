import customtkinter as ctk

class ToolbarPrincipal(ctk.CTkFrame):
    def __init__(self, master, usuario_nom, turno_id, **kwargs):
        super().__init__(master, fg_color="#1a1a1a", height=45, corner_radius=0, **kwargs)
        
        # Estilo Dorado para botones de barra
        estilo_btn = {
            "fg_color": "transparent",
            "text_color": "#FFD700",
            "hover_color": "#333333",
            "font": ("Arial", 12, "bold"),
            "width": 100
        }

        # --- SECCIÓN IZQUIERDA: Botones tipo Menú VBA ---
        self.btn_archivo = ctk.CTkButton(self, text="ARCHIVO", **estilo_btn)
        self.btn_archivo.pack(side="left", padx=2)

        # Usaremos EDICIÓN para abrir Terceros (o puedes crear uno nuevo)
        self.btn_edicion = ctk.CTkButton(self, text="TERCEROS", **estilo_btn, 
                                         command=self.master.abrir_registro_terceros)
        self.btn_edicion.pack(side="left", padx=2)

        self.btn_herramientas = ctk.CTkButton(self, text="HERRAMIENTAS", **estilo_btn)
        self.btn_herramientas.pack(side="left", padx=2)

        # --- SECCIÓN DERECHA: Datos del Sistema ---
        self.lbl_info = ctk.CTkLabel(self, text=f"👤 {usuario_nom} | 🕒 Turno: {turno_id}", 
                                     text_color="#FFD700", font=("Arial", 11))
        self.lbl_info.pack(side="right", padx=20)