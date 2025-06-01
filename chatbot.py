import os
import logging
import requests # Ajout de l'import requests
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from utils import requires_subscription # Importation du décorateur
from models import Analysis

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
chatbot_bp = Blueprint('chatbot', __name__)

# Récupérer l'URL du webhook depuis les variables d'environnement ou utiliser une valeur par défaut
OPTY_BOT_WEBHOOK_URL = os.environ.get(
    "OPTY_BOT_WEBHOOK_URL", 
    "https://primary-production-689f.up.railway.app/webhook/2d255fa8-77d0-4ce5-9120-c7a40309c58b"
)
# Optionnel : Ajouter un header d'authentification si votre webhook le requiert
OPTY_BOT_WEBHOOK_AUTH_TOKEN = os.environ.get("OPTY_BOT_WEBHOOK_AUTH_TOKEN", None)


@chatbot_bp.route('/chatbot', methods=['POST']) 
@login_required
@requires_subscription(['premium', 'enterprise']) # Restriction d'accès
def chatbot_route():
    """
    Chat API endpoint that forwards requests to an external Opty-bot webhook.
    """
    try:
        data = request.json
        if not data or 'message' not in data:
            logger.warning("Chatbot: Missing message parameter in request.")
            return jsonify({'error': 'Missing message parameter'}), 400
        
        user_message = data['message']
        analysis_id = request.args.get('analysis_id') 
        analysis_context = None
        
        if analysis_id:
            try:
                analysis_id_int = int(analysis_id)
                analysis = Analysis.query.filter_by(id=analysis_id_int, user_id=current_user.id).first()
                if analysis:
                    analysis_context = f"Analysis of {analysis.url} (type: {analysis.analysis_type}) with overall score: {analysis.overall_score}/100. "
                    scores = []
                    if analysis.meta_score is not None: scores.append(f"Meta score: {analysis.meta_score}/100")
                    if analysis.content_score is not None: scores.append(f"Content score: {analysis.content_score}/100")
                    if analysis.technical_score is not None: scores.append(f"Technical score: {analysis.technical_score}/100")
                    if scores: analysis_context += " ".join(scores)
                    
                    details = analysis.details.limit(5).all()
                    if details:
                        analysis_context += " Key issues: "
                        issues = [f"{d.component} ({d.status})" for d in details if d.status in ['warning', 'error']]
                        if issues: analysis_context += ", ".join(issues[:3])
                else:
                    logger.warning(f"Chatbot: Analysis ID {analysis_id} not found for user {current_user.id}")
            except ValueError:
                logger.warning(f"Chatbot: Invalid Analysis ID format: {analysis_id}")
            except Exception as e:
                logger.error(f"Chatbot: Error fetching analysis context for ID {analysis_id}: {str(e)}", exc_info=True)

        # Préparer le payload pour le webhook externe
        payload = {
            "user_message": user_message,
            "user_id": current_user.id,
            "username": current_user.username,
            "email": current_user.email, # Peut être utile pour le webhook
            "analysis_context": analysis_context,
            "session_id": request.cookies.get('session') # Exemple d'envoi d'ID de session
        }
        
        headers = {"Content-Type": "application/json"}
        if OPTY_BOT_WEBHOOK_AUTH_TOKEN:
            headers["Authorization"] = f"Bearer {OPTY_BOT_WEBHOOK_AUTH_TOKEN}"

        logger.info(f"Chatbot: Forwarding message from user {current_user.id} to webhook: {OPTY_BOT_WEBHOOK_URL}")
        logger.debug(f"Chatbot: Payload for webhook: {payload}")

        try:
            # CORRIGÉ : Timeout augmenté à 45 secondes
            webhook_response = requests.post(OPTY_BOT_WEBHOOK_URL, json=payload, headers=headers, timeout=45) 
            webhook_response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)
            
            response_data = webhook_response.json()
            # CORRIGÉ : Lire la réponse depuis la clé "output"
            final_response = response_data.get("output", "Désolé, je n'ai pas pu obtenir de réponse claire du service externe (clé 'output' attendue).")
            logger.info(f"Chatbot: Received response from webhook for user {current_user.id}")
            
        except requests.exceptions.Timeout:
            logger.error(f"Chatbot: Timeout calling Opty-bot webhook at {OPTY_BOT_WEBHOOK_URL} after 45 seconds.")
            final_response = "Désolé, le service Opty-bot met trop de temps à répondre (délai de 45s dépassé)."
        except requests.exceptions.HTTPError as e:
            logger.error(f"Chatbot: HTTPError {e.response.status_code} calling Opty-bot webhook. Response: {e.response.text}")
            final_response = f"Désolé, une erreur de communication ({e.response.status_code}) avec le service Opty-bot s'est produite."
        except requests.exceptions.RequestException as e:
            logger.error(f"Chatbot: Error calling Opty-bot webhook: {str(e)}", exc_info=True)
            final_response = "Désolé, une erreur technique m'empêche de contacter Opty-bot pour le moment."
        except ValueError as e: # Erreur de parsing JSON de la réponse du webhook
            logger.error(f"Chatbot: Error parsing Opty-bot webhook JSON response: {str(e)}", exc_info=True)
            final_response = "Désolé, j'ai reçu une réponse inattendue de la part d'Opty-bot."
        
        return jsonify({'response': final_response})
    
    except Exception as e:
        logger.error(f"Error in chatbot_route (outer try-except): {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An error occurred processing your request',
            'response': "Je suis désolé, une erreur interne s'est produite. Veuillez réessayer plus tard."
        }), 500
