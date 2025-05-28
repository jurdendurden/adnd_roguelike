import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class GameState:
    def __init__(self):
        self.party: List[Dict] = []
        self.current_level: int = 1
        self.dungeon: List[List[str]] = []
        self.in_combat: bool = False
        self.combat: Optional[Dict] = None
        self.messages: List[str] = []
        self.save_slots: Dict[str, Dict] = {}

    def add_character(self, character: Dict) -> bool:
        """Add a character to the party"""
        if len(self.party) < 4:
            self.party.append(character)
            return True
        return False

    def remove_character(self, character_index: int) -> bool:
        """Remove a character from the party"""
        if 0 <= character_index < len(self.party):
            self.party.pop(character_index)
            return True
        return False

    def get_character(self, character_index: int) -> Optional[Dict]:
        """Get a character from the party"""
        if 0 <= character_index < len(self.party):
            return self.party[character_index]
        return None

    def update_character(self, character_index: int, updates: Dict) -> bool:
        """Update a character's stats"""
        if 0 <= character_index < len(self.party):
            self.party[character_index].update(updates)
            return True
        return False

    def add_message(self, message: str) -> None:
        """Add a message to the game log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.messages.append(f"[{timestamp}] {message}")
        # Keep only the last 100 messages
        if len(self.messages) > 100:
            self.messages = self.messages[-100:]

    def save_game(self, slot_name: str) -> bool:
        """Save the current game state"""
        try:
            save_data = {
                'party': self.party,
                'current_level': self.current_level,
                'dungeon': self.dungeon,
                'in_combat': self.in_combat,
                'combat': self.combat,
                'messages': self.messages,
                'timestamp': datetime.now().isoformat()
            }
            
            # Create saves directory if it doesn't exist
            os.makedirs('saves', exist_ok=True)
            
            # Save to file
            with open(f'saves/{slot_name}.json', 'w') as f:
                json.dump(save_data, f, indent=2)
            
            # Update save slots
            self.save_slots[slot_name] = {
                'timestamp': save_data['timestamp'],
                'party_size': len(self.party)
            }
            
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, slot_name: str) -> bool:
        """Load a saved game state"""
        try:
            with open(f'saves/{slot_name}.json', 'r') as f:
                save_data = json.load(f)
            
            self.party = save_data['party']
            self.current_level = save_data['current_level']
            self.dungeon = save_data['dungeon']
            self.in_combat = save_data['in_combat']
            self.combat = save_data['combat']
            self.messages = save_data['messages']
            
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    def list_save_slots(self) -> Dict[str, Dict]:
        """List all available save slots"""
        self.save_slots = {}
        try:
            if os.path.exists('saves'):
                for filename in os.listdir('saves'):
                    if filename.endswith('.json'):
                        slot_name = filename[:-5]  # Remove .json extension
                        with open(f'saves/{filename}', 'r') as f:
                            save_data = json.load(f)
                            self.save_slots[slot_name] = {
                                'timestamp': save_data['timestamp'],
                                'party_size': len(save_data['party'])
                            }
        except Exception as e:
            print(f"Error listing save slots: {e}")
        
        return self.save_slots

    def delete_save(self, slot_name: str) -> bool:
        """Delete a saved game"""
        try:
            if os.path.exists(f'saves/{slot_name}.json'):
                os.remove(f'saves/{slot_name}.json')
                if slot_name in self.save_slots:
                    del self.save_slots[slot_name]
                return True
        except Exception as e:
            print(f"Error deleting save: {e}")
        return False

    def to_dict(self) -> Dict:
        """Convert game state to dictionary"""
        # Create a deep copy of the dungeon to avoid modifying the original
        dungeon_copy = []
        for row in self.dungeon:
            row_copy = []
            for cell in row:
                # Create a new dict for each cell to avoid reference issues
                cell_copy = cell.copy()
                # Ensure monster_data is included if present
                if 'monster_data' in cell:
                    cell_copy['monster_data'] = cell['monster_data']
                row_copy.append(cell_copy)
            dungeon_copy.append(row_copy)

        return {
            'party': self.party,
            'current_level': self.current_level,
            'dungeon': dungeon_copy,
            'in_combat': self.in_combat,
            'combat': self.combat,
            'messages': self.messages
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'GameState':
        """Create game state from dictionary"""
        game_state = cls()
        game_state.party = data['party']
        game_state.current_level = data['current_level']
        game_state.dungeon = data['dungeon']
        game_state.in_combat = data['in_combat']
        game_state.combat = data['combat']
        game_state.messages = data['messages']
        return game_state 