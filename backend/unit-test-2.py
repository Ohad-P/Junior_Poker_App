import unittest
from app import Table, Player, PokerGame  # Adjust the import path based on your project structure

class TestPokerApp(unittest.TestCase):

    def test_add_player(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        response, status = player1.join_table(table)
        self.assertEqual(status, 200)
        self.assertIn(player1, table.players)

    def test_sit_down(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player1.join_table(table)
        response, status = player1.sit_down(table, seat=0, buy_in=100)
        self.assertEqual(status, 200)
        self.assertEqual(player1.status, "playing")
        self.assertEqual(player1.in_game_chips, 100)
        self.assertIn(player1, table.active_players)
        self.assertEqual(table.seats[0], player1)

    def test_collect_blinds(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player2 = Player(name="Bob", bankroll=500)
        player1.join_table(table)
        player2.join_table(table)
        player1.sit_down(table, seat=0, buy_in=100)
        player2.sit_down(table, seat=1, buy_in=100)
        table.set_blinds(small_blind=10, big_blind=20)
        table.set_dealer_position(0)
        table.collect_blinds()
        self.assertEqual(player1.in_game_chips, 90)  # Small blind deducted
        self.assertEqual(player2.in_game_chips, 80)  # Big blind deducted
        self.assertEqual(table.pot, 30)

    def test_place_bet(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player1.join_table(table)
        player1.sit_down(table, seat=0, buy_in=100)
        response, status = player1.place_bet(50)
        self.assertEqual(status, 200)
        self.assertEqual(player1.in_game_chips, 50)
        self.assertEqual(player1.bet, 50)

    def test_player_join_and_leave_table(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        response, status = player1.join_table(table)
        self.assertEqual(status, 200)
        self.assertIn(player1, table.players)

        response, status = player1.leave_table(table)
        self.assertEqual(status, 200)
        self.assertNotIn(player1, table.players)

    def test_player_rejoin_game(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player1.join_table(table)
        response, status = player1.sit_down(table, seat=0, buy_in=100)
        self.assertEqual(status, 200)
        response, status = player1.sit_out(table)
        self.assertEqual(status, 200)
        self.assertEqual(player1.status, "sitting out")
        response, status = player1.rejoin_game(table)
        self.assertEqual(status, 200)
        self.assertEqual(player1.status, "playing")

    def test_player_add_on(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player1.join_table(table)
        response, status = player1.sit_down(table, seat=0, buy_in=50)
        self.assertEqual(status, 200)
        response, status = player1.add_on(100, table)
        self.assertEqual(status, 200)
        self.assertEqual(player1.bankroll, 850)
        self.assertEqual(player1.in_game_chips, 150)

    def test_stand_up(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player1.join_table(table)
        response, status = player1.sit_down(table, seat=0, buy_in=100)
        self.assertEqual(status, 200)
        response, status = player1.stand_up(table)
        self.assertEqual(status, 200)
        self.assertEqual(player1.status, "standing")
        self.assertEqual(player1.in_game_chips, 0)
        self.assertEqual(player1.bankroll, 1000)

    def test_set_dealer_position(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player2 = Player(name="Bob", bankroll=500)
        player1.join_table(table)
        player2.join_table(table)
        player1.sit_down(table, seat=0, buy_in=100)
        player2.sit_down(table, seat=1, buy_in=100)
        table.set_dealer_position(0)
        self.assertEqual(table.dealer_position, 0)
        table.next_dealer()
        self.assertEqual(table.dealer_position, 1)

    def test_sit_out_and_stand_up_from_sit_out(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player1.join_table(table)
        response, status = player1.sit_down(table, seat=0, buy_in=100)
        self.assertEqual(status, 200)
        response, status = player1.sit_out(table)
        self.assertEqual(status, 200)
        self.assertEqual(player1.status, "sitting out")
        self.assertIn(player1, table.active_players)  # Ensure the player is still an active player
        response, status = player1.stand_up(table)
        self.assertEqual(status, 200)
        self.assertEqual(player1.status, "standing")
        self.assertEqual(player1.in_game_chips, 0)
        self.assertEqual(player1.bankroll, 1000)
        self.assertNotIn(player1, table.active_players)  # Ensure the player is no longer an active player

    def test_invalid_actions(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player1.join_table(table)
        response, status = player1.sit_down(table, seat=0, buy_in=100)
        self.assertEqual(status, 200)
        player2 = Player(name="Bob", bankroll=500)
        player2.join_table(table)
        response, status = player2.sit_down(table, seat=0, buy_in=100)
        self.assertEqual(status, 400)
        self.assertEqual(response, "Seat already taken")
        response, status = player1.sit_down(table, seat=1, buy_in=100)
        self.assertEqual(status, 400)
        self.assertEqual(response, "Player must be sitting to take a seat")

    def test_evaluate_hands_and_winner(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player2 = Player(name="Bob", bankroll=500)
        player1.join_table(table)
        player2.join_table(table)
        player1.sit_down(table, seat=0, buy_in=100)
        player2.sit_down(table, seat=1, buy_in=100)
        poker_game = PokerGame()
        poker_game.table = table
        poker_game.create_deck()
        poker_game.deal_cards(2)
        poker_game.deal_flop()
        poker_game.deal_turn()
        poker_game.deal_river()
        winner, winning_hand, hand_evaluation = poker_game.determine_winner()
        self.assertIn(winner.name, ["Alice", "Bob","tie"])

    def test_exceeding_max_buy_in_with_add_on(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player1.join_table(table)
        response, status = player1.sit_down(table, seat=0, buy_in=450)
        self.assertEqual(status, 200)
        response, status = player1.add_on(100, table)
        self.assertEqual(status, 400)
        self.assertEqual(response, "Add-on amount exceeds the maximum buy-in limit")

    # New Tests for Poker Game Logic

    def test_deal_cards(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player2 = Player(name="Bob", bankroll=500)
        player1.join_table(table)
        player2.join_table(table)
        player1.sit_down(table, seat=0, buy_in=100)
        player2.sit_down(table, seat=1, buy_in=100)
        poker_game = PokerGame()
        poker_game.table = table
        poker_game.create_deck()
        hands = poker_game.deal_cards(2)
        self.assertEqual(len(hands), 2)
        self.assertEqual(len(player1.hand), 2)
        self.assertEqual(len(player2.hand), 2)

    def test_bet_logic(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player2 = Player(name="Bob", bankroll=500)
        player1.join_table(table)
        player2.join_table(table)
        player1.sit_down(table, seat=0, buy_in=100)
        player2.sit_down(table, seat=1, buy_in=100)
        poker_game = PokerGame()
        poker_game.table = table
        poker_game.create_deck()
        poker_game.deal_cards(2)
        response, status = poker_game.place_bet(player1.name, 20)
        self.assertEqual(status, 200)
        self.assertEqual(player1.in_game_chips, 80)
        self.assertEqual(poker_game.pot, 20)
        response, status = poker_game.place_bet(player2.name, 50)
        self.assertEqual(status, 200)
        self.assertEqual(player2.in_game_chips, 50)
        self.assertEqual(poker_game.pot, 70)

    def test_pot_management(self):
        table = Table(name="Test Table", min_buy_in=50, max_buy_in=500)
        player1 = Player(name="Alice", bankroll=1000)
        player2 = Player(name="Bob", bankroll=500)
        player1.join_table(table)
        player2.join_table(table)
        player1.sit_down(table, seat=0, buy_in=100)
        player2.sit_down(table, seat=1, buy_in=100)
        poker_game = PokerGame()
        poker_game.table = table
        poker_game.create_deck()
        poker_game.deal_cards(2)

        # Pre-flop betting round
        poker_game.place_bet(player1.name, 20)
        poker_game.place_bet(player2.name, 20)
        self.assertEqual(poker_game.pot, 40)

        # Flop
        poker_game.deal_flop()
        poker_game.place_bet(player1.name, 10)
        poker_game.place_bet(player2.name, 10)
        self.assertEqual(poker_game.pot, 60)

        # Turn
        poker_game.deal_turn()
        poker_game.place_bet(player1.name, 10)
        poker_game.place_bet(player2.name, 10)
        self.assertEqual(poker_game.pot, 80)

        # River
        poker_game.deal_river()
        poker_game.place_bet(player1.name, 10)
        poker_game.place_bet(player2.name, 10)
        self.assertEqual(poker_game.pot, 100)

        # Determine the winner
        winner, winning_hand, hand_evaluation = poker_game.determine_winner()
        self.assertIn(winner.name, ["Alice", "Bob", "tie"])
        self.assertEqual(poker_game.pot, 0)

        # Ensure the winner's in-game chips are updated
        if winner.name == "Alice":
            self.assertEqual(player1.in_game_chips, 150)
            self.assertEqual(player2.in_game_chips, 50)
        elif winner.name == "Bob":
            self.assertEqual(player2.in_game_chips, 150)
            self.assertEqual(player1.in_game_chips, 50)
        else:  # in case of a tie
            self.assertEqual(player1.in_game_chips, 100)
            self.assertEqual(player2.in_game_chips, 100)

if __name__ == "__main__":
    unittest.main()
