const {app, BrowserWindow} = require('electron');

app.on('window-all-closed', () => {
  app.quit()
})

app.on('ready', () => {
    var subpy = require('child_process').spawn('python3', ['webapp.py']);
    //var subpy = require('child_process').spawn('python', ['webapp.py']);
    //var subpy = require('child_process').spawn('webapp.exe');
    //var subpy = require('child_process').spawn('webapp.app');
    var rq = require('request-promise');
    var mainAddr = 'http://127.0.0.1:5000';
    
    var openWindow = function(){
        mainWindow = new BrowserWindow({width: 1200,
                                        height: 660,
                                        icon: 'static/img/app_icon.png'});
        mainWindow.setMenu(null) 
        mainWindow.loadURL(mainAddr);
        mainWindow.on('closed', () => {
          mainWindow = null;
          subpy.kill('SIGINT');
          app.quit()
        });
    };
    
    var startUp = function(){
        rq(mainAddr)
          .then(function(htmlString){
            openWindow();
          })
          .catch(function(err){
            startUp();
          });
    };

    startUp();
    });
