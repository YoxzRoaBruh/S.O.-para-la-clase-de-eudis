import customtkinter as ctk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import os
import time
import subprocess
import sys

# Intentamos importar PIL para el visor de imágenes
try:
    from PIL import Image
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False

# Configuraciones base de suavidad
ctk.set_appearance_mode("dark")

# Paleta de colores "Soft Dark"
BG_COLOR = "#1E1E2E"       
PANEL_COLOR = "#313244"    
ACCENT_COLOR = "#89B4FA"   
HOVER_COLOR = "#B4BEFE"    
TEXT_COLOR = "#CDD6F4"
HOST_COLOR = "#F5C2E7"     # Rosa pastel para programas .exe externos

class AetherOS(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AetherOS")
        self.after(0, lambda: self.attributes('-fullscreen', True))
        self.configure(fg_color=BG_COLOR)

        # Base de datos
        self.sistema_archivos = {
            "Documentos": [{"nombre": "notas.txt", "icono": "📝", "info": "12 KB"}],
            "Imágenes": [],
            "Proyectos": []
        }
        self.carpeta_actual = "Documentos"
        self.app_drawer = None
        self.apps_terceros = {} # Para apps .py simuladas
        self.apps_host = {}     # NUEVO: Para programas .exe reales

        self.crear_barra_superior_flotante()
        self.crear_escritorio()

    # ==========================================
    # ESCRITORIO Y BARRA
    # ==========================================
    def crear_barra_superior_flotante(self):
        self.barra = ctk.CTkFrame(self, height=45, corner_radius=25, fg_color=PANEL_COLOR)
        self.barra.pack(side="top", fill="x", padx=20, pady=15)

        self.btn_menu = ctk.CTkButton(self.barra, text="A", width=35, height=35, 
                                      font=("Arial", 16, "bold"), corner_radius=18, 
                                      fg_color=ACCENT_COLOR, hover_color=HOVER_COLOR,
                                      text_color=BG_COLOR, command=self.alternar_menu)
        self.btn_menu.pack(side="left", padx=10, pady=5)

        self.lbl_reloj = ctk.CTkLabel(self.barra, text="", font=("Arial", 13, "bold"), text_color=TEXT_COLOR)
        self.lbl_reloj.pack(side="right", padx=20)
        self.actualizar_reloj()

    def crear_escritorio(self):
        self.frame_iconos = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_iconos.place(relx=0.85, rely=0.20) 

        self.btn_archivos = ctk.CTkButton(self.frame_iconos, text="📁\nArchivos", width=85, height=85, 
                                          compound="top", font=("Arial", 13), fg_color=PANEL_COLOR, 
                                          hover_color="#45475A", corner_radius=20, text_color=TEXT_COLOR,
                                          command=self.abrir_explorador)
        self.btn_archivos.pack(pady=10)

    def actualizar_reloj(self):
        hora_actual = time.strftime("%H:%M | %b %d")
        self.lbl_reloj.configure(text=hora_actual)
        self.after(1000, self.actualizar_reloj)

    # ==========================================
    # CAJÓN DE APLICACIONES ACTUALIZADO
    # ==========================================
    def alternar_menu(self):
        if self.app_drawer: self.cerrar_menu()
        else: self.abrir_menu()

    def abrir_menu(self):
        self.app_drawer = ctk.CTkToplevel(self)
        self.app_drawer.title("Aether Apps")
        self.app_drawer.overrideredirect(True)

        drawer_width, drawer_height = 650, 450
        pos_x = (self.app_drawer.winfo_screenwidth() / 2) - (drawer_width / 2)
        pos_y = (self.app_drawer.winfo_screenheight() / 2) - (drawer_height / 2) + 50 
        self.app_drawer.geometry(f"{drawer_width}x{drawer_height}+{int(pos_x)}+{int(pos_y)}")
        self.app_drawer.configure(fg_color=PANEL_COLOR)

        frame_titulo = ctk.CTkFrame(self.app_drawer, height=40, corner_radius=0, fg_color="#45475A")
        frame_titulo.pack(fill="x")
        ctk.CTkLabel(frame_titulo, text="AETHER APPS", font=("Arial", 14, "bold"), text_color=TEXT_COLOR).pack(side="left", padx=15)
        ctk.CTkButton(frame_titulo, text="✕", width=30, height=30, corner_radius=15, fg_color="transparent", 
                      text_color="#F38BA8", hover_color="#585B70", command=self.cerrar_menu).pack(side="right", padx=10, pady=5)

        self.frame_apps = ctk.CTkScrollableFrame(self.app_drawer, corner_radius=15, fg_color="transparent")
        self.frame_apps.pack(fill="both", expand=True, padx=20, pady=20)

        # NUEVO BOTÓN AÑADIDO A LA BASE: Enlazar PC (.exe)
        apps_base = [
            ("📁", "Archivos", self.abrir_explorador),
            ("📝", "Editor", self.abrir_editor),
            ("📊", "Calculadora", self.abrir_calculadora),
            ("📦", "Instalar App (.py)", self.instalar_app_externa),
            ("🖥️", "Enlazar PC (.exe)", self.enlazar_programa_host),
            ("🔴", "Apagar", self.abrir_apagado)
        ]

        r, c = 0, 0
        
        # Dibujar Apps Base
        for icono, nombre, comando in apps_base:
            btn = ctk.CTkButton(self.frame_apps, text=f"{icono}\n{nombre}", width=120, height=120, 
                                compound="top", font=("Arial", 13), fg_color="#1E1E2E", 
                                hover_color="#45475A", corner_radius=20, text_color=TEXT_COLOR,
                                command=lambda cmd=comando: self.ejecutar_app(cmd) if cmd else None)
            btn.grid(row=r, column=c, padx=10, pady=10)
            c += 1
            if c >= 4: c, r = 0, r + 1

        # Dibujar Apps de Terceros (.py) (Azules)
        for nombre_app, ruta_script in self.apps_terceros.items():
            btn_externa = ctk.CTkButton(self.frame_apps, text=f"✨\n{nombre_app}", width=120, height=120, 
                                compound="top", font=("Arial", 13, "bold"), fg_color="#89B4FA", 
                                text_color="#1E1E2E", hover_color="#B4BEFE", corner_radius=20,
                                command=lambda ruta=ruta_script: self.ejecutar_script_externo(ruta))
            btn_externa.grid(row=r, column=c, padx=10, pady=10)
            c += 1
            if c >= 4: c, r = 0, r + 1
            
        # Dibujar Programas Host (.exe) (Rosas)
        for nombre_prog, ruta_exe in self.apps_host.items():
            btn_host = ctk.CTkButton(self.frame_apps, text=f"🚀\n{nombre_prog}", width=120, height=120, 
                                compound="top", font=("Arial", 13, "bold"), fg_color=HOST_COLOR, 
                                text_color="#1E1E2E", hover_color="#F38BA8", corner_radius=20,
                                command=lambda ruta=ruta_exe: self.ejecutar_programa_host(ruta))
            btn_host.grid(row=r, column=c, padx=10, pady=10)
            c += 1
            if c >= 4: c, r = 0, r + 1

    def cerrar_menu(self):
        if self.app_drawer:
            self.app_drawer.destroy()
            self.app_drawer = None

    def ejecutar_app(self, comando):
        self.cerrar_menu()
        comando()

    # ==========================================
    # LÓGICA DE INSTALACIÓN Y ENLACE
    # ==========================================
    def instalar_app_externa(self): # Para .py
        ruta_archivo = fd.askopenfilename(title="Selecciona el instalador (.py)", filetypes=[("AetherOS Apps", "*.py")])
        if ruta_archivo:
            nombre_app = os.path.basename(ruta_archivo).replace(".py", "").capitalize()
            self.apps_terceros[nombre_app] = ruta_archivo
            mb.showinfo("Éxito", f"'{nombre_app}' ha sido instalada en AetherOS.")
            self.abrir_menu() 

    def ejecutar_script_externo(self, ruta_script):
        self.cerrar_menu()
        try: subprocess.Popen([sys.executable, ruta_script])
        except Exception as e: mb.showerror("Error", f"No se pudo abrir la app.\nDetalle: {e}")

    # NUEVO: LÓGICA PARA PROGRAMAS .EXE DE WINDOWS
    def enlazar_programa_host(self):
        ruta_archivo = fd.askopenfilename(title="Selecciona el programa (.exe)", filetypes=[("Ejecutables", "*.exe"), ("Todos los archivos", "*.*")])
        if ruta_archivo:
            nombre_prog = os.path.basename(ruta_archivo).replace(".exe", "").capitalize()
            self.apps_host[nombre_prog] = ruta_archivo
            mb.showinfo("Enlace Creado", f"Acceso directo a '{nombre_prog}' creado en el menú.")
            self.abrir_menu()

    def ejecutar_programa_host(self, ruta_exe):
        self.cerrar_menu()
        try: 
            # os.startfile es la forma nativa de decirle a Windows que abra algo
            if sys.platform == "win32":
                os.startfile(ruta_exe)
            else:
                subprocess.Popen([ruta_exe])
        except Exception as e: 
            mb.showerror("Error del Sistema", f"Windows no pudo abrir el programa.\nDetalle: {e}")

    # ==========================================
    # EDITOR Y CALCULADORA
    # ==========================================
    def abrir_editor(self):
        editor = ctk.CTkToplevel(self)
        editor.title("Aether Text")
        editor.geometry("700x500")
        editor.attributes("-topmost", True)
        editor.configure(fg_color=BG_COLOR)
        area_texto = ctk.CTkTextbox(editor, corner_radius=15, fg_color=PANEL_COLOR, text_color=TEXT_COLOR, font=("Consolas", 14))
        area_texto.pack(fill="both", expand=True, padx=15, pady=15)

    def abrir_calculadora(self):
        calc = ctk.CTkToplevel(self)
        calc.title("Calculadora")
        calc.geometry("320x450")
        calc.attributes("-topmost", True)
        calc.configure(fg_color=BG_COLOR)
        pantalla = ctk.CTkEntry(calc, height=70, font=("Arial", 36), justify="right", fg_color=PANEL_COLOR, text_color=TEXT_COLOR, border_width=0, corner_radius=15)
        pantalla.pack(fill="x", padx=15, pady=(20, 15))

        def click_boton(valor):
            if valor == "C": pantalla.delete(0, 'end')
            elif valor == "=":
                try:
                    res = eval(pantalla.get())
                    pantalla.delete(0, 'end')
                    pantalla.insert('end', str(res))
                except:
                    pantalla.delete(0, 'end')
                    pantalla.insert('end', "Error")
            else: pantalla.insert('end', valor)

        frame_botones = ctk.CTkFrame(calc, fg_color="transparent")
        frame_botones.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        for r_idx, fila in enumerate([('7','8','9','/'), ('4','5','6','*'), ('1','2','3','-'), ('C','0','=','+')]):
            frame_botones.rowconfigure(r_idx, weight=1)
            for c_idx, tecla in enumerate(fila):
                frame_botones.columnconfigure(c_idx, weight=1)
                color_fondo = ACCENT_COLOR if tecla in ['/','*','-','+','='] else PANEL_COLOR
                color_texto = BG_COLOR if color_fondo == ACCENT_COLOR else TEXT_COLOR
                ctk.CTkButton(frame_botones, text=tecla, font=("Arial", 20, "bold"), fg_color=color_fondo, text_color=color_texto, corner_radius=12, command=lambda v=tecla: click_boton(v)).grid(row=r_idx, column=c_idx, padx=5, pady=5, sticky="nsew")

    # ==========================================
    # EXPLORADOR DE ARCHIVOS
    # ==========================================
    def abrir_explorador(self):
        self.explorador = ctk.CTkToplevel(self)
        self.explorador.title("Archivos - AetherOS")
        self.explorador.geometry("750x550")
        self.explorador.attributes("-topmost", True)
        self.explorador.configure(fg_color=BG_COLOR)

        self.panel_izquierdo = ctk.CTkFrame(self.explorador, width=180, corner_radius=20, fg_color=PANEL_COLOR)
        self.panel_izquierdo.pack(side="left", fill="y", padx=(15, 5), pady=15)
        
        self.contenedor_derecho = ctk.CTkFrame(self.explorador, fg_color="transparent")
        self.contenedor_derecho.pack(side="right", fill="both", expand=True)

        self.barra_herramientas = ctk.CTkFrame(self.contenedor_derecho, height=55, corner_radius=20, fg_color=PANEL_COLOR)
        self.barra_herramientas.pack(side="top", fill="x", padx=(5, 15), pady=(15, 5))

        self.btn_volver = ctk.CTkButton(self.barra_herramientas, text="⬅️", width=40, corner_radius=15, 
                                        fg_color="transparent", text_color=TEXT_COLOR, hover_color="#45475A", 
                                        command=self.retroceder_carpeta)
        self.btn_volver.pack(side="left", padx=(15, 5))

        self.lbl_ruta = ctk.CTkLabel(self.barra_herramientas, text=f"📍 {self.carpeta_actual}", font=("Arial", 15, "bold"), text_color=TEXT_COLOR)
        self.lbl_ruta.pack(side="left", padx=5, pady=10)

        ctk.CTkButton(self.barra_herramientas, text="➕ Carpeta", width=100, corner_radius=15, 
                      fg_color="#A6E3A1", text_color="#1E1E2E", hover_color="#94CC90",
                      command=self.crear_carpeta).pack(side="right", padx=10)
        
        ctk.CTkButton(self.barra_herramientas, text="⬆️ Subir", width=100, corner_radius=15, 
                      fg_color=ACCENT_COLOR, text_color="#1E1E2E", hover_color=HOVER_COLOR,
                      command=self.subir_archivo).pack(side="right", padx=5)

        self.panel_contenido = ctk.CTkScrollableFrame(self.contenedor_derecho, corner_radius=20, fg_color=PANEL_COLOR)
        self.panel_contenido.pack(fill="both", expand=True, padx=(5, 15), pady=(5, 15))

        self.construir_sidebar()
        self.actualizar_vista_archivos()

    def construir_sidebar(self):
        ctk.CTkLabel(self.panel_izquierdo, text="Aether Files", font=("Arial", 18, "bold"), text_color=TEXT_COLOR).pack(pady=25)
        for carpeta in ["Documentos", "Imágenes", "Proyectos"]:
            btn = ctk.CTkButton(self.panel_izquierdo, text=f"  📁 {carpeta}", fg_color="transparent", 
                                anchor="w", hover_color="#45475A", corner_radius=10, font=("Arial", 14),
                                text_color=TEXT_COLOR, command=lambda c=carpeta: self.cambiar_directorio(c))
            btn.pack(fill="x", padx=15, pady=8)

    def cambiar_directorio(self, nueva_carpeta):
        self.carpeta_actual = nueva_carpeta
        self.lbl_ruta.configure(text=f"📍 {self.carpeta_actual}")
        self.actualizar_vista_archivos()

    def retroceder_carpeta(self):
        if "/" in self.carpeta_actual:
            partes = self.carpeta_actual.split("/")
            self.carpeta_actual = "/".join(partes[:-1])
            self.lbl_ruta.configure(text=f"📍 {self.carpeta_actual}")
            self.actualizar_vista_archivos()

    def actualizar_vista_archivos(self):
        for widget in self.panel_contenido.winfo_children(): 
            widget.destroy()
        
        archivos_actuales = self.sistema_archivos.get(self.carpeta_actual, [])
        
        if not archivos_actuales:
            ctk.CTkLabel(self.panel_contenido, text="Carpeta vacía ✨", text_color="#6C7086", font=("Arial", 14)).pack(pady=40)
            return
            
        for item in archivos_actuales:
            frame_archivo = ctk.CTkFrame(self.panel_contenido, fg_color="#45475A", corner_radius=15, cursor="hand2")
            frame_archivo.pack(fill="x", pady=8, padx=10)
            
            nombre_archivo = item["nombre"]
            texto_nombre = nombre_archivo
            texto_ext = ""
            
            if item["info"] != "Carpeta" and "." in nombre_archivo:
                partes = nombre_archivo.rsplit(".", 1)
                texto_nombre = partes[0]
                texto_ext = f".{partes[1]}"
                
            lbl_icono = ctk.CTkLabel(frame_archivo, text=item["icono"], font=("Arial", 26))
            lbl_icono.pack(side="left", padx=15, pady=10)
            
            lbl_nombre = ctk.CTkLabel(frame_archivo, text=texto_nombre, font=("Arial", 15), text_color=TEXT_COLOR)
            lbl_nombre.pack(side="left")
            
            lbl_ext = None
            if texto_ext:
                lbl_ext = ctk.CTkLabel(frame_archivo, text=texto_ext, font=("Arial", 15, "bold"), text_color="#A6E3A1")
                lbl_ext.pack(side="left")
                
            lbl_info = ctk.CTkLabel(frame_archivo, text=item["info"], font=("Arial", 13), text_color="#A6ADC8")
            lbl_info.pack(side="right", padx=20)
            
            def al_hacer_clic(event, i=item):
                self.abrir_item(i)
                
            frame_archivo.bind("<Button-1>", al_hacer_clic)
            lbl_icono.bind("<Button-1>", al_hacer_clic)
            lbl_nombre.bind("<Button-1>", al_hacer_clic)
            if lbl_ext: 
                lbl_ext.bind("<Button-1>", al_hacer_clic)
            lbl_info.bind("<Button-1>", al_hacer_clic)

    def abrir_item(self, item):
        if item["info"] == "Carpeta":
            nueva_ruta = f"{self.carpeta_actual}/{item['nombre']}"
            if nueva_ruta not in self.sistema_archivos:
                self.sistema_archivos[nueva_ruta] = []
            self.carpeta_actual = nueva_ruta
            self.lbl_ruta.configure(text=f"📍 {self.carpeta_actual}")
            self.actualizar_vista_archivos()
            
        elif item["icono"] == "🖼️":
            self.mostrar_imagen(item)
            
        elif item["icono"] == "🐍" and "ruta_real" in item:
            self.ejecutar_script_externo(item["ruta_real"])

    def mostrar_imagen(self, item):
        visor = ctk.CTkToplevel(self.explorador)
        visor.title(f"Visor - {item['nombre']}")
        visor.attributes("-topmost", True)
        visor.configure(fg_color=BG_COLOR)

        if "ruta_real" in item and PIL_DISPONIBLE:
            try:
                img = Image.open(item["ruta_real"])
                img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 300))
                ctk.CTkLabel(visor, image=img_ctk, text="").pack(padx=20, pady=20)
            except Exception as e:
                ctk.CTkLabel(visor, text=f"No se pudo cargar la imagen.\n{e}", text_color=TEXT_COLOR).pack(padx=50, pady=50)
        else:
            mensaje = "Imagen Simulada\n\n(Para ver imágenes reales, instala la librería en consola:\npip install Pillow)" if not PIL_DISPONIBLE else f"Mostrando imagen simulada:\n{item['nombre']}"
            ctk.CTkLabel(visor, text=mensaje, text_color=TEXT_COLOR).pack(padx=50, pady=50)

    def crear_carpeta(self):
        dialogo = ctk.CTkInputDialog(text="Nombre de la carpeta:", title="Nueva Carpeta")
        nombre = dialogo.get_input()
        if nombre:
            self.sistema_archivos[self.carpeta_actual].append({"nombre": nombre, "icono": "📁", "info": "Carpeta"})
            self.actualizar_vista_archivos()

    def subir_archivo(self):
        ruta = fd.askopenfilename(title="Selecciona un archivo")
        if ruta:
            nombre = os.path.basename(ruta)
            tamaño = round(os.path.getsize(ruta) / 1024, 1)
            icono = "🖼️" if nombre.endswith(('.png', '.jpg', '.jpeg', '.webp')) else "🐍" if nombre.endswith(('.py', '.js', '.html')) else "📄"
            self.sistema_archivos[self.carpeta_actual].append({
                "nombre": nombre, "icono": icono, "info": f"{tamaño} KB", "ruta_real": ruta
            })
            self.actualizar_vista_archivos()

    def abrir_apagado(self): 
        self.quit()

if __name__ == "__main__":
    app = AetherOS()
    app.mainloop()