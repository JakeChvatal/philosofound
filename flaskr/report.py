from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('choose', __name__)

@bp.route('/<int:answerId>/report', methods=('POST',))
@login_required
def report(answerId):
    db = get_db()
    error = None

    if db.execute(
        'SELECT *'
        ' FROM report'
        ' WHERE user_id = ?',
        (g.user['user_id'],)
    ) is not None:
        error = "You've already reported that answer."
    else:
        db.execute(
            'INSERT INTO report (user_id, answer_id) VALUES'
            ' (?, ?)',
            (g.user['user_id'], answerId)
        )
        error = "Answer has been reported."

        # TODO: does this work?
        num_reports = db.execute(
            'SELECT COUNT(answer_id) as num_reports'
            ' FROM report'
            ' WHERE answer_id = ?'
            ' GROUP BY answer_id',
            (answerId,)
        )['num_reports']

        if num_reports >= 10:
            db.execute(
                'DELETE FROM answer'
                ' WHERE answer_id = ?',
                (answerId,)
            )

            db.execute(
                'DELETE FROM report'
                ' WHERE answer_id = ?',
                (answerId,)
            )
            error = "Reported answer has been removed."

    if error is not None:
        flash(error)
    
    db.commit()
    return redirect(url_for('question.index'))