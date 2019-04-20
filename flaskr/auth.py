import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# creates a blueprint called auth
bp = Blueprint('auth', __name__, url_prefix='/auth')

# adds route to endpoint
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # request.form is dict mapping for form keys and values
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # catches missing username, missing password, existing db entity
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
            # fetchone gets first row of the query
        ).fetchone() is not None:
            #.format inserts things in order into curly braces
            error = 'User {} is already registered.'.format(username)
        
        # add user to database if there is no error
        if error is None:
            # add username and securely hashed password to db
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            # generates redirect response for the url (???)
            return redirect(url_for('auth.login'))

        # stores message that can be retrieved when using the template
        flash(error)
    
    # return register template 
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # queries db 
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # validates username and password
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            # session: dict that stores data across requests
            # when validation is successful, user id is stored in session
            # this is stored in cookie sent to browser
            # browser sends this cookie back with subsequent requests
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
    
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None

    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# decorator
# returns new view function that wraps view its applied to
# adds function to check if user is loaded: redirect to login otherwise
# if user is loaded, og view is called and continues normally
def login_required(view):
    @functools.wraps(view)
    # i assume kwargs are the args for the original function
    # functional languages are so cool!!!
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapped_view

 # url_for():generates URL for view based on name and args
 # 'endpoint', same name as view function by default
 # when using a blueprint: name of blueprint is prepended to name of function

