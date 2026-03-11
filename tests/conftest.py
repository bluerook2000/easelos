# tests/conftest.py
"""Shared test fixtures — venv path setup."""
import sys
import os

# Ensure the venv's site-packages are available
_venv_path = "/Users/redventra/easelos-venv"
_venv_site = os.path.join(
    _venv_path, "lib",
    f"python{sys.version_info.major}.{sys.version_info.minor}",
    "site-packages",
)
if os.path.isdir(_venv_site) and _venv_site not in sys.path:
    sys.path.insert(0, _venv_site)

# Ensure the pipeline package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
