import os
import logging
import sys

logger = logging.getLogger(__name__)

# Required environment variables for Railway deployment
REQUIRED_ENV_VARS = {
    'SESSION_SECRET': 'Flask session secret key',
    'DATABASE_URL': 'PostgreSQL database connection URL',
    'DEEPSEEK_API_KEY': 'DeepSeek AI API key (ex: sk-your-key). Used if OPTY_BOT_WEBHOOK_URL is not set.',
    'DOMAIN': 'Application domain (e.g., https://your-app.up.railway.app)'
}

# Optional environment variables with defaults
OPTIONAL_ENV_VARS = {
    'FLASK_DEBUG': 'Enable Flask debug mode (True/False - default: False)',
    'LOG_LEVEL': 'Logging level (DEBUG, INFO, WARNING, ERROR - default: INFO)',
    
    'STRIPE_SECRET_KEY': 'Stripe secret key for payments (sk_test_... or sk_live_...)',
    'STRIPE_WEBHOOK_SECRET': 'Stripe webhook secret for payment verification (whsec_...)',
    'STRIPE_BASIC_PRICE_ID': 'Stripe price ID for basic plan',
    'STRIPE_PREMIUM_PRICE_ID': 'Stripe price ID for premium plan',
    'STRIPE_ENTERPRISE_PRICE_ID': 'Stripe price ID for enterprise plan',
    
    'OPTY_BOT_WEBHOOK_URL': 'URL for the external Opty-bot webhook (if used instead of internal DeepSeek for chatbot)',
    'OPTY_BOT_WEBHOOK_AUTH_TOKEN': 'Authentication token for the Opty-bot webhook (if required by the webhook)'
}

def validate_environment():
    """
    Validate that all required environment variables are set.
    Logs warnings for optional variables if not set or if format seems incorrect.
    Returns True if all required vars are present, False otherwise.
    """
    missing_vars = []
    logger.info("--- Validating Environment Variables ---")
    
    # Check Required Variables
    logger.info("--- Required Environment Variables ---")
    for var_name, description in REQUIRED_ENV_VARS.items():
        value = os.environ.get(var_name)
        if not value:
            missing_vars.append(f"  - {var_name}: {description}")
            logger.error(f"❌ Missing: {var_name} ({description})")
        else:
            masked_value = value
            if "KEY" in var_name.upper() or "SECRET" in var_name.upper() or "TOKEN" in var_name.upper():
                masked_value = f"{value[:7]}...{value[-4:]}" if len(value) > 11 else f"{value[:3]}..."
            elif "URL" in var_name.upper() and "DATABASE_URL" not in var_name.upper() : # Avoid masking full DB URL
                 masked_value = f"{value[:30]}..." if len(value) > 30 else value

            logger.info(f"✓ Set: {var_name} = {masked_value} ({description})")
            
            # Specific format warnings for required vars
            if var_name == 'DEEPSEEK_API_KEY' and not value.startswith('sk-'):
                logger.warning(f"  ⚠️  Format Warning: {var_name} does not start with 'sk-'.")
            elif var_name == 'DATABASE_URL' and not value.startswith('postgresql://'):
                logger.warning(f"  ⚠️  Format Warning: {var_name} does not start with 'postgresql://'.")
            elif var_name == 'DOMAIN' and not (value.startswith('http://') or value.startswith('https://')):
                 logger.warning(f"  ⚠️  Format Warning: {var_name} should start with http:// or https://.")


    # Check Optional Variables
    logger.info("\n--- Optional Environment Variables ---")
    for var_name, description in OPTIONAL_ENV_VARS.items():
        value = os.environ.get(var_name)
        if value:
            masked_value = value
            if "KEY" in var_name.upper() or "SECRET" in var_name.upper() or "TOKEN" in var_name.upper():
                masked_value = f"{value[:7]}...{value[-4:]}" if len(value) > 11 else f"{value[:3]}..."
            elif "URL" in var_name.upper():
                 masked_value = f"{value[:30]}..." if len(value) > 30 else value
            logger.info(f"✓ Set: {var_name} = {masked_value} ({description})")

            # Specific format warnings for optional vars if set
            if var_name == 'STRIPE_SECRET_KEY' and not (value.startswith('sk_test_') or value.startswith('sk_live_')):
                logger.warning(f"  ⚠️  Format Warning: {var_name} does not start with 'sk_test_' or 'sk_live_'.")
            elif var_name == 'STRIPE_WEBHOOK_SECRET' and not value.startswith('whsec_'):
                logger.warning(f"  ⚠️  Format Warning: {var_name} does not start with 'whsec_'.")
            elif var_name == 'OPTY_BOT_WEBHOOK_URL' and not (value.startswith('http://') or value.startswith('https://')):
                 logger.warning(f"  ⚠️  Format Warning: {var_name} should start with http:// or https://.")
        else:
            logger.info(f"- Not Set: {var_name} (Optional: {description})")
    
    if missing_vars:
        logger.critical("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        logger.critical("❌ CRITICAL: Environment validation FAILED!")
        logger.critical("Missing REQUIRED environment variables:")
        for var_info in missing_vars:
            logger.critical(var_info)
        logger.critical("Application may not start or function correctly.")
        logger.critical("Please set these variables in your Railway deployment settings.")
        logger.critical("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return False # Critical failure
    
    logger.info("✅ Environment validation PASSED (all required variables are set).")
    logger.info("------------------------------------")
    return True

def validate_or_exit():
    """
    Validate environment and exit if validation fails for required variables.
    """
    if not validate_environment():
        # The validate_environment function already logs critical errors.
        # We exit here to prevent the application from starting in a broken state.
        sys.exit(1)

if __name__ == "__main__":
    # Configure a basic logger for direct script execution
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format='%(levelname)s (env_validator_script): %(message)s')
    logger.info("Running env_validator.py as a standalone script...")
    validate_or_exit()
    logger.info("Standalone script execution finished.")
