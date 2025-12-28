"""
Run all performance tests automatically.
Usage: python run_all.py
"""
import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

BASE_DIR = Path(__file__).parent
REST_APP = BASE_DIR / "rest_app"
GRPC_APP = BASE_DIR / "grpc_app"
LOCUST_DIR = BASE_DIR / "locustfiles"
RESULTS_DIR = BASE_DIR / "results"

# Test configurations
SCENARIOS = [
    {"name": "sanity", "users": 10, "spawn": 1, "time": "30s", "duration_sec": 30},
    {"name": "normal", "users": 100, "spawn": 5, "time": "60s", "duration_sec": 60},
    {"name": "stress", "users": 300, "spawn": 10, "time": "60s", "duration_sec": 60},
    {"name": "stability", "users": 100, "spawn": 5, "time": "180s", "duration_sec": 180},
]


def spinner(stop_event, message="Processing"):
    """Show spinner animation."""
    spinner_chars = ['|', '/', '-', '\\']
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f'\r{message} {spinner_chars[idx]} ')
        sys.stdout.flush()
        idx = (idx + 1) % len(spinner_chars)
        time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * (len(message) + 10) + '\r')
    sys.stdout.flush()


def run_cmd(cmd, cwd=None, check=True, show_spinner=False, spinner_msg="Processing"):
    """Run command and return result."""
    if not show_spinner:
        print(f"[CMD] {cmd}")
    
    stop_event = threading.Event()
    if show_spinner:
        spinner_thread = threading.Thread(target=spinner, args=(stop_event, spinner_msg))
        spinner_thread.start()
    
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    
    if show_spinner:
        stop_event.set()
        spinner_thread.join()
    
    if result.returncode != 0 and check:
        print(f"[ERROR] {result.stderr}")
    return result


def install_dependencies():
    """Install all required packages."""
    print("\n" + "=" * 50)
    print("Installing dependencies...")
    print("=" * 50)
    run_cmd(
        f"{sys.executable} -m pip install -q -r requirements.txt", 
        cwd=BASE_DIR, 
        show_spinner=True, 
        spinner_msg="Installing packages"
    )
    print("Dependencies installed")


def generate_proto():
    """Generate gRPC proto files."""
    print("\n" + "=" * 50)
    print("Generating proto files...")
    print("=" * 50)
    result = run_cmd(f"{sys.executable} generate_proto.py", cwd=GRPC_APP)
    if result.returncode == 0:
        print("Proto files generated")
    else:
        print("Warning: Proto generation may have issues")


def seed_databases():
    """Seed both databases."""
    print("\n" + "=" * 50)
    print("Seeding databases...")
    print("=" * 50)
    result = run_cmd(f"{sys.executable} scripts/seed_database.py", cwd=BASE_DIR)
    if result.stdout:
        print(result.stdout.strip())
    print("Databases seeded")


def start_rest_server():
    """Start REST server in background."""
    print("\n" + "=" * 50)
    print("Starting REST server on port 8000...")
    print("=" * 50)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REST_APP)
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=REST_APP,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    time.sleep(3)  # Wait for server to start
    return process


def start_grpc_server():
    """Start gRPC server in background."""
    print("\n" + "=" * 50)
    print("Starting gRPC server on port 50051...")
    print("=" * 50)
    process = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=GRPC_APP,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    time.sleep(2)  # Wait for server to start
    return process


def run_locust_test(protocol: str, scenario: dict):
    """Run a single Locust test."""
    name = scenario["name"]
    users = scenario["users"]
    spawn = scenario["spawn"]
    duration = scenario["time"]
    duration_sec = scenario["duration_sec"]
    
    print(f"\n--- {protocol.upper()} {name} test ---")
    print(f"Users: {users}, Spawn: {spawn}/s, Duration: {duration}")
    sys.stdout.flush()
    
    if protocol == "rest":
        locustfile = LOCUST_DIR / "rest_locustfile.py"
        host = "http://localhost:8000"
    else:
        locustfile = LOCUST_DIR / "grpc_locustfile.py"
        host = "localhost:50051"
    
    # Create results directory
    result_dir = RESULTS_DIR / protocol
    result_dir.mkdir(parents=True, exist_ok=True)
    
    csv_prefix = result_dir / f"{name}"
    html_report = result_dir / f"{name}_report.html"
    
    cmd = [
        sys.executable, "-m", "locust",
        "-f", str(locustfile),
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(spawn),
        "--run-time", duration,
        "--headless",
        "--csv", str(csv_prefix),
        "--html", str(html_report),
        "--only-summary"
    ]
    
    # Progress indicator
    stop_event = threading.Event()
    spinner_thread = threading.Thread(
        target=progress_indicator, 
        args=(stop_event, duration_sec, f"{protocol.upper()} {name}"),
        daemon=True
    )
    spinner_thread.start()
    
    try:
        result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, timeout=duration_sec + 30)
        
        stop_event.set()
        spinner_thread.join(timeout=1)
        
        if result.returncode == 0:
            print(f"\nCompleted: {name}")
            print(f"Results: {result_dir}/{name}_*")
        else:
            print(f"\nTest completed with issues (code {result.returncode})")
            if result.stderr:
                # Print errors
                lines = result.stderr.strip().split('\n')
                for line in lines[-10:]:
                    if line.strip() and 'warning' not in line.lower():
                        print(f"  ERROR: {line}")
            if result.stdout:
                # Print summary if available
                for line in result.stdout.strip().split('\n')[-5:]:
                    if line.strip():
                        print(f"  {line}")
    
    except subprocess.TimeoutExpired:
        stop_event.set()
        spinner_thread.join(timeout=1)
        print(f"\nTest timed out after {duration_sec + 30}s")
    except Exception as e:
        stop_event.set()
        spinner_thread.join(timeout=1)
        print(f"\nTest error: {e}")
    
    sys.stdout.flush()
    time.sleep(1)  # Brief pause between tests


def progress_indicator(stop_event, total_seconds, test_name):
    """Show progress bar for test."""
    start_time = time.time()
    bar_length = 40
    
    try:
        while not stop_event.is_set():
            elapsed = time.time() - start_time
            progress = min(elapsed / total_seconds, 1.0)
            filled = int(bar_length * progress)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            percent = int(progress * 100)
            remaining = max(0, int(total_seconds - elapsed))
            
            sys.stdout.write(f'\r{test_name}: [{bar}] {percent}% ({remaining}s left)   ')
            sys.stdout.flush()
            
            time.sleep(0.5)
            
            if elapsed >= total_seconds:
                break
    except:
        pass
    finally:
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        sys.stdout.flush()


def stop_process(process, name):
    """Stop a background process."""
    if process:
        print(f"\nStopping {name}...")
        try:
            if os.name == 'nt':
                # Windows: try graceful shutdown
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                             capture_output=True)
            else:
                process.terminate()
                process.wait(timeout=5)
        except Exception as e:
            print(f"Warning: {e}")
            try:
                process.kill()
            except:
                pass


def main():
    print("=" * 60)
    print("Performance Testing: REST vs gRPC")
    print("=" * 60)
    
    rest_process = None
    grpc_process = None
    
    try:
        # Setup
        install_dependencies()
        generate_proto()
        seed_databases()
        
        # Start servers
        rest_process = start_rest_server()
        grpc_process = start_grpc_server()
        
        print("\n" + "=" * 50)
        print(f"Running REST tests ({len(SCENARIOS)} scenarios)...")
        print("=" * 50)
        sys.stdout.flush()
        
        for i, scenario in enumerate(SCENARIOS, 1):
            print(f"\n[{i}/{len(SCENARIOS)}] Starting {scenario['name']} test...")
            sys.stdout.flush()
            run_locust_test("rest", scenario)
        
        print("\n" + "=" * 50)
        print(f"Running gRPC tests ({len(SCENARIOS)} scenarios)...")
        print("=" * 50)
        sys.stdout.flush()
        
        for i, scenario in enumerate(SCENARIOS, 1):
            print(f"\n[{i}/{len(SCENARIOS)}] Starting {scenario['name']} test...")
            sys.stdout.flush()
            run_locust_test("grpc", scenario)
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("Results saved in: results/rest/ and results/grpc/")
        print("=" * 60)
        
        # Generate final report
        print("\n" + "=" * 50)
        print("Generating final report...")
        print("=" * 50)
        run_cmd(f"{sys.executable} generate_report.py", cwd=BASE_DIR)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Cleanup
        print("\nStopping servers...")
        stop_process(rest_process, "REST server")
        stop_process(grpc_process, "gRPC server")
        print("Done")


if __name__ == "__main__":
    main()

