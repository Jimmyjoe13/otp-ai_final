import os
import logging
import sys

logger = logging.getLogger(__name__)

# Required environment variables for Railway deployment
REQUIRED_ENV_VARS = {
    'SESSION_SECRET': 'Flask session secret key',
    'DATABASE_URL': 'PostgreSQL database connection URL',
    'DEEPSEEK_API_KEY': 'DeepSeek AI API key (ex: sk-24989e93c8a84107a8514a7ec1e5e3dd)', # Clé mise à jour
    'STRIPE_SECRET_KEY': 'Stripe secret key for payments',
    'STRIPE_WEBHOOK_SECRET': 'Stripe webhook secret for payment verification',
    'DOMAIN': 'Application domain for Stripe redirects'
}

# Optional environment variables with defaults
OPTIONAL_ENV_VARS = {
    'FLASK_DEBUG': 'Enable Flask debug mode (default: False)',
    'LOG_LEVEL': 'Logging level (DEBUG, INFO, WARNING, ERROR - default: INFO)',
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
    logger.info("--- Validating Environment Variables ---")
    
    for var_name, description in REQUIRED_ENV_VARS.items():
        value = os.environ.get(var_name)
        if not value:
            missing_vars.append(f"  - {var_name}: {description}")
            logger.error(f"❌ Missing required environment variable: {var_name} ({description})")
        else:
            # Masquer partiellement les clés API pour la sécurité dans les logs
            masked_value = value
            if "KEY" in var_name or "SECRET" in var_name:
                masked_value = f"{value[:7]}...{value[-4:]}" if len(value) > 11 else f"{value[:3]}..."
            logger.info(f"✓ {var_name} is set ({masked_value})")
            
            # Validate specific formats
            if var_name == 'DEEPSEEK_API_KEY' and not value.startswith('sk-'):
                logger.warning(f"  ⚠️  DeepSeek API key format may be incorrect for {var_name}.")
            elif var_name == 'STRIPE_SECRET_KEY' and not (value.startswith('sk_test_') or value.startswith('sk_live_')):
                logger.warning(f"  ⚠️  Stripe secret key format may be incorrect for {var_name}.")
            elif var_name == 'STRIPE_WEBHOOK_SECRET' and not value.startswith('whsec_'):
                logger.warning(f"  ⚠️  Stripe webhook secret format may be incorrect for {var_name}.")
            elif var_name == 'DATABASE_URL' and not value.startswith('postgresql://'):
                logger.warning(f"  ⚠️  Database URL format may be incorrect for {var_name}.")
    
    logger.info("\n--- Optional Environment Variables ---")
    for var_name, description in OPTIONAL_ENV_VARS.items():
        value = os.environ.get(var_name)
        if value:
            logger.info(f"✓ {var_name} is set to '{value}' ({description})")
        else:
            logger.info(f"- {var_name} not set (optional, using default if any): {description}")
    
    if missing_vars:
        logger.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.error("❌ Environment validation FAILED!")
        logger.error("Missing required environment variables:")
        for var_info in missing_vars:
            logger.error(var_info)
        logger.error("Please set these variables in your Railway deployment settings.")
        logger.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return False
    
    logger.info("✅ Environment validation PASSED!")
    logger.info("------------------------------------")
    return True

def validate_or_exit():
    """
    Validate environment and exit if validation fails.
    This is useful for scripts that should not run if env is misconfigured.
    """
    if not validate_environment():
        logger.critical("Application cannot start due to missing critical environment variables. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    # Configure un logger basique pour le script de validation lui-même
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format='%(levelname)s (env_validator): %(message)s')
    validate_or_exit()
