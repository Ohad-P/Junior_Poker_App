import unittest
from unittest.mock import patch, MagicMock
from app import app, Table, Player, PokerGame

class TestPokerApp(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.poker_game = PokerGame()
        self.table = self.poker_game.table
        self.table.set_blinds(10, 20, 5)  # Default blinds for testing

    def test_set_table(self):
        response = self.client.post('/set_table', json={
            'name': 'Test Table',
            'max_players': 9,
            'min_buy_in': 50,
            'max_buy_in': 500,
            'small_blind': 10,
            'big_blind': 20,
            'antee': 5
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Table settings updated', response.json['message'])
        self.assertEqual(self.table.name, 'Test Table')
        self.assertEqual(self.table.max_players, 9)
        self.assertEqual(self.table.min_buy_in, 50)
        self.assertEqual(self.table.max_buy_in, 500)
        self.assertEqual(self.table.blinds['small_blind'], 10)
        self.assertEqual(self.table.blinds['big_blind'], 20)
        self.assertEqual(self.table.blinds['antee'], 5)

    def test_add_player(self):
        response = self.client.post('/add_player', json={
            'name': 'Player1',
            'bankroll': 100,
            'seat': 0
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Player Player1 added with bankroll 100', response.json['message'])
        self.assertEqual(len([p for p in self.table.players if p is not None]), 1)
        self.assertEqual(self.table.players[0].name, 'Player1')

    def test_remove_player(self):
        player = Player('Player1', 100)
        self.table.add_player(player, 0)
        response = self.client.post('/remove_player', json={'name': 'Player1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Player removed', response.json['message'])
        self.assertEqual(len([p for p in self.table.players if p is not None]), 0)

    def test_update_player_chips(self):
        player = Player('Player1', 100)
        self.table.add_player(player, 0)
        response = self.client.post('/update_player_chips', json={
            'name': 'Player1',
            'chips': 150
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Player chips updated', response.json['message'])
        self.assertEqual(player.bankroll, 150)

    def test_reshuffle(self):
        response = self.client.post('/reshuffle')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 52)
        self.assertEqual(len(self.poker_game.deck), 52)

    def test_deal(self):
        player1 = Player('Player1', 100)
        player2 = Player('Player2', 100)
        self.table.add_player(player1, 0)
        self.table.add_player(player2, 1)
        self.poker_game.create_deck()
        response = self.client.post('/deal', json={'numPlayers': 2})
        self.assertEqual(response.status_code, 200)
        hands = response.json
        self.assertEqual(len(hands), 2)
        self.assertEqual(len(hands['Player1']['hand']), 2)
        self.assertEqual(len(hands['Player2']['hand']), 2)

    def test_deal_flop(self):
        player1 = Player('Player1', 100)
        player2 = Player('Player2', 100)
        self.table.add_player(player1, 0)
        self.table.add_player(player2, 1)
        self.poker_game.create_deck()
        self.poker_game.deal_cards(2)
        response = self.client.post('/community/flop')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)

    def test_deal_turn(self):
        player1 = Player('Player1', 100)
        player2 = Player('Player2', 100)
        self.table.add_player(player1, 0)
        self.table.add_player(player2, 1)
        self.poker_game.create_deck()
        self.poker_game.deal_cards(2)
        self.poker_game.deal_flop()
        response = self.client.post('/community/turn')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 4)

    def test_deal_river(self):
        player1 = Player('Player1', 100)
        player2 = Player('Player2', 100)
        self.table.add_player(player1, 0)
        self.table.add_player(player2, 1)
        self.poker_game.create_deck()
        self.poker_game.deal_cards(2)
        self.poker_game.deal_flop()
        self.poker_game.deal_turn()
        response = self.client.post('/community/river')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['community']), 5)
        self.assertIn('winner', response.json)
        self.assertIn('winning_hand', response.json)
        self.assertIn('hand_evaluation', response.json)

    def test_bet(self):
        player = Player('Player1', 100)
        self.table.add_player(player, 0)
        self.poker_game.deal_cards(2)
        response = self.client.post('/bet', json={
            'player': 'Player1',
            'amount': 20,
            'action': 'raise'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Bet placed', response.json['message'])
        self.assertEqual(player.bankroll, 80)
        self.assertEqual(self.poker_game.pot, 20)

    def test_fold(self):
        player = Player('Player1', 100)
        self.table.add_player(player, 0)
        self.poker_game.deal_cards(2)
        response = self.client.post('/fold', json={'player': 'Player1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('folded', response.json['message'])

if __name__ == '__main__':
    unittest.main()
