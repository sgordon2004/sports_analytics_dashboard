"""
sports_analytics_dashboard

A Flask web application for predicting NBA game outcomes using recent team statistics,
win probability models, and historical performance data. Integrates NBA API data, 
machine learning models, and rolling average metrics to generate insights and visualizations.
"""

# Import Flask
from flask import Flask
# Create instance of Flask
app = Flask(__name__)
# Import routes for Flask
from . import routes