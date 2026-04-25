const { app, BrowserWindow } = require('electron')

function createWindow () {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    autoHideMenuBar: true, // Esto oculta el menú (Archivo, Editar...) para que luzca más pro
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false 
    }
  })

  // Le decimos qué archivo HTML debe cargar
  win.loadFile('index.html')
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})