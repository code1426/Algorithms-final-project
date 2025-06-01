# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
CELL_SIZE = 12  # Slightly larger for better visibility
GRID_ROWS = WINDOW_HEIGHT // CELL_SIZE
GRID_COLS = (WINDOW_WIDTH - 300) // CELL_SIZE  # Wider button panel for more features

# Colors - Enhanced palette
WHITE = (255, 255, 255)
BLACK = (70, 70, 70)
RED = (220, 20, 60)  # Crimson red for start
GREEN = (34, 139, 34)  # Forest green for end
BLUE = (30, 144, 255)  # Dodger blue for visited
YELLOW = (255, 215, 0)  # Gold for path
PURPLE = (138, 43, 226)  # Blue violet for current
GRAY = (105, 105, 105)  # Dim gray for walls
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (211, 211, 211)
CYAN = (0, 191, 255)  # Deep sky blue for neighbors
ORANGE = (255, 140, 0)  # Dark orange for special effects
PINK = (255, 20, 147)  # Deep pink for highlights

# Button dimensions
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 45
SMALL_BUTTON_WIDTH = 60
SMALL_BUTTON_HEIGHT = 35
BUTTON_MARGIN = 12

# Animation speeds
FAST_SPEED = 0.001
NORMAL_SPEED = 0.01
SLOW_SPEED = 0.05