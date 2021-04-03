import json
import util
import unittest


with open('test/test_bot_participant.json') as bot_participant_file:
    bot_participant = json.load(bot_participant_file)

with open('test/test_mid_participant.json') as mid_participant_file:
    mid_participant = json.load(mid_participant_file)

class ChampUtilTestCase(unittest.TestCase):
    def test_get_champ_id(self):
        self.assertEqual(util.get_champ_id("kaisa"), "145")
        self.assertEqual(util.get_champ_id("aatrox"), "266")
        self.assertEqual(util.get_champ_id("made-up-champ"), None)

    def test_get_champ_name(self):
        self.assertEqual(util.get_champ_name("145"), "Kaisa")
        self.assertEqual(util.get_champ_name(266), "Aatrox")
        self.assertEqual(util.get_champ_name(123456), None)


class ParticipantUtilTestCase(unittest.TestCase):
    def test_is_participant_bot(self):
        self.assertTrue(util.is_participant_bot(bot_participant))
        self.assertFalse(util.is_participant_bot(mid_participant))
