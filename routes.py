from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import Analysis  # Assuming Analysis is the model for SEO analyses
from collections import defaultdict

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/profile/stats')
@login_required
def profile_stats():
    period = request.args.get('period', 'last_month')
    now = datetime.utcnow()

    if period == 'last_month':
        start_date = now - timedelta(days=30)
    elif period == 'last_quarter':
        start_date = now - timedelta(days=90)
    elif period == 'last_year':
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)  # default

    # Query analyses for current user in the period
    analyses = Analysis.query.filter(
        Analysis.user_id == current_user.id,
        Analysis.created_at >= start_date
    ).all()

    # Aggregate data by week
    data_by_week = defaultdict(lambda: {'analyses': 0, 'ai_recommendations': 0})

    for analysis in analyses:
        week_label = analysis.created_at.strftime('Week %U')
        data_by_week[week_label]['analyses'] += 1
        # Assuming analysis has a field ai_recommendations_count
        data_by_week[week_label]['ai_recommendations'] += getattr(analysis, 'ai_recommendations_count', 0)

    # Sort weeks
    sorted_weeks = sorted(data_by_week.keys())

    labels = sorted_weeks
    analyses_counts = [data_by_week[week]['analyses'] for week in sorted_weeks]
    ai_recommendations_counts = [data_by_week[week]['ai_recommendations'] for week in sorted_weeks]

    return jsonify({
        'labels': labels,
        'analyses': analyses_counts,
        'ai_recommendations': ai_recommendations_counts
    })
