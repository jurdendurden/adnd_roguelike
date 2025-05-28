from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from backend.game_state import GameState
from backend.adnd_rules import ADnDRules
from backend.dungeon_generator import DungeonGenerator
from backend.pathfinding import find_path
import os
import random
from backend.spell_utils import generate_illusionist_spells, generate_magic_user_spells

app = Flask(__name__, 
            static_folder='../static',
            template_folder='../templates')
CORS(app)  # Enable CORS for all routes
game_state = GameState()
dungeon_generator = DungeonGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game/new', methods=['POST'])
def new_game():
    try:
        # Reset game state
        game_state.party = []
        game_state.current_level = 1
        game_state.in_combat = False
        game_state.combat = None
        
        # Generate new dungeon
        game_state.dungeon = dungeon_generator.generate()
        
        # Initialize empty party positions
        for character in game_state.party:
            character['position'] = {'x': 0, 'y': 0}
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error in new_game: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 500

@app.route('/api/character/create', methods=['POST'])
def create_character():
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'race', 'characterClass', 'abilities']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create character object
    character = {
        'name': data['name'],
        'race': data['race'],
        'characterClass': data['characterClass'],
        'level': 1,
        'experience': 0,
        'abilities': data['abilities'],
        'hitPoints': ADnDRules.calculate_hit_points(
            data['characterClass'],
            1,
            ADnDRules.get_ability_modifier(data['abilities']['CON'])
        ),
        'maxHitPoints': ADnDRules.calculate_hit_points(
            data['characterClass'],
            1,
            ADnDRules.get_ability_modifier(data['abilities']['CON'])
        ),
        'armorClass': 10,
        'thac0': ADnDRules.calculate_thac0(data['characterClass'], 1),
        'savingThrows': ADnDRules.calculate_saving_throws(data['characterClass'], 1),
        'inventory': [],
        'equipment': {
            'weapon': None,
            'armor': None,
            'shield': None,
            'helmet': None
        },
        'spells': {},
        'spellSlots': {},
        'gold': ADnDRules.calculate_starting_gold(data['characterClass']),
        'silver': 0,
        'copper': 0,
        'position': {'x': 0, 'y': 0}
    }
    
    # Generate starting spells for illusionists
    if data['characterClass'] == 'Illusionist':
        print("Generating spells for Illusionist...")  # Debug log
        character['spells'] = generate_illusionist_spells()
        print(f"Generated spells: {character['spells']}")  # Debug log
        character['spellSlots'] = {'1': 1}  # Starting spell slots for level 1
        print(f"Set spell slots: {character['spellSlots']}")  # Debug log
    # Generate starting spells for magic users
    elif data['characterClass'] == 'Magic-User':
        print("Generating spells for Magic-User...")  # Debug log
        character['spells'] = generate_magic_user_spells()
        print(f"Generated spells: {character['spells']}")  # Debug log
        character['spellSlots'] = {'1': 1}  # Starting spell slots for level 1
        print(f"Set spell slots: {character['spellSlots']}")  # Debug log
    
    # Add character to party
    if game_state.add_character(character):
        print(f"Added character to party: {character}")  # Debug log
        return jsonify(character)
    else:
        return jsonify({'error': 'Party is full'}), 400

@app.route('/api/game/state', methods=['GET'])
def get_game_state():
    return jsonify(game_state.to_dict())

@app.route('/api/game/move', methods=['POST'])
def move_party():
    data = request.json
    direction = data.get('direction')
    
    if not direction:
        return jsonify({'error': 'Missing direction'}), 400
    
    # Get party position (assuming first character's position)
    if not game_state.party:
        return jsonify({'error': 'No party members'}), 400
    
    # Get leader's current position
    leader = game_state.party[0]
    current_x = leader['position']['x']
    current_y = leader['position']['y']
    
    # Calculate new position for leader
    new_x, new_y = current_x, current_y
    if direction == 'north':
        new_y -= 1
    elif direction == 'south':
        new_y += 1
    elif direction == 'east':
        new_x += 1
    elif direction == 'west':
        new_x -= 1
    
    # Check if new position is valid
    if not dungeon_generator.is_valid_position(new_x, new_y):
        return jsonify({'success': False, 'message': 'Cannot move there'})
    
    # Store previous positions for following characters
    previous_positions = []
    
    # Move each character in sequence
    for i, character in enumerate(game_state.party):
        if i == 0:
            # Move leader to new position
            character['position']['x'] = new_x
            character['position']['y'] = new_y
            previous_positions.append((new_x, new_y))
        else:
            # For following characters, find path to previous character's old position
            prev_char = game_state.party[i-1]
            target_x, target_y = previous_positions[-1]
            
            # Find path using A* pathfinding
            path = find_path(
                (character['position']['x'], character['position']['y']),
                (target_x, target_y),
                game_state.dungeon,
                dungeon_generator.width,
                dungeon_generator.height
            )
            
            if path and len(path) > 1:
                # Move to next position in path
                next_x, next_y = path[1]  # path[0] is current position
                character['position']['x'] = next_x
                character['position']['y'] = next_y
                previous_positions.append((next_x, next_y))
            else:
                # If no path found, stay in place
                previous_positions.append((character['position']['x'], character['position']['y']))
    
    # Reveal area around party leader
    dungeon_generator.reveal_area(new_x, new_y)
    
    # Check for special tiles at leader's position
    tile = game_state.dungeon[new_y][new_x]
    message = None
    
    if tile.get('monster_data'):
        monster = tile['monster_data']
        message = f"You encounter a {monster['name']}!"
    elif tile['char'] == '$':
        message = "You found treasure!"
    elif tile['char'] == '<':
        message = "You found stairs leading up!"
    elif tile['char'] == '>':
        message = "You found stairs leading down!"
    elif tile['char'] == '+':
        message = "You found a door!"
    elif tile['char'] == '~':
        message = "You found water!"
    elif tile['char'] == '^':
        message = "You found a trap!"
    elif tile['char'] == 'i':
        message = "You found an item!"
    
    return jsonify({
        'success': True,
        'gameState': game_state.to_dict(),
        'message': message
    })

@app.route('/api/game/save', methods=['POST'])
def save_game():
    data = request.json
    slot_name = data.get('slot_name', 'autosave')
    
    if game_state.save_game(slot_name):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to save game'}), 500

@app.route('/api/game/load', methods=['GET'])
def load_game():
    slot_name = request.args.get('slot_name', 'autosave')
    
    if game_state.load_game(slot_name):
        return jsonify(game_state.to_dict())
    else:
        return jsonify({'error': 'Failed to load game'}), 500

@app.route('/api/rules/ability-modifier', methods=['POST'])
def get_ability_modifier():
    data = request.json
    score = data.get('score')
    if score is None:
        return jsonify({'error': 'Missing ability score'}), 400
    return jsonify({'modifier': ADnDRules.get_ability_modifier(score)})

@app.route('/api/rules/xp-for-level', methods=['POST'])
def get_xp_for_level():
    data = request.json
    character_class = data.get('characterClass')
    level = data.get('level')
    if not character_class or level is None:
        return jsonify({'error': 'Missing character class or level'}), 400
    return jsonify({'xp': ADnDRules.calculate_xp_for_level(character_class, level)})

@app.route('/api/rules/saving-throws', methods=['POST'])
def get_saving_throws():
    data = request.json
    character_class = data.get('characterClass')
    level = data.get('level')
    if not character_class or level is None:
        return jsonify({'error': 'Missing character class or level'}), 400
    return jsonify(ADnDRules.calculate_saving_throws(character_class, level))

@app.route('/api/party/generate', methods=['POST'])
def generate_party():
    """Generate a full party of 4 characters with random class/race combinations"""
    try:
        # Clear existing party
        game_state.party = []
        
        # Define available classes and races
        available_classes = [
            'Fighter', 'Magic-User', 'Cleric', 'Thief', 'Ranger',
            'Paladin', 'Druid', 'Illusionist', 'Bard'
        ]
        
        available_races = [
            'Human', 'Elf', 'Dwarf', 'Halfling', 'Gnome',
            'Half-Orc', 'Half-Elf', 'Lizardfolk', 'Tabaxi', 'Goblin'
        ]
        
        # Generate each character
        for i in range(4):
            # Randomly select class and race
            character_class = random.choice(available_classes)
            race = random.choice(available_races)
            
            # Keep trying until we get a valid combination
            while True:
                # Roll abilities
                abilities = ADnDRules.roll_ability_scores()
                
                # Apply racial modifiers
                abilities = ADnDRules.apply_racial_modifiers(abilities, race)
                
                # Check if this combination is valid
                if ADnDRules.check_class_requirements(abilities, character_class, race):
                    break
                
                # If not valid, try a different race
                race = random.choice(available_races)
            
            # Calculate character stats
            con_modifier = ADnDRules.get_ability_modifier(abilities['CON'])
            hit_points = ADnDRules.calculate_hit_points(character_class, 1, con_modifier)
            thac0 = ADnDRules.calculate_thac0(character_class, 1)
            saving_throws = ADnDRules.calculate_saving_throws(character_class, 1)
            
            # Create character
            character = {
                'name': f"{character_class} {i+1}",
                'race': race,
                'characterClass': character_class,
                'level': 1,
                'experience': 0,
                'abilities': abilities,
                'hitPoints': hit_points,
                'maxHitPoints': hit_points,
                'armorClass': 10,
                'thac0': thac0,
                'savingThrows': saving_throws,
                'inventory': [],
                'equipment': {
                    'weapon': None,
                    'armor': None,
                    'shield': None,
                    'helmet': None
                },
                'gold': ADnDRules.calculate_starting_gold(character_class),
                'silver': 0,
                'copper': 0,
                'spells': {},
                'spellSlots': {},
                'position': {'x': 0, 'y': 0}
            }
            
            # Generate starting spells for illusionists
            if character_class == 'Illusionist':
                character['spells'] = generate_illusionist_spells()
                character['spellSlots'] = {'1': 1}  # Starting spell slots for level 1
            # Generate starting spells for magic users
            elif character_class == 'Magic-User':
                character['spells'] = generate_magic_user_spells()
                character['spellSlots'] = {'1': 1}  # Starting spell slots for level 1
            
            game_state.add_character(character)
        
        # Generate a new dungeon if one doesn't exist
        if not game_state.dungeon:
            game_state.dungeon = dungeon_generator.generate()
        
        # Place party members in the dungeon
        if not dungeon_generator.place_party(game_state.party):
            return jsonify({'error': 'Failed to place party in dungeon'}), 500
        
        return jsonify({
            'status': 'success',
            'party': game_state.party
        })
    except Exception as e:
        print(f"Error generating party: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 