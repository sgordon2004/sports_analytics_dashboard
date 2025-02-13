# Importing Flask app instance from __init__.py
from sports_analytics_dashboard import app
# Use route() decorator to define root route
@app.route('/')
def home():
    return "Sports Analytics Dashboard is up and running!" # Message for testing purposes