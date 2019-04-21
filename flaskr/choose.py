from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('choose', __name__)

# user selects an answer
@bp.route('/answers/<int:answerId>/choose', methods=('POST',))
@login_required
def choose(answerId):
    db = get_db()
    error = None

    # get the question id associated with the given answer id
    questionId = db.execute(
        'SELECT a.question_id from answer a where a.answer_id = ?;',
        (answerId,)
    ).fetchone()['question_id']

    # ensures that the user has not voted for a question before
    if db.execute(
            'SELECT c.user_id'
            ' FROM answer a join choose c on (a.answer_id = c.answer_id)'
            ' where c.user_id = ? AND a.question_id = ?',
        (g.user['user_id'], questionId)
        ).fetchone() is not None:
        error = "You've already voted for that question!"

    if error is not None:
        flash(error)
    else:   
        # if they have not, vote for the answer
        db.execute(
            'INSERT INTO choose (user_id, answer_id)'
            ' VALUES (?, ?)',
            (g.user['user_id'], answerId)
        )

    db.commit()
    return redirect(url_for('answer.index', chosen_answer = answerId))