# Importing Flask app instance from __init__.py
from sports_analytics_dashboard import app
from sports_analytics_dashboard.nba import todays_games
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
    return render_template("games.html", games=games)