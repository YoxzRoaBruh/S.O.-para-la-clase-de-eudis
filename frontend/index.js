async function obtenerDatos() {
    try {
        // Buscamos los datos en la API de Python
        const respuesta = await fetch('http://localhost:5000/api/sistema');
        const datos = await respuesta.json();
        
        // Inyectamos los datos en el HTML
        document.getElementById('cpu-uso').innerText = datos.cpu + '%';
        document.getElementById('ram-uso').innerText = datos.ram.porcentaje + '%';
        document.getElementById('ram-total').innerText = datos.ram.total_gb + ' GB';
        
    } catch (error) {
        console.error("Error conectando con el servidor Python:", error);
    }
}

// Hacemos que la función se repita cada 1000 milisegundos (1 segundo)
setInterval(obtenerDatos, 1000);
obtenerDatos(); // Ejecutamos la primera vez inmediatamente