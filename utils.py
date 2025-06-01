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
            
            user_sub_obj = getattr(current_user, 'subscription', None) # Renamed to avoid confusion
            required_plans_str = ", ".join(plans)

            effective_plan = None
            is_considered_active = False # More descriptive name

            # Priority to Subscription object if it exists and is active
            if user_sub_obj and user_sub_obj.status == 'active':
                effective_plan = user_sub_obj.plan
                is_considered_active = True
            # Fallback to User.subscription_status if Subscription object is not conclusive
            elif hasattr(current_user, 'subscription_status') and current_user.subscription_status:
                effective_plan = current_user.subscription_status
                # Assume 'free' is always active-like, and any other plan string implies it should be active
                # This is a simplification. A robust check for paid plans from User.subscription_status
                # would ideally involve checking current_user.subscription_ends_at > datetime.utcnow()
                if effective_plan == 'free' or (user_sub_obj is None and effective_plan not in ['free', None]):
                    is_considered_active = True
                elif user_sub_obj and user_sub_obj.status != 'active' and effective_plan not in ['free', None]:
                    # If sub_obj exists but not active, but subscription_status is a paid plan,
                    # we might still consider it active based on subscription_status for this fallback.
                    # This depends on how strictly 'active' status from sub_obj should be enforced.
                    # For now, let's assume subscription_status takes precedence if sub_obj isn't 'active'.
                    is_considered_active = True


            if is_considered_active:
                if effective_plan in plans:
                    return f(*args, **kwargs)  # Access granted
                else:
                    # Considered active, but not the right plan
                    message = f'This feature requires a "{required_plans_str}" subscription. Your current plan is "{effective_plan}".'
                    if is_api_route:
                        return jsonify({'error': 'Subscription plan insufficient', 'message': message}), 403
                    else:
                        flash(message, 'warning')
                        return redirect(url_for('main.pricing'))
            
            # Handle 'free' plan access specifically if not covered by the general logic above
            # This is important if 'free' is in plans and effective_plan ended up as None or not 'free'
            # but the user should be considered 'free' by default.
            if 'free' in plans:
                # A user is 'free' if no specific plan is found or explicitly set to 'free'
                is_default_free = not effective_plan or effective_plan == 'free'
                if hasattr(current_user, 'subscription_status') and current_user.subscription_status == 'free':
                    is_default_free = True # Explicitly free

                if is_default_free:
                     return f(*args, **kwargs)

            # CASE 3: Access denied
            denial_message = ""
            if effective_plan: 
                denial_message = f'Access denied. This feature requires a "{required_plans_str}" subscription. Your current plan is "{effective_plan}". The plan may not be active or sufficient.'
            elif user_sub_obj: # Has a subscription object, but it wasn't deemed active or plan was None
                 denial_message = f'Access denied. This feature requires a "{required_plans_str}" subscription. Your subscription (Plan: {user_sub_obj.plan}, Status: {user_sub_obj.status}) is not sufficient or not active.'
            else: # No plan information found at all
                denial_message = f'Access denied. This feature requires a "{required_plans_str}" subscription. No active or known subscription found.'
            
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
