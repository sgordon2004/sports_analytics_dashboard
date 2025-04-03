"""
This module predicts the winner of an NBA game using a machine learning model.

It pulls recent team statistics, processes input features, and returns a win prediction based on historical performance data and model inference.
"""

from .utils import normalize_team_name
from .nba import fetch_team_stats
import pandas as pd
import joblib
import os

# Load model
model_path = os.path.join(os.path.dirname(__file__), "win_probability_model.pkl")
try:
    model = joblib.load(model_path)
    print("✅ Model loaded.")
except FileNotFoundError:
    print("⚠️ Warning: Model file not found. Please train the model first.")
    model = None

# Pre-load stats
team_stats = fetch_team_stats()

def get_team_stats():
    """
    Uses fetch_team_stats() to get the stats of all NBA teams.

    Returns:
        team_stats (dictionary): NBA teams attached to their stats
    """
    global team_stats
    if team_stats is None:
        team_stats = fetch_team_stats()
    return team_stats

def get_features(team, stats, feature_keys):
    # print("Inside get_features, team_a keys:", team.keys()) # debug line
    return [stats[team].get(k) for k in feature_keys]

def predict_win_probability(home_team, away_team):
    """
    Feeds data to the machine learning model so that it can predict the game winner.

    Args:
        home_team (string): team playing at home
        away_team (string): team playing as visitor
    
    Returns:
        dictionary: proabilities
    """
    global team_stats
    if team_stats is None:
        print("❌ team_stats is None")
        return None

    if model is None:
        print("❌ Model is None, cannot predict.")
        return None

    print("🧠 Model is ready, about to predict...")
    print(f"🏷️ Model classes: {getattr(model, 'classes_', 'N/A')}")

    home_team = normalize_team_name(home_team)
    away_team = normalize_team_name(away_team)
    print(f"🔍 Normalized names: home={home_team}, away={away_team}")

    print(f"📊 Available stats keys: {sorted(list(team_stats.keys()))}")

    if home_team not in team_stats:
        print(f"🚫 Missing stats for home team: {home_team}")
        print(f"✅ Available teams: {sorted(list(team_stats.keys()))}")
        return None
    if away_team not in team_stats:
        print(f"🚫 Missing stats for away team: {away_team}")
        print(f"✅ Available teams: {sorted(list(team_stats.keys()))}")
        return None

    features = [
        "W_PCT", "NET_RATING", "TURNOVER_PCT",
        "PLUS_MINUS", "TOV", "FGA", "FTA", "REB", "AST",
        "W_PCT_LAST5", "NET_RATING_LAST5", "TURNOVER_PCT_LAST5", "REB_LAST5", "AST_LAST5"
    ]

    try:
        print(f"🔮 Predicting win probability for {home_team} vs {away_team}")
        home_features = get_features(home_team, team_stats, features)
        away_features = get_features(away_team, team_stats, features)
        print(f"🧬 Keys for {home_team}: {list(team_stats[home_team].keys())}")
        print(f"🧪 home_features: {home_features}")
        print(f"🧪 away_features: {away_features}")

        if any(f is None for f in home_features):
            print(f"⚠️ Incomplete stats for {home_team}:")
            print(f"    Features expected: {features}")
            print(f"    Features found: {team_stats[home_team]}")
            print("❌ Skipping due to missing feature(s)")
            return None
        if any(f is None for f in away_features):
            print(f"⚠️ Incomplete stats for {away_team}:")
            print(f"    Features expected: {features}")
            print(f"    Features found: {team_stats[away_team]}")
            print("❌ Skipping due to missing feature(s)")
            return None

        home = pd.DataFrame([home_features], columns=features)
        away = pd.DataFrame([away_features], columns=features)

        print(f"📥 Model input (home): {home}")
        print(f"📥 Model input (away): {away}")

        print("📤 Predicting with columns (home):", list(home.columns))
        print("📤 Predicting with columns (away):", list(away.columns))
        print("✅ Model expects:", list(model.feature_names_in_))
        home_pred = model.predict_proba(home)
        away_pred = model.predict_proba(away)

        home_prob = home_pred[0][1]
        away_prob = away_pred[0][1]
        total = home_prob + away_prob

        home_win_prob = home_prob / total
        away_win_prob = away_prob / total

        predicted_winner = home_team if home_win_prob > away_win_prob else away_team

        print(f"✅ Predicted winner: {predicted_winner}")
        print(f"    {home_team}: {home_win_prob * 100:.2f}%")
        print(f"    {away_team}: {away_win_prob * 100:.2f}%")

        return {
            "winner": predicted_winner,
            "home_team": home_team,
            "home_prob": round(home_win_prob * 100, 2),
            "away_team": away_team,
            "away_prob": round(away_win_prob * 100, 2),
            "model_input": {
                home_team: home_features,
                away_team: away_features
            }
        }

    except Exception as e:
        print(f"❌ Error predicting win probability for {home_team} vs. {away_team}: {e}")
        return None
