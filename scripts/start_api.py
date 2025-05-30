import os
import subprocess
import sys

def run_with_debugger():
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv_python = os.path.join(current_dir, 'api', '.venv', 'bin', 'python')
    
    if not os.path.exists(venv_python):
        print("Error: Virtual environment not found. Please run:")
        print("cd api && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt debugpy")
        sys.exit(1)

    # Change to api directory and add it to PYTHONPATH
    api_dir = os.path.join(current_dir, 'api')
    os.chdir(current_dir)  # Stay in root directory
    os.environ['PYTHONPATH'] = current_dir  # Add root to Python path
    
    # Launch with debugpy enabled
    cmd = [
        venv_python,
        "-m",
        "debugpy",
        "--listen",
        "0.0.0.0:5678",
        "-m",
        "uvicorn",
        "api.main:app",  # Use full module path
        "--reload"
    ]
    
    print(f"Starting server with debugger enabled on port 5678")
    print("Waiting for debugger to attach...")
    subprocess.run(cmd, env=os.environ)

if __name__ == "__main__":
    run_with_debugger()