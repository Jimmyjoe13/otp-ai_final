from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import Analysis
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', now=datetime.now())

@main.route('/dashboard')
@login_required
def dashboard():
    try:
        # Get user subscription info safely
        subscription_status = getattr(current_user, 'subscription_status', 'free')
        return render_template('dashboard.html', 
                             user=current_user,
                             subscription_status=subscription_status,
                             now=datetime.now())
    except Exception as e:
        # Log the error and show a user-friendly message
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Dashboard error: {str(e)}")
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
            # Get URL from form or JSON
            if request.is_json:
                data = request.get_json()
                url = data.get('url')
                analysis_type = data.get('analysis_type', 'partial')
            else:
                url = request.form.get('url')
                analysis_type = request.form.get('analysis_type', 'partial')
            
            if not url:
                if request.is_json:
                    return jsonify({'error': 'URL is required'}), 400
                flash('URL is required', 'danger')
                return redirect(url_for('main.analyze'))
            
            # Check subscription limits
            if current_user.subscription_status == 'free':
                month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                monthly_count = Analysis.query.filter(
                    Analysis.user_id == current_user.id,
                    Analysis.created_at >= month_start
                ).count()
                
                if monthly_count >= 5:
                    if request.is_json:
                        return jsonify({'error': 'Monthly analysis limit reached. Please upgrade your plan.'}), 403
                    flash('Monthly analysis limit reached. Please upgrade your plan.', 'warning')
                    return redirect(url_for('main.pricing'))
            
            # Create new analysis
            analysis = Analysis(
                url=url,
                analysis_type=analysis_type,
                user_id=current_user.id,
                meta_score=75,  # Demo scores
                content_score=80,
                technical_score=85,
                overall_score=80
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            if request.is_json:
                return jsonify({
                    'id': analysis.id,
                    'status': 'completed',
                    'url': url,
                    'redirect': url_for('main.report', analysis_id=analysis.id)
                })
            
            # Redirect to report page for form submissions
            flash(f'Analysis completed for {url}', 'success')
            return redirect(url_for('main.report'))
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Analysis error: {str(e)}")
            db.session.rollback()
            
            if request.is_json:
                return jsonify({'error': 'Analysis failed. Please try again.'}), 500
            flash('Analysis failed. Please try again.', 'danger')
            return redirect(url_for('main.analyze'))
    
    # GET request - show the form
    try:
        return render_template('analyze.html', 
                             user=current_user,
                             now=datetime.now())
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Analyze page error: {str(e)}")
        return render_template('error.html', 
                             error_message="Unable to load analysis page.",
                             now=datetime.now()), 500

@main.route('/profile')
@login_required
def profile():
    try:
        return render_template('profile.html', 
                             user=current_user,
                             now=datetime.now())
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Profile page error: {str(e)}")
        return render_template('error.html', 
                             error_message="Unable to load profile page.",
                             now=datetime.now()), 500

@main.route('/report')
@login_required
def report():
    try:
        # Get the most recent analysis
        analysis = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).first()
        
        if not analysis:
            flash('No analysis found. Please analyze a URL first.', 'warning')
            return redirect(url_for('main.analyze'))
            
        return render_template('report.html', 
                             user=current_user,
                             analysis=analysis,
                             now=datetime.now())
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Report page error: {str(e)}")
        return render_template('error.html', 
                             error_message="Unable to load report page.",
                             now=datetime.now()), 500

# Error handlers
@main.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_message="Page not found.",
                         now=datetime.now()), 404

@main.errorhandler(500)
def internal_error(error):
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Internal server error: {str(error)}")
    return render_template('error.html', 
                         error_message="Internal server error. Please try again later.",
                         now=datetime.now()), 500

@main.route('/favicon.ico')
def favicon():
    # Return empty response to avoid 404
    return '', 204
