from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('vote', __name__)

@bp.route('/vote', methods=('POST', 'FAKE'))
@login_required
def vote():
    answer = request.form['answer']
    error = None

    # errors if a question is not supplied
    if not question:
        error = 'Question is required.'
    
    if error is not None:
        flash(error)

    # if no error, adds a question to the database
    else:
        db = get_db()
        db.execute(
            'INSERT INTO question (question, author_id)'
            ' VALUES (?, ?)',
            (question, g.user['id'])
        )
        db.commit()
        return redirect(url_for('question.index'))