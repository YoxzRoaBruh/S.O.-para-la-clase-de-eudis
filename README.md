# ⚡ Dashboard del Kernel (Sistema Operativo)

Este proyecto es un sistema de monitoreo en tiempo real desarrollado para demostrar el comportamiento del Kernel. Permite visualizar el uso del procesador, la memoria RAM, el almacenamiento del disco y los procesos activos de la computadora.

## 🚀 Tecnologías utilizadas
* **Backend:** Python con Flask y la librería `psutil` para la comunicación con el Kernel.
* **Frontend:** Tecnologías web (HTML, CSS, JavaScript) empaquetadas con Electron para funcionar como aplicación de escritorio nativa.

## 🛠️ Guía de Instalación

Para que el sistema funcione correctamente, debes seguir estos dos pasos en terminales separadas:

### 1. Configuración del Backend (Cerebro)
1. Entra a la carpeta del backend: `cd backend`
2. Crea un entorno virtual: `python -m venv venv`
3. Activa el entorno virtual:
   - Windows: `.\venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Instala las dependencias: `pip install -r requirements.txt`
5. Inicia el servidor: `python nucleo.py`

### 2. Configuración del Frontend (Interfaz)
1. En una nueva terminal, entra a la carpeta del frontend: `cd frontend`
2. Instala los paquetes de Node: `npm install`
3. Inicia la aplicación: `npm start`

## 👥 Colaboradores
* Proyecto desarrollado para la clase de sistemas operativos.