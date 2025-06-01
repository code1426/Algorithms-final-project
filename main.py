"""
This is the main application file for the Dijkstra's Algorithm Visualizer.
It initializes Pygame, sets up the main window, manages the application's
state, draws the user interface, handles all user input (mouse and keyboard),
and orchestrates the interaction between the `Grid`, `Pathfinder`, and
`WallGenerator` components. It also implements threading for non-blocking
pathfinding visualization.
"""

import pygame
import sys
import threading
from grid import Grid
from wall_generator import WallGenerator
from pathfinder import Pathfinder
from constants import * # Import all constants for configuration and colors
from typing import Tuple

class PathfindingVisualizer:
    """
    The main class for the Pathfinding Visualizer application.
    It encapsulates the entire application logic, including:
    - Pygame initialization and window management.
    - The main game loop and event handling.
    - Drawing the grid and the user interface.
    - Managing application states (e.g., setting start/end, pathfinding).
    - Coordinating with `Grid`, `Pathfinder`, and `WallGenerator` classes.
    - Handling pathfinding in a separate thread for responsiveness.
    """
    def __init__(self):
        """
        Initializes the Pygame environment and all components of the visualizer.
        Sets up the display window, game clock, grid, and initial application state.
        """
        pygame.init() # Initializes all Pygame modules.
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # Creates the display surface.
        pygame.display.set_caption("Dijkstra's Algorithm Visualizer") # Sets the window title.
        self.clock = pygame.time.Clock() # Used to control the frame rate.
        self.grid = Grid() # Instantiates the `Grid` object to manage nodes.
        self.state = "WAITING_START"  # Current application state:
                                      #   "WAITING_START": User needs to set the start node.
                                      #   "WAITING_END": User needs to set the end node.
                                      #   "READY": Start and end nodes are set; ready to run algorithm.
                                      #   "PATHFINDING": Algorithm is actively running.
                                      #   "PAUSED": Algorithm is paused.
        self.wall_type = "maze"       # Default wall generation type ('maze' or 'random').
        self.speed = NORMAL_SPEED     # Current animation speed (from `constants.py`).
        self.drawing_walls = False    # Flag to enable continuous wall drawing via right-click drag.
        self.erasing_walls = False    # Flag to enable continuous wall erasing via right-click drag.
        self.font = pygame.font.SysFont('arial', 16) # Font for general UI text.
        self.title_font = pygame.font.SysFont('arial', 20, bold=True) # Font for the main title.
        self.last_path_length = 0     # Stores the length of the shortest path found.

        # --- Threading and State Management for Pathfinding ---
        self.pathfinding_thread: threading.Thread = None # Reference to the thread running pathfinding.
        self.pathfinding_active = False     # `True` if pathfinding is running or paused.
        self.pathfinding_paused = False     # `True` if pathfinding is currently paused.
        self.pathfinding_completed = False  # `True` if pathfinding has finished (found path or no path).
        self.path_found = False             # `True` if Dijkstra's successfully found a path.
        self.quit_requested = False         # Flag to signal all threads to gracefully shut down.

        # `threading.Lock` for thread-safe access to shared state variables.
        # This prevents race conditions when the main thread and pathfinding thread
        # both try to modify shared flags (e.g., `pathfinding_paused`).
        self.pathfinding_lock = threading.Lock()

        # `button_positions` stores `pygame.Rect` objects and enabled states for UI buttons.
        # This allows efficient collision detection for mouse clicks on UI elements.
        self.button_positions = {}
        self.ui_needs_redraw = True # Optimization flag (can be used for selective UI redrawing).

    def is_pathfinding_in_progress(self) -> bool:
        """
        Checks if the pathfinding algorithm is currently active (running or paused).

        Returns:
            `bool`: `True` if pathfinding is active and not completed, `False` otherwise.
        """
        return self.pathfinding_active and not self.pathfinding_completed

    def can_interact_with_grid(self) -> bool:
        """
        Determines if the user is allowed to interact with the grid (e.g., set walls,
        clear grid). Grid interaction is typically disabled while pathfinding
        is actively running to prevent interference.

        Returns:
            `bool`: `True` if grid interaction is permitted, `False` otherwise.
        """
        return not self.is_pathfinding_in_progress()

    def can_start_pathfinding(self) -> bool:
        """
        Checks if all conditions are met to initiate the pathfinding algorithm.
        Requires both a start and an end node to be set, and no pathfinding
        should currently be in progress.

        Returns:
            `bool`: `True` if pathfinding can be started, `False` otherwise.
        """
        return (self.state == "READY" and
                self.grid.start_node is not None and # Ensure start node is set.
                self.grid.end_node is not None and   # Ensure end node is set.
                not self.is_pathfinding_in_progress())

    def draw_ui(self) -> None:
        """
        Draws the entire user interface panel on the right side of the window.
        This includes the application title, instructions, various control buttons
        (wall generation, pathfinding controls, speed selection, clear options),
        and a status display. Button colors and text reflect their current state
        (enabled, disabled, active).
        """
        # Define the rectangular area for the UI panel.
        ui_panel = pygame.Rect(GRID_COLS * CELL_SIZE, 0,
                               WINDOW_WIDTH - GRID_COLS * CELL_SIZE, WINDOW_HEIGHT)
        pygame.draw.rect(self.window, BG_LIGHT, ui_panel) # Draw the UI panel background

        y_offset = 20 # Initial vertical offset for placing UI elements.

        # --- Application Title ---
        title = self.title_font.render("Dijkstra's Algorithm", True, TEXT_PRIMARY)
        self.window.blit(title, (GRID_COLS * CELL_SIZE + 20, y_offset))
        y_offset += 40 # Move down for next element.

        # --- Instructions ---
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

        for instruction_text in instructions:
            text_surface = self.font.render(instruction_text, True, TEXT_SECONDARY)
            self.window.blit(text_surface, (GRID_COLS * CELL_SIZE + 20, y_offset))
            y_offset += 20 # Move down for the next line of instruction.

        y_offset += 20 # Add extra spacing before buttons.

        # Store button positions and their enabled states for efficient click detection.
        self.button_positions = {}
        button_x = GRID_COLS * CELL_SIZE + BUTTON_MARGIN # X-coordinate for button alignment.

        # --- "Generate Walls" Button ---
        wall_enabled = self.can_interact_with_grid() # Button is enabled if grid interaction is allowed.
        wall_color = BUTTON_NORMAL if wall_enabled else BUTTON_DISABLED # Color changes based on enabled state.
        wall_button_rect = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['generate_wall'] = (wall_button_rect, wall_enabled) # Store rect and state.
        pygame.draw.rect(self.window, wall_color, wall_button_rect) # Draw button background.
        pygame.draw.rect(self.window, ACCENT if wall_enabled else BG_DARK, wall_button_rect, 2) # Draw button border.
        wall_text = self.font.render("Generate Walls", True, TEXT_PRIMARY if wall_enabled else TEXT_SECONDARY)
        text_rect = wall_text.get_rect(center=wall_button_rect.center) # Center text on button.
        self.window.blit(wall_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN # Update offset for next button.

        # --- Wall Type Selection (Maze / Random) Buttons ---
        wall_types = ["Maze", "Random"]
        wall_type_keys = ['maze', 'random']
        self.button_positions['wall_types'] = []
        for i, wtype_name in enumerate(wall_types):
            # Highlight the currently selected wall type.
            if wall_enabled and self.wall_type == wall_type_keys[i]:
                color = BUTTON_ACTIVE
            elif wall_enabled:
                color = BUTTON_NORMAL
            else:
                color = BUTTON_DISABLED

            type_button_rect = pygame.Rect(button_x + i * 55, y_offset, 50, 30) # Small buttons.
            self.button_positions['wall_types'].append((type_button_rect, wall_type_keys[i], wall_enabled))
            pygame.draw.rect(self.window, color, type_button_rect)
            pygame.draw.rect(self.window, BG_DARK, type_button_rect, 1)
            text_color = TEXT_PRIMARY if wall_enabled else TEXT_SECONDARY
            type_text = pygame.font.SysFont('arial', 12).render(wtype_name, True, text_color)
            text_rect = type_text.get_rect(center=type_button_rect.center)
            self.window.blit(type_text, text_rect)
        y_offset += 40 # Update offset.

        # --- "Find Path" / "Pause" / "Resume" Button ---
        path_text_str = "" # Text displayed on the button.
        path_color = BUTTON_DISABLED # Default disabled color.
        path_enabled = False

        if self.is_pathfinding_in_progress():
            if self.pathfinding_paused:
                path_color = STATUS_WARNING # Warning color when paused.
                path_text_str = "Resume Path Finding"
            else:
                path_color = STATUS_ERROR # Error color when actively finding path.
                path_text_str = "Pause Path Finding"
            path_enabled = True # Always enabled when pathfinding is active.
        elif self.can_start_pathfinding():
            path_color = STATUS_SUCCESS # Success color when ready to start.
            path_text_str = "Find Shortest Path"
            path_enabled = True
        else:
            path_color = BUTTON_DISABLED # Disabled state.
            path_text_str = "Find Shortest Path"
            path_enabled = False

        path_button_rect = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['find_path'] = (path_button_rect, path_enabled)
        pygame.draw.rect(self.window, path_color, path_button_rect)
        pygame.draw.rect(self.window, ACCENT if path_enabled else BG_DARK, path_button_rect, 2)
        text_color = TEXT_PRIMARY if path_enabled else TEXT_SECONDARY
        path_text = self.font.render(path_text_str, True, text_color)
        text_rect = path_text.get_rect(center=path_button_rect.center)
        self.window.blit(path_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN

        # --- Speed Control Buttons ---
        speed_text_surface = self.font.render("Animation Speed:", True, TEXT_PRIMARY)
        self.window.blit(speed_text_surface, (button_x, y_offset))
        y_offset += 25

        speeds = [("Fast", FAST_SPEED), ("Normal", NORMAL_SPEED), ("Slow", SLOW_SPEED)]
        self.button_positions['speeds'] = []
        speed_enabled = not self.is_pathfinding_in_progress() # Speed can only be changed when not pathfinding.
        for i, (name, spd) in enumerate(speeds):
            # Highlight currently selected speed button.
            if speed_enabled and abs(self.speed - spd) < 0.001: # Use small delta for float comparison.
                color = BUTTON_ACTIVE
            elif speed_enabled:
                color = BUTTON_NORMAL
            else:
                color = BUTTON_DISABLED

            speed_button_rect = pygame.Rect(button_x + i * 55, y_offset, 50, 30)
            self.button_positions['speeds'].append((speed_button_rect, spd, speed_enabled))
            pygame.draw.rect(self.window, color, speed_button_rect)
            pygame.draw.rect(self.window, BG_DARK, speed_button_rect, 1)
            text_color = TEXT_PRIMARY if speed_enabled else TEXT_SECONDARY
            speed_label = pygame.font.SysFont('arial', 12).render(name, True, text_color)
            text_rect = speed_label.get_rect(center=speed_button_rect.center)
            self.window.blit(speed_label, text_rect)
        y_offset += 40

        # --- Clear Buttons ---
        clear_enabled = self.can_interact_with_grid() # Clear buttons are enabled if grid interaction is allowed.

        # "Clear Path" Button
        clear_path_color = STATUS_WARNING if clear_enabled else BUTTON_DISABLED
        clear_path_button_rect = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['clear_path'] = (clear_path_button_rect, clear_enabled)
        pygame.draw.rect(self.window, clear_path_color, clear_path_button_rect)
        pygame.draw.rect(self.window, ACCENT if clear_enabled else BG_DARK, clear_path_button_rect, 2)
        text_color = BG_LIGHT if clear_enabled else TEXT_SECONDARY # Light text on warning button for contrast.
        clear_path_text = self.font.render("Clear Path", True, text_color)
        text_rect = clear_path_text.get_rect(center=clear_path_button_rect.center)
        self.window.blit(clear_path_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN

        # "Clear All" Button
        clear_all_color = STATUS_ERROR if clear_enabled else BUTTON_DISABLED
        clear_all_button_rect = pygame.Rect(button_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_positions['clear_all'] = (clear_all_button_rect, clear_enabled)
        pygame.draw.rect(self.window, clear_all_color, clear_all_button_rect)
        pygame.draw.rect(self.window, ACCENT if clear_enabled else BG_DARK, clear_all_button_rect, 2)
        text_color = TEXT_PRIMARY if clear_enabled else TEXT_SECONDARY
        clear_all_text = self.font.render("Clear All", True, text_color)
        text_rect = clear_all_text.get_rect(center=clear_all_button_rect.center)
        self.window.blit(clear_all_text, text_rect)
        y_offset += BUTTON_HEIGHT + BUTTON_MARGIN * 2

        # --- Status and Path Length Display ---
        if self.last_path_length > 0:
            path_info = self.font.render(f"Path Length: {self.last_path_length}", True, TEXT_PRIMARY)
            self.window.blit(path_info, (button_x, y_offset))
            y_offset += 25

        # Detailed status message based on current application state.
        state_messages = {
            "WAITING_START": "Click to set START point",
            "WAITING_END": "Click to set END point",
            "READY": "Ready to find path!",
            "PATHFINDING": "Finding path..." if not self.pathfinding_paused else "Path finding PAUSED",
            "PAUSED": "Path finding PAUSED" # Explicitly handled, though covered by PATHFINDING.
        }

        status_color = TEXT_PRIMARY # Default status text color.
        if self.is_pathfinding_in_progress():
            status_color = STATUS_WARNING if self.pathfinding_paused else STATUS_SUCCESS
        elif self.state == "READY":
            status_color = STATUS_SUCCESS

        status_text_surface = self.font.render(state_messages.get(self.state, ""), True, status_color)
        self.window.blit(status_text_surface, (button_x, y_offset))

    def handle_click(self, pos: Tuple[int, int], button: int) -> None:
        """
        Processes mouse click events. Determines if a UI button was clicked
        or if the interaction was with the grid (setting start/end nodes,
        toggling walls).

        Args:
            `pos` (Tuple[int, int]): The (x, y) pixel coordinates of the mouse click.
            `button` (int): The mouse button clicked (1 for left, 3 for right).
        """
        x, y = pos

        # Check for UI button clicks first.
        # This prevents accidental grid interaction when clicking UI elements.
        if x >= GRID_COLS * CELL_SIZE and hasattr(self, 'button_positions'):
            try:
                # Check "Generate Walls" button.
                wall_button_rect, wall_enabled = self.button_positions['generate_wall']
                if wall_button_rect.collidepoint(x, y) and wall_enabled:
                    self.generate_walls()
                    return

                # Check "Wall Type" buttons.
                for type_button_rect, wall_key, type_enabled in self.button_positions['wall_types']:
                    if type_button_rect.collidepoint(x, y) and type_enabled:
                        self.wall_type = wall_key # Update selected wall type.
                        return

                # Check "Find Path" / "Pause" / "Resume" button.
                path_button_rect, path_enabled = self.button_positions['find_path']
                if path_button_rect.collidepoint(x, y) and path_enabled:
                    if self.is_pathfinding_in_progress():
                        self.toggle_pause_pathfinding()
                    elif self.can_start_pathfinding():
                        self.start_pathfinding()
                    return

                # Check "Speed" buttons.
                for speed_button_rect, speed_val, speed_enabled in self.button_positions['speeds']:
                    if speed_button_rect.collidepoint(x, y) and speed_enabled:
                        self.speed = speed_val # Update animation speed.
                        return

                # Check "Clear Path" button.
                clear_path_button_rect, clear_enabled = self.button_positions['clear_path']
                if clear_path_button_rect.collidepoint(x, y) and clear_enabled:
                    self.clear_path()
                    return

                # Check "Clear All" button.
                clear_all_button_rect, clear_all_enabled = self.button_positions['clear_all']
                if clear_all_button_rect.collidepoint(x, y) and clear_all_enabled:
                    self.clear_all()
                    return
            except (KeyError, ValueError):
                # Gracefully handle cases where button_positions might not be fully initialized
                # or unexpected values. This prevents crashes during rapid interaction.
                pass

        # Handle grid clicks only if interaction is currently allowed (i.e., not pathfinding).
        if not self.can_interact_with_grid():
            return

        row, col = self.grid.get_clicked_pos(pos) # Get grid coordinates from mouse position.
        if row is None or col is None: # Click was outside the valid grid area.
            return

        node = self.grid.get_node(row, col) # Get the specific `Node` object that was clicked.
        if node is None: # Should not happen if `get_clicked_pos` is accurate.
            return

        if button == 1:  # Left click: Used to set start/end points.
            if not node.is_wall: # Start/end nodes cannot be placed on walls.
                if self.state == "WAITING_START":
                    if self.grid.start_node: # If a start node already exists, reset its state.
                        self.grid.start_node.reset()
                    self.grid.start_node = node # Assign the clicked node as the start.
                    node.make_start()           # Visually mark it as the start node.
                    self.state = "WAITING_END"  # Transition to waiting for the end node.
                elif self.state == "WAITING_END":
                    if node != self.grid.start_node: # End node cannot be the same as the start node.
                        if self.grid.end_node: # If an end node already exists, reset its state.
                            self.grid.end_node.reset()
                        self.grid.end_node = node # Assign the clicked node as the end.
                        node.make_end()           # Visually mark it as the end node.
                        self.state = "READY"      # Transition to ready to find path.
        elif button == 3:  # Right click: Used to toggle walls.
            # Cannot make start/end nodes into walls.
            if node != self.grid.start_node and node != self.grid.end_node:
                if node.is_wall:
                    node.reset()       # If it's a wall, convert it back to a passage.
                    self.erasing_walls = True # Enable continuous erasing for dragging.
                else:
                    node.make_wall()   # If it's a passage, convert it into a wall.
                    self.drawing_walls = True # Enable continuous drawing for dragging.

    def handle_drag(self, pos: Tuple[int, int]) -> None:
        """
        Handles continuous mouse dragging events for drawing or erasing walls.
        This method is activated when the right mouse button is held down and
        the mouse is moved.

        Args:
            `pos` (Tuple[int, int]): The (x, y) pixel coordinates of the mouse during the drag.
        """
        if not self.can_interact_with_grid(): # Only allow interaction if not pathfinding.
            return

        row, col = self.grid.get_clicked_pos(pos)
        if row is None or col is None:
            return

        node = self.grid.get_node(row, col)
        # Prevent modifying start/end nodes.
        if node is None or node == self.grid.start_node or node == self.grid.end_node:
            return

        # Draw walls if `drawing_walls` flag is set and the node is not already a wall.
        if self.drawing_walls and not node.is_wall:
            node.make_wall()
        # Erase walls if `erasing_walls` flag is set and the node is currently a wall.
        elif self.erasing_walls and node.is_wall:
            node.reset()

    def generate_walls(self) -> None:
        """
        Initiates the wall generation process on the grid based on the
        currently selected `wall_type`. After generation, it resets the
        start/end nodes and path length display, preparing for a new pathfinding run.
        """
        if not self.can_interact_with_grid(): # Only allow generation if grid is interactive.
            return

        # The `generate_wall` method in `WallGenerator` clears the entire grid
        # before generating new walls.
        WallGenerator.generate_wall(self.grid, self.wall_type)
        self.grid.start_node = None # Clear start node reference as grid was reset.
        self.grid.end_node = None   # Clear end node reference.
        self.state = "WAITING_START" # Return to the state of setting a new start node.
        self.last_path_length = 0    # Reset path length display.

    def clear_path(self) -> None:
        """
        Clears only the visual elements of the pathfinding visualization (e.g.,
        blue visited nodes, yellow path nodes). Walls, the start node, and the
        end node remain in place. This is useful for re-running the algorithm
        on the same maze/grid configuration.
        """
        if not self.can_interact_with_grid():
            return

        self.grid.clear_path()      # Call grid method to perform the clearing.
        self.last_path_length = 0   # Reset path length display.

    def clear_all(self) -> None:
        """
        Resets the entire grid and application state to its initial blank condition.
        This removes all walls, start/end nodes, and pathfinding visualization.
        """
        if not self.can_interact_with_grid():
            return

        self.grid.clear_all()       # Call grid method to clear all nodes.
        self.state = "WAITING_START" # Reset state to begin setting up a new scenario.
        self.last_path_length = 0    # Reset path length display.

    def start_pathfinding(self) -> None:
        """
        Initiates Dijkstra's algorithm visualization in a separate thread.
        Sets necessary state flags, clears any previous path, and ensures
        the UI reflects the "pathfinding in progress" state.
        """
        if not self.can_start_pathfinding(): # Pre-check conditions for starting.
            return

        # Use a lock to ensure thread-safe updates to shared state variables.
        # This prevents the main thread from racing with the pathfinding thread.
        with self.pathfinding_lock:
            self.pathfinding_active = True
            self.pathfinding_paused = False
            self.pathfinding_completed = False
            self.state = "PATHFINDING" # Update application state.

        self.clear_path()  # Clear any previous path visualization before starting a new search.

        # Create and start a new `threading.Thread` for the pathfinding algorithm.
        # `daemon=True` ensures the thread will terminate when the main program exits.
        self.pathfinding_thread = threading.Thread(target=self._run_pathfinding_thread)
        self.pathfinding_thread.daemon = True
        self.pathfinding_thread.start()

    def toggle_pause_pathfinding(self) -> None:
        """
        Toggles the `pathfinding_paused` flag. The pathfinding thread
        periodically checks this flag to pause or resume its execution,
        providing user control over the animation.
        """
        if not self.is_pathfinding_in_progress(): # Only allow pausing if pathfinding is active.
            return

        with self.pathfinding_lock:
            self.pathfinding_paused = not self.pathfinding_paused # Invert the pause state.

    def stop_pathfinding(self) -> None:
        """
        Gracefully signals the pathfinding thread to stop its execution.
        This method sets flags that the thread checks, then waits briefly for the
        thread to terminate.
        """
        with self.pathfinding_lock:
            self.pathfinding_active = False    # Signal the thread to deactivate.
            self.pathfinding_completed = True  # Mark as completed (even if stopped prematurely).

        # Attempt to join the thread (wait for it to finish) with a timeout.
        # This ensures the main thread doesn't hang indefinitely if the pathfinding
        # thread gets stuck for some reason.
        if self.pathfinding_thread and self.pathfinding_thread.is_alive():
            self.pathfinding_thread.join(timeout=1.0) # Wait up to 1 second for thread to finish.

    def _run_pathfinding_thread(self) -> None:
        """
        The target function for the pathfinding thread.
        This method executes Dijkstra's algorithm and, if a path is found,
        reconstructs and visualizes it. It constantly checks `should_pause`
        and `should_stop` callbacks to respond to main thread signals.
        """
        try:
            if not self.grid.start_node or not self.grid.end_node:
                # This check acts as a safeguard, though `can_start_pathfinding()`
                # should ideally prevent this state.
                print("Error: Start or end node not set for pathfinding.")
                return

            # Call Dijkstra's algorithm, passing callback functions for pause and stop control.
            path_found = Pathfinder.dijkstra_with_pause(
                self.grid,
                self.grid.start_node,
                self.grid.end_node,
                self.speed,
                self._should_pause, # Callback to check if algorithm should pause.
                self._should_stop   # Callback to check if algorithm should stop completely.
            )

            # If a stop was requested during Dijkstra's execution, exit early.
            if self._should_stop():
                return

            if path_found:
                # If a path was found, reconstruct and visualize it.
                self.last_path_length = Pathfinder.reconstruct_path_with_pause(
                    self.grid.end_node,
                    self.speed,
                    self._should_pause, # Pause/stop checks apply to path reconstruction too.
                    self._should_stop
                )
                self.path_found = True # Set flag indicating a path was found.
            else:
                self.last_path_length = 0   # No path found, so length is 0.
                self.path_found = False     # Set flag to indicate no path.

        except Exception as e:
            # Catch any exceptions that occur within the pathfinding thread.
            print(f"Error in pathfinding thread: {e}")
        finally:
            # Ensure the pathfinding state flags are reset after completion or error.
            with self.pathfinding_lock:
                self.pathfinding_completed = True # Mark as completed.
                self.pathfinding_active = False   # Mark as inactive.
                # If the application is not quitting, set the state back to "READY"
                # to allow further interaction.
                if not self.quit_requested:
                    self.state = "READY"

    def _should_pause(self) -> bool:
        """
        A callback function used by the pathfinding thread to check if it should pause.
        This method is called frequently by the `Pathfinder` class.

        Returns:
            `bool`: `True` if `pathfinding_paused` is `True`, `False` otherwise.
        """
        return self.pathfinding_paused

    def _should_stop(self) -> bool:
        """
        A callback function used by the pathfinding thread to check if it should stop.
        This method is called frequently by the `Pathfinder` class.

        Returns:
            `bool`: `True` if `quit_requested` is `True` OR if `pathfinding_active`
                    has been set to `False` (signaling a stop), `False` otherwise.
        """
        return self.quit_requested or not self.pathfinding_active

    def handle_quit(self) -> None:
        """
        Manages the graceful shutdown process of the application.
        It signals any active threads to terminate and then properly
        uninitializes Pygame and exits the system.
        """
        self.quit_requested = True # Set flag to signal all threads to stop.

        # If pathfinding is active, explicitly tell it to stop and wait for it.
        if self.is_pathfinding_in_progress():
            self.stop_pathfinding()

        pygame.quit() # Uninitialize all Pygame modules.
        sys.exit()    # Exit the Python program.

    def run(self) -> None:
        """
        The main application loop (`game loop`).
        This loop continuously:
        - Processes Pygame events (user input, window close).
        - Updates the display by redrawing the grid and UI.
        - Controls the application's frame rate.
        Includes basic error handling for robustness within the loop.
        """
        running = True # Flag to control the main loop execution.

        try:
            while running and not self.quit_requested: # Loop continues until quit requested or window closed.
                for event in pygame.event.get(): # Process all pending Pygame events.
                    if event.type == pygame.QUIT:
                        running = False # Set flag to exit the loop if window close button is pressed.
                        break # Exit the event processing loop.

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        try:
                            # Handle mouse click based on position and button.
                            self.handle_click(pygame.mouse.get_pos(), event.button)
                        except Exception as e:
                            print(f"Error handling mouse click: {e}")

                    elif event.type == pygame.MOUSEBUTTONUP:
                        # Reset continuous wall drawing/erasing flags when mouse button is released.
                        self.drawing_walls = False
                        self.erasing_walls = False

                    elif event.type == pygame.MOUSEMOTION:
                        # Check if the right mouse button (button 2) is held down for dragging.
                        if pygame.mouse.get_pressed()[2]:
                            try:
                                self.handle_drag(pygame.mouse.get_pos()) # Handle continuous wall drawing/erasing.
                            except Exception as e:
                                print(f"Error handling mouse drag: {e}")

                    elif event.type == pygame.KEYDOWN:
                        try:
                            if event.key == pygame.K_SPACE: # Spacebar: Find Path / Pause / Resume.
                                if self.is_pathfinding_in_progress():
                                    self.toggle_pause_pathfinding()
                                elif self.can_start_pathfinding():
                                    self.start_pathfinding()
                            elif event.key == pygame.K_c and self.can_interact_with_grid(): # 'C' key: Clear Path.
                                self.clear_path()
                            elif event.key == pygame.K_r and self.can_interact_with_grid(): # 'R' key: Reset All.
                                self.clear_all()
                        except Exception as e:
                            print(f"Error handling keyboard input: {e}")

                # --- Drawing Phase ---
                # All drawing operations must occur in the main thread.
                try:
                    self.window.fill(BG_DARK) # Clear the screen with dark background.
                    self.grid.draw(self.window) # Draw the grid (nodes and their current colors).
                    self.draw_ui() # Draw the user interface elements.
                    pygame.display.flip() # Update the entire screen to show the newly drawn elements.
                    self.clock.tick(60)  # Limit the frame rate to 60 frames per second for smooth rendering.
                except Exception as e:
                    print(f"Error in drawing: {e}")

        except Exception as e:
            # Catch any unhandled exceptions that might occur in the main loop.
            print(f"Error in main loop: {e}")
        finally:
            # Ensure proper cleanup (Pygame quit, sys exit) regardless of how the loop ends.
            self.handle_quit()

if __name__ == "__main__":
    # This block ensures that the `PathfindingVisualizer` application runs only
    # when the script is executed directly (not when imported as a module).
    try:
        app = PathfindingVisualizer() # Create an instance of the visualizer application.
        app.run() # Start the main application loop.
    except Exception as e:
        print(f"Error starting application: {e}")
        pygame.quit() # Ensure Pygame is properly uninitialized even if an early error occurs.
        sys.exit()    # Exit the system.