from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('answer', __name__)

@bp.route('/<int:questionId>/createAnswer', methods=('POST',))
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

        # creates a new answer
        db.execute(
            'INSERT INTO answer (answer, question_id, author_id)'
            ' VALUES (?, ?, ?)',
            (answer, questionId, g.user['id'])
        )

        # user automatically chooses an answer they create
        db.execute(
            'INSERT INTO choose (user_id, answer_id)'
            ' VALUES (?, ?)',
            (g.user['id'], answer['id'])
        )
        
        db.commit()
        # TODO: redirect to answer page, not questions
        return redirect(url_for('question.index'))