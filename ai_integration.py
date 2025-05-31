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
    logger.error(f"Error initializing DeepSeek client: {str(e)}")

def get_seo_recommendations(url, analysis_type, analysis_details, lang_code='en'):
    """
    Get AI-powered SEO recommendations based on analysis results
    
    Parameters:
    - url: The URL that was analyzed
    - analysis_type: Type of analysis performed
    - analysis_details: Dictionary of analysis details
    - lang_code: Language code (e.g., 'fr', 'en') for the response
    
    Returns:
    - Dictionary with AI recommendations
    """
    # Check if DeepSeek client is available
    if not openai:
        logger.warning("DeepSeek client not initialized. Returning fallback recommendations.")
        if lang_code == 'fr':
            return {
                "summary": "Les recommandations propulsées par l'IA nécessitent une clé API DeepSeek.",
                "priorities": ["Corriger les erreurs techniques", "Améliorer les balises méta", "Améliorer le contenu"],
                "recommendations": [
                    {
                        "title": "Clé API requise",
                        "description": "Pour accéder aux recommandations propulsées par l'IA, veuillez fournir une clé API DeepSeek valide dans les paramètres de votre compte.",
                        "steps": ["Accédez aux paramètres de votre profil", "Ajoutez votre clé API DeepSeek", "Actualisez cette page pour voir les recommandations IA"]
                    }
                ],
                "insights": "Le rapport d'analyse détaillé ci-dessus fournit des informations précieuses sur les performances SEO de votre site."
            }
        else:
            return {
                "summary": "AI-powered recommendations require a DeepSeek API key.",
                "priorities": ["Fix technical errors", "Improve meta tags", "Enhance content"],
                "recommendations": [
                    {
                        "title": "API Key Required",
                        "description": "To access AI-powered recommendations, please provide a valid DeepSeek API key in your account settings.",
                        "steps": ["Go to your profile settings", "Add your DeepSeek API key", "Refresh this page to see AI recommendations"]
                    }
                ],
                "insights": "The detailed analysis report above provides valuable information about your site's SEO performance."
            }
    
    try:
        # Convert analysis details to a formatted string for the AI
        analysis_text = format_analysis_for_ai(url, analysis_type, analysis_details)
        
        # Prepare prompt with language instruction
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
        
        # Call DeepSeek API
        response = openai.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"You are an expert SEO analyst providing clear, actionable advice {language_instruction}."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        # Parse and return the response
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {str(e)}")
        if lang_code == 'fr':
            return {
                "summary": "Impossible de générer des recommandations IA pour le moment.",
                "priorities": ["Corriger les erreurs techniques", "Améliorer les balises méta", "Améliorer le contenu"],
                "recommendations": [
                    {
                        "title": "Erreur Système",
                        "description": "Nous avons rencontré un problème lors de la génération des recommandations IA. Veuillez réessayer plus tard.",
                        "steps": ["Vérifiez votre connexion internet", "Actualisez la page", "Contactez le support si le problème persiste"]
                    }
                ],
                "insights": "Notre système d'IA est temporairement indisponible. Veuillez consulter le rapport d'analyse détaillé pour des recommandations."
            }
        else:
            return {
                "summary": "Unable to generate AI recommendations at this time.",
                "priorities": ["Fix technical errors", "Improve meta tags", "Enhance content"],
                "recommendations": [
                    {
                        "title": "System Error",
                        "description": "We encountered an issue generating AI recommendations. Please try again later.",
                        "steps": ["Check your internet connection", "Refresh the page", "Contact support if the issue persists"]
                    }
                ],
                "insights": "Our AI system is temporarily unavailable. Please check the detailed analysis report for recommendations."
            }

def get_chat_response(user_query, context=None):
    """
    Get a response from the AI chatbot
    
    Parameters:
    - user_query: The user's question
    - context: Optional context from previous analysis
    
    Returns:
    - String with AI response
    """
    # Check if DeepSeek client is available
    if not openai:
        logger.warning("DeepSeek client not initialized. Returning fallback chat response.")
        return "I'm sorry, but I need a DeepSeek API key to provide intelligent responses. Please add your API key in the settings to enable AI features."
    
    try:
        # Prepare system message with context if available
        system_message = "You are Opty-bot, an AI assistant specialized in SEO. Provide helpful, concise advice about SEO best practices."
        if context:
            system_message += f"\n\nContext about the user's website: {context}"
        
        # Call DeepSeek API
        response = openai.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_query}
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error getting chat response: {str(e)}")
        return "I'm sorry, I'm having trouble generating a response right now. Please try again later."

def analyze_content_semantics(text, keywords=None):
    """
    Analyze content semantics for advanced SEO insights
    
    Parameters:
    - text: The content to analyze
    - keywords: Optional target keywords
    
    Returns:
    - Dictionary with semantic analysis results
    """
    # Check if DeepSeek client is available
    if not openai:
        logger.warning("DeepSeek client not initialized. Returning fallback semantic analysis.")
        return {
            "relevance_score": 50,
            "depth_assessment": "AI-powered semantic analysis requires a DeepSeek API key.",
            "keyword_suggestions": ["seo", "content", "optimization"],
            "structure_recommendations": [
                "Add your DeepSeek API key to enable detailed semantic analysis",
                "Ensure proper heading structure",
                "Add more detailed content"
            ]
        }
    
    try:
        # Prepare prompt
        prompt = f"""
        Analyze the following content semantically for SEO purposes:
        
        {text[:1000]}... (text truncated for brevity)
        
        """
        
        if keywords:
            prompt += f"\nTarget keywords: {', '.join(keywords)}\n"
            
        prompt += """
        Provide a semantic analysis with:
        1. Topic relevance score (0-100)
        2. Content depth assessment
        3. Semantic keyword suggestions
        4. Content structure recommendations
        
        Format your response as JSON with these fields:
        - relevance_score: number
        - depth_assessment: string
        - keyword_suggestions: array of strings
        - structure_recommendations: array of strings
        """
        
        # Call DeepSeek API
        response = openai.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert in semantic SEO analysis."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=800
        )
        
        # Parse and return the response
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing content semantics: {str(e)}")
        return {
            "relevance_score": 50,
            "depth_assessment": "Unable to analyze content depth at this time.",
            "keyword_suggestions": ["seo", "content", "optimization"],
            "structure_recommendations": ["Ensure proper heading structure", "Add more detailed content"]
        }

def format_analysis_for_ai(url, analysis_type, analysis_details):
    """Format analysis details as text for AI input"""
    sections = []
    
    sections.append(f"URL: {url}")
    sections.append(f"Analysis Type: {analysis_type}")
    sections.append("\nFINDINGS:")
    
    # Group by category
    for category in ['meta', 'content', 'technical']:
        if any(key.startswith(f"{category}.") for key in analysis_details.keys()):
            sections.append(f"\n== {category.upper()} ANALYSIS ==")
            
            for key, data in sorted(analysis_details.items()):
                if key.startswith(f"{category}."):
                    component = key.split('.')[1]
                    sections.append(f"- {component}: {data['status'].upper()} (Score: {data['score']}/100)")
                    if 'description' in data:
                        sections.append(f"  {data['description']}")
    
    return "\n".join(sections)
