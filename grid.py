"""
This file defines the `Grid` class, which manages the grid of `Node` objects
for the pathfinding visualization. It handles the creation, initialization,
and rendering of the grid, as well as providing methods for user interaction
such as placing start/end nodes and walls.
"""

from typing import List, Optional, Tuple
import pygame
from node import Node
from constants import * # Import color and dimension constants

class Grid:
    """
    Represents the grid of nodes for the pathfinding visualization.
    This class is responsible for:
    - Initializing and maintaining the 2D array of `Node` objects.
    - Providing access to individual nodes.
    - Updating node neighbors based on grid configuration (e.g., walls).
    - Drawing the grid on the Pygame window.
    - Clearing pathfinding visualizations or the entire grid.
    - Converting mouse click coordinates to grid coordinates.
    """
    def __init__(self):
        """
        Initializes a new `Grid` instance.
        """
        self.grid: List[List[Node]] = []  # A 2D list to store `Node` objects.
        self.start_node: Optional[Node] = None  # Reference to the designated starting node.
        self.end_node: Optional[Node] = None    # Reference to the designated ending node.
        self.initialize_grid() # Calls the method to populate the grid with nodes.

    def initialize_grid(self) -> None:
        """
        Populates the `grid` with `Node` objects.
        Each node is created with its `row` and `col` coordinates, and then
        added to the 2D `grid` list. This effectively resets the grid structure.
        """
        self.grid = [] # Clears any existing grid structure.
        for row in range(GRID_ROWS):
            self.grid.append([]) # Adds a new row list.
            for col in range(GRID_COLS):
                node = Node(row, col) # Creates a new `Node` instance for each cell.
                self.grid[row].append(node) # Adds the node to the current row.

    def get_node(self, row: int, col: int) -> Optional[Node]:
        """
        Retrieves a `Node` object from the grid at the specified coordinates.

        Args:
            `row` (int): The row index of the node to retrieve.
            `col` (int): The column index of the node to retrieve.

        Returns:
            `Optional[Node]`: The `Node` object at (`row`, `col`) if within bounds,
                             otherwise `None`.
        """
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return self.grid[row][col]
        return None

    def set_neighbors(self) -> None:
        """
        Updates the list of valid neighbors for all nodes in the grid.
        A node's neighbors are defined as the directly adjacent (up, down, left, right)
        nodes that are within the grid boundaries and are *not* walls. This method
        should be called before running any pathfinding algorithm to ensure
        accurate connectivity.
        """
        for row_list in self.grid: # Iterate through each row of nodes.
            for node in row_list:  # Iterate through each node in the current row.
                node.neighbors = []  # Clear any previously calculated neighbors.
                # Define possible cardinal directions (right, left, down, up).
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                for dx, dy in directions:
                    new_row, new_col = node.row + dx, node.col + dy # Calculate neighbor coordinates.
                    neighbor = self.get_node(new_row, new_col) # Get the potential neighbor node.
                    # Add the neighbor if it exists (is not None) and is not a wall.
                    if neighbor and not neighbor.is_wall:
                        node.neighbors.append(neighbor)

    def draw(self, window: pygame.Surface) -> None:
        """
        Draws the entire grid on the provided Pygame `window` surface.
        Each node is drawn as a colored rectangle based on its current state (color),
        and subtle light gray lines are drawn to visually delineate individual cells.

        Args:
            `window` (pygame.Surface): The Pygame surface to draw the grid onto.
        """
        for row_list in self.grid:
            for node in row_list:
                # Draw the main colored rectangle representing the node's state.
                pygame.draw.rect(window, node.color,
                               (node.x, node.y, CELL_SIZE, CELL_SIZE))

    def clear_path(self) -> None:
        """
        Clears only the visual elements related to pathfinding, such as visited nodes
        and the final path nodes. Walls, the start node, and the end node
        remain untouched. This allows the user to re-run the algorithm on the
        same grid configuration.
        """
        for row_list in self.grid:
            for node in row_list:
                # Reset only nodes that are not walls, the start node, or the end node.
                if not node.is_wall and node != self.start_node and node != self.end_node:
                    node.reset() # Resets color and pathfinding-specific attributes.

    def clear_all(self) -> None:
        """
        Resets the entire grid to its initial state. This includes removing
        all walls, clearing the start and end node references, and resetting
        all nodes to their default unvisited (white) state.
        """
        for row_list in self.grid:
            for node in row_list:
                node.reset() # Resets all node properties, including `is_wall`.
        self.start_node = None # Clear reference to the start node.
        self.end_node = None   # Clear reference to the end node.

    def get_clicked_pos(self, pos: Tuple[int, int]) -> Tuple[Optional[int], Optional[int]]:
        """
        Converts pixel coordinates (`x`, `y`) from a mouse click event into
        corresponding grid `row` and `col` indices. It also ensures the click
        occurred within the main grid area (excluding the UI panel).

        Args:
            `pos` (Tuple[int, int]): A tuple containing the (x, y) pixel coordinates of the mouse click.

        Returns:
            `Tuple[Optional[int], Optional[int]]`: A tuple (`row`, `col`) if the click was within
                                                   the valid grid area, otherwise (`None`, `None`).
        """
        x, y = pos
        # Calculate the maximum X-coordinate that the grid occupies.
        max_grid_x = GRID_COLS * CELL_SIZE

        # Check if the click is outside the main grid area (e.g., on the UI panel).
        if x >= max_grid_x or x < 0 or y < 0:
            return None, None

        # Calculate the row and column by dividing pixel coordinates by `CELL_SIZE`.
        row = y // CELL_SIZE
        col = x // CELL_SIZE

        # Validate that the calculated row and column are within the grid's dimensions.
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return row, col
        return None, None