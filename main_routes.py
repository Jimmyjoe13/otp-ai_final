from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import Analysis, AnalysisDetail # AnalysisDetail ajouté
from app import db
# Importer le véritable analyseur SEO
from seo_analyzer import analyze_url as perform_seo_analysis
import logging # Importer logging

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__) # Configurer un logger pour ce blueprint

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
            
            # Appeler le véritable analyseur SEO
            try:
                logger.info(f"Starting SEO analysis for {url} (type: {analysis_type}) by user {current_user.id}")
                seo_results = perform_seo_analysis(url, analysis_type)
                logger.info(f"SEO analysis completed for {url}. Overall score: {seo_results['scores'].get('overall')}")
            except Exception as analysis_err:
                logger.error(f"seo_analyzer.analyze_url failed for {url}: {str(analysis_err)}", exc_info=True)
                flash(f"Error during SEO analysis for {url}. Details: {str(analysis_err)}", 'danger')
                return redirect(url_for('main.analyze'))

            analysis = Analysis(
                url=url, 
                analysis_type=analysis_type, 
                user_id=current_user.id,
                meta_score=seo_results['scores'].get('meta', 0),
                content_score=seo_results['scores'].get('content', 0),
                technical_score=seo_results['scores'].get('technical', 0),
                overall_score=seo_results['scores'].get('overall', 0)
            )
            db.session.add(analysis)
            db.session.flush() # Pour obtenir l'ID de l'analyse avant le commit complet

            # Sauvegarder les AnalysisDetail
            if 'details' in seo_results:
                for category, items in seo_results['details'].items():
                    if isinstance(items, dict): # S'assurer que items est un dictionnaire
                        for component, item_details in items.items():
                            if isinstance(item_details, dict): # S'assurer que item_details est un dictionnaire
                                detail = AnalysisDetail(
                                    analysis_id=analysis.id,
                                    category=category,
                                    component=component,
                                    status=item_details.get('status', 'info'),
                                    score=item_details.get('score', 0),
                                    description=item_details.get('description', ''),
                                    recommendation=item_details.get('recommendation', '')
                                )
                                db.session.add(detail)
                            else:
                                logger.warning(f"Skipping malformed item_details for component {component} in category {category}: {item_details}")
                    else:
                        logger.warning(f"Skipping malformed items for category {category}: {items}")
            
            db.session.commit()
            logger.info(f"Analysis and details for {url} (ID: {analysis.id}) saved to database.")
            
            flash(f'Analysis completed for {url}', 'success')
            return redirect(url_for('main.report', analysis_id=analysis.id))
            
        except Exception as e:
            logger.error(f"General error in /analyze POST: {str(e)}", exc_info=True)
            db.session.rollback()
            flash('An unexpected error occurred during analysis. Please try again.', 'danger')
            return redirect(url_for('main.analyze'))
    
    return render_template('analyze.html', user=current_user, now=datetime.now())

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user, now=datetime.now())

@main.route('/report') 
@main.route('/report/<int:analysis_id>') 
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

        analysis_details = analysis.details.all() if analysis else []
        
        return render_template('report.html', 
                             user=current_user,
                             analysis=analysis,
                             details=analysis_details, 
                             now=datetime.now())
    except Exception as e:
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
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return render_template('error.html', error_message="Internal server error. Please try again later.", now=datetime.now()), 500

@main.route('/favicon.ico')
def favicon():
    return '', 204
