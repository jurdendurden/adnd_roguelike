import random
from typing import Dict, List, Optional, Tuple

class ADnDRules:
    # Class hit dice
    HIT_DICE = {
        'Fighter': 10,
        'Paladin': 10,
        'Ranger': 10,
        'Cleric': 8,
        'Druid': 8,
        'Magic-User': 4,
        'Illusionist': 4,
        'Thief': 6,
        'Bard': 6
    }

    # Base saving throws by class
    SAVING_THROWS = {
        'Fighter': {
            'Death': 14, 'Wands': 15, 'Paralysis': 16, 'Breath': 17, 'Spells': 17
        },
        'Paladin': {
            'Death': 14, 'Wands': 15, 'Paralysis': 16, 'Breath': 17, 'Spells': 17
        },
        'Ranger': {
            'Death': 14, 'Wands': 15, 'Paralysis': 16, 'Breath': 17, 'Spells': 17
        },
        'Cleric': {
            'Death': 11, 'Wands': 12, 'Paralysis': 14, 'Breath': 16, 'Spells': 15
        },
        'Druid': {
            'Death': 11, 'Wands': 12, 'Paralysis': 14, 'Breath': 16, 'Spells': 15
        },
        'Magic-User': {
            'Death': 13, 'Wands': 14, 'Paralysis': 13, 'Breath': 16, 'Spells': 15
        },
        'Illusionist': {
            'Death': 13, 'Wands': 14, 'Paralysis': 13, 'Breath': 16, 'Spells': 15
        },
        'Thief': {
            'Death': 13, 'Wands': 14, 'Paralysis': 12, 'Breath': 16, 'Spells': 15
        },
        'Bard': {
            'Death': 14, 'Wands': 15, 'Paralysis': 14, 'Breath': 16, 'Spells': 16
        }
    }

    # Ability score requirements by class
    CLASS_REQUIREMENTS = {
        'Fighter': {'STR': 9},
        'Paladin': {'STR': 12, 'CON': 9, 'WIS': 13, 'CHA': 17},
        'Ranger': {'STR': 13, 'DEX': 13, 'CON': 14, 'WIS': 14},
        'Cleric': {'WIS': 9},
        'Druid': {'WIS': 12, 'CHA': 15},
        'Magic-User': {'INT': 9},
        'Illusionist': {'DEX': 16, 'INT': 15},
        'Thief': {'DEX': 9},
        'Bard': {'DEX': 12, 'INT': 13, 'CHA': 15}
    }

    # Racial ability modifiers
    RACIAL_MODIFIERS = {
        'Human': {},
        'Elf': {'DEX': 1, 'CON': -1},
        'Dwarf': {'CON': 1, 'CHA': -1},
        'Halfling': {'DEX': 1, 'STR': -1},
        'Gnome': {'INT': 1, 'WIS': 1, 'STR': -1},
        'Half-Orc': {'STR': 1, 'CON': 1, 'CHA': -2, 'INT': -1},
        'Half-Elf': {'CHA': 1},
        'Lizardfolk': {'CON': 1, 'DEX': 1, 'INT': -1, 'CHA': -1},
        'Tabaxi': {'DEX': 2, 'STR': -1},
        'Goblin': {'DEX': 1, 'STR': -1, 'CON': -1}
    }

    # Racial class restrictions
    RACIAL_CLASS_RESTRICTIONS = {
        'Lizardfolk': ['Paladin'],
        'Goblin': ['Paladin']
    }

    @staticmethod
    def roll_ability_scores(method: str = '3d6') -> Dict[str, int]:
        """Roll ability scores using specified method"""
        abilities = {}
        if method == '3d6':
            for ability in ['STR', 'INT', 'WIS', 'DEX', 'CON', 'CHA']:
                abilities[ability] = sum(random.randint(1, 6) for _ in range(3))
        return abilities

    @staticmethod
    def apply_racial_modifiers(abilities: Dict[str, int], race: str) -> Dict[str, int]:
        """Apply racial modifiers to ability scores"""
        modifiers = ADnDRules.RACIAL_MODIFIERS.get(race, {})
        for ability, modifier in modifiers.items():
            abilities[ability] = max(3, min(18, abilities[ability] + modifier))
        return abilities

    @staticmethod
    def check_class_requirements(abilities: Dict[str, int], character_class: str, race: str) -> bool:
        """Check if ability scores meet class requirements and race restrictions"""
        # Check racial class restrictions
        restrictions = ADnDRules.RACIAL_CLASS_RESTRICTIONS.get(race, [])
        if character_class in restrictions:
            return False
            
        # Check ability score requirements
        requirements = ADnDRules.CLASS_REQUIREMENTS.get(character_class, {})
        return all(abilities[ability] >= score for ability, score in requirements.items())

    @staticmethod
    def calculate_hit_points(character_class: str, level: int, con_modifier: int) -> int:
        """Calculate hit points based on class, level, and CON modifier"""
        hit_dice = ADnDRules.HIT_DICE.get(character_class, 6)
        hp = 0
        
        # First level
        hp += random.randint(1, hit_dice) + con_modifier
        
        # Additional levels
        for _ in range(level - 1):
            hp += max(1, random.randint(1, hit_dice) + con_modifier)
        
        return max(1, hp)

    @staticmethod
    def calculate_thac0(character_class: str, level: int) -> int:
        """Calculate THAC0 based on class and level"""
        base_thac0 = 20
        level_bonus = (level - 1) // 3
        return base_thac0 - level_bonus

    @staticmethod
    def calculate_saving_throws(character_class: str, level: int) -> Dict[str, int]:
        """Calculate saving throws based on class and level"""
        base_saves = ADnDRules.SAVING_THROWS.get(character_class, {}).copy()
        level_bonus = (level - 1) // 3
        
        for save in base_saves:
            base_saves[save] = max(2, base_saves[save] - level_bonus)
        
        return base_saves

    @staticmethod
    def resolve_attack(attacker_thac0: int, defender_ac: int) -> bool:
        """Resolve an attack using THAC0 system"""
        attack_roll = random.randint(1, 20)
        return attack_roll >= attacker_thac0 - defender_ac

    @staticmethod
    def calculate_damage(weapon_damage: str, strength_modifier: int) -> int:
        """Calculate damage based on weapon and STR modifier"""
        num_dice, dice_type = map(int, weapon_damage.split('d'))
        damage = sum(random.randint(1, dice_type) for _ in range(num_dice))
        return max(1, damage + strength_modifier)

    @staticmethod
    def get_ability_modifier(score: int) -> int:
        """Get ability score modifier"""
        return (score - 10) // 2

    @staticmethod
    def check_morale(morale_score: int) -> bool:
        """Check if a monster passes its morale check"""
        roll = random.randint(1, 20)
        return roll <= morale_score

    @staticmethod
    def calculate_xp_for_level(character_class: str, level: int) -> int:
        """Calculate XP required for next level"""
        # Basic XP progression (simplified)
        base_xp = {
            'Fighter': 2000,
            'Paladin': 2250,
            'Ranger': 2250,
            'Cleric': 1500,
            'Druid': 2000,
            'Magic-User': 2500,
            'Illusionist': 2500,
            'Thief': 1250,
            'Bard': 2000
        }
        return base_xp.get(character_class, 2000) * (2 ** (level - 1))

    @staticmethod
    def calculate_starting_gold(character_class: str) -> int:
        """Calculate starting gold based on character class"""
        # Starting gold rules by class
        gold_rules = {
            'Fighter': {'dice': '5d4', 'multiplier': 10},
            'Paladin': {'dice': '6d4', 'multiplier': 10},
            'Ranger': {'dice': '5d4', 'multiplier': 10},
            'Magic-User': {'dice': '2d4', 'multiplier': 10},
            'Illusionist': {'dice': '2d4', 'multiplier': 10},
            'Cleric': {'dice': '3d4', 'multiplier': 10},
            'Druid': {'dice': '2d4', 'multiplier': 10},
            'Thief': {'dice': '2d4', 'multiplier': 10},
            'Assassin': {'dice': '4d4', 'multiplier': 10},
            'Monk': {'dice': '2d4', 'multiplier': 10},
            'Bard': {'dice': '3d4', 'multiplier': 10}
        }

        # Get the class rules
        rules = gold_rules.get(character_class)
        if not rules:
            return 0  # Default to 0 if class not found

        # Parse dice formula (e.g., "5d4" -> 5 dice, 4 sides)
        num_dice, sides = map(int, rules['dice'].split('d'))
        
        # Roll the dice and apply multiplier
        roll = sum(random.randint(1, sides) for _ in range(num_dice))
        return roll * rules['multiplier']