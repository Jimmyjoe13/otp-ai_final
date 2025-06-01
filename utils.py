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
            # The 'subscription' attribute is a backref from the Subscription model to User
            user_subscription = getattr(current_user, 'subscription', None)

            if not user_subscription:
                # Handles cases where a user might exist without a corresponding Subscription row,
                # or if the subscription relationship isn't loaded.
                # This also implicitly covers 'free' users if 'free' isn't a plan in 'plans' list
                # and no Subscription record means they are effectively free.
                if 'free' in plans: # If 'free' is explicitly allowed for a feature
                    pass # Allow access if 'free' is a valid plan for the decorated route
                else:
                    flash('An active subscription is required to access this feature.', 'warning')
                    return redirect(url_for('main.pricing'))
            
            # Check if the subscription is active and the plan is one of the allowed plans
            if user_subscription and user_subscription.status == 'active':
                if user_subscription.plan in plans:
                    return f(*args, **kwargs) # Access granted
                else:
                    # Active subscription, but not the right plan
                    flash(f'This feature requires a "{", ".join(plans)}" subscription. Your current plan is "{user_subscription.plan}".', 'warning')
                    return redirect(url_for('main.pricing'))
            else:
                # Subscription exists but is not active (e.g., 'past_due', 'canceled')
                # Or it's a 'free' user case not covered by 'free' in plans.
                if 'free' in plans and (not user_subscription or user_subscription.plan == 'free'):
                     # If 'free' is allowed and user is effectively free (no subscription or free plan)
                    return f(*args, **kwargs)

                status_message = f"Your subscription status is \"{user_subscription.status if user_subscription else 'not active'}\"."
                flash(f'Access denied. {status_message} This feature requires a "{", ".join(plans)}" subscription.', 'warning')
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
