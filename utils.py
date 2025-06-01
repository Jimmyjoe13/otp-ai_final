import functools
from flask import flash, redirect, url_for, jsonify, request # Ajout de jsonify et request
from flask_login import current_user

def requires_subscription(plans, is_api_route=False): # Ajout du paramètre is_api_route
    """
    Decorator to check if user has required subscription level.
    
    Parameters:
    - plans: List of allowed subscription plans.
    - is_api_route: Boolean, if True, returns JSON error on failure, else flashes and redirects.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            # Authentication check (applies to both API and web routes)
            if not current_user.is_authenticated:
                if is_api_route:
                    return jsonify({'error': 'Authentication required', 'message': 'Please log in to access this feature.'}), 401
                else:
                    flash('Please log in to access this feature.', 'warning')
                    return redirect(url_for('auth.login'))
                
            # Admin access (applies to both)
            if hasattr(current_user, 'is_admin') and current_user.is_admin:
                return f(*args, **kwargs)
            
            user_sub = getattr(current_user, 'subscription', None)
            required_plans_str = ", ".join(plans)

            # CASE 1: User has an active subscription
            if user_sub and user_sub.status == 'active':
                if user_sub.plan in plans:
                    return f(*args, **kwargs)  # Access granted: Active and correct plan
                else:
                    # Active subscription, but not the right plan
                    message = f'This feature requires a "{required_plans_str}" subscription. Your current plan is "{user_sub.plan}" (active).'
                    if is_api_route:
                        return jsonify({'error': 'Subscription plan insufficient', 'message': message}), 403
                    else:
                        flash(message, 'warning')
                        return redirect(url_for('main.pricing'))

            # CASE 2: Feature allows 'free' plan, and user is effectively 'free'
            if 'free' in plans:
                if not user_sub: 
                    return f(*args, **kwargs) 
                if user_sub and user_sub.plan == 'free':
                     return f(*args, **kwargs)

            # CASE 3: Access denied (no active qualifying subscription, or 'free' not applicable/sufficient)
            denial_message = ""
            if user_sub:
                denial_message = f'Access denied. This feature requires a "{required_plans_str}" subscription. Your current plan is "{user_sub.plan}" with status "{user_sub.status}".'
            else:
                denial_message = f'Access denied. This feature requires a "{required_plans_str}" subscription. No active subscription found.'
            
            if is_api_route:
                return jsonify({'error': 'Subscription required or insufficient', 'message': denial_message}), 403
            else:
                flash(denial_message, 'warning')
                return redirect(url_for('main.pricing'))
                
        return wrapped
    return decorator

def calculate_seo_health(score):
    """
    Calculate SEO health status based on score
    
    Parameters:
    - score: SEO score (0-100)
    
    Returns:
    - Tuple of (status, class)
    """
    if score >= 80:
        return ('Good', 'success')
    elif score >= 60:
        return ('Fair', 'warning')
    else:
        return ('Poor', 'danger')

def truncate_url(url, max_length=40):
    """
    Truncate URL for display purposes
    
    Parameters:
    - url: URL to truncate
    - max_length: Maximum length
    
    Returns:
    - Truncated URL
    """
    if len(url) <= max_length:
        return url
        
    # Remove protocol
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
        
    # Remove www if present
    if url.startswith('www.'):
        url = url[4:]
        
    if len(url) <= max_length:
        return url
        
    # Truncate in the middle
    half = (max_length - 3) // 2
    return url[:half] + '...' + url[-half:]

def format_date(date_obj):
    """Format datetime object to readable string"""
    return date_obj.strftime('%b %d, %Y')

def format_datetime(date_obj):
    """Format datetime object to readable string with time"""
    return date_obj.strftime('%b %d, %Y %H:%M')
