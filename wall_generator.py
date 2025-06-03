import random
from grid import Grid

class WallGenerator:
    @staticmethod
    def generate_wall(grid: Grid, maze_type: str = 'maze') -> None:

        # First, reset the entire grid and convert all cells into walls.
        for row_list in grid.grid:
            for node in row_list:
                node.reset()
                node.make_wall()

        if maze_type == 'maze':
            WallGenerator._recursive_backtracker(grid)
            WallGenerator._add_openings(grid)

        elif maze_type == 'random':
            WallGenerator._random_maze(grid)

    @staticmethod
    def _recursive_backtracker(grid: Grid) -> None:
        visited = set()
        stack = []

        start_row = len(grid.grid) // 2
        start_col = len(grid.grid[0]) // 2

        # Adjust to ensure starting on an odd row/column for maze generation.
        if start_row % 2 == 0:
            start_row -= 1
        if start_col % 2 == 0:
            start_col -= 1

        stack.append((start_row, start_col))

        while stack:
            current_row, current_col = stack[-1]

            if (current_row, current_col) not in visited:
                visited.add((current_row, current_col))
                node = grid.get_node(current_row, current_col)
                if node:
                    node.reset()

            # Find unvisited neighbors that are two cells away in cardinal directions.
            neighbors = []
            # Define directions for 2-cell steps: (dx, dy)
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]

            for dx, dy in directions:
                new_row, new_col = current_row + dx, current_col + dy
                # Check bounds: ensure neighbors are within the grid and not on the outer border
                if (1 <= new_row < len(grid.grid) - 1 and # Avoid top/bottom border row 0, max_row-1
                    1 <= new_col < len(grid.grid[0]) - 1 and # Avoid left/right border col 0, max_col-1
                    (new_row, new_col) not in visited):
                    neighbors.append((new_row, new_col, dx, dy))

            if neighbors:
                new_row, new_col, dx, dy = random.choice(neighbors)

                wall_row = current_row + dx // 2
                wall_col = current_col + dy // 2
                wall_node = grid.get_node(wall_row, wall_col)
                if wall_node:
                    wall_node.reset()

                stack.append((new_row, new_col))
            else:
                stack.pop()

    @staticmethod
    def _random_maze(grid: Grid) -> None:
        for row in range(len(grid.grid)):
            for col in range(len(grid.grid[0])):
                if random.random() < 0.3:
                    grid.get_node(row, col).make_wall()
                else:
                    grid.get_node(row, col).reset()

    @staticmethod
    def _add_openings(grid: Grid) -> None:
        num_openings = (len(grid.grid) ** 2) // 4

        for _ in range(num_openings):
            row = random.randrange(1, len(grid.grid) - 1)
            col = random.randrange(1, len(grid.grid[0]) - 1)

            node = grid.get_node(row, col)
            if node and node.is_wall:
                node.reset()