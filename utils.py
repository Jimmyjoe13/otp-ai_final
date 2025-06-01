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
            
            # Get the user's subscription object
            user_sub = getattr(current_user, 'subscription', None)
            required_plans_str = ", ".join(plans)

            # CASE 1: User has an active subscription
            if user_sub and user_sub.status == 'active':
                if user_sub.plan in plans:
                    return f(*args, **kwargs)  # Access granted: Active and correct plan
                else:
                    # Active subscription, but not the right plan
                    flash(f'This feature requires a "{required_plans_str}" subscription. Your current plan is "{user_sub.plan}" (active).', 'warning')
                    return redirect(url_for('main.pricing'))

            # CASE 2: Feature allows 'free' plan, and user is effectively 'free'
            # A user is considered 'free' for this check if they have no subscription record,
            # or if their subscription record explicitly states plan 'free' (regardless of its status, though typically it wouldn't be 'active' here).
            if 'free' in plans:
                if not user_sub: # No subscription record at all, implies free
                    return f(*args, **kwargs) 
                # If there's a subscription record, but it's for the 'free' plan (e.g. an explicit 'free' tier in Subscription table)
                # and it's not active (covered by CASE 1 if it was active 'free'), we still grant access if 'free' is allowed.
                # This handles if 'free' users have a row in Subscription table with plan='free', status='active' or other.
                # If their plan is 'free' and status is 'active', CASE 1 with 'free' in plans would grant access.
                # If their plan is 'free' and status is not 'active', this grants access if 'free' is in plans.
                if user_sub and user_sub.plan == 'free': # User has a 'free' plan record
                     return f(*args, **kwargs)


            # CASE 3: Access denied (no active qualifying subscription, and 'free' not applicable or not sufficient)
            if user_sub:
                # User has a subscription record, but it's not active or not the correct plan (and 'free' access didn't apply)
                flash(f'Access denied. This feature requires a "{required_plans_str}" subscription. Your current plan is "{user_sub.plan}" with status "{user_sub.status}".', 'warning')
            else:
                # No subscription record at all, and 'free' was not an allowed plan for this feature
                flash(f'Access denied. This feature requires a "{required_plans_str}" subscription. No active subscription found.', 'warning')
            
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
