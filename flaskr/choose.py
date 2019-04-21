from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('choose', __name__)

@bp.route('/<int:answerId>/choose', methods=('POST',))
@login_required
def choose(answerId):
    db = get_db()
    error = None

    questionID = db.execute(
        'SELECT question_id from answer where answer_id = ?;',
        (answerId,)
    ).fetchone()['question_id']

    if db.execute(
            'SELECT c.user_id'
            ' FROM answer a join choose c on (a.answer_id = c.answer_id)'
            ' where c.user_id = ? AND ? = a.question_id',
        (g.user['user_id'], questionID)
        ).fetchone() is not None:
        error = "You've already voted for that question!"

    if error is not None:
        flash(error)
    else:   
        db.execute(
            'INSERT INTO choose (user_id, answer_id)'
            ' VALUES (?, ?)',
            (g.user['user_id'], answerId)
        )
    
    questionId = db.execute(
        'SELECT question_id'
        ' FROM answer'
        ' WHERE answer_id = ?',
        (answerId,)
    ).fetchone()['question_id']

    db.commit()
    return redirect(url_for('answer.index', chosen_answer = answerId))