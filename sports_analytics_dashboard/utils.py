"""
This modules handles all things that don't belong in other more action-specific modules.
It holds helper functions that feed data to other modules, and transforms/manipulates data
that has already been fetched.
"""

from nba_api.stats.static import teams
from datetime import datetime

# Get today's dates in YYYYMMDD format
today = datetime.today().strftime('%Y-%m-%d')

# Fetch all NBA teams
nba_teams = teams.get_teams() # nba_teams is a list of dictionaries (e. dictionary corresponds to a different team)

# Creating a dictionary to map unique team IDs to team names
team_names = {}
for team in nba_teams:
    id = team["id"]
    name = team["full_name"]
    team_names[id] = name

# A dictionary mapping NBA team name abbreviations and common variations to standardized names.
team_name_mapping = {
    "NY Knicks": "New York Knicks",
    "SA Spurs": "San Antonio Spurs",
    "GS Warriors": "Golden State Warriors",
    "OKC Thunder": "Oklahoma City Thunder",
    "Los Angeles Clippers": "LA Clippers",
    "NOP": "New Orleans Pelicans",
    "NYK": "New York Knicks",
    "SAS": "San Antonio Spurs",
    "GSW": "Golden State Warriors",
    "OKC": "Oklahoma City Thunder",
    "ATL": "Atlanta Hawks",
    "BKN": "Brooklyn Nets",
    "BOS": "Boston Celtics",
    "CHA": "Charlotte Hornets",
    "CHI": "Chicago Bulls",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "LAC": "LA Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NO": "New Orleans Pelicans",
    "NOP": "New Orleans Pelicans",
    "NY": "New York Knicks",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHX": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "WAS": "Washington Wizards"
}

def normalize_team_name(team_name):
    """
    Returns the standardized version of an NBA team's name.

    Args:
        team_name (string): the name or abbreviation of the NBA team to standardize.
    
    Returns:
        (string): the standardized version of the team's name.
    """
    return team_name_mapping.get(team_name.strip(), team_name.strip())


def get_current_season():
    """
    Returns the current NBA season.

    Returns:
        string: current NBA season
    """
    year = datetime.today().year
    month = datetime.today().month
    return f"{year}-{str(year + 1)[2:]}" if month >= 10 else f"{year - 1}-{str(year)[2:]}"

def get_team_id(team_name):
    """
    Returns the unique team ID number of a given NBA team.

    Args:
        team_name (string): The NBA team to find the ID of.
    
    Returns:
        None
    """
    standardized_name = normalize_team_name(team_name)
    for team in nba_teams:
        if normalize_team_name(team["full_name"]) == standardized_name:
            return team["id"]
    return None

# Test
# if __name__ == "__main__":
#     test_teams = [
#         "LAC",                      # abbreviation
#         "Los Angeles Clippers",     # official name
#         "LA Clippers",              # normalized/expected match
#         "NYK",
#         "New York Knicks",
#         "NY Knicks",
#         "BOS",
#         "Boston Celtics",
#         "Charlotte Hornets",        # one with no alias
#         "Fake Team"                 # should return None
#     ]

#     for name in test_teams:
#         team_id = get_team_id(name)
#         print(f"{name} -> {team_id}")