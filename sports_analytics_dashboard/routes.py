"""
Defines the Flask routes for the NBA analytics web application.

This module handles the routing logic, connects frontend templates to backend
functions, and facilitates user interaction with the model, team statistics,
and predictions.

Routes include:
- Homepage/dashboard
- Team statistics display
- Game winner predictions
- Model evaluation results
"""

# Importing Flask app instance from __init__.py
from sports_analytics_dashboard import app
from .nba import todays_games
from .predictor import predict_win_probability
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
        probabilities = predict_win_probability(game["home_team"], game["away_team"])
        game["win_probabilities"] = probabilities

    return render_template("games.html", games=games)
