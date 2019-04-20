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
    db.execute(
        'INSERT INTO choose (user_id, answer_id)'
        ' VALUES (?, ?)',
        (g.user['user_id'], answerId)
    )
    db.commit()
    return redirect(url_for('question.index'))