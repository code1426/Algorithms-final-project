from typing import Optional
import heapq
import pygame
import time
from grid import Grid
from node import Node
from constants import *

class Pathfinder:
    @staticmethod
    def dijkstra(grid: Grid, start: Optional[Node], end: Optional[Node], 
                window: Optional[pygame.Surface] = None, speed: float = NORMAL_SPEED) -> bool:
        """
        Dijkstra's shortest path algorithm with visualization
        Returns True if path is found, False otherwise
        """
        if not start or not end:
            return False

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
        # Adjust visualization frequency based on speed
        update_frequency = max(1, int(1 / (speed * 100))) if speed > 0 else 1

        while pq:
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

            # Update visualization periodically for better performance
            nodes_processed += 1
            if window and nodes_processed % update_frequency == 0:
                grid.draw(window)
                pygame.display.flip()
                if speed > 0:
                    time.sleep(speed)

        # No path found
        return False

    @staticmethod
    def reconstruct_path(end: Node, window: Optional[pygame.Surface] = None, 
                        grid: Optional[Grid] = None, speed: float = NORMAL_SPEED) -> int:
        """
        Reconstruct and visualize the shortest path
        Returns the length of the path
        """
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
            node.make_path()
            if window and grid:
                grid.draw(window)
                pygame.display.flip()
                if speed > 0:
                    time.sleep(speed * 2)  # Slightly slower for path visualization

        return path_length