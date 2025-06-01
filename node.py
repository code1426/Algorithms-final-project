"""
This file defines the `Node` class, which represents a single cell in the grid
used by the pathfinding visualizer. Each node stores its position, visual state
(color), and crucial attributes required for the Dijkstra's algorithm.
"""

from typing import List, Optional, Tuple
from constants import * # Import color constants from constants.py

class Node:
    """
    Represents a single cell (node) in the pathfinding grid.
    Each `Node` object holds information pertinent to its graphical representation
    and its role in the Dijkstra's algorithm.

    Attributes:
        `row` (int): The row index of the node in the grid.
        `col` (int): The column index of the node in the grid.
        `x` (int): The x-coordinate (pixel) for drawing the node on the screen.
        `y` (int): The y-coordinate (pixel) for drawing the node on the screen.
        `color` (Tuple[int, int, int]): The RGB color tuple representing the node's current visual state.
        `neighbors` (List['Node']): A list of references to valid (non-wall) adjacent `Node` objects.
        `is_wall` (bool): A boolean flag indicating if this node is an impassable obstacle.

        # Dijkstra's Algorithm Specific Attributes:
        `distance` (float): The shortest distance found so far from the start node to this node.
                            Initialized to infinity (`float('inf')`).
        `previous` (Optional['Node']): A reference to the previous node in the shortest path
                                       from the start node to this node. Used for path reconstruction.
        `visited` (bool): A boolean flag indicating if this node has been fully processed
                          by Dijkstra's algorithm (i.e., its shortest distance has been finalized).
    """
    def __init__(self, row: int, col: int):
        """
        Initializes a new `Node` instance with its grid coordinates and default properties.

        Args:
            `row` (int): The row index of the node.
            `col` (int): The column index of the node.
        """
        self.row: int = row
        self.col: int = col
        self.x: int = col * CELL_SIZE # Calculate pixel x-coordinate.
        self.y: int = row * CELL_SIZE # Calculate pixel y-coordinate.
        self.color: Tuple[int, int, int] = NODE_DEFAULT # Default node color
        self.neighbors: List['Node'] = [] # Empty list initially, populated by `Grid`.
        self.is_wall: bool = False # Initially, not a wall.

        self.distance: float = float('inf') # Set initial distance to infinity.
        self.previous: Optional['Node'] = None # No previous node initially.
        self.visited: bool = False # Not visited initially.

    def __lt__(self, other: 'Node') -> bool:
        """
        Less-than comparison method for `Node` objects.
        This method is crucial for the `heapq` (priority queue) used in Dijkstra's algorithm.
        Nodes are ordered based on their `distance` attribute, ensuring that the node
        with the smallest distance is always retrieved first from the priority queue.

        Args:
            `other` ('Node'): The other `Node` object to compare against.

        Returns:
            `bool`: `True` if `self`'s distance is less than `other`'s distance, `False` otherwise.
        """
        return self.distance < other.distance

    def make_wall(self) -> None:
        """
        Sets the node's state to an impassable wall and updates its color to `BLACK`.
        """
        self.is_wall = True
        self.color = WALL

    def make_path(self) -> None:
        """
        Changes the node's color to `YELLOW` to visually indicate that it is part
        of the final shortest path found by the algorithm.
        """
        self.color = NODE_PATH

    def make_start(self) -> None:
        """
        Sets the node's color to `RED` to visually designate it as the starting node
        for the pathfinding algorithm.
        """
        self.color = NODE_START

    def make_end(self) -> None:
        """
        Sets the node's color to `GREEN` to visually designate it as the ending (target) node
        for the pathfinding algorithm.
        """
        self.color = NODE_END

    def make_visited(self) -> None:
        """
        Changes the node's color to `BLUE` to visually indicate that it has been
        processed (visited) by Dijkstra's algorithm during the search phase.
        """
        self.color = NODE_VISITED

    def make_unvisited_neighbor(self) -> None:
        """
        Changes the node's color to `CYAN` to visually indicate that it is an unvisited
        neighbor currently being considered or placed into the priority queue by
        Dijkstra's algorithm.
        """
        self.color = NODE_NEIGHBOR

    def reset(self) -> None:
        """
        Resets the node to its default state. This clears its visual color to `WHITE`,
        removes its wall status (`is_wall = False`), and resets all Dijkstra's
        algorithm-related attributes (`distance`, `previous`, `visited`) to their initial values.
        This method is used for clearing the grid or preparing for a new pathfinding run.
        """
        self.color = NODE_DEFAULT
        self.is_wall = False
        self.distance = float('inf') # Reset distance to infinity.
        self.previous = None         # Clear previous node reference.
        self.visited = False         # Mark as unvisited.