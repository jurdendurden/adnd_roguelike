import json
import random
import os
from typing import Dict, List

def load_spells(spell_file: str) -> Dict:
    """Load spells from a JSON file."""
    # Get the absolute path to the data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    spell_path = os.path.join(data_dir, os.path.basename(spell_file))
    
    with open(spell_path, 'r') as f:
        return json.load(f)

def get_random_spells(spell_file: str, level: int, count: int, spell_type: str = None) -> List[Dict]:
    """Get a random selection of spells of a specific level.
    
    Args:
        spell_file: Path to the spell JSON file
        level: Spell level (1-9)
        count: Number of spells to return
        spell_type: Type of spells to get (e.g., 'magic_user', 'cleric', 'druid', 'illusionist')
    """
    spells_data = load_spells(spell_file)
    
    # Get the appropriate level key
    level_key = f"{level}_level" if level > 1 else "first_level"
    
    # Get the list of spells for the specified level and type
    if spell_type:
        available_spells = spells_data.get(f"{spell_type}_spells", {}).get(level_key, [])
    else:
        # For backward compatibility, try illusionist spells first
        available_spells = spells_data.get("illusionist_spells", {}).get(level_key, [])
    
    # If there aren't enough spells available, return all of them
    if len(available_spells) <= count:
        return available_spells
    
    # Otherwise, randomly select the requested number of spells
    selected_spells = random.sample(available_spells, count)
    
    # Add memorized and cast properties to each spell
    for spell in selected_spells:
        spell['memorized'] = True  # All starting spells are memorized
        spell['cast'] = False  # No spells have been cast yet
    
    return selected_spells

def generate_magic_user_spells() -> Dict[str, List[Dict]]:
    """Generate starting spells for a magic user character."""
    # Get 4 random first level spells
    first_level_spells = get_random_spells("magic_user_spells.json", 1, 4, "magic_user")
    
    # Add Read Magic to the spells
    read_magic = {
        'name': 'Read Magic',
        'level': 1,
        'memorized': True,
        'cast': False
    }
    first_level_spells.append(read_magic)
    
    # Return the spells organized by level
    return {
        "1": first_level_spells
    }

def generate_illusionist_spells() -> Dict[str, List[Dict]]:
    """Generate starting spells for an illusionist character."""
    # Get 4 random first level spells
    first_level_spells = get_random_spells("illusionist_spells.json", 1, 4, "illusionist")
    
    # Return the spells organized by level
    return {
        "1": first_level_spells
    } 