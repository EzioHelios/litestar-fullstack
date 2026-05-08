
import os
import subprocess
import time
from pathlib import Path


def run_server():
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["LITESTAR_DEBUG"] = "true"

    cwd = Path(__file__).resolve().parents[2] / "src" / "py"
    cmd = ["uv", "run", "app", "run", "--port", "8000", "--host", "0.0.0.0"]

    log_file = cwd / "server.log"
    print(f"Starting server, logging to {log_file}")

    with open(log_file, "w", encoding="utf-8") as f:
        process = subprocess.Popen(
            cmd,
            stdout=f,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=cwd,
        )
        print(f"Server started with PID: {process.pid}")
        # Let it run for a bit to capture startup
        time.sleep(10)
        return process

if __name__ == "__main__":
    run_server()
