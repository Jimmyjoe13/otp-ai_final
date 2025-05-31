import os
import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Analysis # Assurez-vous que Analysis est importé si utilisé
# from app import db # db n'est pas utilisé directement ici, mais pourrait l'être
from ai_integration import get_chat_response

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
chatbot_bp = Blueprint('chatbot', __name__)

# CORRIGÉ : La route est maintenant '/chatbot'. Le préfixe '/api' sera ajouté lors de l'enregistrement du blueprint.
@chatbot_bp.route('/chatbot', methods=['POST']) 
@login_required
def chatbot_route(): # Renommé la fonction pour éviter conflit avec le nom du module/blueprint
    """
    Chat API endpoint that provides AI-powered responses to SEO questions
    """
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message parameter'}), 400
        
        message = data['message']
        analysis_id = request.args.get('analysis_id') # Peut être None
        context = None
        
        if analysis_id:
            try:
                # Tenter de convertir analysis_id en entier.
                analysis_id_int = int(analysis_id)
                # Récupérer l'analyse seulement si analysis_id est un entier valide.
                analysis = Analysis.query.filter_by(id=analysis_id_int, user_id=current_user.id).first()
                if analysis:
                    context = f"Analysis of {analysis.url} (type: {analysis.analysis_type}) with overall score: {analysis.overall_score}/100. "
                    scores = []
                    if analysis.meta_score is not None: scores.append(f"Meta score: {analysis.meta_score}/100")
                    if analysis.content_score is not None: scores.append(f"Content score: {analysis.content_score}/100")
                    if analysis.technical_score is not None: scores.append(f"Technical score: {analysis.technical_score}/100")
                    if scores: context += " ".join(scores)
                    
                    details = analysis.details.limit(5).all()
                    if details:
                        context += " Key issues: "
                        issues = [f"{d.component} ({d.status})" for d in details if d.status in ['warning', 'error']]
                        if issues: context += ", ".join(issues[:3])
                else:
                    logger.warning(f"Chatbot: Analysis ID {analysis_id} not found for user {current_user.id}")
            except ValueError:
                logger.warning(f"Chatbot: Invalid Analysis ID format: {analysis_id}")
            except Exception as e:
                logger.error(f"Chatbot: Error fetching analysis context for ID {analysis_id}: {str(e)}", exc_info=True)

        response_text = get_chat_response(message, context)
        
        logger.info(f"Chat: User {current_user.id} - Q: {message[:50]}... Context provided: {bool(context)}")
        
        return jsonify({'response': response_text})
    
    except Exception as e:
        logger.error(f"Error in chatbot_route: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An error occurred processing your request',
            'response': "I'm sorry, I encountered a problem. Please try again later."
        }), 500

# La fonction format_response n'est pas utilisée par l'API JSON, elle peut être supprimée ou gardée pour un usage futur.
# def format_response(text):
#     """Format the response text with markdown-like syntax for HTML display"""
#     text = text.replace('*', '<strong>', 1)
#     text = text.replace('*', '</strong>', 1)
#     words = text.split()
#     for i, word in enumerate(words):
#         if word.startswith('http://') or word.startswith('https://'):
#             words[i] = f'<a href="{word}" target="_blank">{word}</a>'
#     return ' '.join(words)
