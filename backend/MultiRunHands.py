import multiprocessing
import matplotlib.pyplot as plt
from collections import Counter
from app import PokerGame, HAND_RANKS
import time
from tqdm import tqdm
from datetime import datetime
import os

def run_single_round(game_id):
    start_time = time.time()
    game = PokerGame()
    game.create_deck()
    game.deal_cards(5)
    game.deal_community_cards()
    winner, winning_hand, hand_evaluation = game.determine_winner()
    end_time = time.time()
    run_time = end_time - start_time
    return winner, hand_evaluation, run_time

def main():
    num_rounds = 350  # Adjust the number of rounds as needed
    num_processes = 12  # Adjust this number based on your system's capability
    num_players = 5  # Number of players in the game

    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    stats_folder = "Statistics"
    date_player_folder = os.path.join(stats_folder, f"{date_str}_{num_players}players")

    # Create directories if they don't exist
    os.makedirs(stats_folder, exist_ok=True)
    os.makedirs(date_player_folder, exist_ok=True)

    with multiprocessing.Pool(processes=num_processes) as pool:
        # Use tqdm to display a progress bar
        results = list(tqdm(pool.imap(run_single_round, range(num_rounds)), total=num_rounds))

    win_counts = Counter([result[0] for result in results])
    hand_type_counts = Counter([result[1][0] for result in results])
    run_times = [result[2] for result in results]
    average_run_time = sum(run_times) / len(run_times)

    # Plotting the distribution of wins between the 3 players
    plt.figure(figsize=(10, 5))
    players = list(win_counts.keys())
    win_values = list(win_counts.values())
    win_percentages = [f'{v}/{num_rounds} ({(v/num_rounds)*100:.4f}%)' for v in win_values]

    plt.bar(players, win_values, tick_label=players)
    plt.title('Distribution of Wins Between Players')
    plt.xlabel('Players')
    plt.ylabel('Number of Wins')

    for i, v in enumerate(win_values):
        plt.text(i, v + 1, win_percentages[i], ha='center')

    wins_filename = f"wins_distribution_{date_str}_{num_players}players_{num_rounds}rounds.png"

    plt.savefig(os.path.join(date_player_folder, wins_filename))
    plt.close()

    # Sorting hand types by their counts
    sorted_hand_types = sorted(hand_type_counts.items(), key=lambda item: item[1], reverse=True)
    sorted_hand_keys = [item[0] for item in sorted_hand_types]
    sorted_hand_values = [item[1] for item in sorted_hand_types]
    sorted_hand_percentages = [f'{v}/{num_rounds} ({(v/num_rounds)*100:.4f}%)' for v in sorted_hand_values]

    # Plotting the distribution of total hands won from each type
    plt.figure(figsize=(10, 5))
    hand_types = [HAND_RANKS[hand] for hand in sorted_hand_keys]
    hand_type_values = sorted_hand_values

    plt.bar(hand_types, hand_type_values, tick_label=hand_types)
    plt.title('Distribution of Winning Hand Types')
    plt.xlabel('Hand Type')
    plt.ylabel('Number of Wins')

    for i, v in enumerate(hand_type_values):
        plt.text(i, v + 1, sorted_hand_percentages[i], ha='center')

    hands_filename = f"hand_distribution_{date_str}_{num_players}players_{num_rounds}rounds.png"

    plt.savefig(os.path.join(date_player_folder, hands_filename))
    plt.close()

    # Plotting the pie chart of total hands won from each type
    plt.figure(figsize=(10, 5))
    pie_labels = [f'{HAND_RANKS[hand]}: {count}/{num_rounds} ({(count/num_rounds)*100:.1f}%)' for hand, count in sorted_hand_types]
    plt.pie(hand_type_values, labels=pie_labels, autopct='%1.1f%%', startangle=140)
    plt.title('Pie Chart of Winning Hand Types')

    pie_filename = f"pie_chart_{date_str}_{num_players}players_{num_rounds}rounds.png"

    plt.savefig(os.path.join(date_player_folder, pie_filename))
    plt.close()

    # Print average run time
    print(f'Average time per single run: {average_run_time:.6f} seconds')

if __name__ == '__main__':
    main()
