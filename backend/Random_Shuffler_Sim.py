import secrets
import time
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from tqdm import tqdm  # Import tqdm for progress bar
from scipy.stats import chisquare, kstest, rankdata
from statsmodels.sandbox.stats.runs import runstest_1samp
import threading

RANKS = '23456789TJQKA'
SUITS = 'HDCS'


class Deck:
    def create_deck(self):
        deck = [rank + suit for rank in RANKS for suit in SUITS]
       #seed = secrets.randbits(64) ^ int(time.time() * 1000000) ^ os.getpid()
        #seed = secrets.randbits(64) ^ int(time.time() * 1000000) ^ os.getpid()
        rng = secrets.SystemRandom()#seed)
        rng.shuffle(deck)
        return deck


def run_simulation(deck_instance, num_simulations, progress_bar, lock):
    card_positions = {card: [0] * 53 for card in [rank + suit for rank in RANKS for suit in SUITS]}
    
    for _ in range(num_simulations):
        deck = deck_instance.create_deck()
        for position, card in enumerate(deck):
            card_positions[card][position + 1] += 1
        
        with lock:
            progress_bar.update(1)
    
    return card_positions



def merge_results(results):
    merged_positions = {card: [0] * 53 for card in [rank + suit for rank in RANKS for suit in SUITS]}
    for result in tqdm(results, desc="Merging results"):
        for card, positions in result.items():
            merged_positions[card] = [sum(x) for x in zip(merged_positions[card], positions)]
    return merged_positions


def plot_distribution(card_positions, output_dir, cards_per_page=16):
    cards = list(card_positions.keys())
    num_pages = (len(cards) + cards_per_page - 1) // cards_per_page

    for page in range(num_pages):
        fig, axs = plt.subplots(cards_per_page // 4, 4, figsize=(20, 10), constrained_layout=True)
        fig.suptitle(f'Distribution of Each Card Over All 52 Positions (Page {page + 1})', fontsize=16)

        start_idx = page * cards_per_page
        end_idx = min(start_idx + cards_per_page, len(cards))

        for i, card in enumerate(cards[start_idx:end_idx]):
            ax = axs[i // 4, i % 4]
            ax.bar(range(1, 53), card_positions[card][1:])  # Skip the 0th position
            ax.set_title(card)
            ax.set_xlabel('Position')
            ax.set_ylabel('Frequency')
            ax.set_xlim(1, 52)

        plt.savefig(os.path.join(output_dir, f'card_distribution_page_{page + 1}.png'))
        plt.close(fig)


def save_avg_location_to_csv(card_positions, filename):
    df = pd.DataFrame(card_positions).iloc[1:]  # Skip the 0th position
    avg_locations = df.apply(lambda x: np.average(range(1, 53), weights=x), axis=0) - 0.5  # Correctly calculate weighted average position
    avg_locations = avg_locations.reset_index()
    avg_locations.columns = ['Card', 'Avg Location']
    avg_locations.to_csv(filename, index=False)


def plot_statistical_analysis(card_positions, output_dir):
    df = pd.DataFrame(card_positions).iloc[1:]
    means = df.apply(lambda x: np.average(range(1, 53), weights=x), axis=0)  # Correctly calculate weighted average position
    std_devs = df.std(axis=0)

    fig, axs = plt.subplots(2, 1, figsize=(15, 10), constrained_layout=True)

    axs[0].bar(means.index.astype(str), means.values)
    axs[0].set_title('Mean Position of Each Card')
    axs[0].set_xlabel('Card')
    axs[0].set_ylabel('Mean Position')

    axs[1].bar(std_devs.index.astype(str), std_devs.values)
    axs[1].set_title('Standard Deviation of Each Card\'s Position')
    axs[1].set_xlabel('Card')
    axs[1].set_ylabel('Standard Deviation')

    plt.savefig(os.path.join(output_dir, 'statistical_analysis.png'))
    plt.close(fig)


def plot_heatmap(card_positions, output_dir, num_simulations):
    # Create a DataFrame skipping the 0th position
    df = pd.DataFrame(card_positions).iloc[1:]

    if num_simulations < 10000:
        vmin = 0
        vmax = num_simulations/20

    elif num_simulations < 999999:
        vmin = num_simulations / 53
        vmax = num_simulations / 51
    else:
        vmin = num_simulations / 59
        vmax = num_simulations / 45

    plt.figure(figsize=(20, 15))
    sns.heatmap(df, annot=True, fmt='d', cmap='coolwarm', cbar=True, xticklabels=df.columns, yticklabels=range(1, 53),
                annot_kws={"size": 5},vmin=vmin, vmax=vmax)
    plt.title('Heatmap of Card Positions in the Deck')
    plt.xlabel('Card')
    plt.ylabel('Position in Deck')
    plt.savefig(os.path.join(output_dir, 'heatmap.png'))
    plt.close()


def chi_squared_test(card_positions, num_simulations):
    observed_frequencies = np.array([card_positions[card][1:] for card in card_positions]).flatten()
    expected_frequencies = np.full_like(observed_frequencies, num_simulations / 52)
    
    # Normalize observed frequencies to match the sum of expected frequencies
    observed_sum = np.sum(observed_frequencies)
    expected_sum = np.sum(expected_frequencies)
    normalized_observed_frequencies = observed_frequencies * (expected_sum / observed_sum)
    
    chi2_stat, p_value = chisquare(normalized_observed_frequencies, expected_frequencies)
    return chi2_stat, p_value


def runs_test(deck_instance, num_simulations):
    sequences = []
    for _ in range(num_simulations):
        deck = deck_instance.create_deck()
        sequence = [RANKS.index(card[:-1]) for card in deck]
        sequences.extend(sequence)
    z_stat, p_value = runstest_1samp(sequences)
    return z_stat, p_value


def kolmogorov_smirnov_test(deck_instance, num_simulations):
    positions = np.zeros((52, 52))
    for _ in range(num_simulations):
        deck = deck_instance.create_deck()
        for position, card in enumerate(deck):
            rank_index = RANKS.index(card[:-1])
            positions[rank_index][position] += 1
    cdf_values = np.cumsum(positions, axis=1) / num_simulations
    expected_cdf = np.linspace(1 / 52, 1, 52)
    ks_stat, p_value = kstest(cdf_values.flatten(), expected_cdf)
    return ks_stat, p_value


if __name__ == "__main__":
    start_time = time.time()  # Start time measurement

    base_output_dir = 'Statistics'
    os.makedirs(base_output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("Shuffle_Deck_Analysis_%Y%m%d_%H%M")
    output_dir = os.path.join(base_output_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    deck_instance = Deck()
    num_simulations = 6000000
    num_threads = 12
    simulations_per_thread = num_simulations // num_threads

    lock = threading.Lock()
    progress_bar = tqdm(total=num_simulations, desc="Running simulations")

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(run_simulation, deck_instance, simulations_per_thread, progress_bar, lock) for _ in range(num_threads)]
        results = [future.result() for future in futures]

    progress_bar.close()

    card_positions = merge_results(results)

    plot_distribution(card_positions, output_dir)
    save_avg_location_to_csv(card_positions, os.path.join(output_dir, 'avg_card_locations.csv'))

    plot_statistical_analysis(card_positions, output_dir)
    plot_heatmap(card_positions, output_dir, num_simulations)

    # Chi-Squared Test
    chi2_stat, chi2_p_value = chi_squared_test(card_positions, num_simulations)
    print(f"Chi-Squared Statistic: {chi2_stat}, P-Value: {chi2_p_value}")

    # Runs Test
    runs_z_stat, runs_p_value = runs_test(deck_instance, num_simulations)
    print(f"Runs Test Z-Statistic: {runs_z_stat}, P-Value: {runs_p_value}")

    # Kolmogorov-Smirnov Test
    ks_stat, ks_p_value = kolmogorov_smirnov_test(deck_instance, num_simulations)
    print(f"Kolmogorov-Smirnov Statistic: {ks_stat}, P-Value: {ks_p_value}")

    # Checking the average positions
    df = pd.DataFrame(card_positions).iloc[1:]
    avg_locations = df.apply(lambda x: np.average(range(1, 53), weights=x) , axis=0)  - 0.5 # Adjust to 1-52 range
    print("Average positions:\n", avg_locations)
    print("Mean of averages:", avg_locations.mean())

    end_time = time.time()  # End time measurement
    print(f"Total execution time: {end_time - start_time} seconds")
