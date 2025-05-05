import json
import os
from flask import request, session, g, redirect

def load_translations(lang_code):
    """
    Load translations for the given language code
    
    Parameters:
    - lang_code: Language code (e.g., 'fr', 'en')
    
    Returns:
    - Dictionary with translations
    """
    try:
        with open(f'translations/{lang_code}/messages.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to French if translation file is not found or invalid
        with open('translations/fr/messages.json', 'r', encoding='utf-8') as f:
            return json.load(f)

def get_locale():
    """
    Determine the best language for the current request
    
    Returns:
    - Language code (e.g., 'fr', 'en')
    """
    # 1. Use the language in the session if available
    if 'lang' in session:
        return session['lang']
    
    # 2. Try to get the preferred language from the Accept-Language header
    if request.accept_languages:
        langs = [lang.replace('-', '_') for lang in request.accept_languages.values()]
        for lang in langs:
            if lang.startswith('fr'):
                return 'fr'
            if lang.startswith('en'):
                return 'en'
    
    # 3. Default to French
    return 'fr'

def get_supported_languages():
    """
    Get list of supported languages
    
    Returns:
    - List of dictionaries with language code and name
    """
    languages = []
    for lang_dir in os.listdir('translations'):
        path = os.path.join('translations', lang_dir)
        if os.path.isdir(path):
            if lang_dir == 'fr':
                name = 'Français'
            elif lang_dir == 'en':
                name = 'English'
            else:
                name = lang_dir.upper()
            languages.append({'code': lang_dir, 'name': name})
    return languages

def init_app(app):
    """
    Initialize the translation module with the Flask app
    
    Parameters:
    - app: Flask application instance
    """
    @app.before_request
    def set_locale():
        g.locale = get_locale()
        g.translations = load_translations(g.locale)
        g.languages = get_supported_languages()
    
    @app.route('/set-language/<lang_code>')
    def set_language(lang_code):
        # Store the language preference in session
        session['lang'] = lang_code
        # Redirect back to the previous page or home
        referrer = request.referrer or '/'
        return redirect(referrer)
    
    # Add a translation function to Jinja templates
    @app.template_filter('translate')
    def translate_filter(key, default=None):
        keys = key.split('.')
        value = g.translations
        for k in keys:
            if k in value:
                value = value[k]
            else:
                return default or key
        return value
    
    # Add a shorter alias for translate
    app.jinja_env.globals['_'] = translate_filter
    
    # Add a filter for translating SEO recommendations
    @app.template_filter('translate_recommendation')
    def translate_recommendation(recommendation):
        # Title recommendations
        if recommendation == "Your title is too long. Keep it under 60 characters for better visibility in search results.":
            return translate_filter("report.your_title_is_too_long")
        elif recommendation == "Your title is too short. Make it more descriptive.":
            return "Votre titre est trop court. Rendez-le plus descriptif."
        elif recommendation == "Your title is the optimal length.":
            return "Votre titre a une longueur optimale."
        elif recommendation == "Add a descriptive title tag to your page. This is crucial for SEO.":
            return "Ajoutez une balise titre descriptive à votre page. C'est crucial pour le SEO."
            
        # Meta description recommendations
        elif recommendation == "Add a meta description to improve CTR from search results.":
            return translate_filter("report.add_meta_description")
        elif recommendation == "Your meta description is the optimal length.":
            return "Votre meta description a une longueur optimale."
        elif recommendation == "Your meta description is too short. Aim for 50-160 characters.":
            return "Votre meta description est trop courte. Visez entre 50 et 160 caractères."
        elif recommendation == "Your meta description is too long. Keep it under 160 characters.":
            return "Votre meta description est trop longue. Gardez-la sous 160 caractères."
            
        # Keywords recommendations
        elif recommendation == "While not critical for SEO, meta keywords can help with site organization.":
            return translate_filter("report.while_not_critical")
        elif recommendation == "Your keyword count is good, though search engines give less weight to the keywords meta tag now.":
            return "Votre nombre de mots-clés est bon, bien que les moteurs de recherche accordent maintenant moins d'importance à la balise meta keywords."
        elif recommendation == "Consider adding more keywords, although this tag has diminished SEO value.":
            return "Envisagez d'ajouter plus de mots-clés, bien que cette balise ait une valeur SEO diminuée."
        elif recommendation == "Too many keywords may appear as keyword stuffing.":
            return "Trop de mots-clés peuvent apparaître comme du bourrage de mots-clés."
            
        # Open Graph recommendations
        elif recommendation == "Missing Open Graph tags. Add them to improve appearance when shared on social media.":
            return "Balises Open Graph manquantes. Ajoutez-les pour améliorer l'apparence lors du partage sur les réseaux sociaux."
        elif recommendation == "Some Open Graph tags are missing. Complete them for better social media sharing.":
            return "Certaines balises Open Graph sont manquantes. Complétez-les pour un meilleur partage sur les réseaux sociaux."
        elif recommendation == "Your Open Graph tags are complete, good for social sharing.":
            return "Vos balises Open Graph sont complètes, idéales pour le partage social."
        
        # Content recommendations
        elif recommendation == "Add more content to your page.":
            return "Ajoutez plus de contenu à votre page."
        elif recommendation == "Add an H1 tag to your page.":
            return "Ajoutez une balise H1 à votre page."
        elif recommendation == "Improve your heading structure.":
            return "Améliorez la structure de vos titres."
        
        # Default fallback for non-matched recommendations
        else:
            return recommendation