"""This module interacts with nba_api and gathers today's NBA games."""

from nba_api.stats.endpoints import ScoreboardV2, LeagueGameLog, LeagueDashTeamStats
from .utils import get_current_season, get_team_id, team_names, today
from pathlib import Path
import json

CACHE_FILE = Path("team_stats_cache.json")

# Fetch scoreboard data
scoreboard = ScoreboardV2(day_offset = '0', game_date = today, league_id = '00')
# Convert all of today's games to a dictionary
games = scoreboard.get_dict()['resultSets'][0]['rowSet']

# Function to parse and display game details
def todays_games():
    """
    Parses and formats game details for display.

    Returns:
        game_list (list): A list of all the NBA games being
        played today w/ scheduled time, home team, and away team.
    """
    game_list = []
    for game in games:
        game_id = game[2]  # Game ID
        home_team = team_names[game[6]]  # Home team
        away_team = team_names[game[7]]  # Away team
        game_time = game[4]  # Scheduled time

        game_list.append({
            "game_id": game_id,
            "home_team": home_team,
            "away_team": away_team,
            "game_time": game_time
        })
    return game_list

def get_last5_games_stats(team_id):
    """
    Calculates and returns stats over the past 5 games played for a given NBA team.

    Args:
        team_id (int): the unique identification number of the NBA team

    Returns:
        Dictionary: contains the win percentage, avg. plus/minus,
        turnover %, rebounds, and assists.
    """
    from time import sleep
    import random

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            log = LeagueGameLog(
                season=get_current_season(),
                season_type_all_star="Regular Season",
                timeout=10  # Shorter timeout to avoid long hangs
            )
            df = log.get_data_frames()[0]
            team_games = df[df["TEAM_ID"] == team_id].head(5)

            if team_games.empty:
                print(f"⚠️ No games found for team_id {team_id}")
                return {}

            avg_plus_minus = team_games["PLUS_MINUS"].mean()
            avg_tov_pct = 100 * team_games["TOV"].sum() / (
                team_games["FGA"].sum() + 0.44 * team_games["FTA"].sum() + team_games["TOV"].sum()
            )
            win_pct = team_games["WL"].apply(lambda x: 1 if x == "W" else 0).mean()

            avg_reb = team_games["REB"].mean()
            avg_ast = team_games["AST"].mean()

            return {
                "W_PCT": win_pct,
                "NET_RATING": avg_plus_minus,
                "TURNOVER_PCT": avg_tov_pct,
                "REB": avg_reb,
                "AST": avg_ast
            }

        except Exception as e:
            print(f"⏳ Attempt {attempt+1}/{max_attempts} failed for team_id {team_id}: {e}")
            sleep(random.uniform(1, 3))  # brief delay before retry
    print(f"❌ All {max_attempts} attempts failed for team_id {team_id}")
    return {}

def fetch_team_stats():
    """
    Returns performance statistics for all NBA teams with caching.

    Returns:
        stats (dictionary): contains all NBA teams and their statistics.
    """
    cache_path = CACHE_FILE

    # Load from cache if available
    if cache_path.exists():
        try:
            with cache_path.open("r") as f:
                cached_stats = json.load(f)
            print("📦 Loaded team stats from cache.")
            return cached_stats
        except Exception as e:
            print(f"⚠️ Failed to read cache: {e}")

    try:
        print("Fetching stats for current season:", get_current_season())
        response = LeagueDashTeamStats(season=get_current_season())
        df = response.get_data_frames()[0]

        stats = {}
        for _, row in df.iterrows():
            team = row["TEAM_NAME"]
            print(f"⛳ Team from API: {team}")
            fga = row["FGA"]
            fta = row["FTA"]
            tov = row["TOV"]
            possessions = fga + 0.44 * fta + tov
            tov_pct = 100 * tov / possessions if possessions > 0 else 0

            stats[team] = {
                "W_PCT": row["W_PCT"],
                "NET_RATING": row["PLUS_MINUS"] / row["GP"] if row["GP"] else 0,
                "TURNOVER_PCT": tov_pct,
                "PLUS_MINUS": row["PLUS_MINUS"],
                "TOV": row["TOV"],
                "FGA": row["FGA"],
                "FTA": row["FTA"],
                "REB": row["REB"],
                "AST": row["AST"]
            }

            team_id = get_team_id(team)
            print(f"🔑 Team ID for {team}: {team_id}")
            if team_id:
                try:
                    last5 = get_last5_games_stats(team_id)
                    if last5:
                        stats[team]["W_PCT_LAST5"] = last5["W_PCT"]
                        stats[team]["NET_RATING_LAST5"] = last5["NET_RATING"]
                        stats[team]["TURNOVER_PCT_LAST5"] = last5["TURNOVER_PCT"]
                        stats[team]["REB_LAST5"] = last5["REB"]
                        stats[team]["AST_LAST5"] = last5["AST"]
                except Exception as e:
                    print(f"❌ Failed to get last 5 stats for {team}: {e}")

        print("✅ Teams in team_stats:", list(stats.keys()))

        # Save to cache
        try:
            with cache_path.open("w") as f:
                json.dump(stats, f, indent=2)
            print("💾 Team stats cached.")
        except Exception as e:
            print(f"⚠️ Failed to write cache: {e}")

        return stats
    except Exception as e:
        print("⚠️ Could not fetch stats from NBA API:", e)
        return None
