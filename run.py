import subprocess
import time
import sys

def run_backend():
    return subprocess.Popen(
        ["uvicorn", "backend.app:app", "--reload"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

def run_frontend():
    return subprocess.Popen(
        ["streamlit", "run", "frontend/app.py"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )

if __name__ == "__main__":
    print("🚀 Starting KrishiSaarthi AI...")

    backend = run_backend()
    time.sleep(3)  # wait for backend

    frontend = run_frontend()

    print("✅ System running!")
    print("👉 Open browser if not auto-opened")

    backend.wait()
    frontend.wait()