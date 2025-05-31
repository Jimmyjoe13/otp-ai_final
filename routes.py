from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import Analysis, User
from collections import defaultdict
from app import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/analyses') # Corrigé: suppression de /api
@login_required
def get_analyses():
    """Get all analyses for current user"""
    try:
        analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).all()
        
        result = []
        for analysis in analyses:
            result.append({
                'id': analysis.id,
                'url': analysis.url,
                'analysis_type': analysis.analysis_type,
                'created_at': analysis.created_at.isoformat(),
                'meta_score': analysis.meta_score or 0,
                'content_score': analysis.content_score or 0,
                'technical_score': analysis.technical_score or 0,
                'overall_score': analysis.overall_score or 0
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analyses/<int:analysis_id>') # Corrigé
@login_required
def get_analysis(analysis_id):
    """Get specific analysis details"""
    try:
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        details = []
        for detail in analysis.details:
            details.append({
                'category': detail.category,
                'component': detail.component,
                'status': detail.status,
                'score': detail.score,
                'description': detail.description,
                'recommendation': detail.recommendation
            })
        
        result = {
            'id': analysis.id,
            'url': analysis.url,
            'analysis_type': analysis.analysis_type,
            'created_at': analysis.created_at.isoformat(),
            'meta_score': analysis.meta_score or 0,
            'content_score': analysis.content_score or 0,
            'technical_score': analysis.technical_score or 0,
            'overall_score': analysis.overall_score or 0,
            'details': details
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/profile/stats') # Corrigé
@login_required
def profile_stats():
    """Get user profile statistics"""
    try:
        period = request.args.get('period', 'last_month')
        now = datetime.utcnow()

        if period == 'last_month':
            start_date = now - timedelta(days=30)
        elif period == 'last_quarter':
            start_date = now - timedelta(days=90)
        elif period == 'last_year':
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)

        analyses = Analysis.query.filter(
            Analysis.user_id == current_user.id,
            Analysis.created_at >= start_date
        ).all()

        data_by_week = defaultdict(lambda: {'analyses': 0, 'avg_score': 0, 'total_score': 0})
        for analysis in analyses:
            week_label = analysis.created_at.strftime('Week %U')
            data_by_week[week_label]['analyses'] += 1
            score = analysis.overall_score or 0
            data_by_week[week_label]['total_score'] += score

        for week_data in data_by_week.values():
            if week_data['analyses'] > 0:
                week_data['avg_score'] = week_data['total_score'] / week_data['analyses']

        sorted_weeks = sorted(data_by_week.keys())
        labels = sorted_weeks
        analyses_counts = [data_by_week[week]['analyses'] for week in sorted_weeks]
        avg_scores = [data_by_week[week]['avg_score'] for week in sorted_weeks]

        return jsonify({
            'labels': labels,
            'analyses': analyses_counts,
            'scores': avg_scores
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dashboard/summary') # Corrigé
@login_required
def dashboard_summary():
    """Get dashboard summary data"""
    try:
        total_analyses = Analysis.query.filter_by(user_id=current_user.id).count()
        analyses = Analysis.query.filter_by(user_id=current_user.id).all()
        avg_score = sum(a.overall_score or 0 for a in analyses) / len(analyses) if analyses else 0
        
        recent_analyses = Analysis.query.filter_by(user_id=current_user.id)\
                                       .order_by(Analysis.created_at.desc())\
                                       .limit(5).all()
        recent_data = [{
            'id': analysis.id, 'url': analysis.url, 'analysis_type': analysis.analysis_type,
            'created_at': analysis.created_at.isoformat(), 'overall_score': analysis.overall_score or 0
        } for analysis in recent_analyses]
        
        return jsonify({
            'total_analyses': total_analyses,
            'avg_score': round(avg_score, 1),
            'recent_analyses': recent_data,
            'subscription_status': current_user.subscription_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analyze', methods=['POST']) # Corrigé
@login_required
def analyze_url():
    """Analyze a URL"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        analysis_type = data.get('analysis_type', 'partial')
        
        if current_user.subscription_status == 'free':
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_count = Analysis.query.filter(
                Analysis.user_id == current_user.id,
                Analysis.created_at >= month_start
            ).count()
            if monthly_count >= 5:
                return jsonify({'error': 'Monthly analysis limit reached. Please upgrade your plan.'}), 403
        
        analysis = Analysis(url=url, analysis_type=analysis_type, user_id=current_user.id)
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify({
            'id': analysis.id, 'status': 'created',
            'message': 'Analysis started. This feature will be implemented with the SEO analyzer.'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/user/profile') # Corrigé
@login_required
def user_profile():
    """Get current user profile"""
    try:
        return jsonify({
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'subscription_status': current_user.subscription_status,
            'created_at': current_user.created_at.isoformat(),
            'subscription_ends_at': current_user.subscription_ends_at.isoformat() if current_user.subscription_ends_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
