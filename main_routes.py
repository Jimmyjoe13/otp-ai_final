from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint('main', __name__)

from datetime import datetime

@main.route('/')
def index():
    return render_template('index.html', now=datetime.now())

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/pricing')
def pricing():
    from datetime import datetime
    return render_template('pricing.html', now=datetime.now())
