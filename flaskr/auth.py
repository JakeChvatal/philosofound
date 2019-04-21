import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# adds route to endpoint
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # request.form is dict mapping for form keys and values
        username = request.form['username']
        password = request.form['password']
        gender = request.form['gender']
        income = request.form['income']
        party = request.form['party']
        geography = request.form['geography']
        
        db = get_db()
        error = None
        
        # catches missing username, password or required field
        if not username:
            error = 'Username is required.'
        
        elif not password:
            error = 'Password is required.'
        
        elif gender == "Choose an option...":
            error = 'Gender is required.'
        
        elif income == "Choose an option...":
            error = 'Income is required.'
        
        elif party == "Choose an option...":
            error = 'Party is required.'
        
        elif geography == "Choose an option...":
            error = "Geography is required."

        # enforces unique username constraint
        elif db.execute(
            'SELECT user_id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
        
        # add user to database if there is no error
        if error is None:
            # add username and securely hashed password to db
            db.execute(
                'INSERT INTO user (username, password, gender, income, party, geography) VALUES (?, ?, ?, ?, ?, ?)',
                (username, generate_password_hash(password), gender, income, party, geography)
            )
            db.commit()

            # redirects to login page
            return redirect(url_for('auth.login'))
        else:
            # displays an error, does not permit registration
            flash(error)
    
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    # if this is a POST, login is registered
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # validates username and password
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        # user information is stored in a cookie if the information is valid
        if error is None:
            session.clear()
            session['user_id'] = user['user_id']
            return redirect(url_for('index'))
        
        flash(error)
    
    return render_template('auth/login.html')

# called before the app
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None

    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE user_id = ?', (user_id,)
        ).fetchone()

# logs out the current user
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# decorator which requires login for the function it decorates
def login_required(view):
    @functools.wraps(view)
    
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view