from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import Analysis # Assurez-vous que Analysis est importé
from app import db # Assurez-vous que db est importé

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', now=datetime.now())

@main.route('/dashboard')
@login_required
def dashboard():
    try:
        subscription_status = getattr(current_user, 'subscription_status', 'free')
        return render_template('dashboard.html', 
                             user=current_user,
                             subscription_status=subscription_status,
                             now=datetime.now())
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        return render_template('error.html', 
                             error_message="Unable to load dashboard. Please try again later.",
                             now=datetime.now()), 500

@main.route('/pricing')
def pricing():
    return render_template('pricing.html', now=datetime.now())

@main.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    if request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
                url = data.get('url')
                analysis_type = data.get('analysis_type', 'partial')
            else:
                url = request.form.get('url')
                analysis_type = request.form.get('analysis_type', 'partial')
            
            if not url:
                flash('URL is required', 'danger')
                return redirect(url_for('main.analyze'))
            
            if current_user.subscription_status == 'free':
                month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                monthly_count = Analysis.query.filter(
                    Analysis.user_id == current_user.id,
                    Analysis.created_at >= month_start
                ).count()
                if monthly_count >= 5:
                    flash('Monthly analysis limit reached. Please upgrade your plan.', 'warning')
                    return redirect(url_for('main.pricing'))
            
            analysis = Analysis(
                url=url, analysis_type=analysis_type, user_id=current_user.id,
                meta_score=75, content_score=80, technical_score=85, overall_score=80 # Demo scores
            )
            db.session.add(analysis)
            db.session.commit()
            
            flash(f'Analysis completed for {url}', 'success')
            # CORRIGÉ : Rediriger vers la page de rapport avec l'ID de l'analyse
            return redirect(url_for('main.report', analysis_id=analysis.id))
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Analysis error: {str(e)}", exc_info=True)
            db.session.rollback()
            flash('Analysis failed. Please try again.', 'danger')
            return redirect(url_for('main.analyze'))
    
    return render_template('analyze.html', user=current_user, now=datetime.now())

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user, now=datetime.now())

@main.route('/report') # Route par défaut pour la dernière analyse (optionnel)
@main.route('/report/<int:analysis_id>') # Route pour une analyse spécifique
@login_required
def report(analysis_id=None):
    try:
        if analysis_id:
            analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
            if not analysis:
                flash('Analysis not found or you do not have permission to view it.', 'danger')
                return redirect(url_for('main.dashboard'))
        else:
            analysis = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).first()
            if not analysis:
                flash('No analysis found. Please analyze a URL first.', 'warning')
                return redirect(url_for('main.analyze'))

        # Charger les détails de l'analyse (AnalysisDetail)
        analysis_details = analysis.details.all() if analysis else []
        
        return render_template('report.html', 
                             user=current_user,
                             analysis=analysis,
                             details=analysis_details, # Passer les détails au template
                             now=datetime.now())
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Report page error: {str(e)}", exc_info=True)
        return render_template('error.html', 
                             error_message="Unable to load report page.",
                             now=datetime.now()), 500

# Error handlers
@main.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_message="Page not found.", now=datetime.now()), 404

@main.errorhandler(500)
def internal_error(error):
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return render_template('error.html', error_message="Internal server error. Please try again later.", now=datetime.now()), 500

@main.route('/favicon.ico')
def favicon():
    return '', 204
