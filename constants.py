"""
This file defines global constants used throughout the pathfinding visualizer application.
It centralizes configuration settings like window dimensions, grid cell size,
color palette, button sizes, and animation speeds, making them easy to
manage and adjust.
"""

# Window settings
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 720
CELL_SIZE = 12  # Slightly larger for better visibility

# Calculate grid dimensions after CELL_SIZE is defined
GRID_ROWS = WINDOW_HEIGHT // CELL_SIZE
GRID_COLS = (WINDOW_WIDTH - 250) // CELL_SIZE  # Wider button panel for more features

# Modern Dark Theme
# Background and UI
BG_DARK = (60, 64, 72)             # Dark background
BG_LIGHT = (40, 42, 50)            # Lighter UI elements
TEXT_PRIMARY = (240, 240, 245)     # Primary text
TEXT_SECONDARY = (180, 180, 190)   # Secondary text
ACCENT = (100, 120, 255)           # Primary accent color

# Grid and Walls
GRID_LINE = (40, 42, 50)           # Grid lines
WALL = (18, 18, 24)                # Wall color

# Pathfinding Elements
NODE_START = (255, 85, 114)        # Start node
NODE_END = (46, 213, 115)          # End node
NODE_VISITED = (33, 150, 243)      # Visited nodes
NODE_PATH = (255, 193, 7)          # Path nodes
NODE_CURRENT = (187, 134, 252)     # Current node
NODE_NEIGHBOR = (77, 208, 225)     # Neighbor nodes
NODE_DEFAULT = (30, 32, 40)        # Default node color

# UI Elements
BUTTON_NORMAL = (60, 64, 72)       # Normal button (darker gray)
BUTTON_HOVER = (80, 84, 92)        # Button hover state (slightly lighter)
BUTTON_ACTIVE = (0, 150, 255)      # Button active state (bright blue)
BUTTON_DISABLED = (40, 42, 48)     # Disabled button (darker gray)

# Status Colors
STATUS_SUCCESS = (76, 175, 80)     # Success/Completed
STATUS_WARNING = (255, 193, 7)     # Warning/Paused
STATUS_ERROR = (244, 67, 54)       # Error/Stopped

# Button dimensions
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 45
SMALL_BUTTON_WIDTH = 60
SMALL_BUTTON_HEIGHT = 35
BUTTON_MARGIN = 12

# Animation speeds
INSTANT_SPEED = 0
FAST_SPEED = 0.002
NORMAL_SPEED = 0.01
SLOW_SPEED = 0.05