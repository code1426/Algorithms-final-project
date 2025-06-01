import random
from grid import Grid

class WallGenerator:
    @staticmethod
    def generate_wall(grid: Grid, maze_type: str = 'maze') -> None:
        """Generate different types of mazes"""
        # Reset the entire grid to walls first
        for row in grid.grid:
            for node in row:
                node.reset()
                node.make_wall()

        if maze_type == 'maze':
            WallGenerator._recursive_backtracker(grid)
            WallGenerator._add_openings(grid) # Add some additional openings for more interesting paths

        elif maze_type == 'random':
            WallGenerator._random_maze(grid)


    @staticmethod
    def _recursive_backtracker(grid: Grid) -> None:
        """Generate maze using recursive backtracking algorithm"""
        visited = set()
        stack = []

        # Start from center of the grid
        start_row = len(grid.grid) // 2
        start_col = len(grid.grid[0]) // 2
        
        # Ensure we start on an odd position for proper maze generation
        if start_row % 2 == 0:
            start_row -= 1
        if start_col % 2 == 0:
            start_col -= 1

        stack.append((start_row, start_col))

        while stack:
            current_row, current_col = stack[-1]
            
            # Mark current cell as passage if not already visited
            if (current_row, current_col) not in visited:
                visited.add((current_row, current_col))
                node = grid.get_node(current_row, current_col)
                if node:
                    node.reset()

            # Find unvisited neighbors (2 cells away)
            neighbors = []
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            
            for dx, dy in directions:
                new_row, new_col = current_row + dx, current_col + dy
                if (1 <= new_row < len(grid.grid) - 1 and 
                    1 <= new_col < len(grid.grid[0]) - 1 and
                    (new_row, new_col) not in visited):
                    neighbors.append((new_row, new_col, dx, dy))

            if neighbors:
                # Choose random unvisited neighbor
                new_row, new_col, dx, dy = random.choice(neighbors)
                
                # Remove wall between current cell and chosen neighbor
                wall_row = current_row + dx // 2
                wall_col = current_col + dy // 2
                wall_node = grid.get_node(wall_row, wall_col)
                if wall_node:
                    wall_node.reset()

                # Move to the neighbor
                stack.append((new_row, new_col))
            else:
                # Backtrack
                stack.pop()

    @staticmethod
    def _random_maze(grid: Grid) -> None:
        """Generate a random maze with 30% walls"""
        for row in range(len(grid.grid)):
            for col in range(len(grid.grid[0])):
                if random.random() < 0.3:  # 30% chance of being a wall
                    grid.get_node(row, col).make_wall()
                else:
                    grid.get_node(row, col).reset()

    @staticmethod
    def _add_openings(grid: Grid) -> None:
        """Add random openings to make the maze more solvable"""
        num_openings = max(20, len(grid.grid)) * len(grid.grid[0]) // 4
        
        for _ in range(num_openings):
            row = random.randrange(1, len(grid.grid) - 1)
            col = random.randrange(1, len(grid.grid[0]) - 1)
            
            node = grid.get_node(row, col)
            if node and node.is_wall:
                node.reset()

