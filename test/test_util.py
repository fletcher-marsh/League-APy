import json
from summoner import Summoner
import util
import unittest



with open('test/test_bot_participant.json') as bot_participant_file:
    bot_participant = json.load(bot_participant_file)

with open('test/test_mid_participant.json') as mid_participant_file:
    mid_participant = json.load(mid_participant_file)

with open('test/test_match.json') as match_file:
    test_match = json.load(match_file)

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

    def test_is_participant_on_blue(self):
        self.assertTrue(util.is_participant_on_blue(bot_participant))
        self.assertFalse(util.is_participant_on_blue(mid_participant))


class SummonerUtilTestCase(unittest.TestCase):
    def test_participant_id_for_summoner_in_match(self):
        test_sum_1 = Summoner(sum_id='KQz-bIZbhbAePHwBIv1YWSiObUmQ7-3VFeAvdzluh2_OiAY', offline=True)
        self.assertTrue(util.participant_id_for_summoner_in_match(test_sum_1, test_match))

        test_sum_2 = Summoner(sum_id='cZblwBWSNBQJyXmIyrvuHIhToxB7Zx92-8bmEOQbH_4emuc', offline=True)
        self.assertTrue(util.participant_id_for_summoner_in_match(test_sum_2, test_match))

    def test_is_summoner_on_blue_side_in_match(self):
        test_sum_1 = Summoner(sum_id='b4GC5iDhDIQzR05I_FWcsqXLI398w_fpEXuyfEnY3jjBkcE', offline=True)
        self.assertTrue(util.is_summoner_on_blue_side_in_match(test_sum_1, test_match))

        test_sum_2 = Summoner(sum_id='5XsnqsNCkNphk3nSWU3MfthVWDlL5cKEZUzjL8nUmTPOyQw', offline=True)
        self.assertFalse(util.is_summoner_on_blue_side_in_match(test_sum_2, test_match))
        
    def test_summoner_won_match(self):
        test_sum_1 = Summoner(sum_id='b4GC5iDhDIQzR05I_FWcsqXLI398w_fpEXuyfEnY3jjBkcE', offline=True)
        self.assertTrue(util.summoner_won_match(test_sum_1, test_match))

        test_sum_2 = Summoner(sum_id='5XsnqsNCkNphk3nSWU3MfthVWDlL5cKEZUzjL8nUmTPOyQw', offline=True)
        self.assertFalse(util.summoner_won_match(test_sum_2, test_match))


def make_test_participant(kills, deaths, assists, cs, vision):
    return {
        "stats": {
            "kills": kills,
            "deaths": deaths,
            "assists": assists,
            "totalMinionsKilled": cs,
            "visionScore": vision
        }
    }


class GroupParticipantsScoresTestCase(unittest.TestCase):
    def setUp(self):
        self.test_participants = [
            make_test_participant(5, 1, 3, 100, 19),
            make_test_participant(0, 0, 0, 0, 0),
            make_test_participant(10, 0, 3, 250, 30),
            make_test_participant(1, 7, 2, 50, 3)
        ]

    def test_kda_score(self):
        self.assertEqual(util.kda_score(self.test_participants), (16, 8, 8))
    
    def test_cs_score(self):
        self.assertEqual(util.cs_score(self.test_participants), 400)

    def test_vision_score(self):
        self.assertEqual(util.vision_score(self.test_participants), 52)


class SummonersInMatchTestCase(unittest.TestCase):
    def test_summoner_names_in_match(self):
        expected = [
            'NazSwaqq',
            'Mythical Genie',
            'ATF',
            'Syntinyl',
            'RosesForViolet',
            'who what',
            'SZed',
            'Megumi',
            'TheStormReborn',
            'NaCl Mine'
        ]
        actual = util.summoner_names_in_match(test_match)
        self.assertCountEqual(expected, actual)

    def test_summoner_ids_in_match(self):
        expected = [
            'b4GC5iDhDIQzR05I_FWcsqXLI398w_fpEXuyfEnY3jjBkcE',
            'zrYORzGayC5MjPlHHblAIUQ171xSvJAle3jtqm4D3juEpiI',
            'XTTSR-B1UjlrQGsf3r002msYIb60Rz2cV6_OAeckUCtvKxo',
            'MnQWQZHlXGaaDHR28XJe0aT5VO9wOuLmgLRl6-bLzGvToWQ',
            'KQz-bIZbhbAePHwBIv1YWSiObUmQ7-3VFeAvdzluh2_OiAY',
            '5XsnqsNCkNphk3nSWU3MfthVWDlL5cKEZUzjL8nUmTPOyQw',
            'cZblwBWSNBQJyXmIyrvuHIhToxB7Zx92-8bmEOQbH_4emuc',
            '3IsQcykq-vTjxujgQYMHErBiex2-LxwAt_MPvlUy_97g0RM',
            'wjf_bKubx3V_U1S7KQwTOmBxauE-G8HkF_xKihjDqTjBP_V5',
            'NtU1n6ur3SVvCn3P-p9vrLNmDyoK7kCpNx6aBdGxIx_bfxI'
        ]
        actual = util.summoner_ids_in_match(test_match)
        self.assertCountEqual(expected, actual)
