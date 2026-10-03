"""
config.py
---------
Configuration settings for the Simple Dataset Upload & Query System.
This file centralizes application constants such as window settings,
colors, title, directory paths, and local AI (Ollama) parameters.
"""

import os

# Application Information
APP_TITLE = "Simple Dataset Upload & Query System"
APP_VERSION = "1.0.0 (Final Integration Release)"

# UI Window Geometry
WINDOW_WIDTH = 980
WINDOW_HEIGHT = 740
MIN_WIDTH = 850
MIN_HEIGHT = 650

# Path Configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Local AI / Ollama Configurations
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:latest"  # Alternative local models: llama3.2, mistral, codellama
OLLAMA_TIMEOUT = 5  # Connection timeout in seconds

# Color Palette (Modern, clean UI design)
COLOR_PRIMARY = "#2C3E50"      # Dark Navy Blue for header and primary accents
COLOR_ACCENT = "#3498DB"       # Bright Blue for highlights & focus
COLOR_BG = "#F8F9FA"           # Light Grey background
COLOR_CARD_BG = "#FFFFFF"      # White background for section cards
COLOR_TEXT_PRIMARY = "#2C3E50" # Dark slate for text
COLOR_TEXT_MUTED = "#7F8C8D"   # Muted grey for descriptions
COLOR_SUCCESS = "#2ECC71"      # Green for success status
COLOR_WARNING = "#E67E22"      # Orange for warning/info status
COLOR_DANGER = "#E74C3C"       # Red for quit/delete buttons

# Font Configurations
FONT_HEADER = ("Segoe UI", 16, "bold")
FONT_SUBHEADER = ("Segoe UI", 11, "bold")
FONT_TITLE = ("Segoe UI", 12, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_MUTED = ("Segoe UI", 9, "italic")
FONT_BUTTON = ("Segoe UI", 10, "bold")
