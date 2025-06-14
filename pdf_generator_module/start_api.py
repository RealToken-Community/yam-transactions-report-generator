
import json, subprocess, sys, os
import signal

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down server...")
    sys.exit(0)

def main():
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        with open("config.json") as f:
            config = json.load(f)
        port = config.get("api_port", 5000)
        workers = os.cpu_count() or 2  # Fallback to 2

        print(f"Starting server on port {port} with {workers} workers...")
        print("Press Ctrl+C to stop the server")
        
        subprocess.run([
            "gunicorn",
            "-w", str(workers),
            "-b", f"0.0.0.0:{port}",
            "pdf_generator_module.api.app:create_app()"
        ], check=True)

    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()