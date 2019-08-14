from app import db
from app.auth import bp 
from flask_login import current_user, login_user
from app.models import User



@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    