import importlib.util
import sys

dependencies = ['pymongo', 'dns', 'certifi']
missing = []

for package in dependencies:
    spec = importlib.util.find_spec(package)
    if spec is None:
        missing.append(package)
    else:
        print(f"{package} is installed")

if missing:
    print(f"Missing packages: {', '.join(missing)}")
    sys.exit(1)
else:
    print("All dependencies are installed")
    sys.exit(0)
