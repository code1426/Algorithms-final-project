import pygame
import sys
from grid import Grid
from maze_generator import MazeGenerator
from pathfinder import Pathfinder
from constants import *

class PathfindingVisualizer:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Dijkstra's Algorithm Visualizer")
        self.clock = pygame.time.Clock()
        self.grid = Grid()
        self.state = "WAITING_START"  # States: WAITING_START, WAITING_END, READY, PATHFINDING
        self.maze_type = "recursive_backtracker"
        self.speed = 0.01  # Normal speed
        self.drawing_walls = False
        self.erasing_walls = False
        self.font = pygame.font.SysFont('arial', 16)
        self.title_font = pygame.font.SysFont('arial', 20, bold=True)
        self.last_path_length = 0

    def draw_ui(self):
        """Draw the user interface panel"""
        # Fill the UI panel background
        ui_panel = pygame.Rect(GRID_COLS * CELL_SIZE, 0, 
                              WINDOW_WIDTH - GRID_COLS * CELL_SIZE, WINDOW_HEIGHT)
        pygame.draw.rect(self.window, (200, 200, 200), ui_panel)

        y_offset = 20

        # Title
        title = self.title_font.render("Dijkstra's Algorithm", True, BLACK)
        self.window.blit(title, (GRID_COLS * CELL_SIZE + 20, y_offset))
        y_offset += 40

        # Instructions
        instructions = [
            "1. Click to set START point",
            "2. Click to set END point", 
            "3. Click 'Find Path' to run",
            "",
            "Controls:",
            "• Left click: Set points",
            "• Right click: Toggle walls",
            "• Hold and drag: Draw walls",
            "• Space: Find path",
            "• C: Clear path"
        ]

        for instruction in instructions:
            text = self.font.render(instruction, True, BLACK)
            self.window.blit(text, (GRID_COLS * CELL_SIZE + 20, y_offset))
            y_offset += 20

        y_offset += 20

        # Store button positions for click detection
        self.button_positions = {}
        button_x = GRID_COLS * CELL_SIZE + BUTTON_MARGIN

        # Generate Maze button
        maze_button = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['generate_maze'] = maze_button
        pygame.draw.rect(self.window, GRAY, maze_button)
        pygame.draw.rect(self.window, BLACK, maze_button, 2)
        maze_text = self.font.render("Generate Maze", True, WHITE)
        text_rect = maze_text.get_rect(center=maze_button.center)
        self.window.blit(maze_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN

        # Maze type selection
        maze_types = ["Recursive", "Prim's", "Random"]
        maze_type_keys = ['recursive_backtracker', 'prims', 'random']
        self.button_positions['maze_types'] = []
        for i, mtype in enumerate(maze_types):
            color = BLUE if self.maze_type == maze_type_keys[i] else GRAY
            type_button = pygame.Rect(button_x + i * 55, y_offset, 50, 30)
            self.button_positions['maze_types'].append((type_button, maze_type_keys[i]))
            pygame.draw.rect(self.window, color, type_button)
            pygame.draw.rect(self.window, BLACK, type_button, 1)
            type_text = pygame.font.SysFont('arial', 12).render(mtype, True, WHITE)
            text_rect = type_text.get_rect(center=type_button.center)
            self.window.blit(type_text, text_rect)
        y_offset += 40

        # Find Path button
        path_color = GREEN if self.state == "READY" else DARK_GRAY
        path_button = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['find_path'] = path_button
        pygame.draw.rect(self.window, path_color, path_button)
        pygame.draw.rect(self.window, BLACK, path_button, 2)
        path_text = self.font.render("Find Shortest Path", True, WHITE)
        text_rect = path_text.get_rect(center=path_button.center)
        self.window.blit(path_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN

        # Speed controls
        speed_text = self.font.render("Animation Speed:", True, BLACK)
        self.window.blit(speed_text, (button_x, y_offset))
        y_offset += 25

        speeds = [("Fast", 0.001), ("Normal", 0.01), ("Slow", 0.05)]
        self.button_positions['speeds'] = []
        for i, (name, spd) in enumerate(speeds):
            color = BLUE if abs(self.speed - spd) < 0.001 else GRAY
            speed_button = pygame.Rect(button_x + i * 55, y_offset, 50, 30)
            self.button_positions['speeds'].append((speed_button, spd))
            pygame.draw.rect(self.window, color, speed_button)
            pygame.draw.rect(self.window, BLACK, speed_button, 1)
            speed_label = pygame.font.SysFont('arial', 12).render(name, True, WHITE)
            text_rect = speed_label.get_rect(center=speed_button.center)
            self.window.blit(speed_label, text_rect)
        y_offset += 40

        # Clear buttons
        clear_path_button = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['clear_path'] = clear_path_button
        pygame.draw.rect(self.window, YELLOW, clear_path_button)
        pygame.draw.rect(self.window, BLACK, clear_path_button, 2)
        clear_path_text = self.font.render("Clear Path", True, BLACK)
        text_rect = clear_path_text.get_rect(center=clear_path_button.center)
        self.window.blit(clear_path_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN

        clear_all_button = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['clear_all'] = clear_all_button
        pygame.draw.rect(self.window, RED, clear_all_button)
        pygame.draw.rect(self.window, BLACK, clear_all_button, 2)
        clear_all_text = self.font.render("Clear All", True, WHITE)
        text_rect = clear_all_text.get_rect(center=clear_all_button.center)
        self.window.blit(clear_all_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN * 2

        # Status and stats
        if self.last_path_length > 0:
            path_info = self.font.render(f"Path Length: {self.last_path_length}", True, BLACK)
            self.window.blit(path_info, (button_x, y_offset))
            y_offset += 25

        # Current state
        state_text = {
            "WAITING_START": "Click to set START",
            "WAITING_END": "Click to set END", 
            "READY": "Ready to find path!",
            "PATHFINDING": "Finding path..."
        }
        status = self.font.render(state_text.get(self.state, ""), True, BLACK)
        self.window.blit(status, (button_x, y_offset))

    def handle_click(self, pos, button):
        """Handle mouse clicks"""
        if self.state == "PATHFINDING":
            return  # Ignore clicks during pathfinding

        x, y = pos

        # Check UI button clicks using stored positions
        if x >= GRID_COLS * CELL_SIZE and hasattr(self, 'button_positions'):
            # Generate Maze button
            if self.button_positions['generate_maze'].collidepoint(x, y):
                MazeGenerator.generate_maze(self.grid, self.maze_type)
                self.grid.start_node = None
                self.grid.end_node = None
                self.state = "WAITING_START"
                self.last_path_length = 0
                return

            # Maze type buttons
            for type_button, maze_key in self.button_positions['maze_types']:
                if type_button.collidepoint(x, y):
                    self.maze_type = maze_key
                    return

            # Find Path button
            if (self.button_positions['find_path'].collidepoint(x, y) and 
                self.state == "READY"):
                self.run_dijkstra()
                return

            # Speed buttons
            for speed_button, speed_val in self.button_positions['speeds']:
                if speed_button.collidepoint(x, y):
                    self.speed = speed_val
                    return

            # Clear Path button
            if self.button_positions['clear_path'].collidepoint(x, y):
                self.clear_path()
                return

            # Clear All button
            if self.button_positions['clear_all'].collidepoint(x, y):
                self.clear_all()
                return

        # Handle grid clicks
        row, col = self.grid.get_clicked_pos(pos)
        if row is None or col is None:
            return

        node = self.grid.get_node(row, col)
        if not node:
            return

        if button == 1:  # Left click - set start/end points
            if not node.is_wall:
                if self.state == "WAITING_START":
                    if self.grid.start_node:
                        self.grid.start_node.reset()
                    self.grid.start_node = node
                    node.make_start()
                    self.state = "WAITING_END"
                elif self.state == "WAITING_END":
                    if node != self.grid.start_node:
                        if self.grid.end_node:
                            self.grid.end_node.reset()
                        self.grid.end_node = node
                        node.make_end()
                        self.state = "READY"
        elif button == 3:  # Right click - toggle walls
            if node != self.grid.start_node and node != self.grid.end_node:
                if node.is_wall:
                    node.reset()
                    self.erasing_walls = True
                else:
                    node.make_wall()
                    self.drawing_walls = True

    def handle_drag(self, pos):
        """Handle mouse dragging for wall drawing"""
        if self.state == "PATHFINDING":
            return

        row, col = self.grid.get_clicked_pos(pos)
        if row is None or col is None:
            return

        node = self.grid.get_node(row, col)
        if not node or node == self.grid.start_node or node == self.grid.end_node:
            return

        if self.drawing_walls and not node.is_wall:
            node.make_wall()
        elif self.erasing_walls and node.is_wall:
            node.reset()

    def clear_path(self):
        """Clear only the pathfinding visualization, keeping walls and start/end"""
        for row in self.grid.grid:
            for node in row:
                if not node.is_wall and node != self.grid.start_node and node != self.grid.end_node:
                    node.reset()
        self.last_path_length = 0

    def clear_all(self):
        """Clear everything including walls"""
        for row in self.grid.grid:
            for node in row:
                node.reset()
        self.grid.start_node = None
        self.grid.end_node = None
        self.state = "WAITING_START"
        self.last_path_length = 0

    def run_dijkstra(self):
        """Run Dijkstra's algorithm with visualization"""
        if not self.grid.start_node or not self.grid.end_node:
            return

        self.state = "PATHFINDING"
        self.clear_path()  # Clear previous path visualization

        # Run Dijkstra's algorithm
        path_found = Pathfinder.dijkstra(
            self.grid, 
            self.grid.start_node, 
            self.grid.end_node,
            self.window, 
            self.speed
        )

        if path_found:
            # Reconstruct and visualize the path
            self.last_path_length = Pathfinder.reconstruct_path(
                self.grid.end_node, 
                self.window, 
                self.grid, 
                self.speed
            )
        else:
            self.last_path_length = 0

        self.state = "READY"

    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos(), event.button)

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.drawing_walls = False
                    self.erasing_walls = False

                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[2]:  # Right mouse button held
                        self.handle_drag(pygame.mouse.get_pos())

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == "READY":
                        self.run_dijkstra()
                    elif event.key == pygame.K_c:
                        self.clear_path()
                    elif event.key == pygame.K_r:
                        self.clear_all()

            # Draw everything
            self.window.fill(WHITE)
            self.grid.draw(self.window)
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PathfindingVisualizer()
    app.run()