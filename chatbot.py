import os
import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Analysis
from app import db
from ai_integration import get_chat_response

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot():
    """
    Chat API endpoint that provides AI-powered responses to SEO questions
    """
    try:
        # Get request data
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message parameter'}), 400
        
        message = data['message']
        
        # Check for context
        analysis_id = request.args.get('analysis_id')
        context = None
        
        # If there's an analysis_id, fetch the analysis data to provide context
        if analysis_id:
            analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
            if analysis:
                # Create context from analysis
                context = f"Analysis of {analysis.url} (type: {analysis.analysis_type}) with overall score: {analysis.overall_score}/100. "
                
                # Add meta/content/technical scores if available
                scores = []
                if analysis.meta_score is not None:
                    scores.append(f"Meta score: {analysis.meta_score}/100")
                if analysis.content_score is not None:
                    scores.append(f"Content score: {analysis.content_score}/100")
                if analysis.technical_score is not None:
                    scores.append(f"Technical score: {analysis.technical_score}/100")
                
                if scores:
                    context += " ".join(scores)
                
                # Add some details if available
                details = analysis.details.limit(5).all()
                if details:
                    context += " Key issues: "
                    issues = [f"{d.component} ({d.status})" for d in details if d.status in ['warning', 'error']]
                    if issues:
                        context += ", ".join(issues[:3])
        
        # Get response from AI integration
        response = get_chat_response(message, context)
        
        # Log the interaction for analysis
        logger.info(f"Chat: User {current_user.id} - Q: {message[:50]}...")
        
        return jsonify({
            'response': response
        })
    
    except Exception as e:
        logger.error(f"Error in chatbot: {str(e)}")
        return jsonify({
            'error': 'An error occurred processing your request',
            'response': "I'm sorry, I encountered a problem processing your request. Please try again later."
        }), 500

# Helper functions for the chatbot
def format_response(text):
    """Format the response text with markdown-like syntax for HTML display"""
    # Replace *text* with <strong>text</strong>
    text = text.replace('*', '<strong>', 1)
    text = text.replace('*', '</strong>', 1)
    
    # Replace URLs with links
    words = text.split()
    for i, word in enumerate(words):
        if word.startswith('http://') or word.startswith('https://'):
            words[i] = f'<a href="{word}" target="_blank">{word}</a>'
    
    return ' '.join(words)
