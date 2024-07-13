import unittest
from app import PokerGame  # Adjust the import based on the actual path of your PokerGame class

class TestPokerGame(unittest.TestCase):

    def setUp(self):
        # Initialize the PokerGame class
        self.poker_game = PokerGame()

    def set_community_cards(self, flop, turn, river):
        self.poker_game.community_cards = {
            'flop': flop,
            'turn': turn,
            'river': river
        }

    def test_01_royal_flush(self):
        self.poker_game.players_hands = {
            'Player 1': [('A', 'H'), ('K', 'H')],
            'Player 2': [('2', 'D'), ('3', 'C')]
        }
        self.set_community_cards([('Q', 'H'), ('J', 'H'), ('T', 'H')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Royal Flush test failed")

    def test_02_straight_flush(self):
        self.poker_game.players_hands = {
            'Player 1': [('9', 'H'), ('8', 'H')],
            'Player 2': [('2', 'D'), ('3', 'C')]
        }
        self.set_community_cards([('7', 'H'), ('6', 'H'), ('5', 'H')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Straight Flush test failed")

    def test_03_four_of_a_kind(self):
        self.poker_game.players_hands = {
            'Player 1': [('9', 'H'), ('9', 'D')],
            'Player 2': [('2', 'D'), ('3', 'C')]
        }
        self.set_community_cards([('9', 'S'), ('9', 'C'), ('5', 'H')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Four of a Kind test failed")

    def test_04_full_house(self):
        self.poker_game.players_hands = {
            'Player 1': [('9', 'H'), ('5', 'C')],
            'Player 2': [('2', 'D'), ('3', 'C')]
        }
        self.set_community_cards([('9', 'D'), ('9', 'S'), ('5', 'H')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Full House test failed")

    def test_05_flush(self):
        self.poker_game.players_hands = {
            'Player 1': [('A', 'H'), ('K', 'H')],
            'Player 2': [('2', 'D'), ('3', 'C')]
        }
        self.set_community_cards([('Q', 'H'), ('J', 'H'), ('9', 'H')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Flush test failed")

    def test_06_straight(self):
        self.poker_game.players_hands = {
            'Player 1': [('9', 'H'), ('8', 'D')],
            'Player 2': [('2', 'D'), ('3', 'C')]
        }
        self.set_community_cards([('7', 'S'), ('6', 'C'), ('5', 'H')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Straight test failed")

    def test_07_three_of_a_kind(self):
        self.poker_game.players_hands = {
            'Player 1': [('9', 'H'), ('9', 'D')],
            'Player 2': [('2', 'D'), ('3', 'C')]
        }
        self.set_community_cards([('9', 'S'), ('6', 'C'), ('5', 'H')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Three of a Kind test failed")

    def test_08_two_pairs(self):
        self.poker_game.players_hands = {
            'Player 1': [('9', 'H'), ('8', 'S')],
            'Player 2': [('2', 'D'), ('3', 'C')]
        }
        self.set_community_cards([('9', 'D'), ('8', 'C'), ('5', 'H')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Two Pairs test failed")

    def test_09_one_pair_two_pair(self):
        self.poker_game.players_hands = {
            'Player 1': [('9', 'H'), ('9', 'D')],
            'Player 2': [('2', 'D'), ('3', 'C')]
        }
        self.set_community_cards([('7', 'S'), ('6', 'C'), ('5', 'H')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 2', "One Pair vs two Pairs test failed")

    def test_10_high_card(self):
        self.poker_game.players_hands = {
            'Player 1': [('A', 'H'), ('K', 'D')],
            'Player 2': [('A', 'C'), ('Q', 'H')]
        }
        self.set_community_cards([('7', 'S'), ('6', 'C'), ('5', 'H')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "High Card test failed")

    def test_11_edge_case_duplicate_cards(self):
        self.poker_game.players_hands = {
            'Player 1': [('9', 'H'), ('9', 'H')],
            'Player 2': [('2', 'D'), ('3', 'C')]
        }
        self.set_community_cards([('7', 'S'), ('6', 'C'), ('5', 'H')], ('2', 'S'), ('3', 'S'))
        with self.assertRaises(ValueError, msg="Duplicate Cards test failed"):
            self.poker_game.determine_winner()

    def test_12_edge_case_invalid_card(self):
        self.poker_game.players_hands = {
            'Player 1': [('Z', 'H'), ('K', 'D')],
            'Player 2': [('2', 'D'), ('3', 'C')]
        }
        self.set_community_cards([('7', 'S'), ('6', 'C'), ('5', 'H')], ('2', 'S'), ('3', 'S'))
        with self.assertRaises(ValueError, msg="Invalid Card test failed"):
            self.poker_game.determine_winner()

    # Tie-breaking test cases
    def test_13_tie_breaker_high_card(self):
        self.poker_game.players_hands = {
            'Player 1': [('A', 'S'), ('K', 'D')],
            'Player 2': [('A', 'C'), ('K', 'H')]
        }
        self.set_community_cards([('Q', 'C'), ('J', 'H'), ('9', 'D')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'It\'s a tie!', "High Card tie-breaker test failed")

    def test_14_tie_breaker_one_pair(self):
        self.poker_game.players_hands = {
            'Player 1': [('A', 'S'), ('A', 'D')],
            'Player 2': [('A', 'C'), ('A', 'H')]
        }
        self.set_community_cards([('Q', 'C'), ('J', 'H'), ('9', 'D')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'It\'s a tie!', "One Pair tie-breaker test failed")

    def test_15_tie_breaker_two_pair(self):
        self.poker_game.players_hands = {
            'Player 1': [('A', 'S'), ('A', 'D')],
            'Player 2': [('A', 'C'), ('A', 'H')]
        }
        self.set_community_cards([('K', 'C'), ('K', 'H'), ('9', 'D')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'It\'s a tie!', "Two Pair tie-breaker test failed")

    def test_16_tie_breaker_three_of_a_kind(self):
        self.poker_game.players_hands = {
            'Player 1': [('A', 'S'), ('4', 'D')],
            'Player 2': [('A', 'D'), ('5', 'H')]
        }
        self.set_community_cards([('A', 'C'), ('A', 'H'), ('9', 'D')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 2', "Three of a Kind tie-breaker test failed")

    def test_17_tie_breaker_straight(self):
        self.poker_game.players_hands = {
            'Player 1': [('9', 'S'), ('8', 'D')],
            'Player 2': [('9', 'C'), ('8', 'H')]
        }
        self.set_community_cards([('7', 'C'), ('6', 'H'), ('5', 'D')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'It\'s a tie!', "Straight tie-breaker test failed")

    def test_18_tie_breaker_flush(self):
        self.poker_game.players_hands = {
            'Player 1': [('A', 'S'), ('K', 'S')],
            'Player 2': [('A', 'H'), ('K', 'H')]
        }
        self.set_community_cards([('Q', 'S'), ('J', 'S'), ('9', 'S')], ('2', 'D'), ('3', 'D'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Flush tie-breaker test failed")

    def test_19_tie_breaker_straight_ace_to_five(self):
        self.poker_game.players_hands = {
            'Player 1': [('A', 'S'), ('2', 'D')],
            'Player 2': [('9', 'C'), ('8', 'H')]
        }
        self.set_community_cards([('3', 'C'), ('4', 'H'), ('5', 'D')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Straight (Ace to Five) tie-breaker test failed")

    def test_20_tie_breaker_full_house(self):
        self.poker_game.players_hands = {
            'Player 1': [('A', 'S'), ('K', 'D')],
            'Player 2': [('A', 'C'), ('Q', 'H')]
        }
        self.set_community_cards([('A', 'D'), ('A', 'H'), ('K', 'H')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Full House tie-breaker test failed")

    def test_21_tie_breaker_four_of_a_kind(self):
        self.poker_game.players_hands = {
            'Player 1': [('A', 'S'), ('K', 'D')],
            'Player 2': [('2', 'C'), ('2', 'H')]
        }
        self.set_community_cards([('A', 'C'), ('A', 'H'), ('A', 'D')], ('2', 'S'), ('2', 'D'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Four of a Kind tie-breaker test failed")

    def test_22_tie_breaker_straight_flush(self):
        self.poker_game.players_hands = {
            'Player 1': [('9', 'S'), ('8', 'S')],
            'Player 2': [('8', 'H'), ('7', 'H')]
        }
        self.set_community_cards([('7', 'S'), ('6', 'S'), ('5', 'S')], ('2', 'D'), ('3', 'D'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Straight Flush tie-breaker test failed")

    # New tests
    def test_23_full_house_vs_full_house(self):
        self.poker_game.players_hands = {
            'Player 1': [('3', 'S'), ('3', 'D')],
            'Player 2': [('A', 'C'), ('A', 'H')]
        }
        self.set_community_cards([('3', 'C'), ('9', 'H'), ('2', 'D')], ('2', 'S'), ('2', 'C'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "Full House 33322 vs AA222 test failed")

    def test_24_straight_vs_straight(self):
        self.poker_game.players_hands = {
            'Player 1': [('4', 'S'), ('A', 'D')],
            'Player 2': [('4', 'C'), ('7', 'H')]
        }
        self.set_community_cards([('2', 'C'), ('3', 'H'), ('5', 'D')], ('6', 'S'), ('8', 'C'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 2', "Straight A2345 vs 45678 test failed")

    def test_25_one_pair_vs_one_pair(self):
        self.poker_game.players_hands = {
            'Player 1': [('K', 'S'), ('5', 'D')],
            'Player 2': [('K', 'C'), ('4', 'H')]
        }
        self.set_community_cards([('K', 'H'), ('J', 'H'), ('7', 'D')], ('3', 'S'), ('2', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 1', "One Pair KKJ75 vs One Pair KKJ74 test failed")

    def test_26_four_of_a_kind_vs_four_of_a_kind(self):
        self.poker_game.players_hands = {
            'Player 1': [('8', 'S'), ('8', 'D')],
            'Player 2': [('K', 'C'), ('K', 'H')]
        }
        self.set_community_cards([('A', 'C'), ('A', 'H'), ('A', 'D')], ('A', 'S'), ('7', 'D'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'Player 2', "Four of a Kind AAAA8 vs Four of a Kind AAAAK test failed")

    def test_27_tie_full_house(self):
        self.poker_game.players_hands = {
            'Player 1': [('3', 'S'), ('3', 'D')],
            'Player 2': [('3', 'C'), ('3', 'H')]
        }
        self.set_community_cards([('9', 'S'), ('9', 'H'), ('9', 'D')], ('2', 'S'), ('2', 'C'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'It\'s a tie!', "Tie Full House 99933 vs 99933 test failed")

    def test_28_tie_straight(self):
        self.poker_game.players_hands = {
            'Player 1': [('5', 'S'), ('A', 'D')],
            'Player 2': [('5', 'C'), ('A', 'H')]
        }
        self.set_community_cards([('2', 'C'), ('3', 'H'), ('4', 'D')], ('6', 'S'), ('7', 'C'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'It\'s a tie!', "Tie Straight A2345 vs A2345 test failed")

    def test_29_tie_one_pair(self):
        self.poker_game.players_hands = {
            'Player 1': [('K', 'S'), ('K', 'D')],
            'Player 2': [('K', 'C'), ('K', 'H')]
        }
        self.set_community_cards([('7', 'C'), ('4', 'H'), ('2', 'D')], ('3', 'S'), ('6', 'D'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'It\'s a tie!', "Tie One Pair KK764 vs KK764 test failed")

    def test_30_tie_flush(self):
        self.poker_game.players_hands = {
            'Player 1': [('Q', 'D'), ('J', 'D')],
            'Player 2': [('Q', 'H'), ('J', 'H')]
        }
        self.set_community_cards([('A', 'S'), ('K', 'S'), ('T', 'S')], ('2', 'S'), ('3', 'S'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'It\'s a tie!', "Tie Flush AKQJT vs AKQJT test failed")

    def test_31_tie_full_board(self):
        self.poker_game.players_hands = {
            'Player 1': [('7', 'S'), ('8', 'H')],
            'Player 2': [('5', 'D'), ('6', 'C')]
        }
        self.set_community_cards([('A', 'C'), ('K', 'H'), ('Q', 'D')], ('T', 'S'), ('9', 'H'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'It\'s a tie!', "Tie with full board AKQJT vs AKQJT test failed")

    def test_32_tie_same_hand(self):
        self.poker_game.players_hands = {
            'Player 1': [('K', 'S'), ('K', 'D')],
            'Player 2': [('K', 'C'), ('K', 'H')]
        }
        self.set_community_cards([('A', 'S'), ('Q', 'H'), ('J', 'C')], ('2', 'S'), ('3', 'H'))
        winner, best_hand, evaluation = self.poker_game.determine_winner()
        self.assertEqual(winner, 'It\'s a tie!', "Tie with same hand KKAQJ vs KKAQJ test failed")

if __name__ == '__main__':
    # Custom test runner to display results in a readable format
    test_loader = unittest.TestLoader()
    test_suite = test_loader.loadTestsFromTestCase(TestPokerGame)
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    print("\nSummary:")
    print("========")
    print(f"Tests Run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")

    if result.wasSuccessful():
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed.")
        if result.errors:
            print("\nErrors:")
            for test, error in result.errors:
                print(f"Test {test.id().split('.')[-1]}: {error}")

        if result.failures:
            print("\nFailures:")
            for test, failure in result.failures:
                print(f"Test {test.id().split('.')[-1]}: {failure}")
