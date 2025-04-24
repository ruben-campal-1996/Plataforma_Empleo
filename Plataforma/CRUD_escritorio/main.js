const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs').promises;
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
  ipcMain.handle('login', async (event, { correo, password }) => {
    console.log(`Intento de login: correo=${correo}, password=${password ? '[oculta]' : ''}`);
    if (!correo || !password) {
      console.error('Error: Correo o password vacíos');
      return { error: 'Por favor, ingrese correo y contraseña.' };
    }

    try {
      let pyshell = new PythonShell(path.join(__dirname, 'python/db_connect.py'), {
        mode: 'json',
        args: ['login', correo, password],
        pythonOptions: ['-u'],
        pythonPath: process.platform === 'win32' ? 'python' : 'python3'
      });

      return await new Promise((resolve) => {
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
    } catch (error) {
      console.error('Error en PythonShell:', error);
      return { error: `Error al conectar con el script: ${error.message}` };
    }
  });

  // Manejar datos de análisis
  ipcMain.handle('get-analisis-data', async () => {
    console.log('Solicitando datos de análisis');
    try {
      // Determinar el mes actual
      const now = new Date();
      const year = now.getFullYear();
      const month = now.getMonth() + 1; // getMonth() devuelve 0-11, sumamos 1 para 1-12
      const filename = `busquedas_${year}_${month.toString().padStart(2, '0')}.json`;
      const filepath = path.join(__dirname, 'data', 'busquedas', filename);

      // Leer el archivo del mes actual
      const data = await fs.readFile(filepath, 'utf-8');
      const busquedas = JSON.parse(data);

      // Procesar los datos para análisis
      const top_keywords = {};
      const top_provinces = {};
      const daily_queries = {};

      busquedas.forEach(busqueda => {
        // Top keywords
        const keyword = busqueda.palabra_clave || 'Desconocido';
        top_keywords[keyword] = (top_keywords[keyword] || 0) + 1;

        // Top provinces
        const province = busqueda.provincia || 'Desconocido';
        top_provinces[province] = (top_provinces[province] || 0) + 1;

        // Daily queries
        const day = busqueda.fecha.split('T')[0]; // Extraer la fecha en formato YYYY-MM-DD
        daily_queries[day] = (daily_queries[day] || 0) + 1;
      });

      // Convertir a formato de lista ordenada
      const top_keywords_list = Object.entries(top_keywords)
        .map(([keyword, total]) => ({ keyword, total }))
        .sort((a, b) => b.total - a.total)
        .slice(0, 10);

      const top_provinces_list = Object.entries(top_provinces)
        .map(([provincia, total]) => ({ provincia, total }))
        .sort((a, b) => b.total - a.total)
        .slice(0, 10);

      const daily_queries_list = Object.entries(daily_queries)
        .map(([day, total]) => ({ day, total }))
        .sort((a, b) => b.day.localeCompare(a.day))
        .slice(0, 7);

      return {
        top_keywords: top_keywords_list,
        top_provinces: top_provinces_list,
        daily_queries: daily_queries_list
      };
    } catch (error) {
      console.error('Error leyendo datos de análisis:', error);
      return { error: `No se encontraron datos para el mes actual: ${error.message}` };
    }
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