import customtkinter as ctk
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import os
import time
import subprocess
import sys
import random
import platform

# Librerías externas
try:
    from PIL import Image
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False

try:
    import psutil
    PSUTIL_DISPONIBLE = True
except ImportError:
    PSUTIL_DISPONIBLE = False

# Configuraciones base de suavidad
ctk.set_appearance_mode("dark")

# Paleta de colores "Soft Dark"
BG_COLOR = "#1E1E2E"       
PANEL_COLOR = "#313244"    
ACCENT_COLOR = "#89B4FA"   # Azul (CPU)
RAM_COLOR = "#A6E3A1"      # Verde (RAM)
TEXT_COLOR = "#CDD6F4"
HOST_COLOR = "#F5C2E7"     # Rosa (.exe)

class AetherOS(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AetherOS")
        self.after(0, lambda: self.attributes('-fullscreen', True))
        self.configure(fg_color=BG_COLOR)

        # Base de datos simulada
        self.sistema_archivos = {
            "Documentos": [{"nombre": "notas.txt", "icono": "📝", "info": "12 KB"}],
            "Imágenes": [],
            "Proyectos": []
        }
        self.carpeta_actual = "Documentos"
        self.app_drawer = None
        self.apps_terceros = {} 
        self.apps_host = {}     

        # Historial para gráficos
        self.historial_cpu = [0] * 60
        self.historial_ram = [0] * 60
        self.seccion_actual = "CPU" 

        self.crear_barra_superior_flotante()
        self.crear_escritorio()

    # ==========================================
    # INTERFAZ BASE
    # ==========================================
    def crear_barra_superior_flotante(self):
        self.barra = ctk.CTkFrame(self, height=45, corner_radius=25, fg_color=PANEL_COLOR)
        self.barra.pack(side="top", fill="x", padx=20, pady=15)

        self.btn_menu = ctk.CTkButton(self.barra, text="A", width=35, height=35, 
                                      font=("Arial", 16, "bold"), corner_radius=18, 
                                      fg_color=ACCENT_COLOR, hover_color="#B4BEFE",
                                      text_color=BG_COLOR, command=self.alternar_menu)
        self.btn_menu.pack(side="left", padx=10, pady=5)

        self.lbl_reloj = ctk.CTkLabel(self.barra, text="", font=("Arial", 13, "bold"), text_color=TEXT_COLOR)
        self.lbl_reloj.pack(side="right", padx=20)
        self.actualizar_reloj()

    def crear_escritorio(self):
        self.frame_iconos = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_iconos.place(relx=0.85, rely=0.20) 

        ctk.CTkButton(self.frame_iconos, text="📁\nArchivos", width=85, height=85, 
                      compound="top", font=("Arial", 13), fg_color=PANEL_COLOR, 
                      hover_color="#45475A", corner_radius=20, text_color=TEXT_COLOR,
                      command=self.abrir_explorador).pack(pady=10)

    def actualizar_reloj(self):
        self.lbl_reloj.configure(text=time.strftime("%H:%M | %b %d"))
        self.after(1000, self.actualizar_reloj)

    def alternar_menu(self):
        if self.app_drawer: self.cerrar_menu()
        else: self.abrir_menu()

    def abrir_menu(self):
        self.app_drawer = ctk.CTkToplevel(self)
        self.app_drawer.overrideredirect(True)
        w, h = 650, 500
        px = (self.winfo_screenwidth() // 2) - (w // 2)
        py = (self.winfo_screenheight() // 2) - (h // 2) + 50
        self.app_drawer.geometry(f"{w}x{h}+{px}+{py}")
        self.app_drawer.configure(fg_color=PANEL_COLOR)

        f_tit = ctk.CTkFrame(self.app_drawer, height=40, corner_radius=0, fg_color="#45475A")
        f_tit.pack(fill="x")
        ctk.CTkLabel(f_tit, text="AETHER APPS", font=("Arial", 14, "bold")).pack(side="left", padx=15)
        ctk.CTkButton(f_tit, text="✕", width=30, height=30, corner_radius=15, fg_color="transparent", 
                      text_color="#F38BA8", command=self.cerrar_menu).pack(side="right", padx=10)

        self.frame_apps = ctk.CTkScrollableFrame(self.app_drawer, corner_radius=15, fg_color="transparent")
        self.frame_apps.pack(fill="both", expand=True, padx=20, pady=20)

        # Unificamos el icono de Task Manager e Info PC en "Centro de Control"
        apps = [
            ("📁", "Archivos", self.abrir_explorador),
            ("📝", "Editor", self.abrir_editor),
            ("📊", "Calculadora", self.abrir_calculadora),
            ("🛡️", "Centro de Control", self.abrir_centro_control), # <--- AQUÍ ESTÁ TODO UNIFICADO
            ("📦", "Instalar (.py)", self.instalar_app_externa),
            ("🖥️", "Enlazar (.exe)", self.enlazar_programa_host),
            ("🔴", "Apagar", self.quit)
        ]

        r, c = 0, 0
        for ico, nom, cmd in apps:
            ctk.CTkButton(self.frame_apps, text=f"{ico}\n{nom}", width=120, height=120, compound="top", 
                          fg_color="#1E1E2E", corner_radius=20, command=lambda m=cmd: self.ejecutar_app(m)).grid(row=r, column=c, padx=10, pady=10)
            c += 1
            if c >= 4: c, r = 0, r + 1
        
        # Apps externas
        for n, rt in self.apps_terceros.items():
            ctk.CTkButton(self.frame_apps, text=f"✨\n{n}", width=120, height=120, compound="top", fg_color="#89B4FA", text_color="#1E1E2E", corner_radius=20, command=lambda r=rt: self.ejecutar_script_externo(r)).grid(row=r, column=c, padx=10, pady=10)
            c += 1
            if c >= 4: c, r = 0, r + 1
        for n, rt in self.apps_host.items():
            ctk.CTkButton(self.frame_apps, text=f"🚀\n{n}", width=120, height=120, compound="top", fg_color=HOST_COLOR, text_color="#1E1E2E", corner_radius=20, command=lambda r=rt: self.ejecutar_programa_host(r)).grid(row=r, column=c, padx=10, pady=10)
            c += 1
            if c >= 4: c, r = 0, r + 1

    def cerrar_menu(self):
        if self.app_drawer: self.app_drawer.destroy(); self.app_drawer = None

    def ejecutar_app(self, comando): self.cerrar_menu(); comando()

    # ==========================================
    # CENTRO DE CONTROL UNIFICADO (Rendimiento + Procesos + Info PC)
    # ==========================================
    def abrir_centro_control(self):
        self.control = ctk.CTkToplevel(self)
        self.control.title("Centro de Control - AetherOS")
        self.control.geometry("950x650")
        self.control.attributes("-topmost", True)
        self.control.configure(fg_color=BG_COLOR)

        # Sidebar de navegación
        self.side_ctrl = ctk.CTkFrame(self.control, width=200, corner_radius=0, fg_color=PANEL_COLOR)
        self.side_ctrl.pack(side="left", fill="y")
        self.side_ctrl.pack_propagate(False)

        ctk.CTkLabel(self.side_ctrl, text="Aether Dashboard", font=("Arial", 16, "bold")).pack(pady=20)

        # Botones de navegación
        self.btn_nav_cpu = ctk.CTkButton(self.side_ctrl, text="🟦 CPU", anchor="w", fg_color="#45475A", command=lambda: self.switch_control("CPU"))
        self.btn_nav_cpu.pack(fill="x", padx=10, pady=5)

        self.btn_nav_ram = ctk.CTkButton(self.side_ctrl, text="🟩 Memoria", anchor="w", fg_color="transparent", command=lambda: self.switch_control("RAM"))
        self.btn_nav_ram.pack(fill="x", padx=10, pady=5)

        self.btn_nav_proc = ctk.CTkButton(self.side_ctrl, text="⚙️ Procesos", anchor="w", fg_color="transparent", command=lambda: self.switch_control("PROC"))
        self.btn_nav_proc.pack(fill="x", padx=10, pady=5)

        self.btn_nav_info = ctk.CTkButton(self.side_ctrl, text="ℹ️ Sistema", anchor="w", fg_color="transparent", command=lambda: self.switch_control("INFO"))
        self.btn_nav_info.pack(fill="x", padx=10, pady=5)

        # Área principal de contenido
        self.main_ctrl = ctk.CTkFrame(self.control, fg_color="transparent")
        self.main_ctrl.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.render_seccion_control()
        self.actualizar_centro_control()

    def switch_control(self, target):
        self.seccion_actual = target
        for btn, name in [(self.btn_nav_cpu, "CPU"), (self.btn_nav_ram, "RAM"), (self.btn_nav_proc, "PROC"), (self.btn_nav_info, "INFO")]:
            btn.configure(fg_color="#45475A" if target == name else "transparent")
        self.render_seccion_control()

    def render_seccion_control(self):
        for w in self.main_ctrl.winfo_children(): w.destroy()
        
        if self.seccion_actual in ["CPU", "RAM"]:
            # Gráficos de Rendimiento
            self.lbl_titulo_ctrl = ctk.CTkLabel(self.main_ctrl, text=self.seccion_actual, font=("Arial", 28, "bold"), anchor="w")
            self.lbl_titulo_ctrl.pack(fill="x")
            
            self.canvas_ctrl = tk.Canvas(self.main_ctrl, bg="#11111b", highlightthickness=1, highlightbackground="#45475A")
            self.canvas_ctrl.pack(fill="both", expand=True, pady=15)

            f_stats = ctk.CTkFrame(self.main_ctrl, fg_color="transparent")
            f_stats.pack(fill="x")
            self.lbl_stat_1 = ctk.CTkLabel(f_stats, text="Uso: 0%", font=("Arial", 20))
            self.lbl_stat_1.pack(side="left", padx=20)
            self.lbl_stat_2 = ctk.CTkLabel(f_stats, text="", font=("Arial", 20))
            self.lbl_stat_2.pack(side="left", padx=20)

        elif self.seccion_actual == "PROC":
            # Lista de Procesos
            ctk.CTkLabel(self.main_ctrl, text="Procesos del Kernel", font=("Arial", 24, "bold")).pack(pady=10)
            self.scroll_proc = ctk.CTkScrollableFrame(self.main_ctrl, fg_color=PANEL_COLOR, corner_radius=15)
            self.scroll_proc.pack(fill="both", expand=True)

        elif self.seccion_actual == "INFO":
            # Info PC integrada
            ctk.CTkLabel(self.main_ctrl, text="Especificaciones del Sistema", font=("Arial", 24, "bold")).pack(pady=20)
            os_info = f"{platform.system()} {platform.release()}"
            cpu_info = platform.processor()
            ram_info = f"{psutil.virtual_memory().total / (1024**3):.1f} GB" if PSUTIL_DISPONIBLE else "16 GB"
            
            for ico, tit, val in [("💻", "SO Host", os_info), ("🧠", "CPU", cpu_info), ("⚡", "RAM", ram_info)]:
                f = ctk.CTkFrame(self.main_ctrl, fg_color=PANEL_COLOR, corner_radius=15)
                f.pack(fill="x", pady=10)
                ctk.CTkLabel(f, text=ico, font=("Arial", 30)).pack(side="left", padx=15, pady=10)
                ctk.CTkLabel(f, text=f"{tit}: {val}", font=("Arial", 14)).pack(side="left", padx=10)

    def actualizar_centro_control(self):
        if not hasattr(self, 'control') or not self.control.winfo_exists(): return

        if PSUTIL_DISPONIBLE:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.historial_cpu.pop(0); self.historial_cpu.append(cpu)
            self.historial_ram.pop(0); self.historial_ram.append(ram)

            if self.seccion_actual in ["CPU", "RAM"]:
                self.dibujar_grafico_unificado()
                u = cpu if self.seccion_actual == "CPU" else ram
                self.lbl_stat_1.configure(text=f"Uso actual: {u}%")
                if self.seccion_actual == "CPU":
                    try: self.lbl_stat_2.configure(text=f"Vel: {psutil.cpu_freq().current/1000:.2f} GHz")
                    except: pass
                else:
                    self.lbl_stat_2.configure(text=f"Libre: {psutil.virtual_memory().available / (1024**3):.1f} GB")

            elif self.seccion_actual == "PROC":
                for w in self.scroll_proc.winfo_children(): w.destroy()
                for p in list(psutil.process_iter(['pid', 'name', 'memory_info']))[:20]:
                    f = ctk.CTkFrame(self.scroll_proc, fg_color="transparent")
                    f.pack(fill="x")
                    ctk.CTkLabel(f, text=f"PID: {p.info['pid']} | {p.info['name']}", anchor="w").pack(side="left", padx=10)
                    ctk.CTkLabel(f, text=f"{p.info['memory_info'].rss / (1024**2):.1f} MB", text_color="#A6E3A1").pack(side="right", padx=10)

        self.after(1000, self.actualizar_centro_control)

    def dibujar_grafico_unificado(self):
        if not hasattr(self, 'canvas_ctrl'): return
        self.canvas_ctrl.delete("all")
        w, h = self.canvas_ctrl.winfo_width(), self.canvas_ctrl.winfo_height()
        if w < 10: w, h = 600, 300
        for i in range(1, 10):
            self.canvas_ctrl.create_line(i*(w/10), 0, i*(w/10), h, fill="#313244", dash=(2,4))
            self.canvas_ctrl.create_line(0, i*(h/10), w, i*(h/10), fill="#313244", dash=(2,4))
        
        datos = self.historial_cpu if self.seccion_actual == "CPU" else self.historial_ram
        color = ACCENT_COLOR if self.seccion_actual == "CPU" else RAM_COLOR
        pts = []
        for i, v in enumerate(datos):
            pts.append(i * (w/59)); pts.append(h - (v/100 * h))
        self.canvas_ctrl.create_line(pts, fill=color, width=2)

    # ==========================================
    # LÓGICA DE ARCHIVOS Y APPS (Intacta)
    # ==========================================
    def abrir_explorador(self):
        exp = ctk.CTkToplevel(self)
        exp.title("Archivos")
        exp.geometry("750x550")
        exp.attributes("-topmost", True)
        exp.configure(fg_color=BG_COLOR)
        
        side = ctk.CTkFrame(exp, width=180, corner_radius=20, fg_color=PANEL_COLOR)
        side.pack(side="left", fill="y", padx=15, pady=15)
        
        main = ctk.CTkFrame(exp, fg_color="transparent")
        main.pack(side="right", fill="both", expand=True)
        
        tool = ctk.CTkFrame(main, height=55, corner_radius=20, fg_color=PANEL_COLOR)
        tool.pack(fill="x", padx=15, pady=15)
        
        self.lbl_ruta = ctk.CTkLabel(tool, text=f"📍 {self.carpeta_actual}", font=("Arial", 14, "bold"))
        self.lbl_ruta.pack(side="left", padx=20)
        
        self.panel_archivos = ctk.CTkScrollableFrame(main, corner_radius=20, fg_color=PANEL_COLOR)
        self.panel_archivos.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        ctk.CTkButton(tool, text="➕ Carpeta", width=90, command=self.crear_carpeta).pack(side="right", padx=10)
        ctk.CTkButton(tool, text="⬆️ Subir", width=90, command=self.subir_archivo).pack(side="right", padx=5)
        
        for c in ["Documentos", "Imágenes", "Proyectos"]:
            ctk.CTkButton(side, text=f"📁 {c}", fg_color="transparent", anchor="w", command=lambda x=c: self.set_dir(x)).pack(fill="x", padx=10, pady=5)
        
        self.refresh_files()

    def set_dir(self, d): self.carpeta_actual = d; self.lbl_ruta.configure(text=f"📍 {d}"); self.refresh_files()

    def refresh_files(self):
        for w in self.panel_archivos.winfo_children(): w.destroy()
        for item in self.sistema_archivos.get(self.carpeta_actual, []):
            f = ctk.CTkFrame(self.panel_archivos, fg_color="#45475A", corner_radius=15)
            f.pack(fill="x", pady=5, padx=5)
            
            nom = item["nombre"]
            txt_n, txt_e = (nom.rsplit(".", 1) if "." in nom else (nom, ""))
            
            ctk.CTkLabel(f, text=item["icono"], font=("Arial", 22)).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=txt_n, font=("Arial", 14)).pack(side="left")
            if txt_e: ctk.CTkLabel(f, text=f".{txt_e}", text_color="#A6E3A1", font=("Arial", 14, "bold")).pack(side="left")
            
            btn_abrir = ctk.CTkButton(f, text="Abrir", width=60, height=25, command=lambda i=item: self.open_item(i))
            btn_abrir.pack(side="right", padx=10)

    def open_item(self, i):
        if i["icono"] == "🖼️" and PIL_DISPONIBLE:
            v = ctk.CTkToplevel(self); v.title(i["nombre"])
            img = Image.open(i["ruta_real"])
            ci = ctk.CTkImage(img, size=(400, 300))
            ctk.CTkLabel(v, image=ci, text="").pack(padx=20, pady=20)

    def crear_carpeta(self):
        n = ctk.CTkInputDialog(text="Nombre:", title="Carpeta").get_input()
        if n: self.sistema_archivos[self.carpeta_actual].append({"nombre": n, "icono": "📁", "info": "Carpeta"}); self.refresh_files()

    def subir_archivo(self):
        r = fd.askopenfilename()
        if r:
            n = os.path.basename(r)
            ico = "🖼️" if n.lower().endswith(('.png', '.jpg')) else "📄"
            self.sistema_archivos[self.carpeta_actual].append({"nombre": n, "icono": ico, "info": "Archivo", "ruta_real": r})
            self.refresh_files()

    # Lanzadores
    def instalar_app_externa(self):
        r = fd.askopenfilename(filetypes=[("Python", "*.py")])
        if r: n = os.path.basename(r).replace(".py", ""); self.apps_terceros[n] = r; self.abrir_menu()
    def enlazar_programa_host(self):
        r = fd.askopenfilename(filetypes=[("Exe", "*.exe")])
        if r: n = os.path.basename(r).replace(".exe", ""); self.apps_host[n] = r; self.abrir_menu()
    def ejecutar_script_externo(self, r): self.cerrar_menu(); subprocess.Popen([sys.executable, r])
    def ejecutar_programa_host(self, r): self.cerrar_menu(); os.startfile(r) if sys.platform=="win32" else subprocess.Popen([r])
    
    # Apps simples
    def abrir_editor(self):
        ed = ctk.CTkToplevel(self); ed.geometry("500x400")
        ctk.CTkTextbox(ed, corner_radius=15, fg_color=PANEL_COLOR).pack(fill="both", expand=True, padx=10, pady=10)
    def abrir_calculadora(self):
        ca = ctk.CTkToplevel(self); ca.geometry("300x400")
        e = ctk.CTkEntry(ca, justify="right", font=("Arial", 24)); e.pack(fill="x", padx=10, pady=10)
        f = ctk.CTkFrame(ca); f.pack(fill="both", expand=True)
        def calc(v):
            if v == "=": 
                try: res = eval(e.get()); e.delete(0, 'end'); e.insert(0, str(res))
                except: e.delete(0, 'end'); e.insert(0, "Error")
            else: e.insert('end', v)
        for i, b in enumerate(['7','8','9','/','4','5','6','*','1','2','3','-','0','.','=','+']):
            ctk.CTkButton(f, text=b, width=50, command=lambda x=b: calc(x)).grid(row=i//4, column=i%4, padx=5, pady=5)

if __name__ == "__main__":
    app = AetherOS()
    app.mainloop()