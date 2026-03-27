"""Add test/ to sys.path so test modules can import map_model_names."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
