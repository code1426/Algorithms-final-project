"""
This file contains the core implementation of Dijkstra's shortest path algorithm
and the path reconstruction logic. It includes visualization features
by updating node colors and supports pausing and stopping the algorithm
gracefully via callback functions, allowing for interactive control from the main application.
"""

from typing import Optional, Callable, List
import heapq # Python's built-in min-heap implementation, used for the priority queue.
import time   # For introducing artificial delays to control visualization speed.
from grid import Grid
from node import Node
from constants import * # Import speed constants and color definitions.

class Pathfinder:
    """
    Implements Dijkstra's shortest path algorithm and handles the visualization
    of its progress. It provides static methods to run the algorithm and
    reconstruct the path, with built-in support for pausing and stopping
    the visualization, which is crucial for a responsive user interface.
    """

    @staticmethod
    def dijkstra(grid: Grid, start: Optional[Node], end: Optional[Node],
                           speed: float = NORMAL_SPEED,
                           should_pause: Optional[Callable[[], bool]] = None,
                           should_stop: Optional[Callable[[], bool]] = None) -> bool:
        """
        Implements Dijkstra's shortest path algorithm with visualization.
        The algorithm explores nodes in order of increasing distance from the start node,
        updating their distances and `previous` pointers. Node colors are updated
        to provide a visual representation of the search process.

        Args:
            `grid` (Grid): The `Grid` object representing the search space.
            `start` (Optional[Node]): The starting `Node` from which to find the shortest path.
            `end` (Optional[Node]): The target `Node` that the algorithm aims to reach.
            `speed` (float, optional): The animation speed (delay in seconds) between visualizing
                                     each step of the algorithm. Defaults to `NORMAL_SPEED`.
            `should_pause` (Optional[Callable[[], bool]]): A callable (function or lambda) that
                                                            returns `True` if the algorithm should
                                                            pause its execution. Defaults to a function
                                                            that always returns `False`.
            `should_stop` (Optional[Callable[[], bool]]): A callable that returns `True` if the
                                                           algorithm should terminate immediately.
                                                           Defaults to a function that always returns `False`.

        Returns:
            `bool`: `True` if a path is successfully found from `start` to `end`, `False` otherwise.
        """
        if not start or not end:
            return False # Cannot run without valid start and end nodes.

        # Assign default no-op functions if callbacks are not provided.
        if should_pause is None:
            should_pause = lambda: False
        if should_stop is None:
            should_stop = lambda: False

        # Reset all pathfinding-related attributes for every node before starting a new run.
        # This ensures that previous runs do not affect the current execution.
        for row_list in grid.grid:
            for node in row_list:
                node.distance = float('inf') # Reset distance to infinity.
                node.previous = None         # Clear reference to previous node.
                node.visited = False         # Mark as unvisited.
                # Reset visual state of non-wall, non-start/end nodes.
                if not node.is_wall and node != start and node != end:
                    node.reset()

        # sets the neighbors for each node in the grid before the algorithm starts
        grid.set_neighbors()

        # Initialize the distance of the start node to 0. All other nodes remain infinity.
        start.distance = 0

        # Priority queue (`heapq`) to store nodes to visit.
        # Stores tuples: `(distance, unique_id, node)`. `unique_id` (e.g., `id(start)`)
        # is used to break ties when distances are equal, ensuring consistent ordering
        # and preventing comparison errors if two nodes have the same distance.
        pq = [(0, id(start), start)] # Push the start node with distance 0.
        unvisited_set = {start}      # Keep track of nodes currently in the priority queue
                                     # or that have been considered for it.

        nodes_processed = 0 # Counter for visualization timing.
        # Adjust sleep frequency based on `speed`. For faster speeds, sleep less often
        # to maintain a smoother animation without too many small, unnoticeable delays.
        sleep_frequency = max(1, int(50 / (speed * 1000))) if speed > 0 else 50

        while pq:
            # --- External Control Checks ---
            # Check if the algorithm should stop completely (e.g., application quit).
            if should_stop():
                return False

            # Handle pause state: The algorithm enters a busy-wait loop until unpaused or stopped.
            while should_pause() and not should_stop():
                time.sleep(0.1) # Small delay to prevent high CPU usage during pause.

            # Re-check `should_stop` after potential pause, in case a stop request
            # was made while the algorithm was paused.
            if should_stop():
                return False
            # --- End External Control Checks ---

            # Pop the node with the smallest distance from the priority queue.
            # `_` is used for placeholder variables (distance, unique_id) that are not needed.
            _, _, current_node = heapq.heappop(pq)

            # If this node has already been visited/processed with a shorter path, skip it.
            # This can happen if a node was added to the PQ multiple times with different
            # distances, but we already found a shorter path to it.
            if current_node not in unvisited_set:
                continue

            # Mark the `current_node` as visited and remove it from the set of unvisited nodes.
            unvisited_set.remove(current_node)
            current_node.visited = True

            # If the `current_node` is the `end` node, a path has been found!
            if current_node == end:
                return True

            # Visualize the `current_node` as 'visited' (`BLUE`), unless it is the start node.
            if current_node != start:
                current_node.make_visited()

            # Iterate through all valid neighbors of the `current_node`.
            for neighbor in current_node.neighbors:
                if neighbor.visited:
                    continue # Skip if neighbor has already been fully processed.

                # Calculate the new distance to the `neighbor` through the `current_node`.
                # Assuming a uniform edge weight of 1 for simplicity (each step costs 1).
                new_distance = current_node.distance + 1

                # If this newly calculated path to the `neighbor` is shorter than its
                # currently recorded `distance`.
                if new_distance < neighbor.distance:
                    neighbor.distance = new_distance # Update the neighbor's shortest distance.
                    neighbor.previous = current_node # Set `current_node` as the neighbor's predecessor.

                    # If the neighbor is not already in the priority queue (or has a worse distance), add it.
                    # This check is crucial for the efficiency of Dijkstra's with a priority queue.
                    if neighbor not in unvisited_set:
                        unvisited_set.add(neighbor) 
                        heapq.heappush(pq, (new_distance, id(neighbor), neighbor)) # Add to PQ.
                        # Visualize the neighbor being considered (`CYAN`), unless it's the end node.
                        if neighbor != end:
                            neighbor.make_unvisited_neighbor()

            # Introduce a small delay for visualization purposes.
            # The delay is applied periodically based on `sleep_frequency` to balance
            # responsiveness with clear animation steps.
            nodes_processed += 1
            if nodes_processed % sleep_frequency == 0 and speed > 0:
                time.sleep(speed)

        # If the priority queue becomes empty and the `end` node was not reached,
        # it means no path exists from `start` to `end`.
        return False

    @staticmethod
    def reconstruct_path(end: Node, speed: float = NORMAL_SPEED,
                                   should_pause: Optional[Callable[[], bool]] = None,
                                   should_stop: Optional[Callable[[], bool]] = None) -> int:
        """
        Reconstructs and visualizes the shortest path found by Dijkstra's algorithm.
        This process starts from the `end` node and backtracks to the `start` node
        by following the `previous` pointers established during the Dijkstra's run.
        Each node on the path is colored `YELLOW` with a short delay for animation.

        Args:
            `end` (Node): The `Node` object from which to start path reconstruction.
                          This should be the same `end` node passed to Dijkstra's.
            `speed` (float, optional): The animation speed for path visualization.
                                     Defaults to `NORMAL_SPEED`. The delay is usually
                                     slightly longer here to make the final path more prominent.
            `should_pause` (Optional[Callable[[], bool]]): A callable that returns `True` if the
                                                            visualization should pause.
            `should_stop` (Optional[Callable[[], bool]]): A callable that returns `True` if the
                                                           visualization should terminate immediately.

        Returns:
            `int`: The length of the shortest path (number of steps/nodes, excluding the start node).
        """
        # Assign default no-op functions if callbacks are not provided.
        if should_pause is None:
            should_pause = lambda: False
        if should_stop is None:
            should_stop = lambda: False

        path_length = 0
        current = end
        path_nodes: List[Node] = [] # List to store nodes that form the path (excluding the start node).

        # Traverse backward from the `end` node using the `previous` pointers
        # until the `start` node (which has `previous` as `None`) is reached.
        while current.previous:
            current = current.previous
            # Ensure the start node itself is not marked as part of the 'path' path.
            if current.color != NODE_START:
                path_nodes.append(current)
                path_length += 1 # Increment path length for each node added.

        # Animate path reconstruction in reverse order, which means
        # from the node *next to the start* towards the end node,
        # giving a visual flow from start to end.
        for node in reversed(path_nodes):
            # --- External Control Checks ---
            # Check if we should stop completely.
            if should_stop():
                return path_length

            # Handle pause state: busy-wait until unpaused or stopped.
            while should_pause() and not should_stop():
                time.sleep(0.1)

            # Check for stop request again after potential pause.
            if should_stop():
                return path_length
            # --- End External Control Checks ---

            node.make_path() # Change node color to `YELLOW` to indicate it's part of the path.

            # Introduce a slightly longer delay for path visualization to make it more noticeable.
            if speed > 0:
                time.sleep(speed * 2) # Delay is twice the normal speed.

        return path_length