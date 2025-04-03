import os
import sys
import pydoc

# Ensure root project directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

modules = [
    'sports_analytics_dashboard.__init__',
    'sports_analytics_dashboard.accuracy',
    'sports_analytics_dashboard.ml_model',
    'sports_analytics_dashboard.nba',
    'sports_analytics_dashboard.predictor',
    'sports_analytics_dashboard.routes',
    'sports_analytics_dashboard.test',
]

output_dir = os.path.join(os.path.dirname(__file__))
print("📄 Generating PyDocs...\n")

for mod in modules:
    try:
        print(f"📄 Generating doc for {mod}")
        html = pydoc.HTMLDoc().docmodule(__import__(mod, fromlist=['']))
        filename = os.path.join(output_dir, f"{mod.split('.')[-1]}.html")
        with open(filename, 'w') as f:
            f.write(html)
    except Exception as e:
        print(f"⚠️  Could not generate doc for {mod}: {e}")

print("\n✅ All docs generated and saved to ./docs")