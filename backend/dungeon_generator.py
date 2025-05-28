import random
import json
import os
from typing import List, Tuple, Dict
from backend.pathfinding import find_path

class Room:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.connected = False

    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    def intersects(self, other: 'Room', padding: int = 1) -> bool:
        return (self.x - padding <= other.x + other.width and
                self.x + self.width + padding >= other.x and
                self.y - padding <= other.y + other.height and
                self.y + self.height + padding >= other.y)

class DungeonGenerator:
    def __init__(self, width: int = 80, height: int = 48):
        self.width = width
        self.height = height
        self.rooms: List[Room] = []
        self.corridors: List[Tuple[int, int]] = []
        self.dungeon: List[List[Dict]] = []
        
        # Load monster definitions
        try:
            # Get the absolute path to the project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            monsters_path = os.path.join(project_root, 'data', 'monsters.json')
            
            with open(monsters_path, 'r') as f:
                self.monsters = json.load(f)['monsters']
                print(f"Loaded {len(self.monsters)} monsters successfully")
        except Exception as e:
            print(f"Error loading monsters.json: {str(e)}")
            self.monsters = []  # Initialize with empty list if loading fails
        
        # Tile definitions
        self.TILES = {
            'wall': {'char': '#', 'color': '#666666', 'walkable': False, 'visible': True},
            'floor': {'char': '.', 'color': '#cccccc', 'walkable': True, 'visible': True},
            'door': {'char': '+', 'color': '#8B4513', 'walkable': True, 'visible': True},
            'stairs_up': {'char': '<', 'color': '#00ff00', 'walkable': True, 'visible': True},
            'stairs_down': {'char': '>', 'color': '#ff0000', 'walkable': True, 'visible': True},
            'treasure': {'char': '$', 'color': '#ffd700', 'walkable': True, 'visible': True},
            'item': {'char': 'i', 'color': '#00ffff', 'walkable': True, 'visible': True},
            'fog': {'char': ' ', 'color': '#000000', 'walkable': False, 'visible': False},
            'water': {'char': '~', 'color': '#0000ff', 'walkable': False, 'visible': True},
            'trap': {'char': '^', 'color': '#ff00ff', 'walkable': True, 'visible': False}
        }
        
        # Character colors by class
        self.CLASS_COLORS = {
            'Fighter': '#ff0000',    # Red
            'Magic-User': '#0000ff', # Blue
            'Cleric': '#ffff00',     # Yellow
            'Thief': '#00ff00',      # Green
            'Ranger': '#ffa500',     # Orange
            'Paladin': '#ff00ff',    # Magenta
            'Druid': '#008000',      # Dark Green
            'Illusionist': '#800080', # Purple
            'Bard': '#00ffff'        # Cyan
        }

    def generate(self, min_rooms: int = 12, max_rooms: int = 20) -> List[List[Dict]]:
        """Generate a new dungeon level"""
        # Initialize empty map with walls
        self.dungeon = [[self.TILES['wall'].copy() for _ in range(self.width)] for _ in range(self.height)]
        self.rooms = []
        self.corridors = []

        # Generate rooms
        num_rooms = random.randint(min_rooms, max_rooms)
        for _ in range(num_rooms):
            self._try_add_room()

        # Connect rooms with corridors
        self._connect_rooms()

        # Add doors
        self._add_doors()

        # Add stairs
        self._add_stairs()

        # Add monsters and treasure
        self._add_monsters_and_treasure()

        # Add water features
        self._add_water_features()

        # Add traps
        self._add_traps()

        # Add fog of war
        self._add_fog_of_war()

        return self.dungeon

    def _try_add_room(self, max_attempts: int = 100) -> bool:
        """Try to add a room to the dungeon"""
        for _ in range(max_attempts):
            # Random room dimensions
            width = random.randint(5, 12)
            height = random.randint(5, 8)
            
            # Random position
            x = random.randint(1, self.width - width - 1)
            y = random.randint(1, self.height - height - 1)
            
            new_room = Room(x, y, width, height)
            
            # Check if room overlaps with existing rooms
            if not any(new_room.intersects(room) for room in self.rooms):
                self.rooms.append(new_room)
                self._carve_room(new_room)
                return True
        
        return False

    def _carve_room(self, room: Room) -> None:
        """Carve out a room in the dungeon"""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if 0 <= y < self.height and 0 <= x < self.width:
                    self.dungeon[y][x] = self.TILES['floor'].copy()

    def _connect_rooms(self) -> None:
        """Connect rooms with corridors"""
        for i in range(len(self.rooms) - 1):
            start = self.rooms[i].center()
            end = self.rooms[i + 1].center()
            self._carve_corridor(start, end)

    def _carve_corridor(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """Carve a corridor between two points"""
        x1, y1 = start
        x2, y2 = end

        # Randomly decide whether to go horizontal or vertical first
        if random.random() < 0.5:
            # Horizontal then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.dungeon[y1][x] = self.TILES['floor'].copy()
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.dungeon[y][x2] = self.TILES['floor'].copy()
        else:
            # Vertical then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.dungeon[y][x1] = self.TILES['floor'].copy()
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.dungeon[y2][x] = self.TILES['floor'].copy()

    def _add_doors(self) -> None:
        """Add doors to room entrances"""
        for room in self.rooms:
            # Check each wall for potential door placement
            for x in range(room.x, room.x + room.width):
                for y in range(room.y, room.y + room.height):
                    if self._is_valid_door_position(x, y):
                        if random.random() < 0.3:  # 30% chance to place a door
                            self.dungeon[y][x] = self.TILES['door'].copy()

    def _is_valid_door_position(self, x: int, y: int) -> bool:
        """Check if a position is valid for a door"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Check if position is a wall
        if self.dungeon[y][x]['char'] != '#':
            return False
        
        # Check if adjacent to floor
        floor_count = 0
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.width and 0 <= ny < self.height and 
                self.dungeon[ny][nx]['char'] == '.'):
                floor_count += 1
        
        return floor_count == 2  # Door should connect exactly two floor tiles

    def _add_stairs(self) -> None:
        """Add up and down stairs to the dungeon"""
        # Add up stairs in first room
        if self.rooms:
            x, y = self.rooms[0].center()
            self.dungeon[y][x] = self.TILES['stairs_up'].copy()

        # Add down stairs in last room
        if self.rooms:
            x, y = self.rooms[-1].center()
            self.dungeon[y][x] = self.TILES['stairs_down'].copy()

    def _add_monsters_and_treasure(self) -> None:
        """Add monsters and treasure to the dungeon"""
        if not self.monsters:
            print("Warning: No monsters available to place")
            return
            
        for room in self.rooms[1:-1]:  # Skip first and last rooms (stairs)
            # 50% chance to add a monster
            if random.random() < 0.5:
                # Try up to 10 times to find a valid position
                for _ in range(10):
                    x = random.randint(room.x + 1, room.x + room.width - 2)
                    y = random.randint(room.y + 1, room.y + room.height - 2)
                    if self.dungeon[y][x]['char'] == '.':
                        try:
                            monster = random.choice(self.monsters)
                            # Ensure monster has required fields
                            if 'display_char' not in monster:
                                monster['display_char'] = monster['name'][0].upper()
                            if 'color' not in monster:
                                monster['color'] = '#ff0000'  # Default to red
                                
                            self.dungeon[y][x] = {
                                'char': monster['display_char'],
                                'color': monster['color'],
                                'walkable': False,
                                'visible': True,
                                'monster_data': monster
                            }
                            print(f"Placed monster {monster['name']} at ({x}, {y})")
                            break
                        except Exception as e:
                            print(f"Error placing monster: {str(e)}")
                            continue

            # 30% chance to add treasure
            if random.random() < 0.3:
                # Try up to 10 times to find a valid position
                for _ in range(10):
                    x = random.randint(room.x + 1, room.x + room.width - 2)
                    y = random.randint(room.y + 1, room.y + room.height - 2)
                    if self.dungeon[y][x]['char'] == '.':
                        self.dungeon[y][x] = self.TILES['treasure'].copy()
                        break

    def _add_water_features(self) -> None:
        """Add water features to the dungeon"""
        for room in self.rooms:
            if random.random() < 0.2:  # 20% chance for water in a room
                water_x = random.randint(room.x + 1, room.x + room.width - 2)
                water_y = random.randint(room.y + 1, room.y + room.height - 2)
                self.dungeon[water_y][water_x] = self.TILES['water'].copy()

    def _add_traps(self) -> None:
        """Add traps to the dungeon"""
        for room in self.rooms[1:-1]:  # Skip first and last rooms
            if random.random() < 0.3:  # 30% chance for trap in a room
                trap_x = random.randint(room.x + 1, room.x + room.width - 2)
                trap_y = random.randint(room.y + 1, room.y + room.height - 2)
                if self.dungeon[trap_y][trap_x]['char'] == '.':
                    self.dungeon[trap_y][trap_x] = self.TILES['trap'].copy()

    def _add_fog_of_war(self) -> None:
        """Add fog of war to the dungeon"""
        for y in range(self.height):
            for x in range(self.width):
                if self.dungeon[y][x]['char'] == '#':
                    continue
                self.dungeon[y][x]['visible'] = False

    def reveal_area(self, x: int, y: int, radius: int = 5) -> None:
        """Reveal an area around a point"""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.width and 0 <= ny < self.height and
                    dx*dx + dy*dy <= radius*radius):
                    self.dungeon[ny][nx]['visible'] = True

    def get_empty_position(self) -> Tuple[int, int]:
        """Get a random empty position in the dungeon"""
        while True:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.dungeon[y][x]['char'] == '.':
                return (x, y)

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is valid for movement"""
        return (0 <= x < self.width and
                0 <= y < self.height and
                self.dungeon[y][x]['char'] != '#')

    def place_party(self, party: List[Dict]) -> bool:
        """Place the party members in the dungeon using A* pathfinding"""
        if not party:
            return False
            
        # Find a suitable starting position on the left side
        start_x = 1
        start_y = self.height // 2
        
        # Find the first valid floor tile
        while start_x < self.width // 4:  # Look in the left quarter of the map
            if self.dungeon[start_y][start_x]['char'] == '.':
                break
            start_x += 1
        else:
            return False  # No valid starting position found
            
        # Place the first character (party leader)
        party[0]['position'] = {'x': start_x, 'y': start_y}
        self.dungeon[start_y][start_x] = {
            'char': '@',
            'color': self.CLASS_COLORS.get(party[0]['characterClass'], '#ffffff'),
            'walkable': True,
            'visible': True
        }
        
        # Place remaining party members using A* pathfinding
        for i in range(1, len(party)):
            # Calculate target position (one step behind the previous character)
            prev_char = party[i-1]
            target_x = prev_char['position']['x']
            target_y = prev_char['position']['y']
            
            # Find a path to the target position
            path = find_path(
                (start_x, start_y),
                (target_x, target_y),
                self.dungeon,
                self.width,
                self.height
            )
            
            if not path:
                continue  # Skip if no path found
                
            # Place character at the last position in the path
            pos_x, pos_y = path[-1]
            party[i]['position'] = {'x': pos_x, 'y': pos_y}
            self.dungeon[pos_y][pos_x] = {
                'char': '@',
                'color': self.CLASS_COLORS.get(party[i]['characterClass'], '#ffffff'),
                'walkable': True,
                'visible': True
            }
            
        return True 