from typing import List, Optional, Tuple
from constants import *

class Node:
    def __init__(self, row: int, col: int):
        self.row: int = row
        self.col: int = col
        self.x: int = col * CELL_SIZE
        self.y: int = row * CELL_SIZE
        self.color: Tuple[int, int, int] = WHITE
        self.neighbors: List['Node'] = []
        self.is_wall: bool = False

        # Dijkstra's algorithm attributes
        self.distance: float = float('inf')
        self.previous: Optional['Node'] = None
        self.visited: bool = False

    def __lt__(self, other: 'Node') -> bool:
        return self.distance < other.distance

    def make_wall(self) -> None:
        self.is_wall = True
        self.color = BLACK

    def make_path(self) -> None:
        self.color = YELLOW

    def make_start(self) -> None:
        self.color = RED

    def make_end(self) -> None:
        self.color = GREEN

    def make_visited(self) -> None:
        self.color = BLUE

    def make_unvisited_neighbor(self) -> None:
        self.color = CYAN

    def reset(self) -> None:
        self.color = WHITE
        self.is_wall = False
        self.distance = float('inf')
        self.previous = None
        self.visited = False

    def get_pos(self) -> Tuple[int, int]:
        return self.row, self.col