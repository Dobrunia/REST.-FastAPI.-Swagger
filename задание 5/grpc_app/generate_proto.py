"""Generate Python code from proto file."""
import subprocess
import sys
from pathlib import Path

PROTO_DIR = Path(__file__).parent / "proto"
OUT_DIR = Path(__file__).parent


def generate():
    proto_file = PROTO_DIR / "glossary.proto"
    
    cmd = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"-I{PROTO_DIR}",
        f"--python_out={OUT_DIR}",
        f"--grpc_python_out={OUT_DIR}",
        str(proto_file)
    ]
    
    print(f"Generating from {proto_file}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    
    print("Generated: glossary_pb2.py, glossary_pb2_grpc.py")


if __name__ == "__main__":
    generate()

