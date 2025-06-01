from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from utils import requires_subscription # Ajout de l'import
from models import Analysis, User, AnalysisDetail # AnalysisDetail ajouté
from collections import defaultdict
from app import db
# Importer la fonction pour obtenir les recommandations IA
from ai_integration import get_seo_recommendations, format_analysis_for_ai as format_details_for_ai_prompt

api_bp = Blueprint('api', __name__)

@api_bp.route('/analyses') 
@login_required
@requires_subscription(['enterprise'])
def get_analyses():
    """Get all analyses for current user"""
    try:
        analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).all()
        result = [{
            'id': analysis.id, 'url': analysis.url, 'analysis_type': analysis.analysis_type,
            'created_at': analysis.created_at.isoformat(), 'meta_score': analysis.meta_score or 0,
            'content_score': analysis.content_score or 0, 'technical_score': analysis.technical_score or 0,
            'overall_score': analysis.overall_score or 0
        } for analysis in analyses]
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error in /api/analyses: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analyses/<int:analysis_id>') 
@login_required
@requires_subscription(['enterprise'])
def get_analysis_details_route(analysis_id): # Renommé pour éviter conflit avec une potentielle variable 'analysis'
    """Get specific analysis details"""
    try:
        analysis_obj = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
        if not analysis_obj:
            return jsonify({'error': 'Analysis not found'}), 404
        
        details_list = [{
            'category': detail.category, 'component': detail.component, 'status': detail.status,
            'score': detail.score, 'description': detail.description, 'recommendation': detail.recommendation
        } for detail in analysis_obj.details]
        
        result = {
            'id': analysis_obj.id, 'url': analysis_obj.url, 'analysis_type': analysis_obj.analysis_type,
            'created_at': analysis_obj.created_at.isoformat(), 'meta_score': analysis_obj.meta_score or 0,
            'content_score': analysis_obj.content_score or 0, 'technical_score': analysis_obj.technical_score or 0,
            'overall_score': analysis_obj.overall_score or 0, 'details': details_list
        }
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error in /api/analyses/<id>: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# NOUVELLE ROUTE POUR LES RECOMMANDATIONS IA
@api_bp.route('/ai-recommendations/<int:analysis_id>')
@login_required
@requires_subscription(['enterprise']) # Cohérent avec API Access pour Enterprise, la logique interne est plus permissive mais sera court-circuitée si non-enterprise
def ai_recommendations_route(analysis_id):
    """Get AI-powered SEO recommendations for a specific analysis."""
    try:
        current_app.logger.info(f"Request for AI recommendations for analysis ID: {analysis_id} by user {current_user.id}")
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()

        if not analysis:
            current_app.logger.warning(f"Analysis ID {analysis_id} not found for user {current_user.id}")
            return jsonify({'error': 'Analysis not found or not authorized'}), 404

        # Vérifier si l'utilisateur a le droit aux recommandations IA (premium/enterprise et analyse complete/deep)
        # Cette logique est déjà dans le template, mais une vérification backend est plus sûre.
        if not (current_user.subscription_status in ['premium', 'enterprise'] and analysis.analysis_type in ['complete', 'deep']):
            current_app.logger.info(f"User {current_user.id} (plan: {current_user.subscription_status}) not eligible for AI recommendations for analysis type {analysis.analysis_type}.")
            return jsonify({'error': 'AI recommendations not available for this plan or analysis type.'}), 403

        # Récupérer les AnalysisDetail et les formater pour la fonction get_seo_recommendations
        # La fonction get_seo_recommendations attend un dictionnaire de détails.
        # Nous devons reconstruire ce dictionnaire à partir des objets AnalysisDetail.
        analysis_details_from_db = AnalysisDetail.query.filter_by(analysis_id=analysis.id).all()
        
        # Reformater les détails pour correspondre à ce que seo_analyzer.py produirait initialement
        # et ce que format_analysis_for_ai attend.
        # La fonction format_analysis_for_ai attend un dictionnaire où les clés sont comme "category.component"
        # et les valeurs sont des dictionnaires avec "status", "score", "description".
        
        formatted_details_for_prompt = {}
        for detail_item in analysis_details_from_db:
            key = f"{detail_item.category}.{detail_item.component}"
            formatted_details_for_prompt[key] = {
                "status": detail_item.status,
                "score": detail_item.score,
                "description": detail_item.description,
                # La valeur originale n'est pas stockée dans AnalysisDetail, donc on ne peut pas la passer ici.
                # Ce n'est pas grave si format_analysis_for_ai gère l'absence de 'value'.
            }
        
        current_app.logger.debug(f"Formatted details for AI prompt: {formatted_details_for_prompt}")

        # Obtenir la langue de l'utilisateur (si vous avez un système de i18n pour les préférences utilisateur)
        # Pour l'instant, on peut utiliser la langue de la requête ou une valeur par défaut.
        lang_code = request.accept_languages.best_match(['fr', 'en']) or 'en'
        
        recommendations = get_seo_recommendations(
            url=analysis.url,
            analysis_type=analysis.analysis_type,
            analysis_details=formatted_details_for_prompt, # Utiliser les détails formatés
            lang_code=lang_code
        )
        
        current_app.logger.info(f"Successfully generated AI recommendations for analysis ID: {analysis_id}")
        return jsonify(recommendations)

    except Exception as e:
        current_app.logger.error(f"Error in /ai-recommendations/{analysis_id}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to generate AI recommendations', 'details': str(e)}), 500


@api_bp.route('/profile/stats') 
@login_required
@requires_subscription(['enterprise'])
def profile_stats():
    # ... (code existant inchangé)
    try:
        period = request.args.get('period', 'last_month')
        now = datetime.utcnow()
        if period == 'last_month': start_date = now - timedelta(days=30)
        elif period == 'last_quarter': start_date = now - timedelta(days=90)
        elif period == 'last_year': start_date = now - timedelta(days=365)
        else: start_date = now - timedelta(days=30)
        analyses = Analysis.query.filter(Analysis.user_id == current_user.id, Analysis.created_at >= start_date).all()
        data_by_week = defaultdict(lambda: {'analyses': 0, 'avg_score': 0, 'total_score': 0})
        for analysis_item in analyses: # Renommé pour éviter conflit
            week_label = analysis_item.created_at.strftime('Week %U')
            data_by_week[week_label]['analyses'] += 1
            score = analysis_item.overall_score or 0
            data_by_week[week_label]['total_score'] += score
        for week_data in data_by_week.values():
            if week_data['analyses'] > 0: week_data['avg_score'] = week_data['total_score'] / week_data['analyses']
        sorted_weeks = sorted(data_by_week.keys())
        return jsonify({'labels': sorted_weeks, 'analyses': [data_by_week[week]['analyses'] for week in sorted_weeks], 'scores': [data_by_week[week]['avg_score'] for week in sorted_weeks]})
    except Exception as e:
        current_app.logger.error(f"Error in /api/profile/stats: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dashboard/summary') 
@login_required
@requires_subscription(['enterprise'])
def dashboard_summary():
    # ... (code existant inchangé)
    try:
        total_analyses = Analysis.query.filter_by(user_id=current_user.id).count()
        analyses_items = Analysis.query.filter_by(user_id=current_user.id).all() # Renommé
        avg_score = sum(a.overall_score or 0 for a in analyses_items) / len(analyses_items) if analyses_items else 0
        recent_analyses_items = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).limit(5).all() # Renommé
        recent_data = [{'id': item.id, 'url': item.url, 'analysis_type': item.analysis_type, 'created_at': item.created_at.isoformat(), 'overall_score': item.overall_score or 0} for item in recent_analyses_items]
        return jsonify({'total_analyses': total_analyses, 'avg_score': round(avg_score, 1), 'recent_analyses': recent_data, 'subscription_status': current_user.subscription_status})
    except Exception as e:
        current_app.logger.error(f"Error in /api/dashboard/summary: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analyze', methods=['POST']) 
@login_required
@requires_subscription(['enterprise'])
def analyze_url_route(): # Renommé
    # ... (code existant inchangé)
    try:
        data = request.get_json()
        url = data.get('url')
        analysis_type = data.get('analysis_type', 'partial')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Monthly analysis limits (consistent with main_routes.py)
        # Note: This route is already protected by @requires_subscription(['enterprise'])
        # So, this internal limit check for 'free' or 'basic' will likely not be hit
        # unless the decorator logic changes or fails.
        # However, for consistency in the function's structure:
        user_plan = getattr(current_user, 'subscription_status', 'free')

        ANALYSIS_LIMITS = {
            'free': 5,
            'basic': 25,
        }

        if user_plan in ANALYSIS_LIMITS:
            limit = ANALYSIS_LIMITS[user_plan]
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_count = Analysis.query.filter(
                Analysis.user_id == current_user.id,
                Analysis.created_at >= month_start
            ).count()
            
            if monthly_count >= limit:
                return jsonify({'error': f'Monthly analysis limit of {limit} reached for your {user_plan} plan. Please upgrade your plan or wait until next month.'}), 403
        
        # Check analysis type permissions based on plan
        # Note: This route is already protected by @requires_subscription(['enterprise'])
        # So, user_plan here should ideally be 'enterprise' if decorator works.
        # This internal check adds another layer or would be primary if decorator was different.
        ANALYSIS_TYPE_PERMISSIONS = {
            'meta': ['free', 'basic', 'premium', 'enterprise'],
            'partial': ['basic', 'premium', 'enterprise'],
            'complete': ['premium', 'enterprise'],
            'deep': ['enterprise'] 
        }

        allowed_plans_for_requested_type = ANALYSIS_TYPE_PERMISSIONS.get(analysis_type)

        if allowed_plans_for_requested_type is None:
            return jsonify({'error': f"Invalid analysis type requested: {analysis_type}"}), 400

        # user_plan was defined above for monthly limits.
        # If this route is strictly 'enterprise' due to decorator, this check might seem redundant
        # for 'enterprise' users but is good practice.
        if user_plan not in allowed_plans_for_requested_type:
            return jsonify({'error': f"The requested analysis type '{analysis_type}' is not available for your current plan ('{user_plan}'). Please upgrade your plan."}), 403

        analysis_obj = Analysis(url=url, analysis_type=analysis_type, user_id=current_user.id)
        db.session.add(analysis_obj)
        db.session.commit()
        return jsonify({'id': analysis_obj.id, 'status': 'created', 'message': 'Analysis started...'})
    except Exception as e:
        db.session.rollback(); current_app.logger.error(f"Error in /api/analyze: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@api_bp.route('/user/profile') 
@login_required
@requires_subscription(['enterprise'])
def user_profile_route(): # Renommé
    # ... (code existant inchangé)
    try:
        return jsonify({'id': current_user.id, 'username': current_user.username, 'email': current_user.email, 'subscription_status': current_user.subscription_status, 'created_at': current_user.created_at.isoformat(), 'subscription_ends_at': current_user.subscription_ends_at.isoformat() if current_user.subscription_ends_at else None})
    except Exception as e:
        current_app.logger.error(f"Error in /api/user/profile: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
