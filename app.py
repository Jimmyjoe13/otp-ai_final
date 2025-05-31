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
LOG_LEVEL_STR = os.environ.get('LOG_LEVEL', 'INFO').upper()
numeric_level = getattr(logging, LOG_LEVEL_STR, None)
if not isinstance(numeric_level, int):
    logging.warning(f"Invalid LOG_LEVEL '{LOG_LEVEL_STR}'. Defaulting to INFO.")
    numeric_level = logging.INFO
logging.basicConfig(stream=sys.stdout, level=numeric_level,
                    format='%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s')
logger = logging.getLogger(__name__)
logger.info(f"Logging level set to {logging.getLevelName(logger.getEffectiveLevel())}")

from env_validator import validate_environment
if not validate_environment():
    logger.error("Environment validation failed. Please check your Railway environment variables.")

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("SESSION_SECRET")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

db.init_app(app)
jwt = JWTManager(app)

allowed_origins = [
    os.environ.get("DOMAIN", "https://opt-ai.up.railway.app"),
    "http://localhost:5000", "http://127.0.0.1:5000" 
]
CORS(app, resources={
    r"/api/*": {"origins": allowed_origins},
    r"/payment/*": {"origins": allowed_origins},
    r"/auth/*": {"origins": allowed_origins}
}, supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

with app.app_context():
    import models
    db.create_all()
    import translation
    translation.init_app(app)
    
    from routes import api_bp
    from auth import auth_bp
    from chatbot import chatbot_bp # Assurez-vous que chatbot_bp est importé
    from payment import payment_bp
    from health import health_bp
    from main_routes import main as main_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # CORRECTION : Enregistrer chatbot_bp sous /api pour que la route /chatbot devienne /api/chatbot
    app.register_blueprint(chatbot_bp, url_prefix='/api') 
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(health_bp) 
    app.register_blueprint(main_bp)
    
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

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
