import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from app import db
from models import Analysis, AnalysisDetail, User
from seo_analyzer import analyze_url
from ai_integration import get_seo_recommendations
from utils import requires_subscription

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    from datetime import datetime
    return render_template('index.html', now=datetime.now())

@main_bp.route('/dashboard')
@login_required
def dashboard():
    from datetime import datetime
    # Get user's analyses
    analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).all()
    return render_template('dashboard.html', analyses=analyses, now=datetime.now())

@main_bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    from datetime import datetime
    if request.method == 'POST':
        url = request.form.get('url')
        analysis_type = request.form.get('analysis_type', 'meta')
        
        # Validate URL
        if not url:
            flash('Please enter a valid URL', 'danger')
            return redirect(url_for('main.analyze'))
        
        # Check if user has permission for this analysis type based on subscription
        if not check_analysis_permission(analysis_type):
            flash(f'Your current subscription does not allow {analysis_type} analysis. Please upgrade.', 'warning')
            return redirect(url_for('main.pricing'))
        
        try:
            # Create analysis record
            analysis = Analysis(
                url=url,
                analysis_type=analysis_type,
                user_id=current_user.id
            )
            db.session.add(analysis)
            db.session.commit()
            
            # Run analysis
            results = analyze_url(url, analysis_type)
            
            # Save analysis details
            for category, components in results['details'].items():
                for component, data in components.items():
                    detail = AnalysisDetail(
                        analysis_id=analysis.id,
                        category=category,
                        component=component,
                        status=data['status'],
                        score=data['score'],
                        description=data.get('description', ''),
                        recommendation=data.get('recommendation', '')
                    )
                    db.session.add(detail)
            
            # Update analysis scores
            analysis.meta_score = results['scores']['meta']
            analysis.content_score = results['scores'].get('content', 0)
            analysis.technical_score = results['scores'].get('technical', 0)
            analysis.overall_score = results['scores']['overall']
            db.session.commit()
            
            return redirect(url_for('main.report', analysis_id=analysis.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error analyzing URL: {str(e)}', 'danger')
            return redirect(url_for('main.analyze'))
    
    return render_template('analyze.html', now=datetime.now())

@main_bp.route('/report/<int:analysis_id>')
@login_required
def report(analysis_id):
    from datetime import datetime
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Security check - ensure analysis belongs to current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    details = analysis.details.all()
    return render_template('report.html', analysis=analysis, details=details, now=datetime.now())

@main_bp.route('/api/ai-recommendations/<int:analysis_id>')
@login_required
@requires_subscription(['premium', 'enterprise'])
def ai_recommendations(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Security check - ensure analysis belongs to current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    # Get analysis details
    details = analysis.details.all()
    details_dict = {f"{d.category}.{d.component}": {
        "status": d.status,
        "score": d.score,
        "description": d.description,
        "recommendation": d.recommendation
    } for d in details}
    
    # Get AI recommendations
    recommendations = get_seo_recommendations(analysis.url, analysis.analysis_type, details_dict)
    
    return jsonify(recommendations)

@main_bp.route('/pricing')
def pricing():
    from datetime import datetime
    return render_template('pricing.html', now=datetime.now())

@main_bp.route('/profile')
@login_required
def profile():
    from datetime import datetime
    return render_template('profile.html', now=datetime.now())

@main_bp.route('/api/analyses')
@login_required
def get_analyses():
    analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).all()
    result = []
    
    for analysis in analyses:
        result.append({
            'id': analysis.id,
            'url': analysis.url,
            'type': analysis.analysis_type,
            'date': analysis.created_at.strftime('%Y-%m-%d %H:%M'),
            'overall_score': analysis.overall_score
        })
    
    return jsonify(result)

# Helper function to check if user has permission for analysis type
def check_analysis_permission(analysis_type):
    if analysis_type == 'meta':
        return True  # All users can do meta analysis
    
    if analysis_type == 'partial' and current_user.subscription_status in ['basic', 'premium', 'enterprise']:
        return True
        
    if analysis_type == 'complete' and current_user.subscription_status in ['premium', 'enterprise']:
        return True
        
    if analysis_type == 'deep' and current_user.subscription_status == 'enterprise':
        return True
        
    return False
