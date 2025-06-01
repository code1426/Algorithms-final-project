"""
This file provides static methods for generating different types of wall patterns
on the grid, which serve as obstacles for the pathfinding algorithm.
It includes algorithms for creating structured mazes (recursive backtracking)
and simple random wall distributions.
"""

import random
from grid import Grid

class WallGenerator:
    """
    A utility class that contains static methods for generating various wall
    configurations on a `Grid` object. These walls act as barriers that the
    pathfinding algorithm must navigate around.
    """
    @staticmethod
    def generate_wall(grid: Grid, maze_type: str = 'maze') -> None:
        """
        Generates walls on the provided `grid` based on the specified `maze_type`.
        The process involves:
        1. Resetting the entire grid and making all cells walls initially.
        2. Carving out paths according to the chosen generation algorithm.

        Args:
            `grid` (Grid): The `Grid` object on which to generate walls.
            `maze_type` (str, optional): A string specifying the type of wall generation:
                                        - `'maze'`: Generates a structured maze using
                                          the recursive backtracking algorithm.
                                        - `'random'`: Generates a random scattering of walls.
                                        Defaults to `'maze'`.
        """
        # First, reset the entire grid and convert all cells into walls.
        # This provides a clean slate before carving out the maze paths.
        for row_list in grid.grid:
            for node in row_list:
                node.reset()      # Clear any existing state (start/end/visited/path).
                node.make_wall()  # Convert every node into a wall.

        if maze_type == 'maze':
            # Generate a "perfect" maze (no loops, single path between any two points)
            # using the recursive backtracking algorithm.
            WallGenerator._recursive_backtracker(grid)
            # Add some additional openings to introduce complexity and potentially
            # create multiple paths, making the shortest path more interesting.
            WallGenerator._add_openings(grid)

        elif maze_type == 'random':
            # Generate random scattered walls across the grid.
            WallGenerator._random_maze(grid)

    @staticmethod
    def _recursive_backtracker(grid: Grid) -> None:
        """
        Generates a maze using the Recursive Backtracking algorithm.
        This algorithm is known for creating perfect mazes where there is
        exactly one path between any two points.

        The algorithm operates by:
        1. Starting from a random cell in the grid.
        2. Marking the current cell as visited and converting it into a passage.
        3. Randomly selecting an unvisited neighbor that is two cells away.
        4. Carving a path (converting a wall to a passage) through the wall
           separating the current cell and the chosen neighbor.
        5. Pushing the chosen neighbor onto a stack and making it the new current cell.
        6. If the current cell has no unvisited neighbors, it "backtracks" by
           popping a cell from the stack and making it the current cell.
        7. The process continues until the stack is empty, indicating all reachable
           cells have been visited.

        Args:
            `grid` (Grid): The `Grid` object on which to generate the maze.
        """
        visited = set()  # A set to keep track of visited cells using (row, col) tuples.
        stack = []       # A stack to manage the cells for backtracking.

        # Determine a starting cell. It's common practice for grid-based maze
        # generation to start from an odd-indexed cell to ensure proper wall/passage
        # carving relative to a 2-cell step.
        start_row = len(grid.grid) // 2
        start_col = len(grid.grid[0]) // 2

        # Adjust to ensure starting on an odd row/column for maze generation.
        if start_row % 2 == 0:
            start_row -= 1
        if start_col % 2 == 0:
            start_col -= 1

        stack.append((start_row, start_col)) # Push the starting cell onto the stack.

        while stack:
            current_row, current_col = stack[-1] # Get the current cell from the top of the stack.

            # Mark the current cell as a passage if it hasn't been visited yet.
            if (current_row, current_col) not in visited:
                visited.add((current_row, current_col))
                node = grid.get_node(current_row, current_col)
                if node:
                    node.reset() # Convert the wall node into a passage node (reset its state).

            # Find unvisited neighbors that are two cells away in cardinal directions.
            neighbors = []
            # Define directions for 2-cell steps: (dx, dy)
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]

            for dx, dy in directions:
                new_row, new_col = current_row + dx, current_col + dy
                # Check bounds: ensure neighbors are within the grid and not on the outer border
                # (which should remain solid walls to enclose the maze).
                if (1 <= new_row < len(grid.grid) - 1 and # Avoid top/bottom border row 0, max_row-1
                    1 <= new_col < len(grid.grid[0]) - 1 and # Avoid left/right border col 0, max_col-1
                    (new_row, new_col) not in visited):
                    # Store neighbor coordinates along with the direction (dx, dy) to carve the wall.
                    neighbors.append((new_row, new_col, dx, dy))

            if neighbors:
                # If there are unvisited neighbors, choose one randomly.
                new_row, new_col, dx, dy = random.choice(neighbors)

                # Carve a path by converting the wall *between* the current cell and
                # the chosen neighbor into a passage. The wall's coordinates are
                # midway between the current cell and the neighbor.
                wall_row = current_row + dx // 2
                wall_col = current_col + dy // 2
                wall_node = grid.get_node(wall_row, wall_col)
                if wall_node:
                    wall_node.reset() # Convert the wall node into a passage.

                # Move to the chosen neighbor by pushing it onto the stack.
                stack.append((new_row, new_col))
            else:
                # If no unvisited neighbors exist for the current cell, backtrack
                # by popping the cell from the stack.
                stack.pop()

    @staticmethod
    def _random_maze(grid: Grid) -> None:
        """
        Generates a simple "random maze" by assigning a fixed percentage of cells
        as walls. This results in a scattered pattern of obstacles rather than
        a structured, solvable maze.

        Args:
            `grid` (Grid): The `Grid` object on which to generate random walls.
        """
        for row in range(len(grid.grid)):
            for col in range(len(grid.grid[0])):
                # There's a 30% chance for a cell to become a wall.
                if random.random() < 0.3:
                    grid.get_node(row, col).make_wall()
                else:
                    grid.get_node(row, col).reset() # Ensure it's a passage if not a wall.

    @staticmethod
    def _add_openings(grid: Grid) -> None:
        """
        Adds random "openings" (converts walls to passages) to an existing maze.
        This is typically used after a perfect maze generation algorithm (like
        recursive backtracking) to introduce loops and potentially multiple paths,
        making the shortest path problem more complex and interesting.

        Args:
            `grid` (Grid): The `Grid` object (presumably containing a maze) to modify.
        """
        # Calculate a suitable number of openings based on the grid size.
        # This creates roughly `(rows * cols) / 4` openings.
        num_openings = max(20, len(grid.grid) * len(grid.grid[0]) // 4)

        for _ in range(num_openings):
            # Choose random coordinates, ensuring they are not on the very edge of the grid.
            # This prevents breaking the outer boundary walls of the maze.
            row = random.randrange(1, len(grid.grid) - 1)
            col = random.randrange(1, len(grid.grid[0]) - 1)

            node = grid.get_node(row, col)
            # If the randomly chosen node is currently a wall, convert it to a passage.
            if node and node.is_wall:
                node.reset() # Convert the wall node back to a passage.