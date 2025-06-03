from typing import Optional, Callable, List
import heapq
import time
from grid import Grid
from node import Node
from constants import *

class Pathfinder:

    @staticmethod
    def dijkstra(grid: Grid, start: Optional[Node], end: Optional[Node],
                           speed: float = NORMAL_SPEED,
                           should_pause: Optional[Callable[[], bool]] = None,
                           should_stop: Optional[Callable[[], bool]] = None) -> bool:

        if not start or not end:
            return False

        if should_pause is None:
            should_pause = lambda: False
        if should_stop is None:
            should_stop = lambda: False

        for row_list in grid.grid:
            for node in row_list:
                node.distance = float('inf')
                node.previous = None
                node.visited = False
                if not node.is_wall and node != start and node != end:
                    node.reset()

        grid.set_neighbors()
        start.distance = 0

        pq = [(0, id(start), start)]
        unvisited_set = {start}

        nodes_processed = 0 
        sleep_frequency = max(1, int(50 / (speed * 1000))) if speed > 0 else 50

        while pq:
            if should_stop():
                return False

            # Handle pause state: The algorithm enters a busy-wait loop until unpaused or stopped.
            while should_pause() and not should_stop():
                time.sleep(0.1) # Small delay to prevent high CPU usage during pause.

            if should_stop():
                return False

            _, _, current_node = heapq.heappop(pq)

            if current_node not in unvisited_set:
                continue

            unvisited_set.remove(current_node)
            current_node.visited = True

            if current_node == end:
                return True

            if current_node != start:
                current_node.make_visited()

            for neighbor in current_node.neighbors:
                if neighbor.visited:
                    continue # Skip if neighbor has already been fully processed.

                new_distance = current_node.distance + 1

                if new_distance < neighbor.distance:
                    neighbor.distance = new_distance
                    neighbor.previous = current_node

                    if neighbor not in unvisited_set:
                        unvisited_set.add(neighbor) 
                        heapq.heappush(pq, (new_distance, id(neighbor), neighbor))
                        if neighbor != end:
                            neighbor.make_unvisited_neighbor()

            nodes_processed += 1
            if nodes_processed % sleep_frequency == 0 and speed > 0:
                time.sleep(speed)

        return False

    @staticmethod
    def reconstruct_path(end: Node, speed: float = NORMAL_SPEED,
                                   should_pause: Optional[Callable[[], bool]] = None,
                                   should_stop: Optional[Callable[[], bool]] = None) -> int:

        if should_pause is None:
            should_pause = lambda: False
        if should_stop is None:
            should_stop = lambda: False

        path_length = 0
        current = end
        path_nodes: List[Node] = [] 

        while current.previous:
            current = current.previous

            # Ensure the start node itself is not marked as part of the 'path' path.
            if current.color != NODE_START:
                path_nodes.append(current)
                path_length += 1

        for node in reversed(path_nodes):
            if should_stop():
                return path_length

            while should_pause() and not should_stop():
                time.sleep(0.1)

            if should_stop():
                return path_length

            node.make_path()

            if speed > 0:
                time.sleep(speed * 2)

        return path_length