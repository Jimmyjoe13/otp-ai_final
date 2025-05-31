#!/usr/bin/env python3
"""
Diagnostic complet pour Opt-AI SaaS
Identifie tous les problèmes potentiels du projet
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_environment_variables():
    """Vérifier les variables d'environnement critiques"""
    print("🔍 VÉRIFICATION DES VARIABLES D'ENVIRONNEMENT")
    print("=" * 50)
    
    required_vars = {
        'SESSION_SECRET': 'Clé secrète Flask',
        'DATABASE_URL': 'URL de la base de données',
        'DEEPSEEK_API_KEY': 'Clé API DeepSeek',
        'DOMAIN': 'Domaine de l\'application'
    }
    
    optional_vars = {
        'STRIPE_SECRET_KEY': 'Clé secrète Stripe',
        'STRIPE_WEBHOOK_SECRET': 'Secret webhook Stripe',
        'FLASK_DEBUG': 'Mode debug Flask'
    }
    
    issues = []
    
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if not value:
            print(f"❌ {var}: MANQUANT - {description}")
            issues.append(f"Variable d'environnement manquante: {var}")
        else:
            masked_value = f"{value[:10]}..." if len(value) > 10 else value
            print(f"✅ {var}: {masked_value}")
    
    print("\nVariables optionnelles:")
    for var, description in optional_vars.items():
        value = os.environ.get(var)
        if value:
            masked_value = f"{value[:10]}..." if len(value) > 10 else value
            print(f"✅ {var}: {masked_value}")
        else:
            print(f"⚠️  {var}: Non défini - {description}")
    
    return issues

def check_file_structure():
    """Vérifier la structure des fichiers"""
    print("\n🗂️  VÉRIFICATION DE LA STRUCTURE DES FICHIERS")
    print("=" * 50)
    
    required_files = [
        'app.py',
        'main.py',
        'models.py',
        'routes.py',
        'auth.py',
        'main_routes.py',
        'health.py',
        'ai_integration.py',
        'payment.py',
        'requirements.txt',
        'Dockerfile',
        'railway.json'
    ]
    
    required_dirs = [
        'templates',
        'static',
        'static/css',
        'static/js'
    ]
    
    required_templates = [
        'templates/base.html',
        'templates/index.html',
        'templates/login.html',
        'templates/register.html',
        'templates/dashboard.html',
        'templates/profile.html',
        'templates/analyze.html',
        'templates/report.html',
        'templates/error.html',
        'templates/pricing.html'
    ]
    
    issues = []
    
    # Vérifier les fichiers
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}: MANQUANT")
            issues.append(f"Fichier manquant: {file}")
    
    # Vérifier les dossiers
    for dir in required_dirs:
        if os.path.exists(dir):
            print(f"✅ {dir}/")
        else:
            print(f"❌ {dir}/: MANQUANT")
            issues.append(f"Dossier manquant: {dir}")
    
    # Vérifier les templates
    print("\nTemplates:")
    for template in required_templates:
        if os.path.exists(template):
            print(f"✅ {template}")
        else:
            print(f"❌ {template}: MANQUANT")
            issues.append(f"Template manquant: {template}")
    
    return issues

def check_python_imports():
    """Vérifier les imports Python"""
    print("\n🐍 VÉRIFICATION DES IMPORTS PYTHON")
    print("=" * 50)
    
    files_to_check = [
        'app.py',
        'main.py',
        'models.py',
        'routes.py',
        'auth.py',
        'main_routes.py',
        'health.py',
        'ai_integration.py',
        'payment.py'
    ]
    
    issues = []
    
    for file in files_to_check:
        if os.path.exists(file):
            try:
                spec = importlib.util.spec_from_file_location("module", file)
                module = importlib.util.module_from_spec(spec)
                # Ne pas exécuter, juste vérifier la syntaxe
                with open(file, 'r', encoding='utf-8') as f:
                    compile(f.read(), file, 'exec')
                print(f"✅ {file}: Syntaxe OK")
            except SyntaxError as e:
                print(f"❌ {file}: Erreur de syntaxe - {e}")
                issues.append(f"Erreur de syntaxe dans {file}: {e}")
            except Exception as e:
                print(f"⚠️  {file}: Avertissement - {e}")
    
    return issues

def check_database_models():
    """Vérifier les modèles de base de données"""
    print("\n🗄️  VÉRIFICATION DES MODÈLES DE BASE DE DONNÉES")
    print("=" * 50)
    
    issues = []
    
    if os.path.exists('models.py'):
        try:
            with open('models.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_models = ['User', 'Analysis', 'AnalysisDetail', 'Subscription', 'PaymentHistory']
            
            for model in required_models:
                if f"class {model}" in content:
                    print(f"✅ Modèle {model}: Trouvé")
                else:
                    print(f"❌ Modèle {model}: MANQUANT")
                    issues.append(f"Modèle manquant: {model}")
        
        except Exception as e:
            print(f"❌ Erreur lors de la lecture de models.py: {e}")
            issues.append(f"Erreur models.py: {e}")
    else:
        print("❌ models.py: MANQUANT")
        issues.append("Fichier models.py manquant")
    
    return issues

def check_api_routes():
    """Vérifier les routes API"""
    print("\n🌐 VÉRIFICATION DES ROUTES API")
    print("=" * 50)
    
    issues = []
    
    if os.path.exists('routes.py'):
        try:
            with open('routes.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_routes = [
                '/api/analyses',
                '/api/dashboard/summary',
                '/api/profile/stats',
                '/api/analyze',
                '/api/user/profile'
            ]
            
            for route in required_routes:
                if route in content:
                    print(f"✅ Route {route}: Trouvée")
                else:
                    print(f"❌ Route {route}: MANQUANTE")
                    issues.append(f"Route API manquante: {route}")
        
        except Exception as e:
            print(f"❌ Erreur lors de la lecture de routes.py: {e}")
            issues.append(f"Erreur routes.py: {e}")
    else:
        print("❌ routes.py: MANQUANT")
        issues.append("Fichier routes.py manquant")
    
    return issues

def check_static_files():
    """Vérifier les fichiers statiques"""
    print("\n📁 VÉRIFICATION DES FICHIERS STATIQUES")
    print("=" * 50)
    
    issues = []
    
    static_files = [
        'static/css/custom.css',
        'static/js/main.js',
        'static/js/dashboard.js',
        'static/js/analyzer.js',
        'static/js/profile.js',
        'static/favicon.ico'
    ]
    
    for file in static_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}: MANQUANT")
            issues.append(f"Fichier statique manquant: {file}")
    
    return issues

def generate_summary(all_issues):
    """Générer un résumé des problèmes"""
    print("\n📋 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    
    if not all_issues:
        print("🎉 AUCUN PROBLÈME CRITIQUE DÉTECTÉ!")
        print("Votre application semble prête pour le déploiement.")
        return
    
    print(f"⚠️  {len(all_issues)} PROBLÈME(S) DÉTECTÉ(S):")
    print()
    
    for i, issue in enumerate(all_issues, 1):
        print(f"{i}. {issue}")
    
    print("\n🔧 ACTIONS RECOMMANDÉES:")
    print("1. Corrigez les variables d'environnement manquantes")
    print("2. Créez les fichiers manquants")
    print("3. Vérifiez les erreurs de syntaxe")
    print("4. Testez les routes API")
    print("5. Redéployez sur Railway")

def main():
    """Fonction principale du diagnostic"""
    print("🚀 DIAGNOSTIC COMPLET - OPT-AI SAAS")
    print("=" * 50)
    print()
    
    all_issues = []
    
    # Exécuter toutes les vérifications
    all_issues.extend(check_environment_variables())
    all_issues.extend(check_file_structure())
    all_issues.extend(check_python_imports())
    all_issues.extend(check_database_models())
    all_issues.extend(check_api_routes())
    all_issues.extend(check_static_files())
    
    # Générer le résumé
    generate_summary(all_issues)
    
    return len(all_issues)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
