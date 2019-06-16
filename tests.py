import stats
import unittest

class GetSumID(unittest.TestCase):
    def test(self):
        self.assertEqual(stats.get_sum_id('woke bloke'), 'C8O-kooob0Y_Rl8rDRAOJCsKhhfnzWLpEdURkXUqmCwnktc')

class GetChampID(unittest.TestCase):
    def test(self):
        self.assertEqual(stats.get_champ_id('aatrox'), '266')
        self.assertEqual(stats.get_champ_id('Zyra'), '143')

if __name__ == '__main__':
    unittest.main(exit=False)