# logic.py
import tkinter as tk
from tkinter import messagebox
from database import ejecutar_query, buscar_tercero_por_id
from config import *

def abrir_checkin(num_hab, callback_update):
    ventana = tk.Toplevel()
    ventana.title(f"Check-In Habitación {num_hab}")
    ventana.geometry("500x750")
    ventana.configure(bg=NEGRO_LATERAL)
    ventana.grab_set()

    entries = {}
    # Definimos los campos que pediste
    campos = [
        ("Identificación (DNI)", "id"), ("Nombres", "nom"), ("Apellidos", "ape"), 
        ("Dirección", "dir"), ("Correo", "mail"), ("Teléfono", "tel"),
        ("Ocupación", "ocu"), ("Procedencia", "proc"), ("Turno", "turno"), 
        ("Unir a Folio (Vacio = Nuevo)", "folio")
    ]

    for i, (label_text, key) in enumerate(campos):
        tk.Label(ventana, text=label_text, bg=NEGRO_LATERAL, fg="white", font=("Arial", 9)).pack(pady=2)
        e = tk.Entry(ventana, bg=NEGRO_FONDO, fg="white", insertbackground="white", relief="flat")
        e.pack(pady=5, fill="x", padx=40, ipady=3)
        entries[key] = e

    def auto_completar():
        """Busca en la tabla terceros y rellena si existe"""
        id_t = entries["id"].get()
        data = buscar_tercero_por_id(id_t)
        if data:
            # Orden: nombres, apellidos, direccion, correo, telefono, ocupacion, procedencia
            claves = ["nom", "ape", "dir", "mail", "tel", "ocu", "proc"]
            for i, clave in enumerate(claves):
                entries[clave].delete(0, tk.END)
                entries[clave].insert(0, str(data[i]) if data[i] else "")
            messagebox.showinfo("Imperial", "Datos de Tercero cargados correctamente.")

    tk.Button(ventana, text="🔍 Buscar en Terceros", command=auto_completar, bg=DORADO, font=("Arial", 8, "bold")).pack(pady=10)

    def guardar():
        id_t = entries["id"].get()
        nom = entries["nom"].get()
        if not id_t or not nom:
            messagebox.showwarning("Error", "ID y Nombres son obligatorios.")
            return

        # 1. UPSERT en Terceros (Actualiza datos si ya existe el ID)
        ejecutar_query("""
            INSERT INTO terceros (identificacion, nombres, apellidos, direccion, correo, telefono, ocupacion, procedencia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (identificacion) DO UPDATE SET 
            nombres=EXCLUDED.nombres, apellidos=EXCLUDED.apellidos, correo=EXCLUDED.correo, telefono=EXCLUDED.telefono
        """, (id_t, nom, entries["ape"].get(), entries["dir"].get(), entries["mail"].get(), 
              entries["tel"].get(), entries["ocu"].get(), entries["proc"].get()))
        
        # 2. Lógica de Folio: Si está vacío, crea uno nuevo
        f_id = entries["folio"].get()
        if not f_id:
            res = ejecutar_query("INSERT INTO cuentas_folios (nombre_responsable, identificacion) VALUES (%s, %s) RETURNING id", 
                                 (f"{nom} {entries['ape'].get()}", id_t), fetch=True)
            f_id = res[0][0]

        # 3. Crear Reserva y ocupar habitación
        ejecutar_query("INSERT INTO reservas (folio_id, habitacion_num, identificacion_tercero, turno) VALUES (%s, %s, %s, %s)", 
                       (f_id, num_hab, id_t, entries["turno"].get()))
        ejecutar_query("UPDATE habitaciones SET estado = 'Ocupado' WHERE numero = %s", (num_hab,))
        
        messagebox.showinfo("Éxito", f"Check-in completado. Folio: {f_id}")
        ventana.destroy()
        callback_update() # Esta función redibuja el mapa automáticamente

    tk.Button(ventana, text="CONFIRMAR ENTRADA", command=guardar, bg=DORADO, fg=NEGRO_FONDO, font=("Arial", 10, "bold"), pady=10).pack(pady=20, fill="x", padx=40)