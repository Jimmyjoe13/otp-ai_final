import os
import logging
import sys # Ajouté pour le logging vers stdout
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from datetime import timedelta # Import timedelta

# Configure logging pour une sortie structurée vers stdout (compatible Railway)
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s')
logger = logging.getLogger(__name__)

# Validate environment variables before starting
from env_validator import validate_environment
if not validate_environment():
    logger.error("Environment validation failed. Please check your Railway environment variables.")
    # In production, we'll continue but log warnings
    # In development, you might want to exit here

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure JWT
app.config["JWT_SECRET_KEY"] = os.environ.get("SESSION_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

# Initialize extensions with app
db.init_app(app)
jwt = JWTManager(app)

# Configure CORS for specific origins
allowed_origins = [
    os.environ.get("DOMAIN", "https://opt-ai.up.railway.app"),
    "http://localhost:5000", 
    "http://127.0.0.1:5000" 
]
CORS(app, resources={
    r"/api/*": {"origins": allowed_origins},
    r"/payment/*": {"origins": allowed_origins},
    r"/auth/*": {"origins": allowed_origins}
}, supports_credentials=True)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

with app.app_context():
    # Import models
    import models  # noqa: F401
    
    # Create database tables
    db.create_all()
    
    # Initialize translations
    import translation
    translation.init_app(app)
    
    # Import and register blueprints
    from routes import api_bp
    from auth import auth_bp
    from chatbot import chatbot_bp
    from payment import payment_bp
    from health import health_bp
    from main_routes import main as main_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(health_bp) 
    app.register_blueprint(main_bp)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # Global error handlers
    @app.errorhandler(500)
    def handle_500(e):
        logger.error(f"Internal server error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
    
    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "Not found", "message": "The requested URL was not found on the server."}), 404
    
    @app.errorhandler(405)
    def handle_405(e):
        return jsonify({"error": "Method not allowed", "message": "The method is not allowed for the requested URL."}), 405
