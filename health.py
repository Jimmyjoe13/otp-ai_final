from flask import Blueprint, jsonify
from app import db
from sqlalchemy import text

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway deployment"""
    try:
        # Test database connection
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Test DeepSeek API connection
        from ai_integration import openai
        ai_status = "connected" if openai else "not_configured"
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "ai_service": ai_status,
            "version": "1.0.0"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500
