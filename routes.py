# Importing Flask app instance from __init__.py
from sports_analytics_dashboard import app
from sports_analytics_dashboard.nba import todays_games
from sports_analytics_dashboard.predictor import predict_winner
# Flask returns rendered templates instead of plain text
from flask import render_template
# Use route() decorator to define root route
@app.route('/')
def home():
    return render_template("index.html")
# Page showing all games today
@app.route('/games')
def games():
    games = todays_games()
    for game in games:
        game["predicted_winner"] = predict_winner(game["home_team"], game["away_team"])
    return render_template("games.html", games=games)
