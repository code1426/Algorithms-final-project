from typing import List, Optional, Tuple
import pygame
from node import Node
from constants import *

class Grid:
    def __init__(self):
        self.grid: List[List[Node]] = []
        self.start_node: Optional[Node] = None
        self.end_node: Optional[Node] = None
        self.initialize_grid()

    def initialize_grid(self) -> None:
        self.grid = []
        for row in range(GRID_ROWS):
            self.grid.append([])
            for col in range(GRID_COLS):
                node = Node(row, col)
                self.grid[row].append(node)

    def get_node(self, row: int, col: int) -> Optional[Node]:
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return self.grid[row][col]
        return None

    def set_neighbors(self) -> None:
        for row_list in self.grid:
            for node in row_list:
                node.neighbors = []
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                for dx, dy in directions:
                    new_row, new_col = node.row + dx, node.col + dy
                    neighbor = self.get_node(new_row, new_col)
                    if neighbor and not neighbor.is_wall:
                        node.neighbors.append(neighbor)

    def draw(self, window: pygame.Surface) -> None:
        for row_list in self.grid:
            for node in row_list:
                pygame.draw.rect(window, node.color,
                               (node.x, node.y, CELL_SIZE, CELL_SIZE))

    def clear_path(self) -> None:
        for row_list in self.grid:
            for node in row_list:
                if not node.is_wall and node != self.start_node and node != self.end_node:
                    node.reset()

    def clear_all(self) -> None:
        for row_list in self.grid:
            for node in row_list:
                node.reset()
        self.start_node = None
        self.end_node = None

    def get_clicked_pos(self, pos: Tuple[int, int]) -> Tuple[Optional[int], Optional[int]]:
        x, y = pos
        max_grid_x = GRID_COLS * CELL_SIZE
        if x >= max_grid_x or x < 0 or y < 0:
            return None, None

        row = y // CELL_SIZE
        col = x // CELL_SIZE

        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return row, col
        return None, None