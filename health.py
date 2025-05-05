from flask import Blueprint, jsonify
from app import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway deployment"""
    try:
        # Test database connection
        with db.engine.connect() as conn:
            conn.execute("SELECT 1")
        
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500