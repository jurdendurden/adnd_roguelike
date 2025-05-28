import unittest
from backend.adnd_rules import ADnDRules
from backend.game_state import GameState
from backend.dungeon_generator import DungeonGenerator

class TestADnDRules(unittest.TestCase):
    def test_ability_scores(self):
        abilities = ADnDRules.roll_ability_scores()
        self.assertEqual(len(abilities), 6)
        for score in abilities.values():
            self.assertTrue(3 <= score <= 18)

    def test_racial_modifiers(self):
        abilities = {'STR': 10, 'DEX': 10, 'CON': 10, 'INT': 10, 'WIS': 10, 'CHA': 10}
        modified = ADnDRules.apply_racial_modifiers(abilities, 'Elf')
        self.assertEqual(modified['DEX'], 11)
        self.assertEqual(modified['CON'], 9)

    def test_hit_points(self):
        hp = ADnDRules.calculate_hit_points('Fighter', 1, 0)
        self.assertTrue(1 <= hp <= 10)

class TestGameState(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()

    def test_add_character(self):
        character = {
            'name': 'Test',
            'race': 'Human',
            'characterClass': 'Fighter',
            'level': 1
        }
        self.assertTrue(self.game_state.add_character(character))
        self.assertEqual(len(self.game_state.party), 1)

    def test_party_limit(self):
        for i in range(5):
            character = {
                'name': f'Test{i}',
                'race': 'Human',
                'characterClass': 'Fighter',
                'level': 1
            }
            if i < 4:
                self.assertTrue(self.game_state.add_character(character))
            else:
                self.assertFalse(self.game_state.add_character(character))

class TestDungeonGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = DungeonGenerator()

    def test_dungeon_generation(self):
        dungeon = self.generator.generate()
        self.assertEqual(len(dungeon), 24)  # Height
        self.assertEqual(len(dungeon[0]), 80)  # Width

    def test_room_generation(self):
        dungeon = self.generator.generate()
        # Check if there are any rooms (floor tiles)
        has_rooms = any('.' in row for row in dungeon)
        self.assertTrue(has_rooms)

if __name__ == '__main__':
    unittest.main() 