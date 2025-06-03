"""
This is the main application file for the Dijkstra's Algorithm Visualizer.
It initializes Pygame, sets up the main window, manages the application's
state, draws the user interface, handles all user input (mouse and keyboard),
and orchestrates the interaction between the `Grid`, `Pathfinder`, and
`WallGenerator` components. It now utilizes refactored modules for UI,
Pathfinding Management, and Input Handling.
"""

import pygame
import sys
from grid import Grid
from wall_generator import WallGenerator
from constants import *
from typing import Dict, Any

# Import refactored modules
from ui_manager import UIManager
from pathfinding_manager import PathfindingManager
from input_handler import InputHandler

class PathfindingVisualizer:
    """
    The main class for the Pathfinding Visualizer application.
    It encapsulates the entire application logic, including:
    - Pygame initialization and window management.
    - The main game loop and event handling.
    - Drawing the grid and coordinating with UIManager for UI.
    - Managing application states (e.g., setting start/end, pathfinding).
    - Coordinating with `Grid`, `WallGenerator`, `UIManager`, `PathfindingManager`, and `InputHandler`.
    """
    def __init__(self):
        """
        Initializes the Pygame environment and all components of the visualizer.
        Sets up the display window, game clock, grid, and initial application state.
        """
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Dijkstra's Algorithm Visualizer")
        self.clock = pygame.time.Clock()
        self.grid = Grid()

        # Initialize manager classes
        self.ui_manager = UIManager()
        self.pathfinding_manager = PathfindingManager()
        self.input_handler = InputHandler()

        # Application state
        self.app_state: Dict[str, Any] = {
            "state": "WAITING_START", # "WAITING_START", "WAITING_END", "READY", "PATHFINDING", "PAUSED"
            "wall_type": "maze",
            "speed": NORMAL_SPEED,
            "last_path_length": 0,
            # These will be updated by pathfinding_manager's get_state()
            'is_pathfinding_in_progress': False,
            'pathfinding_paused': False,
            'pathfinding_completed': False,
            'path_found': False,
            'can_interact_with_grid': True, # Derived state
            'can_start_pathfinding': False # Derived state
        }
        
        self.quit_requested = False

    def _update_derived_app_state(self) -> None:
        """
        Updates derived application states based on current manager states.
        This method should be called before drawing or handling input that
        depends on these derived states.
        """
        path_mgr_state = self.pathfinding_manager.get_state()
        self.app_state.update(path_mgr_state)

        self.app_state['can_interact_with_grid'] = not self.pathfinding_manager.is_pathfinding_in_progress()
        self.app_state['can_start_pathfinding'] = self.pathfinding_manager.can_start_pathfinding(self.grid)
        self.app_state['last_path_length'] = self.pathfinding_manager.last_path_length
        # Update the main state string based on pathfinding manager's state
        if self.pathfinding_manager.is_pathfinding_in_progress():
            self.app_state['state'] = "PATHFINDING"
        elif self.grid.start_node and self.grid.end_node:
            self.app_state['state'] = "READY"
        elif self.grid.start_node:
            self.app_state['state'] = "WAITING_END"
        else:
            self.app_state['state'] = "WAITING_START"

    def generate_walls(self) -> None:
        """
        Initiates the wall generation process on the grid based on the
        currently selected `wall_type`. After generation, it resets the
        start/end nodes and path length display, preparing for a new pathfinding run.
        """
        if not self.app_state['can_interact_with_grid']:
            return

        WallGenerator.generate_wall(self.grid, self.app_state['wall_type'])
        self.grid.start_node = None
        self.grid.end_node = None
        self.app_state['state'] = "WAITING_START"
        self.pathfinding_manager.last_path_length = 0

    def clear_path(self) -> None:
        """
        Clears only the visual elements of the pathfinding visualization.
        """
        if not self.app_state['can_interact_with_grid']:
            return
        self.grid.clear_path()
        self.pathfinding_manager.last_path_length = 0

    def clear_all(self) -> None:
        """
        Resets the entire grid and application state.
        """
        if not self.app_state['can_interact_with_grid']:
            return
        self.grid.clear_all()
        self.grid.start_node = None
        self.grid.end_node = None
        self.app_state['state'] = "WAITING_START"
        self.pathfinding_manager.last_path_length = 0
        self.pathfinding_manager.stop_pathfinding() # Ensure pathfinding thread is stopped

    def handle_quit(self) -> None:
        """
        Manages the graceful shutdown process of the application.
        """
        self.quit_requested = True
        self.pathfinding_manager.request_quit()
        pygame.quit()
        sys.exit()

    def run(self) -> None:
        """
        The main application loop (`game loop`).
        """
        running = True
        try:
            while running and not self.quit_requested:
                # Always update derived states at the beginning of each loop iteration
                self._update_derived_app_state()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Check for UI clicks first
                        action_type, action_data = self.ui_manager.handle_ui_click(pygame.mouse.get_pos())
                        if action_type:
                            if action_type == "generate_walls":
                                self.generate_walls()
                            elif action_type == "set_wall_type":
                                self.app_state['wall_type'] = action_data
                            elif action_type == "toggle_pathfinding":
                                if self.pathfinding_manager.is_pathfinding_in_progress():
                                    self.pathfinding_manager.toggle_pause()
                                elif self.app_state['can_start_pathfinding']:
                                    self.pathfinding_manager.start_pathfinding(
                                        self.grid, self.app_state['speed'], self.clear_path
                                    )
                            elif action_type == "set_speed":
                                self.app_state['speed'] = action_data
                            elif action_type == "clear_path":
                                self.clear_path()
                            elif action_type == "clear_all":
                                self.clear_all()
                        else:
                            # If not a UI click, handle as a grid click
                            self.app_state = self.input_handler.handle_grid_click(
                                pygame.mouse.get_pos(), event.button, self.grid,
                                self.app_state, lambda: self.app_state['can_interact_with_grid']
                            )

                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.input_handler.handle_mouse_button_up()

                    elif event.type == pygame.MOUSEMOTION:
                        if pygame.mouse.get_pressed()[2]: # Right click held for dragging
                            self.input_handler.handle_mouse_drag(
                                pygame.mouse.get_pos(), self.grid,
                                lambda: self.app_state['can_interact_with_grid']
                            )

                    elif event.type == pygame.KEYDOWN:
                        action = self.input_handler.handle_keyboard_input(event, self.app_state)
                        if action == "toggle_pause":
                            self.pathfinding_manager.toggle_pause()
                        elif action == "start_pathfinding":
                            self.pathfinding_manager.start_pathfinding(
                                self.grid, self.app_state['speed'], self.clear_path
                            )
                        elif action == "clear_path":
                            self.clear_path()
                        elif action == "clear_all":
                            self.clear_all()

                # Drawing Phase
                self.window.fill(BG_DARK)
                self.grid.draw(self.window)
                self.ui_manager.draw_ui(self.window, self.app_state) # Pass the consolidated app_state
                pygame.display.flip()
                self.clock.tick(60)

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