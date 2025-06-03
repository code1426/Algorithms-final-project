"""
Pathfinding Manager handles all pathfinding-related operations including
threading, state management, and coordination with the Pathfinder class.
"""

import threading
from typing import Callable, Optional
from grid import Grid
from pathfinder import Pathfinder

class PathfindingManager:
    """
    Manages pathfinding operations including threading, pause/resume functionality,
    and state tracking. Provides a clean interface between the main application
    and the pathfinding algorithm.
    """
    
    def __init__(self):
        """Initialize pathfinding manager."""
        self.pathfinding_thread: Optional[threading.Thread] = None
        self.pathfinding_active = False
        self.pathfinding_paused = False
        self.pathfinding_completed = False
        self.path_found = False
        self.quit_requested = False
        self.last_path_length = 0
        
        # Thread safety lock
        self.pathfinding_lock = threading.Lock()
    
    def is_pathfinding_in_progress(self) -> bool:
        """Check if pathfinding is currently active."""
        return self.pathfinding_active and not self.pathfinding_completed
    
    def can_start_pathfinding(self, grid: Grid) -> bool:
        """Check if pathfinding can be started."""
        return (grid.start_node is not None and
                grid.end_node is not None and
                not self.is_pathfinding_in_progress())
    
    def start_pathfinding(self, grid: Grid, speed: float,
                         clear_path_callback: Callable[[], None]) -> None:
        """
        Start pathfinding in a separate thread.
        
        Args:
            grid: Grid instance
            speed: Animation speed
            clear_path_callback: Function to clear previous path
        """
        if not self.can_start_pathfinding(grid):
            return
        
        with self.pathfinding_lock:
            self.pathfinding_active = True
            self.pathfinding_paused = False
            self.pathfinding_completed = False
        
        # Clear any previous path
        clear_path_callback()
        
        # Start pathfinding thread
        self.pathfinding_thread = threading.Thread(
            target=self._run_pathfinding_thread,
            args=(grid, speed)
        )
        self.pathfinding_thread.daemon = True
        self.pathfinding_thread.start()
    
    def toggle_pause(self) -> None:
        """Toggle pause state of pathfinding."""
        if not self.is_pathfinding_in_progress():
            return
        
        with self.pathfinding_lock:
            self.pathfinding_paused = not self.pathfinding_paused
    
    def stop_pathfinding(self) -> None:
        """Stop pathfinding gracefully."""
        with self.pathfinding_lock:
            self.pathfinding_active = False
            self.pathfinding_completed = True
        
        if self.pathfinding_thread and self.pathfinding_thread.is_alive():
            self.pathfinding_thread.join(timeout=1.0)
    
    def request_quit(self) -> None:
        """Request application quit and stop pathfinding."""
        self.quit_requested = True
        if self.is_pathfinding_in_progress():
            self.stop_pathfinding()
    
    def _run_pathfinding_thread(self, grid: Grid, speed: float) -> None:
        """
        Main pathfinding thread function.
        
        Args:
            grid: Grid instance
            speed: Animation speed
        """
        try:
            if not grid.start_node or not grid.end_node:
                print("Error: Start or end node not set for pathfinding.")
                return
            
            # Run Dijkstra's algorithm
            path_found = Pathfinder.dijkstra(
                grid,
                grid.start_node,
                grid.end_node,
                speed,
                self._should_pause,
                self._should_stop
            )
            
            if self._should_stop():
                return
            
            if path_found:
                # Reconstruct and visualize path
                self.last_path_length = Pathfinder.reconstruct_path(
                    grid.end_node,
                    speed,
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
    
    def _should_pause(self) -> bool:
        """Check if pathfinding should pause."""
        return self.pathfinding_paused
    
    def _should_stop(self) -> bool:
        """Check if pathfinding should stop."""
        return self.quit_requested or not self.pathfinding_active
    
    def get_state(self) -> dict:
        """Get current pathfinding state as dictionary."""
        return {
            'is_pathfinding_in_progress': self.is_pathfinding_in_progress(),
            'pathfinding_paused': self.pathfinding_paused,
            'pathfinding_completed': self.pathfinding_completed,
            'path_found': self.path_found,
            'last_path_length': self.last_path_length
        }