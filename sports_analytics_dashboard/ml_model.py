"""
This module creates and trains the machine learning model used to predict NBA game winners.

It defines the feature set, trains the model on historical game data, and saves the trained model for future use.
"""

import pandas as pd
import numpy as np
import time
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib
from datetime import datetime
from nba_api.stats.endpoints import LeagueDashTeamStats
from .nba import get_last5_games_stats
from .utils import get_team_id

def get_current_season():
    """
    Returns the current NBA season.

    Returns:
        string: current NBA season
    """
    year = datetime.today().year
    month = datetime.today().month
    return f"{year}-{str(year + 1)[2:]}" if month >= 10 else f"{year - 1}-{str(year)[2:]}"


def retry_get_last5_games_stats(team_id, retries=3, delay=3):
    """
    Retries the API call to get last 5 game stats up to `retries` times.

    Args:
        team_id (int): NBA team ID.
        retries (int): Number of retry attempts.
        delay (int): Delay in seconds between retries.

    Returns:
        dict: last 5 game stats or empty dictionary on failure.
    """
    for attempt in range(retries):
        result = get_last5_games_stats(team_id)
        if result:
            return result
        print(f"⏳ Retrying team_id {team_id} (attempt {attempt + 1})...")
        time.sleep(delay)
    print(f"❌ Final failure for team_id {team_id}")
    return {}


def fetch_historical_data():
    """
    Uses current season stats to create and populate a Pandas dataframe
    containing important statistics for later use in determining
    likely outcome.

    Returns:
        df (Pandas Dataframe): dataframe with team identifiers and necessary statistics
        for calculating likely winner.
    """
    current_season = get_current_season()
    stats = LeagueDashTeamStats(season=current_season).get_dict()

    actual_columns = stats["resultSets"][0]["headers"]
    team_data = stats["resultSets"][0]["rowSet"]

    df = pd.DataFrame(team_data, columns=actual_columns)
    df = df[["TEAM_ID", "TEAM_NAME", "GP", "W", "L", "W_PCT", "PLUS_MINUS", "TOV", "FGA", "FTA"]]
    df["NET_RATING"] = df["PLUS_MINUS"] / df["GP"]
    df["TURNOVER_PCT"] = (df["TOV"] / (df["FGA"] + (0.44 * df["FTA"]) + df["TOV"])) * 100

    df["REB"] = None
    df["AST"] = None
    df["W_PCT_LAST5"] = None
    df["NET_RATING_LAST5"] = None
    df["TURNOVER_PCT_LAST5"] = None
    df["REB_LAST5"] = None
    df["AST_LAST5"] = None

    for idx, row in df.iterrows():
        team_name = row["TEAM_NAME"]
        team_id = get_team_id(team_name)
        if team_id:
            last5 = retry_get_last5_games_stats(team_id)
            if last5:
                df.at[idx, "W_PCT_LAST5"] = last5.get("W_PCT")
                df.at[idx, "NET_RATING_LAST5"] = last5.get("NET_RATING")
                df.at[idx, "TURNOVER_PCT_LAST5"] = last5.get("TURNOVER_PCT")
                df.at[idx, "REB_LAST5"] = last5.get("REB")
                df.at[idx, "AST_LAST5"] = last5.get("AST")

        # You can pull REB/AST from the base df if not pulling from last5
        # These are part of the original API response
        df.at[idx, "REB"] = team_data[idx][actual_columns.index("REB")]
        df.at[idx, "AST"] = team_data[idx][actual_columns.index("AST")]

    df["WIN"] = (df["NET_RATING"] > 0).astype(int)
    return df


def train_model():
    """
    Trains a logistic regression model to predict win probabilites.
    """
    df = fetch_historical_data()
    print("✅ Final training columns:", df.columns.tolist())

    print("📊 Nulls per column:\n", df.isna().sum())

    df = df.dropna()
    print(f"🧪 Training on {len(df)} teams after dropping NaNs")

    # Optional: Save for debugging
    df.to_csv("training_data.csv", index=False)

    # Define features and target
    X = df[[
        'W_PCT', 'NET_RATING', 'TURNOVER_PCT', 'PLUS_MINUS', 'TOV',
        'FGA', 'FTA', 'REB', 'AST', 'W_PCT_LAST5', 'NET_RATING_LAST5',
        'TURNOVER_PCT_LAST5', 'REB_LAST5', 'AST_LAST5'
    ]]
    y = df["WIN"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=1000)
    print("Training columns:", list(X_train.columns))
    print("Predicting with:", list(X.columns))
    print("🔎 Features passed to model:", list(X.columns))
    
    model.fit(X_train, y_train)
    print("✅ Model was trained on:", list(model.feature_names_in_))
    joblib.dump(model, "win_probability_model.pkl")

    print("✅ Model trained and saved!")


if __name__ == "__main__":
    train_model()