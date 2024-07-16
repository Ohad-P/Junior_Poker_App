from flask import Flask, jsonify, request
from flask_cors import CORS
import secrets
import time
import os
from itertools import combinations
from collections import Counter
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

# Constants
RANKS = '23456789TJQKA'
SUITS = 'HDCS'
HAND_RANKS = {
    1: "High card", 2: "One pair", 3: "Two pairs", 4: "Three of a kind",
    5: "Straight", 6: "Flush", 7: "Full house", 8: "Four of a kind", 9: "Straight flush", 10: "Royal flush"
}


class Table:
    def __init__(self, name, game_type="Texas Hold'em", max_players=9, min_buy_in=50, max_buy_in=500):
        self.name = name
        self.game_type = game_type
        self.max_players = max_players
        self.min_buy_in = min_buy_in
        self.max_buy_in = max_buy_in
        self.blinds = {"small_blind": 0, "big_blind": 0, "antee": 0}
        self.dealer_position = -1
        self.players = []  # List to store players who have joined the table
        self.active_players = []  # List to store players who have bought in and have chips
        self.seats = [None] * max_players  # List to store players based on their seat positions
        self.pot = 0

    def set_blinds(self, small_blind, big_blind, antee=0):
        self.blinds["small_blind"] = small_blind
        self.blinds["big_blind"] = big_blind
        self.blinds["antee"] = antee

    def add_player(self, player):
        self.players.append(player)
        player.tables.append(self)

    def sit_down(self, player, seat, buy_in):
        if seat < 0 or seat >= self.max_players:
            raise ValueError("Invalid seat number")
        if self.seats[seat] is not None:
            raise ValueError("Seat already taken")
        if buy_in < self.min_buy_in or buy_in > self.max_buy_in:
            raise ValueError("Buy-in amount must be between the minimum and maximum buy-in limits")
        if buy_in > player.bankroll:
            raise ValueError("Insufficient bankroll for the buy-in")
        self.seats[seat] = player
        player.seat = seat
        player.bankroll -= buy_in
        player.in_game_chips = buy_in
        player.status = "playing"
        self.active_players.append(player)

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
        if player in self.active_players:
            self.active_players.remove(player)
        if player.seat is not None and self.seats[player.seat] == player:
            self.seats[player.seat] = None
        player.status = "standing"
        player.seat = None
        player.tables.remove(self)

    def set_dealer_position(self, position):
        if position < 0 or position >= self.max_players or self.seats[position] is None:
            raise ValueError("Invalid dealer position")
        self.dealer_position = position

    def next_dealer(self):
        if self.dealer_position == -1:
            self.dealer_position = 0
        else:
            while True:
                self.dealer_position = (self.dealer_position + 1) % self.max_players
                if self.seats[self.dealer_position] is not None:
                    break

    def collect_blinds(self):
        active_players = [p for p in self.active_players if p.status == "playing"]
        if self.dealer_position == -1 or len(active_players) < 2:
            raise ValueError("Not enough players to collect blinds")

        if len(active_players) == 2:
            small_blind_position = self.dealer_position
            big_blind_position = (self.dealer_position + 1) % self.max_players
        else:
            small_blind_position = (self.dealer_position + 1) % self.max_players
            big_blind_position = (self.dealer_position + 2) % self.max_players

        small_blind_player = self.seats[small_blind_position]
        big_blind_player = self.seats[big_blind_position]

        if small_blind_player not in self.active_players or big_blind_player not in self.active_players:
            raise ValueError("Blinds must be posted by active players")

        if small_blind_player.in_game_chips < self.blinds["small_blind"]:
            raise ValueError("Small blind player does not have enough chips")
        if big_blind_player.in_game_chips < self.blinds["big_blind"]:
            raise ValueError("Big blind player does not have enough chips")

        small_blind_player.in_game_chips -= self.blinds["small_blind"]
        big_blind_player.in_game_chips -= self.blinds["big_blind"]
        self.pot += self.blinds["small_blind"] + self.blinds["big_blind"]

        for player in active_players:
            player.in_game_chips -= self.blinds["antee"]
            self.pot += self.blinds["antee"]

    def distribute_pot(self, winners):
        split_pot = self.pot // len(winners)
        for winner in winners:
            winner.in_game_chips += split_pot
        self.pot = 0


class Player:
    def __init__(self, name, bankroll):
        self.name = name
        self.bankroll = bankroll
        self.hand = []
        self.in_game_chips = 0
        self.bet = 0
        self.status = "standing"  # "standing", "sitting", "playing", "sitting out"
        self.seat = None  # Player's seat at the table
        self.tables = []  # List of tables the player has joined

    def place_bet(self, amount):
        if amount > self.in_game_chips:
            return "Insufficient chips", 400
        self.in_game_chips -= amount
        self.bet += amount
        return "Bet placed", 200

    def join_table(self, table):
        table.add_player(self)
        self.status = "sitting"
        return "Player joined the table", 200

    def leave_table(self, table):
        if table in self.tables:
            table.remove_player(self)
            if len(self.tables) == 0:
                self.status = "standing"
            return "Player left the table", 200
        return "Player not at the table", 400

    def sit_down(self, table, seat, buy_in):
        if self.status != "sitting":
            return "Player must be sitting to take a seat", 400
        if table not in self.tables:
            return "Player must join the table before sitting down", 400
        try:
            table.sit_down(self, seat, buy_in)
            return "Player took a seat and bought in", 200
        except ValueError as e:
            return str(e), 400

    def stand_up(self, table):
        if self.status != "playing" and self.status != "sitting out":
            return "Player is not seated", 400
        self.bankroll += self.in_game_chips
        self.in_game_chips = 0
        self.status = "standing"
        table.active_players.remove(self)
        self.seat = None
        return "Player stood up", 200

    def sit_out(self, table):
        if self.status != "playing":
            return "Player is not playing", 400
        self.status = "sitting out"
        return "Player is sitting out", 200

    def rejoin_game(self, table):
        if self.status != "sitting out":
            return "Player is not sitting out", 400
        self.status = "playing"
        return "Player rejoined the game", 200

    def add_on(self, amount, table):
        if self.status != "playing":
            return "Player must be playing to add on chips", 400
        if self.in_game_chips + amount > table.max_buy_in:
            return "Add-on amount exceeds the maximum buy-in limit", 400
        if amount > self.bankroll:
            return "Insufficient bankroll for the add-on", 400
        self.bankroll -= amount
        self.in_game_chips += amount
        return "Add-on successful", 200

class PokerGame:
    def __init__(self):
        self.deck = []
        self.table = Table(name='init_table')
        self.community_cards = []
        self.current_phase = "none"
        self.players = []  # List to store all players

    def create_deck(self):
        deck = [rank + suit for rank in RANKS for suit in SUITS]
        seed = secrets.randbits(64) ^ int(time.time() * 1000000) ^ os.getpid()
        rng = secrets.SystemRandom(seed)
        rng.shuffle(deck)
        self.deck = deck
        self.community_cards = []
        self.current_phase = "none"

    def add_player(self, name, bankroll):
        player = Player(name, bankroll)
        self.players.append(player)  # Add player to the list of all players
        return player

    def remove_player(self, name):
        player = next((p for p in self.players if p.name == name), None)
        if player:
            self.players.remove(player)
            for table in player.tables:
                table.remove_player(player)
            return "Player removed", 200
        return "Player not found", 404

    def update_player_chips(self, name, chips):
        player = next((p for p in self.players if p.name == name), None)
        if player:
            player.bankroll = chips
            return "Player chips updated", 200
        return "Player not found", 404

    def deal_cards(self, num_players):
        if num_players < 2 or num_players > self.table.max_players:
            return "Number of players must be between 2 and " + str(self.table.max_players), 400
        if num_players * 2 > len(self.deck):
            return "Not enough cards in the deck", 400

        if len([p for p in self.table.active_players if p.status == "playing"]) < num_players:
            return "Not enough active players", 400

        self.table.set_dealer_position(0)  # Ensure dealer position is set
        for player in self.table.active_players:
            if player.status == "playing":
                player.hand = [self.deck.pop(), self.deck.pop()]
        self.current_phase = "pre-flop"
        return {player.name: {'hand': player.hand, 'bankroll': player.bankroll, 'in_game_chips': player.in_game_chips,
                              'bet': player.bet} for player in self.table.active_players if player.status == "playing"}

    def deal_flop(self):
        if self.current_phase != "pre-flop":
            return "Invalid game phase", 400
        burn = self.deck.pop()
        self.community_cards = [self.deck.pop() for _ in range(3)]
        self.current_phase = "flop"
        return self.community_cards

    def deal_turn(self):
        if self.current_phase != "flop":
            return "Invalid game phase", 400
        burn = self.deck.pop()
        self.community_cards.append(self.deck.pop())
        self.current_phase = "turn"
        return self.community_cards

    def deal_river(self):
        if self.current_phase != "turn":
            return "Invalid game phase", 400
        burn = self.deck.pop()
        self.community_cards.append(self.deck.pop())
        self.current_phase = "river"
        if not self.table.active_players:
            return "No players in game", 400
        return self.community_cards

    def evaluate_hand(self, hand):
        """
        Evaluate the strength of a poker hand.

        Args:
            hand (list): A list of 5 cards in the format 'RS' where 'R' is the rank and 'S' is the suit.

        Returns:
            tuple: A tuple where the first element is the hand's rank (1-10) and the second is a list of card ranks for tie-breaking.
        """
        # Define the order of ranks and suits
        values = '--23456789TJQKA'
        suits = 'CDHS'

        # Check for invalid cards
        if any(len(card) != 2 or card[0] not in values or card[1] not in suits for card in hand):
            raise ValueError("Invalid card in hand")

        # Check for duplicate cards
        if len(hand) != len(set(hand)):
            raise ValueError("Duplicate cards in hand")

        # Convert card ranks to numerical values and sort them in descending order
        sorted_ranks = sorted([values.index(r) for r, s in hand], reverse=True)
        rank_counts = Counter(sorted_ranks)
        sorted_rank_counts = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

        # Check if all cards have the same suit (flush)
        is_flush = len(set(s for r, s in hand)) == 1

        # Check if the ranks form a sequence (straight)
        is_straight = len(set(sorted_ranks)) == 5 and (sorted_ranks[0] - sorted_ranks[-1] == 4 or sorted_ranks == [14, 5, 4, 3, 2])

        # Determine the hand ranking
        if is_straight and is_flush:
            # Royal Flush
            if sorted_ranks == [14, 13, 12, 11, 10]:
                return (10, sorted_ranks)
            # Straight flush
            else:
                return (9, sorted_ranks if sorted_ranks != [14, 5, 4, 3, 2] else [5, 4, 3, 2, 1])
        elif sorted_rank_counts[0][1] == 4:
            # Four of a kind
            four_kind = sorted_rank_counts[0][0]
            kicker = sorted_rank_counts[1][0]
            return (8, [four_kind, kicker])
        elif sorted_rank_counts[0][1] == 3 and sorted_rank_counts[1][1] == 2:
            # Full house
            three_kind = sorted_rank_counts[0][0]
            pair = sorted_rank_counts[1][0]
            return (7, [three_kind, pair])
        elif is_flush:
            # Flush
            return (6, sorted_ranks)
        elif is_straight:
            # Straight
            return (5, sorted_ranks if sorted_ranks != [14, 5, 4, 3, 2] else [5, 4, 3, 2, 1])
        elif sorted_rank_counts[0][1] == 3:
            # Three of a kind
            three_kind = sorted_rank_counts[0][0]
            kickers = [rank for rank, count in sorted_rank_counts if count == 1]
            return (4, [three_kind] + kickers)
        elif sorted_rank_counts[0][1] == 2 and sorted_rank_counts[1][1] == 2:
            # Two pair
            pairs = [rank for rank, count in sorted_rank_counts if count == 2]
            kicker = [rank for rank, count in sorted_rank_counts if count == 1][0]
            return (3, pairs + [kicker])
        elif sorted_rank_counts[0][1] == 2:
            # One pair
            pair = sorted_rank_counts[0][0]
            kickers = [rank for rank, count in sorted_rank_counts if count == 1]
            return (2, [pair] + kickers)
        else:
            # High card
            return (1, sorted_ranks)

    def best_hand(self, hand):
        all_cards = hand + self.community_cards
        all_combinations = combinations(all_cards, 5)
        return max(all_combinations, key=lambda comb: self.evaluate_hand(comb))

    def determine_winner(self):
        if not self.table.active_players:
            return "No players in game", 400
        
        best_hands = {player: self.best_hand(player.hand) for player in self.table.active_players if player.status == "playing"}
        best_evaluations = {player: self.evaluate_hand(best_hands[player]) for player in best_hands}

        if not best_evaluations:
            return "No valid hands", 400

        best_rank = max(best_evaluations.values())

        # Filter players with the best evaluation
        best_players = [player for player in best_evaluations if best_evaluations[player] == best_rank]

        if len(best_players) == 1:
            winner = best_players[0]
            self.table.distribute_pot([winner])
            return winner, best_hands[winner], best_evaluations[winner]

        # Tie-breaking among players with the same best evaluation
        def compare_hands(player1, player2):
            eval1 = best_evaluations[player1]
            eval2 = best_evaluations[player2]
            for i in range(len(eval1[1])):
                if eval1[1][i] > eval2[1][i]:
                    return player1
                elif eval1[1][i] < eval2[1][i]:
                    return player2
            return None  # This would mean a tie

        winner = best_players[0]
        for player in best_players[1:]:
            new_winner = compare_hands(winner, player)
            if new_winner is None:
                self.table.distribute_pot(best_players)
                return "tie", best_hands[best_players[0]], best_evaluations[best_players[0]]
            winner = new_winner

        self.table.distribute_pot([winner])
        return winner, best_hands[winner], best_evaluations[winner]

    def handle_bet(self, player_name, amount):
        player = next((p for p in self.table.players if p.name == player_name), None)
        if not player:
            return "Player not found", 404
        message, status = player.place_bet(amount)
        if status == 200:
            self.table.pot += amount
        return message, status

    def player_action(self, player_name, action, amount=0):
        player = next((p for p in self.table.players if p.name == player_name), None)
        if not player:
            return "Player not found", 404

        if action == 'fold':
            if player_name in self.table.bets:
                del self.table.bets[player_name]
            return f'{player_name} folded', 200
        elif action == 'check':
            return f'{player_name} checked', 200
        elif action == 'call':
            return f'{player_name} called', 200
        elif action == 'raise':
            return self.handle_bet(player_name, amount)
        elif action == 'all-in':
            return self.handle_bet(player_name, amount)

poker_game = PokerGame()

@app.route('/')
def hello():
    return 'Hello, Poker!'

@app.route('/tables', methods=['GET'])
def get_tables():
    tables = [
        {"name": table.name, "max_players": table.max_players, "min_buy_in": table.min_buy_in, "max_buy_in": table.max_buy_in, "players": [{"name": player.name, "bankroll": player.bankroll, "status": player.status} for player in table.players]}
        for table in [poker_game.table] if table.name != 'init_table'
    ]
    print("Tables fetched:", tables)  # Debugging output
    return jsonify(tables), 200

@app.route('/delete_table', methods=['POST'])
def delete_table():
    data = request.get_json()
    name = data.get('name')
    if poker_game.table.name == name:
        poker_game.table = Table(name='init_table')  # Reset the table
        return jsonify({'message': f'Table {name} deleted'}), 200
    return jsonify({'message': 'Table not found'}), 404

@app.route('/add_player_to_table', methods=['POST'])
def add_player_to_table():
    data = request.get_json()
    player_name = data.get('player_name')
    table_name = data.get('table_name')
    logging.info(f"Attempting to add player {player_name} to table {table_name}")
    logging.info(f"Current players: {[p.name for p in poker_game.players]}")
    if poker_game.table.name != table_name:
        logging.error(f"Table {table_name} not found")
        return jsonify({'message': 'Table not found'}), 404
    player = next((p for p in poker_game.players if p.name == player_name), None)
    if not player:
        logging.error(f"Player {player_name} not found")
        return jsonify({'message': 'Player not found'}), 404
    poker_game.table.add_player(player)
    logging.info(f"Player {player_name} added to table {table_name}")
    return jsonify({'message': f'Player {player_name} added to table {table_name}'}), 200

@app.route('/remove_player_from_table', methods=['POST'])
def remove_player_from_table():
    data = request.get_json()
    player_name = data.get('player_name')
    table_name = data.get('table_name')
    if poker_game.table.name != table_name:
        return jsonify({'message': 'Table not found'}), 404
    player = next((p for p in poker_game.table.players if p.name == player_name), None)
    if not player:
        return jsonify({'message': 'Player not found'}), 404
    poker_game.table.remove_player(player)
    return jsonify({'message': f'Player {player_name} removed from table {table_name}'}), 200

@app.route('/set_table', methods=['POST'])
def set_table():
    # Add manager verification logic here
    data = request.get_json()
    name = data.get('name', 'Default Table')
    max_players = data.get('max_players', 9)
    min_buy_in = data.get('min_buy_in', 50)
    max_buy_in = data.get('max_buy_in', 500)
    small_blind = data.get('small_blind', 10)
    big_blind = data.get('big_blind', 20)
    antee = data.get('antee', 0)
    poker_game.table = Table(name=name, max_players=max_players, min_buy_in=min_buy_in, max_buy_in=max_buy_in)
    poker_game.table.set_blinds(small_blind, big_blind, antee)
    return jsonify({'message': 'Table settings updated'}), 200

@app.route('/add_player', methods=['POST'])
def add_player():
    data = request.get_json()
    name = data.get('name')
    bankroll = data.get('bankroll')
    if not name or not isinstance(bankroll, int):
        return jsonify({'message': 'Invalid player data'}), 400
    try:
        player = poker_game.add_player(name, bankroll)
        logging.info(f"Player {name} added with bankroll {bankroll}")
        logging.info(f"Current players: {[p.name for p in poker_game.players]}")
        return jsonify({'message': f'Player {name} added with bankroll {bankroll}'}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400

@app.route('/remove_player', methods=['POST'])
def remove_player():
    data = request.get_json()
    name = data.get('name')
    message, status = poker_game.remove_player(name)
    return jsonify({'message': message}), status

@app.route('/update_player_chips', methods=['POST'])
def update_player_chips():
    data = request.get_json()
    name = data.get('name')
    chips = data.get('chips')
    message, status = poker_game.update_player_chips(name, chips)
    return jsonify({'message': message}), status

@app.route('/reshuffle', methods=['POST'])
def reshuffle():
    poker_game.create_deck()
    return jsonify(poker_game.deck), 200

@app.route('/deck')
def deck():
    if not poker_game.deck:
        poker_game.create_deck()
    return jsonify(poker_game.deck)

@app.route('/deal', methods=['POST'])
def deal():
    data = request.get_json()
    num_players = data.get('numPlayers', 2)
    players_hands = poker_game.deal_cards(num_players)
    if isinstance(players_hands, tuple):
        return jsonify({'error': players_hands[0]}), players_hands[1]
    return jsonify(players_hands)

@app.route('/community/flop', methods=['POST'])
def deal_flop():
    community_cards = poker_game.deal_flop()
    if isinstance(community_cards, tuple):
        return jsonify({'error': community_cards[0]}), community_cards[1]
    return jsonify(community_cards)

@app.route('/community/turn', methods=['POST'])
def deal_turn():
    community_cards = poker_game.deal_turn()
    if isinstance(community_cards, tuple):
        return jsonify({'error': community_cards[0]}), community_cards[1]
    return jsonify(community_cards)

@app.route('/community/river', methods=['POST'])
def deal_river():
    community_cards = poker_game.deal_river()
    if isinstance(community_cards, tuple):
        return jsonify({'error': community_cards[0]}), community_cards[1]
    winner, winning_hand, hand_evaluation = poker_game.determine_winner()
    if isinstance(winner, tuple):
        return jsonify({'error': winner[0]}), winner[1]
    return jsonify({
        'community': community_cards,
        'winner': winner,
        'winning_hand': winning_hand,
        'hand_evaluation': hand_evaluation,
        'pot': poker_game.table.pot
    })

@app.route('/bet', methods=['POST'])
def bet():
    data = request.get_json()
    player = data.get('player')
    amount = data.get('amount')
    action = data.get('action')
    message, status = poker_game.player_action(player, action, amount)
    return jsonify({'message': message}), status

@app.route('/fold', methods=['POST'])
def fold():
    data = request.get_json()
    player = data.get('player')
    message, status = poker_game.player_action(player, 'fold')
    return jsonify({'message': message}), status

if __name__ == '__main__':
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(port=3001, debug=True)
