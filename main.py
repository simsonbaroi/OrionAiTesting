from app import app
from models import *  # Import all models to ensure tables are created

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
