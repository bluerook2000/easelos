# tests/conftest.py
"""Shared test fixtures."""
import sys
import os

# Ensure the pipeline package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
