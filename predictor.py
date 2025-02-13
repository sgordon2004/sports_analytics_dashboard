from nba_api.stats.endpoints import LeagueDashTeamStats
from datetime import datetime

team_name_mapping = {
    "LA Clippers": "Los Angeles Clippers",
    "NY Knicks": "New York Knicks",
    "SA Spurs": "San Antonio Spurs",
    "GS Warriors": "Golden State Warriors",
    "OKC Thunder": "Oklahoma City Thunder"
}

def normalize_team_name(team_name):
    """Ensures team names match between different NBA API endpoints."""
    return team_name_mapping.get(team_name, team_name)

def get_current_season():
    """Automatically determine the current NBA season based on the date"""
    year = datetime.today().year
    month = datetime.today().month
    # NBA seasons start in October and end in June of the following year
    if month >= 10: # if it's October or later, we're in a new season
        return f"{year}-{str(year + 1)[2:]}"
    else: # Otherwise, it's still last season
        return f"{year - 1}-{str(year)[2:]}"
    
def fetch_team_stats():
    """Fetch current NBA team stats (Net Rating, Offensive and Defensive Rating)"""
    current_season = get_current_season() # Gets dynamically updated season
    print(f"Fetching stats for season: {current_season}") # Debugging

    try:
        stats = LeagueDashTeamStats(season=current_season)
        print("Raw API Response:", stats.nba_response)  # Debugging
        team_data = stats.get_dict()["resultSets"][0]["rowSet"]

        team_stats = {}
        for team in team_data:
            team_name = normalize_team_name(team[1])  # Team Name
            net_rating = team[7] - team[8]  # Net Rating (ORTG - DRTG)
            team_stats[team_name] = {"net_rating": net_rating}

        print("Available team stats:", team_stats.keys()) # Debugging
        return team_stats

    except Exception as e:
        print("Error fetching NBA stats:", e)
        return {}

# Map possible shortenings/variations of team names



def predict_winner(home_team, away_team):
    """Predicts the winner of an NBA game using Net Rating."""
    team_stats = fetch_team_stats()
    
    # Normalize team names
    home_team = normalize_team_name(home_team)
    away_team = normalize_team_name(away_team)

    # Debugging: Print if teams are missing from the dataset
    if home_team not in team_stats:
        print(f"Warning: No stats found for home team: {home_team}")
    if away_team not in team_stats:
        print(f"Warning: No stats found for away team: {away_team}")
    
    if home_team not in team_stats or away_team not in team_stats:
        return "Unknown (insufficient data)"
    
    home_net = team_stats[home_team]["net_rating"]
    away_net = team_stats[away_team]["net_rating"]
    home_win = f"{home_team}"
    away_win = f"{away_team}"

    return home_win if home_net > away_net else away_win