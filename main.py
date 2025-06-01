import pygame
import sys
import threading
from grid import Grid
from wall_generator import WallGenerator
from pathfinder import Pathfinder
from constants import *

class PathfindingVisualizer:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Dijkstra's Algorithm Visualizer")
        self.clock = pygame.time.Clock()
        self.grid = Grid()
        self.state = "WAITING_START"  # States: WAITING_START, WAITING_END, READY, PATHFINDING, PAUSED
        self.wall_type = "maze"
        self.speed = 0.01  # Normal speed
        self.drawing_walls = False
        self.erasing_walls = False
        self.font = pygame.font.SysFont('arial', 16)
        self.title_font = pygame.font.SysFont('arial', 20, bold=True)
        self.last_path_length = 0
        
        # Enhanced state management
        self.pathfinding_thread = None
        self.pathfinding_active = False
        self.pathfinding_paused = False
        self.pathfinding_completed = False
        self.path_found = False
        self.quit_requested = False
        
        # Thread synchronization
        self.pathfinding_lock = threading.Lock()
        
        # UI optimization
        self.button_positions = {}
        self.ui_needs_redraw = True

    def is_pathfinding_in_progress(self):
        """Check if pathfinding is currently active"""
        return self.pathfinding_active and not self.pathfinding_completed

    def can_interact_with_grid(self):
        """Check if user can interact with the grid"""
        return not self.is_pathfinding_in_progress()

    def can_start_pathfinding(self):
        """Check if pathfinding can be started"""
        return (self.state == "READY" and 
                self.grid.start_node and 
                self.grid.end_node and 
                not self.is_pathfinding_in_progress())

    def draw_ui(self):
        """Draw the user interface panel with accurate state information"""
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
            "• Space: Find/Pause path",
            "• C: Clear path",
            "• R: Reset all"
        ]

        for instruction in instructions:
            text = self.font.render(instruction, True, BLACK)
            self.window.blit(text, (GRID_COLS * CELL_SIZE + 20, y_offset))
            y_offset += 20

        y_offset += 20

        # Store button positions for click detection
        self.button_positions = {}
        button_x = GRID_COLS * CELL_SIZE + BUTTON_MARGIN

        # Generate wall button
        wall_enabled = self.can_interact_with_grid()
        wall_color = GRAY if wall_enabled else DARK_GRAY
        wall_button = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['generate_wall'] = (wall_button, wall_enabled)
        pygame.draw.rect(self.window, wall_color, wall_button)
        pygame.draw.rect(self.window, BLACK, wall_button, 2)
        wall_text = self.font.render("Generate Walls", True, WHITE if wall_enabled else LIGHT_GRAY)
        text_rect = wall_text.get_rect(center=wall_button.center)
        self.window.blit(wall_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN

        # Wall type selection
        wall_types = ["Maze", "Random"]
        wall_type_keys = ['maze', 'random']
        self.button_positions['wall_types'] = []
        for i, wtype in enumerate(wall_types):
            type_enabled = self.can_interact_with_grid()
            if type_enabled and self.wall_type == wall_type_keys[i]:
                color = BLUE
            elif type_enabled:
                color = GRAY
            else:
                color = DARK_GRAY
            
            type_button = pygame.Rect(button_x + i * 55, y_offset, 50, 30)
            self.button_positions['wall_types'].append((type_button, wall_type_keys[i], type_enabled))
            pygame.draw.rect(self.window, color, type_button)
            pygame.draw.rect(self.window, BLACK, type_button, 1)
            text_color = WHITE if type_enabled else LIGHT_GRAY
            type_text = pygame.font.SysFont('arial', 12).render(wtype, True, text_color)
            text_rect = type_text.get_rect(center=type_button.center)
            self.window.blit(type_text, text_rect)
        y_offset += 40

        # Find Path / Pause button
        if self.is_pathfinding_in_progress():
            if self.pathfinding_paused:
                path_color = ORANGE
                path_text_str = "Resume Path Finding"
            else:
                path_color = RED
                path_text_str = "Pause Path Finding"
            path_enabled = True
        elif self.can_start_pathfinding():
            path_color = GREEN
            path_text_str = "Find Shortest Path"
            path_enabled = True
        else:
            path_color = DARK_GRAY
            path_text_str = "Find Shortest Path"
            path_enabled = False

        path_button = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['find_path'] = (path_button, path_enabled)
        pygame.draw.rect(self.window, path_color, path_button)
        pygame.draw.rect(self.window, BLACK, path_button, 2)
        text_color = WHITE if path_enabled else LIGHT_GRAY
        path_text = self.font.render(path_text_str, True, text_color)
        text_rect = path_text.get_rect(center=path_button.center)
        self.window.blit(path_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN

        # Speed controls
        speed_text = self.font.render("Animation Speed:", True, BLACK)
        self.window.blit(speed_text, (button_x, y_offset))
        y_offset += 25

        speeds = [("Fast", FAST_SPEED), ("Normal", NORMAL_SPEED), ("Slow", SLOW_SPEED)]
        self.button_positions['speeds'] = []
        speed_enabled = not self.is_pathfinding_in_progress()
        for i, (name, spd) in enumerate(speeds):
            if speed_enabled and abs(self.speed - spd) < 0.001:
                color = BLUE
            elif speed_enabled:
                color = GRAY
            else:
                color = DARK_GRAY
                
            speed_button = pygame.Rect(button_x + i * 55, y_offset, 50, 30)
            self.button_positions['speeds'].append((speed_button, spd, speed_enabled))
            pygame.draw.rect(self.window, color, speed_button)
            pygame.draw.rect(self.window, BLACK, speed_button, 1)
            text_color = WHITE if speed_enabled else LIGHT_GRAY
            speed_label = pygame.font.SysFont('arial', 12).render(name, True, text_color)
            text_rect = speed_label.get_rect(center=speed_button.center)
            self.window.blit(speed_label, text_rect)
        y_offset += 40

        # Clear buttons
        clear_enabled = self.can_interact_with_grid()
        
        # Clear Path button
        clear_path_color = YELLOW if clear_enabled else DARK_GRAY
        clear_path_button = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['clear_path'] = (clear_path_button, clear_enabled)
        pygame.draw.rect(self.window, clear_path_color, clear_path_button)
        pygame.draw.rect(self.window, BLACK, clear_path_button, 2)
        text_color = BLACK if clear_enabled else LIGHT_GRAY
        clear_path_text = self.font.render("Clear Path", True, text_color)
        text_rect = clear_path_text.get_rect(center=clear_path_button.center)
        self.window.blit(clear_path_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN

        # Clear All button
        clear_all_color = RED if clear_enabled else DARK_GRAY
        clear_all_button = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['clear_all'] = (clear_all_button, clear_enabled)
        pygame.draw.rect(self.window, clear_all_color, clear_all_button)
        pygame.draw.rect(self.window, BLACK, clear_all_button, 2)
        text_color = WHITE if clear_enabled else LIGHT_GRAY
        clear_all_text = self.font.render("Clear All", True, text_color)
        text_rect = clear_all_text.get_rect(center=clear_all_button.center)
        self.window.blit(clear_all_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN * 2

        # Status and stats
        if self.last_path_length > 0:
            path_info = self.font.render(f"Path Length: {self.last_path_length}", True, BLACK)
            self.window.blit(path_info, (button_x, y_offset))
            y_offset += 25

        # Current state with more detailed information
        state_text = {
            "WAITING_START": "Click to set START point",
            "WAITING_END": "Click to set END point", 
            "READY": "Ready to find path!",
            "PATHFINDING": "Finding path..." if not self.pathfinding_paused else "Path finding PAUSED",
            "PAUSED": "Path finding PAUSED"
        }
        
        status_color = BLACK
        if self.is_pathfinding_in_progress():
            if self.pathfinding_paused:
                status_color = ORANGE
            else:
                status_color = BLUE
        elif self.state == "READY":
            status_color = GREEN

        status = self.font.render(state_text.get(self.state, ""), True, status_color)
        self.window.blit(status, (button_x, y_offset))

    def handle_click(self, pos, button):
        """Handle mouse clicks with proper state validation"""
        x, y = pos

        # Check UI button clicks using stored positions
        if x >= GRID_COLS * CELL_SIZE and hasattr(self, 'button_positions'):
            try:
                # Generate Wall button
                wall_button, wall_enabled = self.button_positions['generate_wall']
                if wall_button.collidepoint(x, y) and wall_enabled:
                    self.generate_walls()
                    return

                # Wall type buttons
                for type_button, wall_key, type_enabled in self.button_positions['wall_types']:
                    if type_button.collidepoint(x, y) and type_enabled:
                        self.wall_type = wall_key
                        return

                # Find Path button
                path_button, path_enabled = self.button_positions['find_path']
                if path_button.collidepoint(x, y) and path_enabled:
                    if self.is_pathfinding_in_progress():
                        self.toggle_pause_pathfinding()
                    elif self.can_start_pathfinding():
                        self.start_pathfinding()
                    return

                # Speed buttons
                for speed_button, speed_val, speed_enabled in self.button_positions['speeds']:
                    if speed_button.collidepoint(x, y) and speed_enabled:
                        self.speed = speed_val
                        return

                # Clear Path button
                clear_path_button, clear_enabled = self.button_positions['clear_path']
                if clear_path_button.collidepoint(x, y) and clear_enabled:
                    self.clear_path()
                    return

                # Clear All button
                clear_all_button, clear_all_enabled = self.button_positions['clear_all']
                if clear_all_button.collidepoint(x, y) and clear_all_enabled:
                    self.clear_all()
                    return
            except (KeyError, ValueError):
                # Handle cases where button positions might not be properly initialized
                pass

        # Handle grid clicks only if interaction is allowed
        if not self.can_interact_with_grid():
            return

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
        if not self.can_interact_with_grid():
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

    def generate_walls(self):
        """Generate walls with proper state management"""
        if not self.can_interact_with_grid():
            return
            
        WallGenerator.generate_wall(self.grid, self.wall_type)
        self.grid.start_node = None
        self.grid.end_node = None
        self.state = "WAITING_START"
        self.last_path_length = 0

    def clear_path(self):
        """Clear only the pathfinding visualization, keeping walls and start/end"""
        if not self.can_interact_with_grid():
            return
            
        for row in self.grid.grid:
            for node in row:
                if not node.is_wall and node != self.grid.start_node and node != self.grid.end_node:
                    node.reset()
        self.last_path_length = 0

    def clear_all(self):
        """Clear everything including walls"""
        if not self.can_interact_with_grid():
            return
            
        for row in self.grid.grid:
            for node in row:
                node.reset()
        self.grid.start_node = None
        self.grid.end_node = None
        self.state = "WAITING_START"
        self.last_path_length = 0

    def start_pathfinding(self):
        """Start pathfinding in a separate thread"""
        if not self.can_start_pathfinding():
            return

        with self.pathfinding_lock:
            self.pathfinding_active = True
            self.pathfinding_paused = False
            self.pathfinding_completed = False
            self.state = "PATHFINDING"

        self.clear_path()  # Clear previous path visualization
        
        # Start pathfinding in a separate thread
        self.pathfinding_thread = threading.Thread(target=self._run_pathfinding_thread)
        self.pathfinding_thread.daemon = True
        self.pathfinding_thread.start()

    def toggle_pause_pathfinding(self):
        """Toggle pause state of pathfinding"""
        if not self.is_pathfinding_in_progress():
            return
            
        with self.pathfinding_lock:
            self.pathfinding_paused = not self.pathfinding_paused

    def stop_pathfinding(self):
        """Stop pathfinding gracefully"""
        with self.pathfinding_lock:
            self.pathfinding_active = False
            self.pathfinding_completed = True
            
        # Wait for thread to finish
        if self.pathfinding_thread and self.pathfinding_thread.is_alive():
            self.pathfinding_thread.join(timeout=1.0)

    def _run_pathfinding_thread(self):
        """Run Dijkstra's algorithm in a separate thread"""
        try:
            if not self.grid.start_node or not self.grid.end_node:
                return

            # Run Dijkstra's algorithm with pause support
            path_found = Pathfinder.dijkstra_with_pause(
                self.grid, 
                self.grid.start_node, 
                self.grid.end_node,
                None,  # Don't pass window to avoid threading conflicts
                self.speed,
                self._should_pause,
                self._should_stop
            )

            # Check if we should stop before reconstructing path
            if self._should_stop():
                return

            if path_found:
                # Reconstruct and visualize the path
                self.last_path_length = Pathfinder.reconstruct_path_with_pause(
                    self.grid.end_node, 
                    None,  # Don't pass window to avoid threading conflicts
                    None,  # Don't pass grid to avoid threading conflicts
                    self.speed,
                    self._should_pause,
                    self._should_stop
                )
                self.path_found = True
            else:
                self.last_path_length = 0
                self.path_found = False

        except Exception as e:
            print(f"Error in pathfinding thread: {e}")
        finally:
            with self.pathfinding_lock:
                self.pathfinding_completed = True
                self.pathfinding_active = False
                if not self.quit_requested:
                    self.state = "READY"

    def _should_pause(self):
        """Check if pathfinding should pause"""
        return self.pathfinding_paused

    def _should_stop(self):
        """Check if pathfinding should stop completely"""
        return self.quit_requested or not self.pathfinding_active

    def handle_quit(self):
        """Handle application quit with proper cleanup"""
        self.quit_requested = True
        
        # Stop pathfinding if active
        if self.is_pathfinding_in_progress():
            self.stop_pathfinding()
        
        pygame.quit()
        sys.exit()

    def run(self):
        """Main game loop with improved error handling and optimized rendering"""
        running = True
        
        try:
            while running and not self.quit_requested:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        try:
                            self.handle_click(pygame.mouse.get_pos(), event.button)
                        except Exception as e:
                            print(f"Error handling mouse click: {e}")

                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.drawing_walls = False
                        self.erasing_walls = False

                    elif event.type == pygame.MOUSEMOTION:
                        if pygame.mouse.get_pressed()[2]:  # Right mouse button held
                            try:
                                self.handle_drag(pygame.mouse.get_pos())
                            except Exception as e:
                                print(f"Error handling mouse drag: {e}")

                    elif event.type == pygame.KEYDOWN:
                        try:
                            if event.key == pygame.K_SPACE:
                                if self.is_pathfinding_in_progress():
                                    self.toggle_pause_pathfinding()
                                elif self.can_start_pathfinding():
                                    self.start_pathfinding()
                            elif event.key == pygame.K_c and self.can_interact_with_grid():
                                self.clear_path()
                            elif event.key == pygame.K_r and self.can_interact_with_grid():
                                self.clear_all()
                        except Exception as e:
                            print(f"Error handling keyboard input: {e}")

                # Draw everything - only main thread updates display
                try:
                    self.window.fill(WHITE)
                    self.grid.draw(self.window)
                    self.draw_ui()
                    pygame.display.flip()
                    self.clock.tick(60)  # 60 FPS for smooth UI
                except Exception as e:
                    print(f"Error in drawing: {e}")

        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self.handle_quit()

if __name__ == "__main__":
    try:
        app = PathfindingVisualizer()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        pygame.quit()
        sys.exit()