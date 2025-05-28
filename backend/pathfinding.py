from typing import List, Tuple, Dict, Set
import heapq

class Node:
    def __init__(self, x: int, y: int, g_cost: float = 0, h_cost: float = 0):
        self.x = x
        self.y = y
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.parent = None

    @property
    def f_cost(self) -> float:
        return self.g_cost + self.h_cost

    def __lt__(self, other):
        return self.f_cost < other.f_cost

def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Calculate the Manhattan distance between two points"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(pos: Tuple[int, int], dungeon: List[List[Dict]], width: int, height: int) -> List[Tuple[int, int]]:
    """Get valid neighboring positions"""
    x, y = pos
    neighbors = []
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if (0 <= nx < width and 0 <= ny < height and 
            dungeon[ny][nx]['char'] == '.'):
            neighbors.append((nx, ny))
    return neighbors

def find_path(start: Tuple[int, int], end: Tuple[int, int], 
              dungeon: List[List[Dict]], width: int, height: int) -> List[Tuple[int, int]]:
    """Find a path using A* algorithm"""
    start_node = Node(start[0], start[1])
    end_node = Node(end[0], end[1])
    
    open_set: List[Node] = []
    closed_set: Set[Tuple[int, int]] = set()
    
    heapq.heappush(open_set, start_node)
    
    while open_set:
        current = heapq.heappop(open_set)
        
        if (current.x, current.y) == (end_node.x, end_node.y):
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]
        
        closed_set.add((current.x, current.y))
        
        for neighbor_pos in get_neighbors((current.x, current.y), dungeon, width, height):
            if neighbor_pos in closed_set:
                continue
                
            neighbor = Node(neighbor_pos[0], neighbor_pos[1])
            neighbor.g_cost = current.g_cost + 1
            neighbor.h_cost = heuristic(neighbor_pos, (end_node.x, end_node.y))
            neighbor.parent = current
            
            # Check if neighbor is already in open set with better path
            for node in open_set:
                if (node.x, node.y) == neighbor_pos and node.g_cost <= neighbor.g_cost:
                    break
            else:
                heapq.heappush(open_set, neighbor)
    
    return []  # No path found 