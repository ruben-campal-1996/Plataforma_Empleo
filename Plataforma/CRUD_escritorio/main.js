const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { PythonShell } = require('python-shell');

function createLoginWindow() {
  const loginWindow = new BrowserWindow({
    width: 600,
    height: 400,
    resizable: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  loginWindow.loadFile(path.join(__dirname, 'renderer/login.html'));
  return loginWindow;
}

function createMainWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    minWidth: 600,
    minHeight: 400,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'renderer/index.html'));
  return mainWindow;
}

app.whenReady().then(() => {
  const loginWindow = createLoginWindow();

  // Manejar login
  ipcMain.handle('login', async (event, { username, password }) => {
    console.log(`Intento de login: username=${username}, password=${password ? '[oculta]' : ''}`);
    if (!username || !password) {
      console.error('Error: Username o password vacíos');
      return { error: 'Por favor, ingrese correo y contraseña.' };
    }

    let pyshell = new PythonShell(path.join(__dirname, 'python/db_connect.py'), {
      mode: 'json',
      args: ['login', username, password],
      pythonOptions: ['-u'],
      pythonPath: process.platform === 'win32' ? 'python' : 'python3'
    });

    return new Promise((resolve) => {
      pyshell.on('message', (message) => {
        console.log('Respuesta de Python:', message);
        resolve(message);
      });
      pyshell.on('error', (err) => {
        console.error('Error ejecutando db_connect.py:', err);
        resolve({ error: `Error en el servidor: ${err.message}` });
      });
      pyshell.on('pythonError', (err) => {
        console.error('Error de Python:', err);
        resolve({ error: `Error de Python: ${err.message}` });
      });
      pyshell.end((err) => {
        if (err) {
          console.error('PythonShell terminó con error:', err);
          resolve({ error: `Error al ejecutar script: ${err.message}` });
        }
      });
    });
  });

  // Manejar datos de análisis
  ipcMain.handle('get-analisis-data', async () => {
    console.log('Solicitando datos de análisis');
    let pyshell = new PythonShell(path.join(__dirname, 'python/db_connect.py'), {
      mode: 'json',
      args: ['analisis'],
      pythonOptions: ['-u'],
      pythonPath: process.platform === 'win32' ? 'python' : 'python3'
    });

    return new Promise((resolve) => {
      pyshell.on('message', (message) => {
        console.log('Datos de análisis recibidos:', message);
        resolve(message);
      });
      pyshell.on('error', (err) => {
        console.error('Error ejecutando db_connect.py (análisis):', err);
        resolve({});
      });
      pyshell.end(() => {});
    });
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createLoginWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});