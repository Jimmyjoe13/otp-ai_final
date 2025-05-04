import functools
from flask import flash, redirect, url_for
from flask_login import current_user

def requires_subscription(plans):
    """
    Decorator to check if user has required subscription level
    
    Parameters:
    - plans: List of allowed subscription plans
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this feature', 'warning')
                return redirect(url_for('auth.login'))
                
            # Administrateurs ont accès à toutes les fonctionnalités
            if hasattr(current_user, 'is_admin') and current_user.is_admin:
                return f(*args, **kwargs)
                
            if current_user.subscription_status not in plans:
                flash(f'This feature requires a {" or ".join(plans)} subscription', 'warning')
                return redirect(url_for('main.pricing'))
                
            return f(*args, **kwargs)
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
