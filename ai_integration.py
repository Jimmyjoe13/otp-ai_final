import os
import json
import logging
from openai import OpenAI

# Migration to DeepSeek AI - using deepseek-chat model
# DeepSeek provides cost-effective AI with good performance

logger = logging.getLogger(__name__)

# Initialize DeepSeek client (compatible with OpenAI API)
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
openai = None
try:
    if DEEPSEEK_API_KEY:
        openai = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        logger.info("DeepSeek client initialized successfully")
    else:
        logger.warning("DEEPSEEK_API_KEY not set. AI features will be disabled.")
except Exception as e:
    logger.error(f"Error initializing DeepSeek client: {str(e)}", exc_info=True)

def get_seo_recommendations(url, analysis_type, analysis_details, lang_code='en'):
    """
    Get AI-powered SEO recommendations based on analysis results
    """
    if not openai:
        logger.warning("DeepSeek client not initialized. Returning fallback recommendations.")
        # ... (code de fallback inchangé)
        if lang_code == 'fr':
            return {
                "summary": "Les recommandations propulsées par l'IA nécessitent une clé API DeepSeek.",
                "priorities": ["Corriger les erreurs techniques", "Améliorer les balises méta", "Améliorer le contenu"],
                "recommendations": [{"title": "Clé API requise", "description": "...", "steps": ["..."]}]
            }
        else:
            return {
                "summary": "AI-powered recommendations require a DeepSeek API key.",
                "priorities": ["Fix technical errors", "Improve meta tags", "Enhance content"],
                "recommendations": [{"title": "API Key Required", "description": "...", "steps": ["..."]}]
            }

    try:
        logger.debug(f"get_seo_recommendations called for URL: {url}, Type: {analysis_type}")
        # Utiliser json.dumps pour logger les dictionnaires de manière lisible
        logger.debug(f"Raw analysis_details: {json.dumps(analysis_details, indent=2, ensure_ascii=False)}")
        
        analysis_text = format_analysis_for_ai(url, analysis_type, analysis_details)
        logger.debug(f"Formatted analysis_text for AI: \n{analysis_text}")
        
        language_instruction = "in French" if lang_code == 'fr' else "in English"
        prompt = f"""
        You are an expert SEO consultant analyzing the following website: {url}
        Here is the SEO analysis data:
        {analysis_text}
        Based on this analysis, please provide your response {language_instruction}:
        1. A summary of the main SEO issues identified
        2. The top 3-5 most important recommendations to improve the site's SEO
        3. Specific actionable steps for each recommendation
        4. Additional insights based on current SEO best practices
        Structure your response as JSON with these fields:
        - summary: A concise summary of findings
        - priorities: Array of top issues to address
        - recommendations: Array of objects with 'title', 'description', and 'steps' (array of specific steps)
        - insights: Additional expert insights
        """
        
        logger.info(f"Sending request to DeepSeek API for URL: {url}")
        response = openai.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"You are an expert SEO analyst providing clear, actionable advice {language_instruction}."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1500 # Augmenté pour des recommandations plus complètes
        )
        
        ai_response_content = response.choices[0].message.content
        logger.debug(f"Raw AI response content for {url}: {ai_response_content}")
        result = json.loads(ai_response_content)
        logger.info(f"Successfully received and parsed AI recommendations for URL: {url}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting AI recommendations for URL {url}: {str(e)}", exc_info=True)
        # ... (code de fallback en cas d'erreur inchangé)
        if lang_code == 'fr':
            return {"summary": "Impossible de générer des recommandations IA pour le moment.", "recommendations": [{"title": "Erreur Système", "description": "..."}]}
        else:
            return {"summary": "Unable to generate AI recommendations at this time.", "recommendations": [{"title": "System Error", "description": "..."}]}


def get_chat_response(user_query, context=None):
    if not openai:
        # ... (inchangé)
        return "I'm sorry, but I need a DeepSeek API key..."
    try:
        # ... (inchangé)
        response = openai.chat.completions.create(
            model="deepseek-chat",
            # ... (messages inchangés)
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting chat response: {str(e)}", exc_info=True)
        return "I'm sorry, I'm having trouble..."

def analyze_content_semantics(text, keywords=None):
    if not openai:
        # ... (inchangé)
        return {"relevance_score": 50, "depth_assessment": "AI-powered semantic analysis requires a DeepSeek API key."}
    try:
        # ... (inchangé)
        response = openai.chat.completions.create(
            model="deepseek-chat",
            # ... (messages inchangés)
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Error analyzing content semantics: {str(e)}", exc_info=True)
        return {"relevance_score": 50, "depth_assessment": "Unable to analyze content depth..."}

def format_analysis_for_ai(url, analysis_type, analysis_details):
    sections = []
    sections.append(f"URL: {url}")
    sections.append(f"Analysis Type: {analysis_type}")
    
    if not analysis_details: # Gérer le cas où analysis_details est None ou vide
        sections.append("\nNO ANALYSIS DETAILS PROVIDED.")
        return "\n".join(sections)

    sections.append("\nFINDINGS:")
    
    for category in ['meta', 'content', 'technical']:
        # Filtrer les détails pour la catégorie actuelle
        category_details = {k: v for k, v in analysis_details.items() if k.startswith(f"{category}.")}
        
        if category_details:
            sections.append(f"\n== {category.upper()} ANALYSIS ==")
            for key, data in sorted(category_details.items()):
                # S'assurer que data est un dictionnaire et a les clés attendues
                if isinstance(data, dict) and 'status' in data and 'score' in data:
                    component = key.split('.')[-1] # Prendre la dernière partie pour le nom du composant
                    sections.append(f"- {component.replace('_', ' ').capitalize()}: {data['status'].upper()} (Score: {data.get('score', 'N/A')}/100)")
                    if 'description' in data and data['description']:
                        sections.append(f"  Description: {data['description']}")
                    if 'value' in data and data['value']: # Afficher la valeur si présente
                        sections.append(f"  Current Value: {data['value']}")
                else:
                    logger.warning(f"Skipping malformed detail item: {key} -> {data}")
        else:
            sections.append(f"\n== NO {category.upper()} ANALYSIS DETAILS PROVIDED ==")
            
    return "\n".join(sections)
