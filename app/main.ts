import { app, BrowserWindow, shell } from 'electron';
import * as fs from 'fs';
import * as path from 'path';

function createWindow(): BrowserWindow {
  const inDebugMode = process.argv.slice(1).some((val) => val === '--serve');

  const browserWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    autoHideMenuBar: true,
    webPreferences: {
      nodeIntegration: true,
      allowRunningInsecureContent: inDebugMode,
      contextIsolation: false,
    },
  });
  browserWindow.center();

  if (inDebugMode) {
    const debug = require('electron-debug');
    debug();

    require('electron-reloader')(module);
    browserWindow.loadURL('http://localhost:4200');
  } else {
    let pathIndex = './index.html';

    if (fs.existsSync(path.join(__dirname, '../dist/index.html'))) {
      pathIndex = '../dist/index.html';
    }

    const url = new URL(path.join('file:', __dirname, pathIndex));
    browserWindow.loadURL(url.href);
  }

  // Open external links in the default browser
  browserWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  return browserWindow;
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
