import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL environment variable is required")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize scheduler
scheduler = BackgroundScheduler()

with app.app_context():
    # Import models to ensure tables are created
    import models
    
    # Create all tables
    db.create_all()
    
    # Import and register routes
    from api.routes import init_routes
    from api.enhanced_routes import init_enhanced_routes
    from api.multi_language_routes import multi_lang_bp
    init_routes(app)
    init_enhanced_routes(app)
    app.register_blueprint(multi_lang_bp)
    
    # Start the scheduler for automated tasks
    from scheduler.tasks import setup_scheduled_tasks
    setup_scheduled_tasks(scheduler)
    
    if not scheduler.running:
        scheduler.start()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

if __name__ != "__main__":
    # When running with gunicorn, ensure scheduler is started
    if not scheduler.running:
        scheduler.start()
