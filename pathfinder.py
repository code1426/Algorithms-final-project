from typing import Optional, Callable
import heapq
import pygame
import time
from grid import Grid
from node import Node
from constants import *

class Pathfinder:
    @staticmethod
    def dijkstra(grid: Grid, start: Optional[Node], end: Optional[Node], 
                speed: float = NORMAL_SPEED) -> bool:
        """
        Original Dijkstra's shortest path algorithm with visualization
        Returns True if path is found, False otherwise
        """
        return Pathfinder.dijkstra_with_pause(grid, start, end, speed)

    @staticmethod
    def dijkstra_with_pause(grid: Grid, start: Optional[Node], end: Optional[Node], 
                           speed: float = NORMAL_SPEED,
                           should_pause: Optional[Callable[[], bool]] = None,
                           should_stop: Optional[Callable[[], bool]] = None) -> bool:
        """
        Dijkstra's shortest path algorithm with visualization and pause support
        Returns True if path is found, False otherwise
        """
        if not start or not end:
            return False

        # Default pause and stop functions
        if should_pause is None:
            should_pause = lambda: False
        if should_stop is None:
            should_stop = lambda: False

        # Reset all pathfinding attributes
        for row in grid.grid:
            for node in row:
                node.distance = float('inf')
                node.previous = None
                node.visited = False
                if not node.is_wall and node != start and node != end:
                    node.reset()

        # Initialize start node
        start.distance = 0
        
        # Priority queue: (distance, unique_id, node)
        # Using id() ensures consistent ordering when distances are equal
        pq = [(0, id(start), start)]
        unvisited_set = {start}

        nodes_processed = 0
        # Adjust sleep frequency based on speed - longer intervals for better performance
        sleep_frequency = max(1, int(50 / (speed * 1000))) if speed > 0 else 50

        while pq:
            # Check if we should stop completely
            if should_stop():
                return False
                
            # Handle pause state
            while should_pause() and not should_stop():
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            # Check again after potential pause
            if should_stop():
                return False

            _, _, current_node = heapq.heappop(pq)

            # Skip if this node was already processed with a shorter distance
            if current_node not in unvisited_set:
                continue

            # Remove from unvisited set and mark as visited
            unvisited_set.remove(current_node)
            current_node.visited = True

            # Found the target!
            if current_node == end:
                return True

            # Visualize current node (but not start node)
            if current_node != start:
                current_node.make_visited()

            # Update neighbors for current node
            grid.update_neighbors()
            
            # Check all neighbors
            for neighbor in current_node.neighbors:
                if neighbor.visited:
                    continue

                # Calculate new distance through current node
                new_distance = current_node.distance + 1

                # If we found a shorter path to this neighbor
                if new_distance < neighbor.distance:
                    neighbor.distance = new_distance
                    neighbor.previous = current_node
                    
                    # Add to queue if not already there with better distance
                    if neighbor not in unvisited_set:
                        unvisited_set.add(neighbor)
                        heapq.heappush(pq, (new_distance, id(neighbor), neighbor))
                        
                        # Visualize neighbor being considered (but not end node)
                        if neighbor != end:
                            neighbor.make_unvisited_neighbor()

            # Add sleep delay periodically for visualization
            # REMOVED: All pygame display updates from this thread
            nodes_processed += 1
            if nodes_processed % sleep_frequency == 0 and speed > 0:
                time.sleep(speed)

        # No path found
        return False

    @staticmethod
    def reconstruct_path(end: Node, speed: float = NORMAL_SPEED) -> int:
        """
        Original reconstruct and visualize the shortest path
        Returns the length of the path
        """
        return Pathfinder.reconstruct_path_with_pause(end, speed)

    @staticmethod
    def reconstruct_path_with_pause(end: Node, speed: float = NORMAL_SPEED,
                                   should_pause: Optional[Callable[[], bool]] = None,
                                   should_stop: Optional[Callable[[], bool]] = None) -> int:
        """
        Reconstruct and visualize the shortest path with pause support
        Returns the length of the path
        """
        # Default pause and stop functions
        if should_pause is None:
            should_pause = lambda: False
        if should_stop is None:
            should_stop = lambda: False

        path_length = 0
        current = end
        path_nodes = []

        # Collect all path nodes (excluding start and end)
        while current.previous:
            current = current.previous
            if current.color != RED:  # Not the start node
                path_nodes.append(current)
                path_length += 1

        # Animate path reconstruction in reverse order (from start to end)
        for node in reversed(path_nodes):
            # Check if we should stop completely
            if should_stop():
                return path_length
                
            # Handle pause state
            while should_pause() and not should_stop():
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            # Check again after potential pause
            if should_stop():
                return path_length

            node.make_path()
            
            # REMOVED: All pygame display updates from this thread
            # Just add a delay for timing
            if speed > 0:
                time.sleep(speed * 2)  # Slightly slower for path visualization

        return path_length