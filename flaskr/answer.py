from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('answer', __name__)

@bp.route('/<int:questionId>/createAnswer', methods=('POST',))
@login_required
def create(questionId):
    answer_text = request.form['answer_text']
    error = None
    db = get_db()

    # errors if a question is not supplied
    if not answer_text:
        error = 'Answer is required.'
    
    duplicate_answer = db.execute(
        'SELECT *'
        ' FROM answer'
        ' WHERE answer.question_id = ? AND answer.text = ?;',
        (questionId, answer_text,)
    ).fetchone()

    if duplicate_answer is not None:
        error = "This answer already exists! Vote for that answer."

    if error is not None:
        flash(error)

    # if no error, adds an answer to the database
    else:

        # creates a new answer
        db.execute(
            'INSERT INTO answer (text, question_id, author_id)'
            ' VALUES (?, ?, ?)',
            (answer_text, questionId, g.user['user_id'])
        )

        answer_id = db.execute(
            'SELECT answer.answer_id'
            ' FROM answer'
            ' WHERE answer.text = ? AND answer.question_id = ?',
            (answer_text, questionId)
        ).fetchone()['answer_id']

        # user automatically chooses an answer they create
        db.execute(
            'INSERT INTO choose (user_id, answer_id)'
            ' VALUES (?, ?)',
            (g.user['user_id'], answer_id)
        )
        
        db.commit()
        # TODO: redirect to answer page, not questions
    return redirect(url_for('question.index'))