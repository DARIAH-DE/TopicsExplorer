#!/usr/bin/env python3

from pathlib import Path
import platform
import subprocess
import sys
from threading import Thread
from urllib import request


BACKEND_RUNNING = False
URL = "http://localhost:5000"

if __name__ == "__main__":
    root = Path(sys.executable).parent

    os = platform.system()
    if os in {"Linux"}:
        backend_executable = "topics-explorer-backend"
        frontend_executable = "topics-explorer-frontend"
    elif os in {"Windows"}:
        backend_executable = "topics-explorer-backend.exe"
        frontend_executable = "topics-explorer-frontend.exe"
    elif os in {"Darwin"}:
        backend_executable = "topics-explorer-backend"
        frontend_executable = "topics-explorer-frontend.app"
    else:
        raise OSError(f"The operating system '{os}' is not supported.")

    backend = str(Path(root, "resources", "backend", backend_executable))
    frontend = str(Path(root, "resources", "webengine", frontend_executable))

    # Start backend:
    backend_command = [backend]
    backend_process = Thread(target=subprocess.call, args=(backend_command,))
    backend_process.start()

    # Check if backend has started yet:
    while not BACKEND_RUNNING:
        try:
            response = request.urlopen(URL)
            if response.status == 200:
                BACKEND_RUNNING = True
            else:
                raise ValueError(f"Response status of {URL} was not 200")
        except:
            pass

    # Start frontend:
    frontend_command = [frontend]
    if os in {"Darwin"}:
        # On macOS, .app files are directories. Use `open` to treat them as
        # an executable:
        frontend_command.insert(0, "open")
    frontend_process = Thread(target=subprocess.call, args=(frontend_command,))
    frontend_process.start()

