import subprocess
import time
import sys
import os
import socket

def check_port(port):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def wait_for_server(port, timeout=30):
    """Wait for server to start"""
    print(f"⏳ Waiting for server on port {port}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_port(port):
            print(f"✅ Server on port {port} is ready!")
            return True
        time.sleep(1)
    return False

def run_fastapi():
    """Run FastAPI backend on port 8000"""
    print("🚀 Starting FastAPI backend on http://localhost:8000")
    
    if sys.platform == "win32":
        # Windows-specific subprocess flags
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        # Linux/Mac
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ])

def run_streamlit():
    """Run Streamlit frontend on port 8501"""
    print("🚀 Starting Streamlit frontend on http://localhost:8501")
    subprocess.run([
        sys.executable, "-m", "streamlit", 
        "run", 
        "app.py",
        "--server.port", "8501",
        "--server.address", "127.0.0.1"
    ])

def main():
    print("=" * 60)
    print("🎯 Complaint Management System")
    print("=" * 60)
    
    # Check if ports are already in use
    if check_port(8000):
        print("⚠️  Port 8000 is already in use!")
        print("Please close the application using this port and try again.")
        return
    
    if check_port(8501):
        print("⚠️  Port 8501 is already in use!")
        print("Please close the application using this port and try again.")
        return
    
    print("\n📋 Starting servers...\n")
    
    # Start FastAPI
    run_fastapi()
    
    # Wait for FastAPI to be ready
    if not wait_for_server(8000, timeout=30):
        print("❌ FastAPI failed to start. Please check for errors.")
        return
    
    print("\n" + "=" * 60)
    print("✅ FastAPI is running at: http://localhost:8000")
    print("=" * 60)
    print("\n⏳ Now starting Streamlit...\n")
    
    # Start Streamlit
    try:
        run_streamlit()
    except KeyboardInterrupt:
        print("\n\n⚠️  Shutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()