import json
import util
import unittest

class ChampUtilTestCase(unittest.TestCase):
    def test_get_champ_id(self):
        self.assertEqual(util.get_champ_id("kaisa"), "145")
        self.assertEqual(util.get_champ_id("aatrox"), "266")
        self.assertEqual(util.get_champ_id("made-up-champ"), None)

    def test_get_champ_name(self):
        self.assertEqual(util.get_champ_name("145"), "kaisa")
        self.assertEqual(util.get_champ_name(266), "aatrox")
        self.assertEqual(util.get_champ_name(123456), None)


class PlayerUtilTestCase(unittest.TestCase):
    with open('test_player.json') as player_file:
        sample_player = json.load(player_file)

    def test_is_player_bot(self):
        self.assertTrue(util.is_player_bot(sample_player))

