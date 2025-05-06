import os
import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, url_for, flash, render_template, jsonify
from flask_login import login_required, current_user
import stripe
from app import db
from models import User, Subscription, PaymentHistory

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Configuration for Stripe products
STRIPE_PRODUCTS = {
    'basic': {
        'name': 'Basic Plan',
        'description': 'Great for bloggers and small websites',
        'amount': 1900,  # $19.00
        'price_id': os.environ.get('STRIPE_BASIC_PRICE_ID', None),
        'features': ['Meta Tag Analysis', 'Partial Analysis', 'Dashboard Access']
    },
    'premium': {
        'name': 'Premium Plan',
        'description': 'Perfect for businesses and marketing teams',
        'amount': 4900,  # $49.00
        'price_id': os.environ.get('STRIPE_PREMIUM_PRICE_ID', None),
        'features': ['Meta Tag Analysis', 'Partial Analysis', 'Complete Analysis', 'AI Recommendations', 'Priority Support']
    },
    'enterprise': {
        'name': 'Enterprise Plan',
        'description': 'For agencies and large enterprise websites',
        'amount': 14900,  # $149.00
        'price_id': os.environ.get('STRIPE_ENTERPRISE_PRICE_ID', None),
        'features': ['All Premium Features', 'Deep Analysis with AI', 'Custom Reports', 'API Access', 'Dedicated Support']
    }
}

def create_stripe_products():
    """Create Stripe products if they don't exist"""
    logger.info("Creating Stripe products if needed...")
    
    for plan, details in STRIPE_PRODUCTS.items():
        # Skip if price_id is already set
        if details['price_id']:
            continue
            
        try:
            # Check if product exists
            products = stripe.Product.list(active=True)
            product_id = None
            
            # Look for existing product with this name
            for product in products:
                if product.name == details['name']:
                    product_id = product.id
                    break
                    
            # Create product if it doesn't exist
            if not product_id:
                product = stripe.Product.create(
                    name=details['name'],
                    description=details['description'],
                    metadata={'plan': plan}
                )
                product_id = product.id
                logger.info(f"Created Stripe product: {details['name']}")
                
            # Check if price exists for this product
            prices = stripe.Price.list(product=product_id, active=True)
            if not prices.data:
                # Create price
                price = stripe.Price.create(
                    product=product_id,
                    unit_amount=details['amount'],
                    currency='usd',
                    recurring={'interval': 'month'},
                    metadata={'plan': plan}
                )
                
                # Update price_id in our configuration
                STRIPE_PRODUCTS[plan]['price_id'] = price.id
                logger.info(f"Created Stripe price for {details['name']}: {price.id}")
            else:
                # Use existing price
                STRIPE_PRODUCTS[plan]['price_id'] = prices.data[0].id
                logger.info(f"Using existing Stripe price for {details['name']}: {prices.data[0].id}")
                
        except Exception as e:
            logger.error(f"Error creating Stripe product/price for {plan}: {str(e)}")
            
    logger.info("Stripe products setup complete.")

# Get domain for redirects
from flask import request

def get_domain():
    # Prioritize Railway or custom environment variable for domain
    domain = os.environ.get('DOMAIN')
    if not domain:
        # Fallback to Replit environment variables for compatibility
        domain = os.environ.get('REPLIT_DEV_DOMAIN')
        if os.environ.get('REPLIT_DEPLOYMENT'):
            domains = os.environ.get('REPLIT_DOMAINS', '').split(',')
            if domains:
                domain = domains[0]
    if not domain:
        # Fallback to request host if running in a web request context
        try:
            domain = request.host
        except RuntimeError:
            # Outside request context
            domain = None
    return domain

# Create Blueprint
payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/init-products', methods=['GET'])
@login_required
def init_products():
    """Initialize Stripe products - admin only route"""
    if not current_user.is_authenticated or current_user.id != 1:  # Assuming user ID 1 is admin
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.index'))
        
    try:
        create_stripe_products()
        flash('Stripe products initialized successfully', 'success')
    except Exception as e:
        logger.error(f"Error initializing Stripe products: {str(e)}")
        flash(f'Error initializing products: {str(e)}', 'danger')
        
    return redirect(url_for('main.pricing'))

@payment_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        plan = request.form.get('plan')
        if plan not in STRIPE_PRODUCTS:
            flash('Invalid plan selected', 'danger')
            return redirect(url_for('main.pricing'))
        
        domain = get_domain()
        if not domain:
            flash('Unable to determine domain for checkout', 'danger')
            return redirect(url_for('main.pricing'))
        
        # Ensure we have Stripe products and prices
        create_stripe_products()
        
        # Create or retrieve Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.username,
                metadata={'user_id': current_user.id}
            )
            
            # Save Stripe customer ID to user
            user = User.query.get(current_user.id)
            user.stripe_customer_id = customer.id
            db.session.commit()
        else:
            customer = stripe.Customer.retrieve(current_user.stripe_customer_id)
        
        # Check if we have a price_id for this plan
        if not STRIPE_PRODUCTS[plan]['price_id']:
            # Create price for this plan
            product = stripe.Product.create(
                name=STRIPE_PRODUCTS[plan]['name'],
                description=STRIPE_PRODUCTS[plan]['description'],
                metadata={'plan': plan}
            )
            
            price = stripe.Price.create(
                product=product.id,
                unit_amount=STRIPE_PRODUCTS[plan]['amount'],
                currency='usd',
                recurring={'interval': 'month'},
                metadata={'plan': plan}
            )
            
            STRIPE_PRODUCTS[plan]['price_id'] = price.id
            logger.info(f"Created new Stripe price for {plan}: {price.id}")
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': STRIPE_PRODUCTS[plan]['price_id'],
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=f'https://{domain}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{domain}/payment/cancel',
        )
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        flash(f'Payment processing error: {str(e)}', 'danger')
        return redirect(url_for('main.pricing'))

@payment_bp.route('/success')
@login_required
def payment_success():
    session_id = request.args.get('session_id')
    if not session_id:
        flash('Invalid session', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Retrieve the session
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Update user subscription
        subscription = stripe.Subscription.retrieve(session.subscription)
        
        # Get the plan from the product
        product = stripe.Product.retrieve(subscription.plan.product)
        plan_name = product.metadata.get('plan', 'basic')  # Default to basic if not specified
        
        # Update user subscription in database
        user_sub = Subscription.query.filter_by(user_id=current_user.id).first()
        
        if not user_sub:
            user_sub = Subscription(
                user_id=current_user.id,
                stripe_customer_id=session.customer,
                stripe_subscription_id=session.subscription,
                plan=plan_name,
                status='active',
                ends_at=datetime.utcnow() + timedelta(days=30)  # Default to 30 days
            )
            db.session.add(user_sub)
        else:
            user_sub.stripe_subscription_id = session.subscription
            user_sub.plan = plan_name
            user_sub.status = 'active'
            user_sub.ends_at = datetime.utcnow() + timedelta(days=30)
        
        # Update user status
        user = User.query.get(current_user.id)
        user.subscription_status = plan_name
        user.subscription_ends_at = datetime.utcnow() + timedelta(days=30)
        
        # Record payment
        payment = PaymentHistory(
            user_id=current_user.id,
            stripe_payment_id=session.payment_intent,
            amount=session.amount_total / 100,  # Convert cents to dollars
            currency=session.currency,
            status='succeeded'
        )
        db.session.add(payment)
        
        db.session.commit()
        
        flash('Subscription successful! Thank you for subscribing.', 'success')
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        logger.error(f"Error processing successful payment: {str(e)}")
        flash('Error processing payment. Please contact support.', 'danger')
        return redirect(url_for('main.dashboard'))

@payment_bp.route('/cancel')
@login_required
def payment_cancel():
    flash('Payment was cancelled.', 'info')
    return redirect(url_for('main.pricing'))

@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Handle the case where webhook secret is not set
    if not webhook_secret:
        # In development, we'll parse the payload directly
        try:
            event = json.loads(payload)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {str(e)}")
            return jsonify(success=False), 400
    else:
        # In production, validate the signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            return jsonify(success=False), 400
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return jsonify(success=False), 400
    
    # Handle specific events
    if event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_payment_succeeded(invoice)
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_payment_failed(invoice)
    
    return jsonify(success=True)

# Helper functions for webhook handling
def handle_subscription_updated(subscription):
    try:
        # Find subscription in database
        sub = Subscription.query.filter_by(stripe_subscription_id=subscription.id).first()
        if sub:
            # Update status
            sub.status = subscription.status
            
            # Update end date if applicable
            if subscription.current_period_end:
                end_date = datetime.fromtimestamp(subscription.current_period_end)
                sub.ends_at = end_date
                
                # Update user subscription end date
                user = User.query.get(sub.user_id)
                if user:
                    user.subscription_ends_at = end_date
            
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error handling subscription update: {str(e)}")

def handle_subscription_deleted(subscription):
    try:
        # Find subscription in database
        sub = Subscription.query.filter_by(stripe_subscription_id=subscription.id).first()
        if sub:
            # Mark as cancelled
            sub.status = 'canceled'
            
            # Update user subscription
            user = User.query.get(sub.user_id)
            if user:
                user.subscription_status = 'free'
            
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error handling subscription deletion: {str(e)}")

def handle_payment_succeeded(invoice):
    try:
        # Only process subscription invoices
        if not invoice.subscription:
            return
            
        # Find subscription
        sub = Subscription.query.filter_by(stripe_subscription_id=invoice.subscription).first()
        if not sub:
            return
            
        # Record payment
        payment = PaymentHistory(
            user_id=sub.user_id,
            stripe_payment_id=invoice.payment_intent,
            amount=invoice.amount_paid / 100,  # Convert cents to dollars
            currency=invoice.currency,
            status='succeeded'
        )
        db.session.add(payment)
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error handling payment success: {str(e)}")

def handle_payment_failed(invoice):
    try:
        # Only process subscription invoices
        if not invoice.subscription:
            return
            
        # Find subscription
        sub = Subscription.query.filter_by(stripe_subscription_id=invoice.subscription).first()
        if not sub:
            return
            
        # Record failed payment
        payment = PaymentHistory(
            user_id=sub.user_id,
            stripe_payment_id=invoice.payment_intent,
            amount=invoice.amount_due / 100,  # Convert cents to dollars
            currency=invoice.currency,
            status='failed'
        )
        db.session.add(payment)
        
        # Update subscription status
        sub.status = 'past_due'
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}")
