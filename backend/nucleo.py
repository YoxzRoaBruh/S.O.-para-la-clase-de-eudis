from flask import Flask, jsonify
from flask_cors import CORS
import psutil

app = Flask(__name__)
# Habilitamos CORS para que nuestro frontend en Electron/HTML pueda leer esta API
CORS(app) 

@app.route('/api/sistema', methods=['GET'])
def obtener_datos():
    # 1. CPU y RAM
    uso_cpu = psutil.cpu_percent(interval=0.1) # Intervalo más corto para respuestas rápidas
    memoria = psutil.virtual_memory()
    ram_total_gb = memoria.total / (1024**3)
    
    # 2. Almacenamiento (Disco C)
    disco = psutil.disk_usage('C:\\')
    disco_total_gb = disco.total / (1024**3)
    
    # 3. Procesos en vivo
    procesos = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            if proc.info['memory_percent'] is not None:
                procesos.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    procesos_ordenados = sorted(procesos, key=lambda p: p['memory_percent'], reverse=True)[:3]
    
    # Empaquetamos todo en un diccionario (JSON)
    datos_sistema = {
        "cpu": uso_cpu,
        "ram": {
            "porcentaje": memoria.percent,
            "total_gb": round(ram_total_gb, 2)
        },
        "disco": {
            "porcentaje": disco.percent,
            "total_gb": round(disco_total_gb, 2)
        },
        "procesos": procesos_ordenados
    }
    
    return jsonify(datos_sistema)

if __name__ == "__main__":
    print("🚀 Servidor del Kernel iniciado en el puerto 5000...")
    print("👉 Entra en tu navegador a: http://localhost:5000/api/sistema")
    # debug=False para evitar que reinicie dos veces los hilos de psutil
    app.run(port=5000, debug=False)