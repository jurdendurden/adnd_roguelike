import random
from typing import Dict, List, Optional

class Character:
    def __init__(self, name: str, race: str, character_class: str):
        self.name = name
        self.race = race
        self.character_class = character_class
        self.level = 1
        self.experience = 0
        self.abilities = {
            'STR': 0, 'INT': 0, 'WIS': 0,
            'DEX': 0, 'CON': 0, 'CHA': 0
        }
        self.hit_points = 0
        self.max_hit_points = 0
        self.armor_class = 10
        self.thac0 = 20
        self.saving_throws = {
            'Death': 0, 'Wands': 0, 'Paralysis': 0,
            'Breath': 0, 'Spells': 0
        }
        self.inventory = []
        self.equipment = {
            'weapon': None,
            'armor': None,
            'shield': None,
            'helmet': None
        }
        self.spells = []
        self.spell_slots = {}

    def roll_ability_scores(self, method: str = '3d6') -> None:
        """Roll ability scores using specified method (3d6 or point-buy)"""
        if method == '3d6':
            for ability in self.abilities:
                self.abilities[ability] = sum(random.randint(1, 6) for _ in range(3))
        # TODO: Implement point-buy system

    def calculate_hit_points(self) -> None:
        """Calculate hit points based on class and CON modifier"""
        hit_dice = {
            'Fighter': 10, 'Paladin': 10, 'Ranger': 10,
            'Cleric': 8, 'Druid': 8,
            'Magic-User': 4, 'Illusionist': 4,
            'Thief': 6, 'Bard': 6
        }
        con_mod = (self.abilities['CON'] - 10) // 2
        self.max_hit_points = random.randint(1, hit_dice[self.character_class]) + con_mod
        self.hit_points = self.max_hit_points

    def calculate_thac0(self) -> None:
        """Calculate THAC0 based on class and level"""
        base_thac0 = {
            'Fighter': 20, 'Paladin': 20, 'Ranger': 20,
            'Cleric': 20, 'Druid': 20,
            'Magic-User': 20, 'Illusionist': 20,
            'Thief': 20, 'Bard': 20
        }
        level_bonus = (self.level - 1) // 3
        self.thac0 = base_thac0[self.character_class] - level_bonus

class Combat:
    def __init__(self):
        self.initiative = {}
        self.current_turn = 0
        self.combatants = []

    def roll_initiative(self) -> None:
        """Roll initiative for all combatants"""
        for combatant in self.combatants:
            self.initiative[combatant] = random.randint(1, 6)
        self.combatants.sort(key=lambda x: self.initiative[x], reverse=True)

    def resolve_attack(self, attacker: Character, defender: Character) -> bool:
        """Resolve an attack using THAC0 system"""
        attack_roll = random.randint(1, 20)
        if attack_roll >= attacker.thac0 - defender.armor_class:
            return True
        return False

    def calculate_damage(self, attacker: Character, weapon: Dict) -> int:
        """Calculate damage based on weapon and STR modifier"""
        str_mod = (attacker.abilities['STR'] - 10) // 2
        damage_dice = weapon['damage_dice']
        num_dice, dice_type = map(int, damage_dice.split('d'))
        damage = sum(random.randint(1, dice_type) for _ in range(num_dice))
        return max(1, damage + str_mod)

class GameState:
    def __init__(self):
        self.party = []
        self.current_level = 1
        self.dungeon = None
        self.in_combat = False
        self.combat = None

    def add_character(self, character: Character) -> None:
        """Add a character to the party"""
        if len(self.party) < 4:
            self.party.append(character)

    def move_party(self, direction: str) -> bool:
        """Move the party in the specified direction"""
        # TODO: Implement party movement
        return True

    def start_combat(self, monsters: List[Dict]) -> None:
        """Initialize combat with monsters"""
        self.in_combat = True
        self.combat = Combat()
        # TODO: Add monsters to combat 