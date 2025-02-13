from nba_api.stats.endpoints import ScoreboardV2
from nba_api.stats.static import teams
from datetime import datetime

# Fetch all NBA teams
nba_teams = teams.get_teams() # List of dictionaries
# print(nba_teams)
# # Print team data (ID and name)
# for team in nba_teams:
#     print(f"ID: {team['id']} | Name: {team['full_name']}")

# Dictionary to map team IDs to team names
team_names = {}
for team in nba_teams:
    id = team["id"]
    name = team["full_name"]
    team_names[id] = name
# print(team_names)

# Get today's dates in YYYYMMDD format
today = datetime.today().strftime('%Y-%m-%d')

# Fetch scoreboard data
scoreboard = ScoreboardV2(day_offset = '0', game_date = today, league_id = '00')

# Convert to a dictionary
games = scoreboard.get_dict()['resultSets'][0]['rowSet']

# Function to parse and display game details
def todays_games():
    game_list = []
    for game in games:
        game_id = game[2]  # Game ID
        home_team = team_names[game[6]]  # Home team
        away_team = team_names[game[7]]  # Away team
        game_time = game[4]  # Scheduled time
        print(f"Game ID: {game_id} | {away_team} @ {home_team} at {game_time}")
        game_list.append({
            "game_id": game_id,
            "home_team": home_team,
            "away_team": away_team,
            "game_time": game_time
        })
    return game_list

# print(todays_games())