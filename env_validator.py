import os
import logging
import sys

logger = logging.getLogger(__name__)

# Required environment variables for Railway deployment
REQUIRED_ENV_VARS = {
    'SESSION_SECRET': 'Flask session secret key',
    'DATABASE_URL': 'PostgreSQL database connection URL',
    'DEEPSEEK_API_KEY': 'DeepSeek AI API key for AI features',
    'STRIPE_SECRET_KEY': 'Stripe secret key for payments',
    'STRIPE_WEBHOOK_SECRET': 'Stripe webhook secret for payment verification',
    'DOMAIN': 'Application domain for Stripe redirects'
}

# Optional environment variables with defaults
OPTIONAL_ENV_VARS = {
    'FLASK_DEBUG': 'Enable Flask debug mode (default: False)',
    'STRIPE_BASIC_PRICE_ID': 'Stripe price ID for basic plan',
    'STRIPE_PREMIUM_PRICE_ID': 'Stripe price ID for premium plan',
    'STRIPE_ENTERPRISE_PRICE_ID': 'Stripe price ID for enterprise plan'
}

def validate_environment():
    """
    Validate that all required environment variables are set
    Returns True if all required vars are present, False otherwise
    """
    missing_vars = []
    
    for var_name, description in REQUIRED_ENV_VARS.items():
        value = os.environ.get(var_name)
        if not value:
            missing_vars.append(f"  - {var_name}: {description}")
            logger.error(f"Missing required environment variable: {var_name}")
        else:
            # Validate specific formats
            if var_name == 'DEEPSEEK_API_KEY' and not value.startswith('sk-'):
                logger.warning(f"DeepSeek API key format may be incorrect: {value[:10]}...")
            elif var_name == 'STRIPE_SECRET_KEY' and not value.startswith('sk_'):
                logger.warning(f"Stripe secret key format may be incorrect: {value[:10]}...")
            elif var_name == 'STRIPE_WEBHOOK_SECRET' and not value.startswith('whsec_'):
                logger.warning(f"Stripe webhook secret format may be incorrect: {value[:10]}...")
            elif var_name == 'DATABASE_URL' and not value.startswith('postgresql://'):
                logger.warning(f"Database URL format may be incorrect: {value[:20]}...")
            else:
                logger.info(f"✓ {var_name} is set")
    
    # Log optional variables status
    for var_name, description in OPTIONAL_ENV_VARS.items():
        value = os.environ.get(var_name)
        if value:
            logger.info(f"✓ {var_name} is set (optional)")
        else:
            logger.info(f"- {var_name} not set (optional): {description}")
    
    if missing_vars:
        logger.error("❌ Environment validation failed!")
        logger.error("Missing required environment variables:")
        for var in missing_vars:
            logger.error(var)
        logger.error("\nPlease set these variables in your Railway deployment settings.")
        return False
    
    logger.info("✅ Environment validation passed!")
    return True

def validate_or_exit():
    """
    Validate environment and exit if validation fails
    """
    if not validate_environment():
        logger.error("Application cannot start without required environment variables.")
        sys.exit(1)

def get_env_status():
    """
    Get a dictionary with the status of all environment variables
    """
    status = {
        'required': {},
        'optional': {},
        'validation_passed': True
    }
    
    for var_name, description in REQUIRED_ENV_VARS.items():
        value = os.environ.get(var_name)
        status['required'][var_name] = {
            'set': bool(value),
            'description': description,
            'masked_value': f"{value[:10]}..." if value and len(value) > 10 else "Not set"
        }
        if not value:
            status['validation_passed'] = False
    
    for var_name, description in OPTIONAL_ENV_VARS.items():
        value = os.environ.get(var_name)
        status['optional'][var_name] = {
            'set': bool(value),
            'description': description,
            'value': value if value else "Not set"
        }
    
    return status

if __name__ == "__main__":
    # Run validation when script is executed directly
    validate_or_exit()
