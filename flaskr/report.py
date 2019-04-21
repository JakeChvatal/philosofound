from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('report', __name__)

# allows the user to report an answer
# TODO: remove everything because of foreign key constraints
@bp.route('/<int:answerId>/report', methods=('POST',))
@login_required
def report(answerId):
    db = get_db()
    error = None

    # if the answer has already been reported by the current user:
    if db.execute(
        'SELECT *'
        ' FROM report'
        ' WHERE user_id = ? AND answer_id = ?',
        (g.user['user_id'], answerId)
    ).fetchone() is not None:
        error = "You've already reported that answer."
    else:
        # if the answer has not been reported by the current user, add a report
        db.execute(
            'INSERT INTO report (user_id, answer_id) VALUES'
            ' (?, ?)',
            (g.user['user_id'], answerId)
        )
        error = "Answer has been reported."

        # TODO: does this work?
        # if the number of reports for a given answer is > 10, delete the answer
        # in the future we will have an administrative body able to log in and view
        # answers with certain numbers of reports and manually determine whether answers should be removed
        num_reports = db.execute(
            'SELECT COUNT(answer_id) as num_reports'
            ' FROM report'
            ' WHERE answer_id = ?'
            ' GROUP BY answer_id',
            (answerId,)
        ).fetchone()['num_reports']

        # if the number of reports is high enough, the answer is removed and the report is removed
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