const {app, BrowserWindow} = require('electron');
var path = require('path');

let mainWindow;

function createWindow() {
  const url = 'http://localhost:5000';

  mainWindow = new BrowserWindow({
    width: 1250,
    height: 660,
    icon: path.join(__dirname, 'assets/img/favicon-template.png'),
    webPreferences: {
      nodeIntegration: false
    }
  });

  mainWindow.loadURL(url);
  mainWindow.setMenu(null);

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
};

app.on('ready', createWindow);

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit()
  };
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  };
});
