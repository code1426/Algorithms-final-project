"""
Input Handler manages all user input including mouse clicks, drags, and keyboard events.
This separates input handling logic from the main application for better organization.
"""

import pygame
from typing import Tuple, Optional, Callable
from grid import Grid
from constants import *

class InputHandler:
    """
    Handles all user input events including mouse clicks, mouse dragging,
    and keyboard events. Provides clean separation between input detection
    and application logic.
    """
    
    def __init__(self):
        """Initialize input handler state."""
        self.drawing_walls = False
        self.erasing_walls = False
    
    def handle_grid_click(self, pos: Tuple[int, int], button: int, grid: Grid,
                         app_state: dict, can_interact_callback: Callable[[], bool]) -> dict:
        """
        Handle mouse clicks on the grid area.
        
        Args:
            pos: Mouse click position (x, y)
            button: Mouse button (1=left, 3=right)
            grid: Grid instance
            app_state: Current application state
            can_interact_callback: Function to check if grid interaction is allowed
            
        Returns:
            Updated application state dictionary
        """
        if not can_interact_callback():
            return app_state
            
        row, col = grid.get_clicked_pos(pos)
        if row is None or col is None:
            return app_state
            
        node = grid.get_node(row, col)
        if node is None:
            return app_state
        
        new_state = app_state.copy()
        
        if button == 1:  # Left click - set start/end points
            new_state = self._handle_left_click(node, grid, new_state)
        elif button == 3:  # Right click - toggle walls
            new_state = self._handle_right_click(node, grid, new_state)
            
        return new_state
    
    def _handle_left_click(self, node, grid: Grid, app_state: dict) -> dict:
        """Handle left click for setting start/end points."""
        if node.is_wall:
            return app_state
            
        new_state = app_state.copy()
        
        if app_state['state'] == "WAITING_START":
            if grid.start_node:
                grid.start_node.reset()
            grid.start_node = node
            node.make_start()
            new_state['state'] = "WAITING_END"
            
        elif app_state['state'] == "WAITING_END":
            if node != grid.start_node:
                if grid.end_node:
                    grid.end_node.reset()
                grid.end_node = node
                node.make_end()
                new_state['state'] = "READY"
                
        return new_state
    
    def _handle_right_click(self, node, grid: Grid, app_state: dict) -> dict:
        """Handle right click for toggling walls."""
        if node == grid.start_node or node == grid.end_node:
            return app_state
            
        if node.is_wall:
            node.reset()
            self.erasing_walls = True
        else:
            node.make_wall()
            self.drawing_walls = True
            
        return app_state
    
    def handle_mouse_drag(self, pos: Tuple[int, int], grid: Grid,
                         can_interact_callback: Callable[[], bool]) -> None:
        """
        Handle mouse dragging for continuous wall drawing/erasing.
        
        Args:
            pos: Current mouse position
            grid: Grid instance
            can_interact_callback: Function to check if interaction is allowed
        """
        if not can_interact_callback():
            return
            
        row, col = grid.get_clicked_pos(pos)
        if row is None or col is None:
            return
            
        node = grid.get_node(row, col)
        if node is None or node == grid.start_node or node == grid.end_node:
            return
        
        if self.drawing_walls and not node.is_wall:
            node.make_wall()
        elif self.erasing_walls and node.is_wall:
            node.reset()
    
    def handle_mouse_button_up(self) -> None:
        """Reset drag flags when mouse button is released."""
        self.drawing_walls = False
        self.erasing_walls = False
    
    def handle_keyboard_input(self, event: pygame.event.Event, app_state: dict) -> Optional[str]:
        """
        Handle keyboard input events.
        
        Args:
            event: Pygame keyboard event
            app_state: Current application state
            
        Returns:
            Action string or None
        """
        if event.key == pygame.K_SPACE:
            # Space: Find Path / Pause / Resume
            if app_state['is_pathfinding_in_progress']:
                return "toggle_pause"
            elif app_state['can_start_pathfinding']:
                return "start_pathfinding"
                
        elif event.key == pygame.K_c and app_state['can_interact_with_grid']:
            # C: Clear Path
            return "clear_path"
            
        elif event.key == pygame.K_r and app_state['can_interact_with_grid']:
            # R: Reset All
            return "clear_all"
            
        return None