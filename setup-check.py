import os
import subprocess
import sys
from pathlib import Path

print("Python:", sys.version)
print("Interpreter:", sys.executable)

java_home = os.environ.get("JAVA_HOME")
print("JAVA_HOME:", java_home)

try:
    subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT)
    print("Java OK")
except Exception:
    raise RuntimeError("Java not found. Install JDK 11 and set JAVA_HOME.")

print("Environment looks good")
