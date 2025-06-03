from typing import List, Optional, Tuple
from constants import *

class Node:
    def __init__(self, row: int, col: int):
        self.row: int = row
        self.col: int = col
        self.x: int = col * CELL_SIZE
        self.y: int = row * CELL_SIZE
        self.color: Tuple[int, int, int] = NODE_DEFAULT
        self.neighbors: List['Node'] = []
        self.is_wall: bool = False

        self.distance: float = float('inf')
        self.previous: Optional['Node'] = None
        self.visited: bool = False

    def __lt__(self, other: 'Node') -> bool:
        return self.distance < other.distance

    def make_wall(self) -> None:
        self.is_wall = True
        self.color = WALL

    def make_path(self) -> None:
        self.color = NODE_PATH

    def make_start(self) -> None:
        self.color = NODE_START

    def make_end(self) -> None:
        self.color = NODE_END

    def make_visited(self) -> None:
        self.color = NODE_VISITED

    def make_unvisited_neighbor(self) -> None:
        self.color = NODE_NEIGHBOR

    def reset(self) -> None:
        self.color = NODE_DEFAULT
        self.is_wall = False
        self.distance = float('inf')
        self.previous = None
        self.visited = False