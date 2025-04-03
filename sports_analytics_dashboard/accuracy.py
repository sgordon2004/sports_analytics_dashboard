"""
Evaluates model accuracy by comparing predictions against actual outcomes.
"""

from .predictor import predict_win_probability
from .ml_model import train_model
from nba_api.stats.endpoints import LeagueGameLog
from .utils import normalize_team_name
from .nba import fetch_team_stats
import pandas as pd
import os
import time
from datetime import datetime

CACHE_PATH = "game_logs.csv"

def fetch_game_logs_with_cache(season, retries=3, delay=2):
    """
    Returns cached logs if available, else fetches from API and caches result.

    Args:
        season (string): the NBA season to cache games for
        retries (int): the number of times the function should retry after a fail until terminating
        delay (int): the number of seconds the function should wait in between API requests
    Returns:
        None
    """
    # Check if cache exists and is fresh
    if os.path.exists(CACHE_PATH):
        modified = datetime.fromtimestamp(os.path.getmtime(CACHE_PATH))
        if modified.date() == datetime.today().date():
            print("📦 Using cached game logs.")
            return pd.read_csv(CACHE_PATH)

    # Else fetch from API
    for attempt in range(retries):
        try:
            print(f"📥 Fetching game logs for {season} (attempt {attempt + 1})")
            df = LeagueGameLog(season=season, season_type_all_star="Regular Season").get_data_frames()[0]
            df.to_csv(CACHE_PATH, index=False)
            return df
        except Exception as e:
            print(f"❌ Failed to fetch game logs (attempt {attempt + 1}): {e}")
            time.sleep(delay)

    print("🚫 Could not retrieve game logs after retries.")
    return None


if __name__ == "__main__":
    # Optionally retrain model
    train_model()

    # Evaluate accuracy
    current_year = datetime.today().year
    season = f"{current_year - 1}-{str(current_year)[2:]}" if datetime.today().month < 10 else f"{current_year}-{str(current_year + 1)[2:]}"
    games = fetch_game_logs_with_cache(season)
    games = games.drop_duplicates(subset="GAME_ID")

    if games is None:
        print("❌ Accuracy check aborted due to missing game logs.")
        exit()

    correct = 0
    total = 0

    all_team_stats = fetch_team_stats()
    if all_team_stats is None:
        print("🚫 Could not retrieve team stats.")
    print(all_team_stats)

    for _, row in games.iterrows():
        matchup = row["MATCHUP"]  # Example: "LAL vs. BOS" or "LAL @ BOS"

        if "vs." in matchup:
            home_raw = row["TEAM_NAME"]
            away_raw = matchup.split("vs. ")[-1]
        else:
            away_raw = row["TEAM_NAME"]
            home_raw = matchup.split("@ ")[-1]

        home = normalize_team_name(home_raw.strip())
        away = normalize_team_name(away_raw.strip())

        

        home_stats = all_team_stats.get(home)
        away_stats = all_team_stats.get(away)

        if home_stats is None:
            print(f"🚫 Missing stats for home team: {home}")
        if away_stats is None:
            print(f"🚫 Missing stats for away team: {away}")

        predicted_probs = predict_win_probability(home, away)
        if not predicted_probs or "winner" not in predicted_probs:
            print(f"⚠️ Skipping game {home} vs. {away} — missing prediction output.")
            continue
        
        print(f"✅ Predicted winner: {predicted_probs['winner']}")
        predicted_winner = predicted_probs["winner"]
        actual = home if row["WL"] == "W" else away

        if predicted_winner == actual:
            correct += 1
        total += 1

    if total > 0:
        print(f"✅ Model Accuracy: {correct / total:.2%} ({correct}/{total})")
    else:
        print("⚠️ No valid games to evaluate accuracy.")