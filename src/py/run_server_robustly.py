
import subprocess
import os
import sys
import time

def run_server():
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["LITESTAR_DEBUG"] = "true"
    
    cwd = r"C:\Users\ASUS\Desktop\project1\litestar-fullstack\src\py"
    cmd = ["uv", "run", "app", "run", "--port", "8000", "--host", "0.0.0.0"]
    
    log_file = os.path.join(cwd, "server.log")
    print(f"Starting server, logging to {log_file}")
    
    with open(log_file, "w", encoding="utf-8") as f:
        process = subprocess.Popen(
            cmd,
            stdout=f,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=cwd
        )
        print(f"Server started with PID: {process.pid}")
        # Let it run for a bit to capture startup
        time.sleep(10)
        return process

if __name__ == "__main__":
    run_server()
