from collections import Counter

def evaluate_hand(hand):
    """
    Evaluate the strength of a poker hand.

    Args:
        hand (list): A list of 5 cards in the format 'RS' where 'R' is the rank and 'S' is the suit.

    Returns:
        tuple: A tuple where the first element is the hand's rank (0-9) and the second is a list of card ranks for tie-breaking.
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
        # Straight flush
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

# Sample test cases
test_hands = [
    (['AH', 'KH', 'QH', 'JH', 'TH'], (9, [14, 13, 12, 11, 10])),  # Royal Flush
    (['9H', '8H', '7H', '6H', '5H'], (9, [9, 8, 7, 6, 5])),       # Straight Flush
    (['9H', '9D', '9S', '9C', '2D'], (8, [9, 2])),                # Four of a Kind
    (['TH', 'TD', 'TS', '3C', '3D'], (7, [10, 3])),               # Full House
    (['AH', 'KH', 'QH', '7H', '3H'], (6, [14, 13, 12, 7, 3])),    # Flush
    (['9H', '8D', '7S', '6C', '5D'], (5, [9, 8, 7, 6, 5])),       # Straight
    (['KH', 'KD', 'KS', '7C', '3D'], (4, [13, 7, 3])),            # Three of a Kind
    (['AH', 'AD', 'KC', 'KD', '2D'], (3, [14, 13, 2])),           # Two Pair
    (['QH', 'QD', '7S', '3C', '2D'], (2, [12, 7, 3, 2])),         # One Pair
    (['AH', 'KD', 'QC', 'JS', '9D'], (1, [14, 13, 12, 11, 9])),   # High Card
    # Straight Flush - High and Low
    (['9H', '8H', '7H', '6H', '5H'], (9, [9, 8, 7, 6, 5])),  # High Straight Flush
    (['5H', '4H', '3H', '2H', 'AH'], (9, [5, 4, 3, 2, 1])),  # Low Straight Flush

    # Four of a Kind with different kickers
    (['9H', '9D', '9S', '9C', '3D'], (8, [9, 3])),  # Four of a Kind with 3 kicker
    (['9H', '9D', '9S', '9C', '4D'], (8, [9, 4])),  # Four of a Kind with 4 kicker

    # Full House with different pairs
    (['TH', 'TD', 'TS', '3C', '3D'], (7, [10, 3])),  # Full House (Tens over Threes)
    (['TH', 'TD', 'TS', '4C', '4D'], (7, [10, 4])),  # Full House (Tens over Fours)

    # Flushes with different high cards
    (['AH', 'KH', 'QH', '7H', '3H'], (6, [14, 13, 12, 7, 3])),  # Flush with Ace high
    (['KH', 'QH', 'JH', '7H', '3H'], (6, [13, 12, 11, 7, 3])),  # Flush with King high

    # High and Low Straights
    (['9H', '8D', '7S', '6C', '5D'], (5, [9, 8, 7, 6, 5])),  # High Straight
    (['5H', '4D', '3S', '2C', 'AH'], (5, [5, 4, 3, 2, 1])),  # Low Straight

    # Three of a Kind with different kickers
    (['KH', 'KD', 'KS', '7C', '3D'], (4, [13, 7, 3])),  # Three of a Kind with 7 and 3 kickers
    (['KH', 'KD', 'KS', '6C', '4D'], (4, [13, 6, 4])),  # Three of a Kind with 6 and 4 kickers

    # Two Pair with different kickers
    (['AH', 'AD', 'KC', 'KD', '2D'], (3, [14, 13, 2])),  # Two Pair (Aces and Kings) with 2 kicker
    (['AH', 'AD', 'KC', 'KD', '3D'], (3, [14, 13, 3])),  # Two Pair (Aces and Kings) with 3 kicker

    # One Pair with different kickers
    (['QH', 'QD', '7S', '3C', '2D'], (2, [12, 7, 3, 2])),  # One Pair (Queens) with 7, 3, and 2 kickers
    (['QH', 'QD', '8S', '3C', '2D'], (2, [12, 8, 3, 2])),  # One Pair (Queens) with 8, 3, and 2 kickers

    # High Card with different high cards
    (['AH', 'KD', 'QC', 'JS', '9D'], (1, [14, 13, 12, 11, 9])),  # High Card with Ace high
    (['KH', 'QD', 'JC', '9S', '8D'], (1, [13, 12, 11, 9, 8])),  # High Card with King high

    # Edge cases and other scenarios
    (['2H', '3D', '5S', '9C', 'KH'], (1, [13, 9, 5, 3, 2])),  # High Card with mixed low and high cards
    (['3H', '3D', '3S', '9C', 'KH'], (4, [3, 13, 9])),  # Three of a Kind (Threes) with King and Nine kickers
    (['2H', '2D', '3S', '3C', '4H'], (3, [3, 2, 4])),  # Two Pair (Threes and Twos) with Four kicker
    (['2H', '2D', '2S', '9C', 'KH'], (4, [2, 13, 9])),
]

for hand, expected in test_hands:
    result = evaluate_hand(hand)
    assert result == expected, f"Failed for hand {hand}. Expected {expected}, got {result}"

print("All test cases passed!")
