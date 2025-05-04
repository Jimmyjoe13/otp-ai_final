from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_status = db.Column(db.String(20), default='free')
    subscription_ends_at = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    analysis_type = db.Column(db.String(20), nullable=False)  # meta, partial, complete, deep
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Analysis results
    meta_score = db.Column(db.Integer, nullable=True)
    content_score = db.Column(db.Integer, nullable=True)
    technical_score = db.Column(db.Integer, nullable=True)
    overall_score = db.Column(db.Integer, nullable=True)
    
    # Relationship
    details = db.relationship('AnalysisDetail', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')

class AnalysisDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'))
    category = db.Column(db.String(50), nullable=False)  # title, meta, headings, content, etc.
    component = db.Column(db.String(50), nullable=False)  # specific component name
    status = db.Column(db.String(20), nullable=False)  # good, warning, error
    score = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    recommendation = db.Column(db.Text, nullable=True)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    stripe_subscription_id = db.Column(db.String(100), nullable=True)
    plan = db.Column(db.String(20), nullable=False)  # free, basic, premium, enterprise
    status = db.Column(db.String(20), nullable=False)  # active, canceled, past_due
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ends_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('subscription', uselist=False))

class PaymentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    stripe_payment_id = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    status = db.Column(db.String(20), nullable=False)  # succeeded, pending, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='payments')
