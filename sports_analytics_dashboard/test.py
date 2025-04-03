from nba_api.stats.endpoints import PlayByPlayV2, LeagueDashTeamStats, ScoreboardV2
from datetime import datetime, timedelta
import pandas as pd

# Manually mapping team IDs to names
team_id_map = {
    1610612764: "Washington Wizards",
    1610612737: "Atlanta Hawks",
    1610612738: "Boston Celtics",
    1610612751: "Brooklyn Nets",
    1610612749: "Milwaukee Bucks",
    1610612752: "New York Knicks",
    1610612753: "Orlando Magic",
    1610612755: "Philadelphia 76ers",
    1610612761: "Toronto Raptors",
    1610612741: "Chicago Bulls",
    # Add more teams as needed...
}

def get_last_n_games(team_name, num_games=5):
    """Fetches the last `num_games` games for a given team."""
    today = datetime.today()
    game_ids = []
    
    # Iterate over the last `num_games` days to find games
    for i in range(num_games * 3):  # Search up to 3x the number of requested games
        date_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        scoreboard = ScoreboardV2(game_date=date_str)
        games = scoreboard.get_dict()['resultSets'][0]['rowSet']

        for game in games:
            home_team_id = game[6]
            away_team_id = game[7]

            home_team = team_id_map.get(home_team_id, f"Team {home_team_id}")
            away_team = team_id_map.get(away_team_id, f"Team {away_team_id}")

            if team_name in [home_team, away_team]:
                game_ids.append(game[2])  # Game ID

            if len(game_ids) >= num_games:
                return game_ids

    return game_ids

def get_free_throw_data(game_id):
    """Extracts play-by-play data for free throw events."""
    pbp = PlayByPlayV2(game_id=game_id).get_data_frames()[0]
    free_throws = pbp[pbp["EVENTMSGTYPE"] == 3]  # Free throws are event type 3
    return free_throws

def count_possession_changing_fts(free_throws):
    """Counts free throws that result in a possession change."""
    possession_end_fts = 0
    current_shooter = None
    last_free_throw = None

    for _, row in free_throws.iterrows():
        shooter = row["PLAYER1_ID"]
        event_desc = row["HOMEDESCRIPTION"] or row["VISITORDESCRIPTION"]
        
        if event_desc and ("1 of 1" in event_desc or "2 of 2" in event_desc or "3 of 3" in event_desc):
            last_free_throw = row  # Store the last free throw
        
        if last_free_throw is not None and not free_throws.empty:
            last_free_throw = last_free_throw.iloc[0] if isinstance(last_free_throw, pd.DataFrame) else last_free_throw

        if last_free_throw is not None and shooter != current_shooter:
            if "MISS" in str(last_free_throw["HOMEDESCRIPTION"]) or "MISS" in str(last_free_throw["VISITORDESCRIPTION"]):
                possession_end_fts += 1

        current_shooter = shooter
    
    return possession_end_fts

def get_average_ft_possession_factor(team_name, num_games=5):
    """Calculates the average possession-ending FT factor across multiple games."""
    game_ids = get_last_n_games(team_name, num_games)
    
    total_fts = 0
    possession_ending_fts = 0
    
    for game_id in game_ids:
        free_throws = get_free_throw_data(game_id)
        possession_ending_fts += count_possession_changing_fts(free_throws)
        total_fts += len(free_throws)
    
    if total_fts == 0:
        return 0.44  # Default fallback if no data is available

    return possession_ending_fts / total_fts  # Compute new FT Possession Factor

def fetch_team_stats(team_name, num_games=5):
    """Fetches team stats and recalculates TOV% using the new FT Possession Factor."""
    current_season = datetime.today().year  # Current season year (can be adjusted)
    
    try:
        stats = LeagueDashTeamStats(season=f"{current_season-1}-{str(current_season)[2:]}").get_dict()
        print(f"Season {current_season}-{str(current_season+1)[2:]}")
        team_data = stats["resultSets"][0]["rowSet"]

        team_stats = {}
        available_teams = [team[1] for team in team_data]  # Extract all team names
        print(f"✅ Available Teams in API: {available_teams}")  # Debugging

        for team in team_data:
            if team_name in team[1]:  # Check if exact match
                gp = team[2]
                tov_per_game = team[20] / gp if gp > 0 else 0
                fta_per_game = team[14] / gp if gp > 0 else 0
                fga_per_game = team[8] / gp if gp > 0 else 0

                # Get new Free Throw Possession Factor
                ft_possession_factor = get_average_ft_possession_factor(team_name, num_games)

                # Compute new TOV%
                denominator = (tov_per_game + fga_per_game + (ft_possession_factor * fta_per_game))
                tov_percentage = (tov_per_game / denominator) * 100 if denominator > 0 else 0

                team_stats[team_name] = {
                    "GP": gp,
                    "TOV_PER_GAME": tov_per_game,
                    "FTA_PER_GAME": fta_per_game,
                    "FGA_PER_GAME": fga_per_game,
                    "FT_POSS_FACTOR": ft_possession_factor,
                    "TOV_PERCENTAGE": tov_percentage
                }

        if team_name not in team_stats:
            print(f"⚠️ ERROR: '{team_name}' not found in API response!")

        return team_stats.get(team_name, {})

    except Exception as e:
        print("Error fetching NBA stats:", e)
        return {}


# Fetch updated TOV% for the Wizards
wizards_stats = fetch_team_stats("Washington Wizards", num_games=5)

if wizards_stats:
    print(f"📊 Updated Turnover Percentage (TOV%) for Wizards: {wizards_stats.get('TOV_PERCENTAGE', 'N/A'):.2f}%")
    print(f"🏀 Free Throw Possession Factor Used: {wizards_stats.get('FT_POSS_FACTOR', 'N/A'):.3f}")
else:
    print("⚠️ No team stats found for Washington Wizards.")

from .ml_model import train_model
train_model()