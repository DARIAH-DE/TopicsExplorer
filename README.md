This branch contains code for the Topics Explorer **frozen** frontend. Central component is the JavaScript Framework [Electron](https://electronjs.org/). Electron allows for the development of desktop GUI applications using front and back end components originally developed for web applications: Node.js runtime for the backend and Chromium for the frontend. For Topics Explorer we only use the frontend component, Node.js will be disabled and replaced by a [Flask](http://flask.pocoo.org/) application.


## Getting started
Install the project’s dependencies:

```
$ npm install
```

Install Electron Forge:

```
$ npm install -g electron-forge
```

Start the application:

```
$ electron-forge start
```

Package the application:

```
$ electron-forge package
```

> Unlike [PyInstaller](https://www.pyinstaller.org/), the frontend for _all_ operating systems (Windows, macOS, Linux) can be deployed by e.g. Jenkins on a Linux machine.
