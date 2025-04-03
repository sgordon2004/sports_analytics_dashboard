from nba_api.stats.endpoints import LeagueDashTeamStats
from .predictor import get_team_stats

# Fetch team stats for 2023-24 regular season
df = LeagueDashTeamStats(season='2023-24').get_data_frames()[0]

# Print all columns returned by the API
# print(df.columns.tolist())

features = [
    "W_PCT", "NET_RATING", "TURNOVER_PCT",
    "PLUS_MINUS", "TOV", "FGA", "FTA", "REB", "AST",
    "W_PCT_LAST5", "NET_RATING_LAST5", "TURNOVER_PCT_LAST5", "REB_LAST5", "AST_LAST5"
]

# stats = {}
# for _, row in df.iterrows():
#     team = row["TEAM_NAME"]
#     print(f"⛳ Team from API: {team}")
#     fga = row["FGA"]
#     fta = row["FTA"]
#     tov = row["TOV"]
#     possessions = fga + 0.44 * fta + tov
#     tov_pct = 100 * tov / possessions if possessions > 0 else 0

#     stats[team] = {
#         "W_PCT": row["W_PCT"],
#         "NET_RATING": row["PLUS_MINUS"] / row["GP"] if row["GP"] else 0,
#         "TURNOVER_PCT": tov_pct,
#         "PLUS_MINUS": row["PLUS_MINUS"],
#         "TOV": row["TOV"],
#         "FGA": row["FGA"],
#         "FTA": row["FTA"],
#         "REB": row["REB"],
#         "AST": row["AST"]
#     }

#     print(stats[team])

# for k in stats[team]:
#     print(stats[team].get(k))

from .ml_model import train_model
train_model()