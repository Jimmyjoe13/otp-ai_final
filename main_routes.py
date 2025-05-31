from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime

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

@main.route('/analyze')
@login_required
def analyze():
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
        return render_template('report.html', 
                             user=current_user,
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
