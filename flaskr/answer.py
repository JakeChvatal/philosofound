from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('answer', __name__)

@bp.route('/<int:questionId>/createAnswer', methods=('POST', 'FAKEPOST'))
@login_required
def create(questionId):
    answer = request.form['answer']
    error = None

    # errors if a question is not supplied
    if not answer:
        error = 'Answer is required.'
    
    if error is not None:
        flash(error)

    # if no error, adds an answer to the database
    else:
        db = get_db()
        db.execute(
            'INSERT INTO answer (answer, question_id, author_id)'
            ' VALUES (?, ?, ?)',
            (answer, questionId, g.user['id'])
        )
        db.commit()
        return redirect(url_for('question.index'))