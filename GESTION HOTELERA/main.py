# main.py
import tkinter as tk
from database import obtener_habitaciones, ejecutar_query
from logic import abrir_checkin
from config import *

class HotelImperialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SISTEMA HOTELERO IMPERIAL v3.0")
        self.root.geometry("1100x850")
        self.root.configure(bg=NEGRO_FONDO)
        
        # Sidebar Lateral
        self.sidebar = tk.Frame(self.root, bg=NEGRO_LATERAL, width=200)
        self.sidebar.pack(side="left", fill="y")
        
        tk.Label(self.sidebar, text="IMPERIAL", fg=DORADO, bg=NEGRO_LATERAL, font=("Times New Roman", 22, "bold")).pack(pady=40)
        
        # Área Principal (Mapa)
        self.area_mapa = tk.Frame(self.root, bg=NEGRO_FONDO)
        self.area_mapa.pack(side="left", expand=True, fill="both", padx=30, pady=30)
        
        tk.Button(self.sidebar, text="MAPA DE HABITACIONES", command=self.dibujar_mapa, bg=DORADO, relief="flat", font=("Arial", 9, "bold")).pack(fill="x", padx=20, pady=10)
        
        self.dibujar_mapa()

    def dibujar_mapa(self):
        # Limpiar el área antes de dibujar para que no se encimen
        for widget in self.area_mapa.winfo_children():
            widget.destroy()
            
        habitaciones = obtener_habitaciones()
        if not habitaciones:
            tk.Label(self.area_mapa, text="No hay habitaciones cargadas en la DB.", fg="white", bg=NEGRO_FONDO).pack()
            return

        r, c = 0, 0
        for hab in habitaciones:
            num, tipo, est, mant = hab
            color = COLORES_ESTADO.get(est, DORADO) if mant == 'Activa' else COLORES_ESTADO['Inactiva']
            
            # Contenedor de cada habitación
            f = tk.Frame(self.area_mapa, bg=NEGRO_FONDO, width=130, height=170)
            f.grid(row=r, column=c, padx=15, pady=15)
            f.pack_propagate(False)
            
            tk.Label(f, text=f"Hab {num}", bg=NEGRO_FONDO, fg="white", font=("Arial", 8, "bold")).pack()
            
            # Icono de la Puerta
            lbl_puerta = tk.Label(f, text="走", font=("Arial", 55), bg=NEGRO_FONDO, fg=DORADO, cursor="hand2")
            # Si prefieres el emoji: lbl_puerta = tk.Label(f, text="🚪", font=("Arial", 50), bg=NEGRO_FONDO, fg=DORADO)
            lbl_puerta.pack()
            
            # Etiqueta de Estado
            lbl_est = tk.Label(f, text=est.upper(), font=("Arial", 7, "bold"), bg=color, fg="white")
            lbl_est.pack(fill="x", pady=2)

            # Lógica de clicks según el estado
            if est == "Disponible":
                lbl_puerta.bind("<Button-1>", lambda e, n=num: abrir_checkin(n, self.dibujar_mapa))
            elif est == "Limpieza":
                lbl_puerta.bind("<Button-1>", lambda e, n=num: self.liberar_limpieza(n))
            elif est == "Ocupado":
                lbl_puerta.bind("<Button-1>", lambda e, n=num: messagebox.showinfo("Ocupado", f"Habitación {n} ocupada. Gestión de cuenta en desarrollo."))

            c += 1
            if c > 4: # 5 columnas
                c = 0
                r += 1

    def liberar_limpieza(self, num_hab):
        if messagebox.askyesno("Limpieza", f"¿Marcar habitación {num_hab} como Disponible?"):
            ejecutar_query("UPDATE habitaciones SET estado = 'Disponible' WHERE numero = %s", (num_hab,))
            self.dibujar_mapa()

if __name__ == "__main__":
    root = tk.Tk()
    app = HotelImperialApp(root)
    root.mainloop()