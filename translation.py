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
        if recommendation == "Your title is too long. Keep it under 60 characters for better visibility in search results.":
            return translate_filter("report.your_title_is_too_long")
        elif recommendation == "Add a meta description to improve CTR in search results.":
            return translate_filter("report.add_meta_description")
        elif recommendation == "Implement Open Graph tags":
            return translate_filter("report.implement_open_graph")
        elif recommendation == "While not critical for SEO, meta keywords can help with site organization.":
            return translate_filter("report.while_not_critical")
        else:
            return recommendation