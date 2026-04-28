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
import json

# Librerías externas
try:
    from PIL import Image, ImageTk 
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

BG_COLOR = "#1E1E2E"       
PANEL_COLOR = "#313244"    
ACCENT_COLOR = "#89B4FA"   
RAM_COLOR = "#A6E3A1"      
TEXT_COLOR = "#CDD6F4"
HOST_COLOR = "#F5C2E7"     

# Colores específicos para los gráficos de rendimiento
COLORES_REND = {
    "CPU": "#89B4FA", 
    "RAM": "#A6E3A1", 
    "DISCO": "#FAB387", 
    "RED": "#F9E2AF", 
    "GPU": "#F5C2E7"
}

class AetherOS(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AetherOS")
        self.after(0, lambda: self.attributes('-fullscreen', True))
        self.configure(fg_color=BG_COLOR)

        self.sistema_archivos = {
            "Documentos": [{"nombre": "notas.txt", "icono": "📝", "info": "12 KB"}],
            "Imágenes": [],
            "Proyectos": []
        }
        self.carpeta_actual = "Documentos"
        self.apps_terceros = {} 
        self.apps_host = {}     

        self.archivo_memoria = "aether_memoria.json"
        self.cargar_memoria()

        self.app_drawer = None
        
        # Historial unificado para hardware
        self.historial_rend = {k: [0]*60 for k in COLORES_REND.keys()}
        self.seccion_actual = "REND" 
        self.sub_seccion_rend = "CPU"
        
        if PSUTIL_DISPONIBLE:
            self.last_net_bytes = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

        self.mostrar_pantalla_carga()

    # ==========================================
    # MEMORIA Y VENTANAS
    # ==========================================
    def cargar_memoria(self):
        if os.path.exists(self.archivo_memoria):
            try:
                with open(self.archivo_memoria, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    self.sistema_archivos = datos.get("archivos", self.sistema_archivos)
                    self.apps_terceros = datos.get("apps_terceros", {})
                    self.apps_host = datos.get("apps_host", {})
            except: pass

    def guardar_memoria(self):
        datos = {"archivos": self.sistema_archivos, "apps_terceros": self.apps_terceros, "apps_host": self.apps_host}
        try:
            with open(self.archivo_memoria, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
        except: pass

    def apagar_sistema(self):
        self.guardar_memoria()
        self.destroy()

    def crear_ventana_nativa(self, titulo, geometria="750x550"):
        win = ctk.CTkToplevel(self)
        win.geometry(geometria)
        win.overrideredirect(True) 
        win.attributes("-topmost", True)
        
        marco = ctk.CTkFrame(win, fg_color=BG_COLOR, border_width=1, border_color="#585B70", corner_radius=0)
        marco.pack(fill="both", expand=True)

        barra = ctk.CTkFrame(marco, height=35, fg_color=PANEL_COLOR, corner_radius=0)
        barra.pack(fill="x", side="top")
        
        lbl_titulo = ctk.CTkLabel(barra, text=f"  {titulo}", font=("Arial", 12, "bold"), text_color=TEXT_COLOR)
        lbl_titulo.pack(side="left")

        btn_cerrar = ctk.CTkButton(barra, text="✕", width=35, height=35, fg_color="transparent", hover_color="#F38BA8", corner_radius=0, command=win.destroy)
        btn_cerrar.pack(side="right")

        def start_move(event): win.x, win.y = event.x, event.y
        def do_move(event): win.geometry(f"+{win.winfo_x() + event.x - win.x}+{win.winfo_y() + event.y - win.y}")

        barra.bind("<ButtonPress-1>", start_move); barra.bind("<B1-Motion>", do_move)
        lbl_titulo.bind("<ButtonPress-1>", start_move); lbl_titulo.bind("<B1-Motion>", do_move)

        contenedor = ctk.CTkFrame(marco, fg_color="transparent")
        contenedor.pack(fill="both", expand=True)
        return win, contenedor

    # ==========================================
    # PANTALLA DE CARGA Y ESCRITORIO
    # ==========================================
    def mostrar_pantalla_carga(self):
        self.frame_carga = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_carga.place(relx=0.5, rely=0.5, anchor="center")
        self.lbl_logo = ctk.CTkLabel(self.frame_carga, text="A", font=("Arial", 140, "bold"), text_color=COLORES_REND["CPU"])
        self.lbl_logo.pack(pady=(0, 10))
        self.lbl_nombre = ctk.CTkLabel(self.frame_carga, text="AetherOS", font=("Arial", 28, "bold"), text_color=TEXT_COLOR)
        self.lbl_nombre.pack(pady=(0, 40))
        self.barra_carga = ctk.CTkProgressBar(self.frame_carga, width=350, height=8, progress_color=COLORES_REND["CPU"], fg_color=PANEL_COLOR)
        self.barra_carga.set(0); self.barra_carga.pack()
        self.lbl_estado = ctk.CTkLabel(self.frame_carga, text="Iniciando kernel...", font=("Arial", 13), text_color="#A6ADC8")
        self.lbl_estado.pack(pady=(15, 0))
        self.progreso_actual = 0.0
        self.animar_carga()

    def animar_carga(self):
        self.progreso_actual += random.uniform(0.02, 0.08)
        if 0.2 < self.progreso_actual < 0.5: self.lbl_estado.configure(text="Cargando entorno gráfico...")
        elif 0.5 < self.progreso_actual < 0.8: self.lbl_estado.configure(text="Montando sistema de archivos...")
        elif self.progreso_actual > 0.8: self.lbl_estado.configure(text="Iniciando AetherOS...")
        if self.progreso_actual >= 1.0:
            self.barra_carga.set(1.0); self.after(500, self.iniciar_sistema)
        else:
            self.barra_carga.set(self.progreso_actual); self.after(100, self.animar_carga)

    def iniciar_sistema(self):
        self.frame_carga.destroy()
        self.crear_escritorio()
        self.crear_barra_tareas()

    def crear_escritorio(self):
        self.canvas_desk = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.canvas_desk.place(x=0, y=0, relwidth=1, relheight=1)
        self.img_ref = None 
        self.fondo_id = self.canvas_desk.create_image(0, 0, anchor="nw")
        self.drag_data = {"x": 0, "y": 0, "item": None, "moved": False}

        self.crear_icono_canvas("Archivos", "📁", 40, 40, self.abrir_explorador)
        self.crear_icono_canvas("Google Chrome", "🌐", 40, 160, lambda: self.ejecutar_programa_host(r"C:\Program Files\Google\Chrome\Application\chrome.exe"))

    def crear_icono_canvas(self, texto, icono, x, y, comando):
        tag_grupo = f"icono_{texto.replace(' ', '_')}"
        self.canvas_desk.create_rectangle(x, y, x + 100, y + 100, fill="", outline="", tags=(tag_grupo, "draggable"))
        self.canvas_desk.create_text(x + 51, y + 41, text=icono, font=("Arial", 40), fill="#000000", tags=(tag_grupo, "draggable"))
        self.canvas_desk.create_text(x + 51, y + 86, text=texto, font=("Arial", 12, "bold"), fill="#000000", tags=(tag_grupo, "draggable"))
        self.canvas_desk.create_text(x + 50, y + 40, text=icono, font=("Arial", 40), fill=TEXT_COLOR, tags=(tag_grupo, "draggable"))
        self.canvas_desk.create_text(x + 50, y + 85, text=texto, font=("Arial", 12, "bold"), fill=TEXT_COLOR, tags=(tag_grupo, "draggable"))

        def on_press(event):
            self.drag_data["item"] = tag_grupo; self.drag_data["x"] = event.x; self.drag_data["y"] = event.y; self.drag_data["moved"] = False
            self.canvas_desk.tag_raise(tag_grupo)
        def on_drag(event):
            if self.drag_data["item"] == tag_grupo:
                self.canvas_desk.move(tag_grupo, event.x - self.drag_data["x"], event.y - self.drag_data["y"])
                self.drag_data["x"] = event.x; self.drag_data["y"] = event.y; self.drag_data["moved"] = True
        def on_release(event):
            if self.drag_data["item"] == tag_grupo:
                if not self.drag_data["moved"]: comando()
                self.drag_data["item"] = None

        self.canvas_desk.tag_bind(tag_grupo, "<ButtonPress-1>", on_press)
        self.canvas_desk.tag_bind(tag_grupo, "<B1-Motion>", on_drag)
        self.canvas_desk.tag_bind(tag_grupo, "<ButtonRelease-1>", on_release)
        self.canvas_desk.tag_bind(tag_grupo, "<Enter>", lambda e: self.canvas_desk.config(cursor="hand2"))
        self.canvas_desk.tag_bind(tag_grupo, "<Leave>", lambda e: self.canvas_desk.config(cursor=""))

    # ==========================================
    # BARRA Y MENÚ
    # ==========================================
    def crear_barra_tareas(self):
        self.barra = ctk.CTkFrame(self, height=52, corner_radius=0, fg_color="#11111b")
        self.barra.pack(side="bottom", fill="x"); self.barra.pack_propagate(False) 
        self.btn_menu = ctk.CTkButton(self.barra, text="A", width=40, height=40, font=("Arial", 18, "bold"), corner_radius=12, fg_color=COLORES_REND["CPU"], hover_color="#B4BEFE", text_color=BG_COLOR, command=self.alternar_menu)
        self.btn_menu.place(relx=0.5, rely=0.5, anchor="center")
        self.tray_frame = ctk.CTkFrame(self.barra, fg_color="transparent")
        self.tray_frame.pack(side="right", fill="y", padx=15, pady=5)
        self.lbl_tray_icons = ctk.CTkLabel(self.tray_frame, text="🔊  📶", font=("Arial", 15), text_color=TEXT_COLOR)
        self.lbl_tray_icons.pack(side="left", padx=15)
        self.lbl_reloj = ctk.CTkLabel(self.tray_frame, text="", font=("Arial", 13, "bold"), text_color=TEXT_COLOR)
        self.lbl_reloj.pack(side="left", padx=5)
        self.actualizar_reloj()

    def actualizar_reloj(self):
        if hasattr(self, 'lbl_reloj') and self.lbl_reloj.winfo_exists():
            self.lbl_reloj.configure(text=time.strftime("%H:%M | %b %d"))
        self.after(1000, self.actualizar_reloj)

    def alternar_menu(self):
        if self.app_drawer: self.cerrar_menu()
        else: self.abrir_menu()

    def abrir_menu(self):
        self.app_drawer = ctk.CTkToplevel(self)
        self.app_drawer.overrideredirect(True)
        w, h = 650, 500
        self.app_drawer.geometry(f"{w}x{h}+{(self.winfo_screenwidth() // 2) - (w // 2)}+{self.winfo_screenheight() - h - 60}")
        self.app_drawer.configure(fg_color=PANEL_COLOR)
        
        f_tit = ctk.CTkFrame(self.app_drawer, height=40, corner_radius=0, fg_color="#45475A"); f_tit.pack(fill="x")
        ctk.CTkLabel(f_tit, text="AETHER APPS", font=("Arial", 14, "bold")).pack(side="left", padx=15)
        ctk.CTkButton(f_tit, text="✕", width=30, height=30, corner_radius=15, fg_color="transparent", text_color="#F38BA8", command=self.cerrar_menu).pack(side="right", padx=10)
        
        self.frame_apps = ctk.CTkScrollableFrame(self.app_drawer, corner_radius=15, fg_color="transparent")
        self.frame_apps.pack(fill="both", expand=True, padx=20, pady=20)

        apps = [("📁", "Archivos", self.abrir_explorador), ("📝", "Editor", self.abrir_editor), ("📊", "Calculadora", self.abrir_calculadora), ("🛡️", "Task Manager", self.abrir_centro_control), ("🎨", "Personalizar", self.abrir_personalizacion), ("📦", "Instalar (.py)", self.instalar_app_externa), ("🖥️", "Enlazar (.exe)", self.enlazar_programa_host), ("🔴", "Apagar", self.apagar_sistema)]
        r, c = 0, 0
        for ico, nom, cmd in apps:
            ctk.CTkButton(self.frame_apps, text=f"{ico}\n{nom}", width=120, height=120, compound="top", fg_color="#1E1E2E", corner_radius=20, command=lambda m=cmd: self.ejecutar_app(m)).grid(row=r, column=c, padx=10, pady=10)
            c += 1; c, r = (0, r + 1) if c >= 4 else (c, r)
        for n, rt in self.apps_terceros.items():
            ctk.CTkButton(self.frame_apps, text=f"✨\n{n}", width=120, height=120, compound="top", fg_color=COLORES_REND["CPU"], text_color="#1E1E2E", corner_radius=20, command=lambda r=rt: self.ejecutar_script_externo(r)).grid(row=r, column=c, padx=10, pady=10)
            c += 1; c, r = (0, r + 1) if c >= 4 else (c, r)
        for n, rt in self.apps_host.items():
            ctk.CTkButton(self.frame_apps, text=f"🚀\n{n}", width=120, height=120, compound="top", fg_color=HOST_COLOR, text_color="#1E1E2E", corner_radius=20, command=lambda r=rt: self.ejecutar_programa_host(r)).grid(row=r, column=c, padx=10, pady=10)
            c += 1; c, r = (0, r + 1) if c >= 4 else (c, r)

    def cerrar_menu(self):
        if self.app_drawer: self.app_drawer.destroy(); self.app_drawer = None
    def ejecutar_app(self, comando): self.cerrar_menu(); comando()

    # ==========================================
    # CENTRO DE CONTROL / TASK MANAGER
    # ==========================================
    def abrir_centro_control(self):
        self.control, contenedor = self.crear_ventana_nativa("Administrador de Tareas - AetherOS", "1050x650")
        
        self.side_ctrl = ctk.CTkFrame(contenedor, width=200, corner_radius=0, fg_color=PANEL_COLOR)
        self.side_ctrl.pack(side="left", fill="y"); self.side_ctrl.pack_propagate(False)
        ctk.CTkLabel(self.side_ctrl, text="Aether Dashboard", font=("Arial", 16, "bold")).pack(pady=20)
        
        self.btn_nav_rend = ctk.CTkButton(self.side_ctrl, text="📊 Rendimiento", anchor="w", fg_color="#45475A", command=lambda: self.switch_control("REND"))
        self.btn_nav_rend.pack(fill="x", padx=10, pady=5)
        self.btn_nav_proc = ctk.CTkButton(self.side_ctrl, text="⚙️ Procesos", anchor="w", fg_color="transparent", command=lambda: self.switch_control("PROC"))
        self.btn_nav_proc.pack(fill="x", padx=10, pady=5)
        self.btn_nav_info = ctk.CTkButton(self.side_ctrl, text="ℹ️ Sistema", anchor="w", fg_color="transparent", command=lambda: self.switch_control("INFO"))
        self.btn_nav_info.pack(fill="x", padx=10, pady=5)
        
        self.main_ctrl = ctk.CTkFrame(contenedor, fg_color="transparent")
        self.main_ctrl.pack(side="right", fill="both", expand=True, padx=15, pady=15)
        
        self.render_seccion_control()
        self.actualizar_centro_control()

    def switch_control(self, target):
        self.seccion_actual = target
        self.btn_nav_rend.configure(fg_color="#45475A" if target == "REND" else "transparent")
        self.btn_nav_proc.configure(fg_color="#45475A" if target == "PROC" else "transparent")
        self.btn_nav_info.configure(fg_color="#45475A" if target == "INFO" else "transparent")
        self.render_seccion_control()

    def render_seccion_control(self):
        for w in self.main_ctrl.winfo_children(): w.destroy()
        
        if self.seccion_actual == "REND":
            self.rend_izq = ctk.CTkFrame(self.main_ctrl, width=200, fg_color=PANEL_COLOR, corner_radius=15)
            self.rend_izq.pack(side="left", fill="y", padx=(0, 15)); self.rend_izq.pack_propagate(False)
            
            self.rend_der = ctk.CTkFrame(self.main_ctrl, fg_color="transparent")
            self.rend_der.pack(side="right", fill="both", expand=True)
            
            self.botones_rend = {}
            for hw, icon in [("CPU", "🟦"), ("RAM", "🟩"), ("DISCO", "🟫"), ("RED", "🟨"), ("GPU", "🟪")]:
                btn = ctk.CTkButton(self.rend_izq, text=f"{icon} {hw}\n...", font=("Arial", 13), anchor="w", 
                                    fg_color="#45475A" if self.sub_seccion_rend == hw else "transparent",
                                    height=55, command=lambda h=hw: self.switch_rend(h))
                btn.pack(fill="x", padx=10, pady=5)
                self.botones_rend[hw] = btn

            self.lbl_titulo_graf = ctk.CTkLabel(self.rend_der, text=f"{self.sub_seccion_rend}", font=("Arial", 28, "bold"), anchor="w")
            self.lbl_titulo_graf.pack(fill="x")
            
            self.canvas_ctrl = tk.Canvas(self.rend_der, bg="#11111b", highlightthickness=1, highlightbackground="#45475A")
            self.canvas_ctrl.pack(fill="both", expand=True, pady=15)
            
            f_stats = ctk.CTkFrame(self.rend_der, fg_color="transparent")
            f_stats.pack(fill="x")
            self.lbl_stat_1 = ctk.CTkLabel(f_stats, text="Uso: 0%", font=("Arial", 16)); self.lbl_stat_1.pack(side="left", padx=20)
            self.lbl_stat_2 = ctk.CTkLabel(f_stats, text="", font=("Arial", 16)); self.lbl_stat_2.pack(side="left", padx=20)

        elif self.seccion_actual == "PROC":
            ctk.CTkLabel(self.main_ctrl, text="Procesos y Subprocesos Activos", font=("Arial", 24, "bold"), anchor="w").pack(fill="x", pady=(0, 10))
            
            cab = ctk.CTkFrame(self.main_ctrl, fg_color="transparent")
            cab.pack(fill="x", padx=10)
            ctk.CTkLabel(cab, text="Nombre", width=200, anchor="w", font=("Arial", 13, "bold")).pack(side="left")
            ctk.CTkLabel(cab, text="PID", width=60, anchor="w", font=("Arial", 13, "bold")).pack(side="left")
            ctk.CTkLabel(cab, text="Hilos", width=80, anchor="w", font=("Arial", 13, "bold")).pack(side="left")
            ctk.CTkLabel(cab, text="Tipo", width=80, anchor="w", font=("Arial", 13, "bold")).pack(side="left")
            
            # Cabeceras para el botón y la memoria
            ctk.CTkLabel(cab, text="Acción", width=80, anchor="e", font=("Arial", 13, "bold")).pack(side="right", padx=10)
            ctk.CTkLabel(cab, text="Memoria", width=80, anchor="e", font=("Arial", 13, "bold")).pack(side="right", padx=10)

            self.scroll_proc = ctk.CTkScrollableFrame(self.main_ctrl, fg_color=PANEL_COLOR, corner_radius=15)
            self.scroll_proc.pack(fill="both", expand=True)

        elif self.seccion_actual == "INFO":
            ctk.CTkLabel(self.main_ctrl, text="Especificaciones del Sistema", font=("Arial", 24, "bold")).pack(pady=20)
            os_info = f"{platform.system()} {platform.release()}"
            cpu_info = platform.processor()
            ram_info = f"{psutil.virtual_memory().total / (1024**3):.1f} GB" if PSUTIL_DISPONIBLE else "16 GB"
            for ico, tit, val in [("💻", "SO Host", os_info), ("🧠", "CPU", cpu_info), ("⚡", "RAM", ram_info)]:
                f = ctk.CTkFrame(self.main_ctrl, fg_color=PANEL_COLOR, corner_radius=15)
                f.pack(fill="x", pady=10)
                ctk.CTkLabel(f, text=ico, font=("Arial", 30)).pack(side="left", padx=15, pady=10)
                ctk.CTkLabel(f, text=f"{tit}: {val}", font=("Arial", 14)).pack(side="left", padx=10)

    def switch_rend(self, hardware):
        self.sub_seccion_rend = hardware
        for hw, btn in self.botones_rend.items():
            btn.configure(fg_color="#45475A" if hw == hardware else "transparent")
        self.lbl_titulo_graf.configure(text=hardware)

    # ==========================================
    # LÓGICA DE MATAR PROCESOS (NUEVO)
    # ==========================================
    def matar_proceso(self, pid, nombre):
        respuesta = mb.askyesno("Finalizar Tarea", f"¿Estás seguro de que deseas finalizar '{nombre}' (PID: {pid})?\n\nAdvertencia: Finalizar procesos del sistema puede causar inestabilidad temporal en tu PC.")
        if respuesta:
            try:
                psutil.Process(pid).terminate()
                mb.showinfo("Éxito", f"El proceso '{nombre}' ha sido finalizado correctamente.")
            except psutil.NoSuchProcess:
                mb.showwarning("Aviso", "El proceso ya no se está ejecutando.")
            except psutil.AccessDenied:
                mb.showerror("Acceso Denegado", f"Windows ha bloqueado la acción.\n\nNo tienes permisos de Administrador para finalizar '{nombre}'. Es probable que sea un proceso crítico del núcleo de Windows.")
            except Exception as e:
                mb.showerror("Error", f"No se pudo finalizar el proceso.\nDetalle: {e}")

    def actualizar_centro_control(self):
        if hasattr(self, 'control') and self.control.winfo_exists() and PSUTIL_DISPONIBLE:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disco = psutil.disk_usage('/').percent
            gpu = random.randint(1, 15) 
            
            net_io = psutil.net_io_counters()
            cur_net = net_io.bytes_sent + net_io.bytes_recv
            kbps = ((cur_net - getattr(self, 'last_net_bytes', cur_net)) / 1024) * 8
            self.last_net_bytes = cur_net
            red_act = min((kbps / 5000) * 100, 100) 

            for hw, val in [("CPU", cpu), ("RAM", ram), ("DISCO", disco), ("RED", red_act), ("GPU", gpu)]:
                self.historial_rend[hw].pop(0)
                self.historial_rend[hw].append(val)

            if self.seccion_actual == "REND":
                self.dibujar_grafico_unificado()
                
                self.botones_rend["CPU"].configure(text=f"🟦 CPU\n{cpu}%")
                self.botones_rend["RAM"].configure(text=f"🟩 Memoria\n{ram}%")
                self.botones_rend["DISCO"].configure(text=f"🟫 Disco (C:)\n{disco}%")
                self.botones_rend["RED"].configure(text=f"🟨 Ethernet\n{int(kbps)} Kbps")
                self.botones_rend["GPU"].configure(text=f"🟪 Video\n{gpu}%")

                val_actual = {"CPU": cpu, "RAM": ram, "DISCO": disco, "RED": int(kbps), "GPU": gpu}[self.sub_seccion_rend]
                lbl_1 = f"Uso: {val_actual}%" if self.sub_seccion_rend != "RED" else f"Tráfico: {val_actual} Kbps"
                self.lbl_stat_1.configure(text=lbl_1)
                
                if self.sub_seccion_rend == "CPU":
                    try: self.lbl_stat_2.configure(text=f"Vel: {psutil.cpu_freq().current/1000:.2f} GHz")
                    except: pass
                elif self.sub_seccion_rend == "RAM": self.lbl_stat_2.configure(text=f"Libre: {psutil.virtual_memory().available / (1024**3):.1f} GB")
                else: self.lbl_stat_2.configure(text="")

            elif self.seccion_actual == "PROC":
                for w in self.scroll_proc.winfo_children(): w.destroy()
                
                procesos = list(psutil.process_iter(['pid', 'name', 'memory_info', 'num_threads', 'username']))
                procesos.sort(key=lambda x: x.info['memory_info'].rss if x.info.get('memory_info') else 0, reverse=True)
                
                for p in procesos[:25]:
                    f = ctk.CTkFrame(self.scroll_proc, fg_color="transparent"); f.pack(fill="x", pady=1)
                    
                    nombre = p.info['name'] or "Desconocido"
                    es_sys = "Sistema" if p.info.get('username') == 'NT AUTHORITY\\SYSTEM' or nombre.lower() in ['svchost.exe', 'system', 'registry', 'csrss.exe', 'smss.exe'] else "Usuario"
                    color_tipo = "#A6ADC8" if es_sys == "Sistema" else COLORES_REND["CPU"]

                    ctk.CTkLabel(f, text=nombre[:22], width=200, anchor="w").pack(side="left")
                    ctk.CTkLabel(f, text=str(p.info['pid']), width=60, anchor="w").pack(side="left")
                    ctk.CTkLabel(f, text=str(p.info.get('num_threads', 0)), width=80, anchor="w").pack(side="left")
                    ctk.CTkLabel(f, text=f"[{es_sys}]", width=80, anchor="w", text_color=color_tipo).pack(side="left")
                    
                    # BOTÓN FINALIZAR TAREA 
                    btn_matar = ctk.CTkButton(f, text="Finalizar", width=70, height=24, fg_color="#F38BA8", hover_color="#E64553", text_color="#11111B", font=("Arial", 11, "bold"), command=lambda p_id=p.info['pid'], nom=nombre: self.matar_proceso(p_id, nom))
                    btn_matar.pack(side="right", padx=10)

                    mem = p.info['memory_info'].rss / (1024**2) if p.info.get('memory_info') else 0
                    ctk.CTkLabel(f, text=f"{mem:.1f} MB", text_color=COLORES_REND["RAM"], width=80, anchor="e").pack(side="right", padx=10)

            self.after(1000, self.actualizar_centro_control)

    def dibujar_grafico_unificado(self):
        if not hasattr(self, 'canvas_ctrl'): return
        self.canvas_ctrl.delete("all")
        w, h = self.canvas_ctrl.winfo_width(), self.canvas_ctrl.winfo_height()
        if w < 10: w, h = 600, 300
        for i in range(1, 10):
            self.canvas_ctrl.create_line(i*(w/10), 0, i*(w/10), h, fill="#313244", dash=(2,4))
            self.canvas_ctrl.create_line(0, i*(h/10), w, i*(h/10), fill="#313244", dash=(2,4))
            
        datos = self.historial_rend[self.sub_seccion_rend]
        color = COLORES_REND[self.sub_seccion_rend]
        
        pts = []
        for i, v in enumerate(datos): pts.append(i * (w/59)); pts.append(h - (v/100 * h))
        self.canvas_ctrl.create_line(pts, fill=color, width=2)

    # ==========================================
    # UTILIDADES Y APPS
    # ==========================================
    def abrir_personalizacion(self):
        self.cerrar_menu()
        ruta_img = fd.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")])
        if ruta_img and PIL_DISPONIBLE:
            try:
                img = ImageTk.PhotoImage(Image.open(ruta_img).resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.Resampling.LANCZOS))
                self.img_ref = img; self.canvas_desk.itemconfig(self.fondo_id, image=self.img_ref)
            except: pass

    # ==========================================
    # EXPLORADOR DE ARCHIVOS 
    # ==========================================
    def abrir_explorador(self):
        self.explorador, contenedor = self.crear_ventana_nativa("Archivos - AetherOS", "750x550")
        side = ctk.CTkFrame(contenedor, width=180, fg_color=PANEL_COLOR); side.pack(side="left", fill="y", padx=15, pady=15)
        main = ctk.CTkFrame(contenedor, fg_color="transparent"); main.pack(side="right", fill="both", expand=True)
        tool = ctk.CTkFrame(main, height=55, fg_color=PANEL_COLOR); tool.pack(fill="x", padx=15, pady=15)
        
        btn_volver = ctk.CTkButton(tool, text="⬅️", width=40, fg_color="transparent", hover_color="#45475A", command=self.retroceder_carpeta)
        btn_volver.pack(side="left", padx=(15, 5))
        
        self.lbl_ruta = ctk.CTkLabel(tool, text=f"📍 {self.carpeta_actual}", font=("Arial", 14, "bold"))
        self.lbl_ruta.pack(side="left", padx=5)
        
        self.panel_archivos = ctk.CTkScrollableFrame(main, fg_color=PANEL_COLOR); self.panel_archivos.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        ctk.CTkButton(tool, text="➕ Carpeta", width=90, command=self.crear_carpeta).pack(side="right", padx=10)
        ctk.CTkButton(tool, text="⬆️ Subir", width=90, command=self.subir_archivo).pack(side="right", padx=5)
        for c in ["Documentos", "Imágenes", "Proyectos"]:
            ctk.CTkButton(side, text=f"📁 {c}", fg_color="transparent", anchor="w", command=lambda x=c: self.set_dir(x)).pack(fill="x", padx=10, pady=5)
        self.refresh_files()

    def set_dir(self, d): self.carpeta_actual = d; self.lbl_ruta.configure(text=f"📍 {d}"); self.refresh_files()

    def retroceder_carpeta(self):
        if "/" in self.carpeta_actual:
            partes = self.carpeta_actual.split("/")
            nueva_ruta = "/".join(partes[:-1]) 
            self.set_dir(nueva_ruta)

    def refresh_files(self):
        for w in self.panel_archivos.winfo_children(): w.destroy()
        for item in self.sistema_archivos.get(self.carpeta_actual, []):
            f = ctk.CTkFrame(self.panel_archivos, fg_color="#45475A", corner_radius=15); f.pack(fill="x", pady=5, padx=5)
            nom = item["nombre"]
            txt_n, txt_e = (nom.rsplit(".", 1) if "." in nom and item["info"] != "Carpeta" else (nom, ""))
            ctk.CTkLabel(f, text=item["icono"], font=("Arial", 22)).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=txt_n, font=("Arial", 14)).pack(side="left")
            if txt_e: ctk.CTkLabel(f, text=f".{txt_e}", text_color=COLORES_REND["RAM"], font=("Arial", 14, "bold")).pack(side="left")
            ctk.CTkLabel(f, text=item.get("info", ""), font=("Arial", 13), text_color="#A6ADC8").pack(side="right", padx=15)
            ctk.CTkButton(f, text="Abrir", width=70, height=30, command=lambda i=item: self.open_item(i)).pack(side="right", padx=10)

    def open_item(self, i):
        if i["info"] == "Carpeta": self.set_dir(f"{self.carpeta_actual}/{i['nombre']}")
        elif i["icono"] == "🖼️" and PIL_DISPONIBLE and "ruta_real" in i:
            v, cont = self.crear_ventana_nativa(i["nombre"], "450x400")
            ci = ctk.CTkImage(Image.open(i["ruta_real"]), size=(400, 300))
            ctk.CTkLabel(cont, image=ci, text="").pack(padx=20, pady=20)
        elif "ruta_real" in i: self.ejecutar_programa_host(i["ruta_real"])

    def crear_carpeta(self):
        n = ctk.CTkInputDialog(text="Nombre:", title="Carpeta").get_input()
        if n: self.sistema_archivos[self.carpeta_actual].append({"nombre": n, "icono": "📁", "info": "Carpeta"}); self.guardar_memoria(); self.refresh_files()

    def subir_archivo(self):
        r = fd.askopenfilename()
        if r:
            n = os.path.basename(r)
            if n.lower().endswith('.exe'):
                self.apps_host[n.replace(".exe", "").capitalize()] = r
                self.sistema_archivos[self.carpeta_actual].append({"nombre": n, "icono": "🚀", "info": "Ejecutable", "ruta_real": r})
            else:
                ico = "🖼️" if n.lower().endswith(('.png', '.jpg')) else "📄"
                self.sistema_archivos[self.carpeta_actual].append({"nombre": n, "icono": ico, "info": "Archivo", "ruta_real": r})
            self.guardar_memoria(); self.refresh_files()

    def enlazar_programa_host(self):
        r = fd.askopenfilename(filetypes=[("Exe", "*.exe")])
        if r: self.apps_host[os.path.basename(r).replace(".exe", "")] = r; self.guardar_memoria(); self.abrir_menu()
    def ejecutar_programa_host(self, ruta_exe, nombre="Programa"):
        self.cerrar_menu()
        try: os.startfile(ruta_exe) if sys.platform == "win32" else subprocess.Popen([ruta_exe])
        except: pass
    def instalar_app_externa(self):
        r = fd.askopenfilename(filetypes=[("Python", "*.py")])
        if r: self.apps_terceros[os.path.basename(r).replace(".py", "")] = r; self.guardar_memoria(); self.abrir_menu()
    def ejecutar_script_externo(self, ruta_script):
        self.cerrar_menu()
        try: subprocess.Popen([sys.executable, ruta_script])
        except: pass
            
    def abrir_editor(self):
        ed, contenedor = self.crear_ventana_nativa("Aether Text", "700x500")
        ctk.CTkTextbox(contenedor, corner_radius=15, fg_color=PANEL_COLOR).pack(fill="both", expand=True, padx=15, pady=15)
        
    def abrir_calculadora(self):
        ca, contenedor = self.crear_ventana_nativa("Calculadora", "300x430")
        e = ctk.CTkEntry(contenedor, justify="right", font=("Arial", 24)); e.pack(fill="x", padx=10, pady=10)
        f = ctk.CTkFrame(contenedor, fg_color="transparent"); f.pack(fill="both", expand=True)
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