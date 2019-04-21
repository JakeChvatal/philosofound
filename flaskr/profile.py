from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.queries import get_question, get_question_answers, count_answers, get_demographic_info, has_duplicate_answer, has_duplicate_vote, create_answer

bp = Blueprint('answer', __name__)
# accepts a chosen answer, retrieving all of the associated questions and answers for it
@bp.route('/profile/<int:user_id>', methods = ('POST','GET'))
def profile(user_id):
    db = get_db()
    
    questions = db.execute(
        'SELECT *'
        ' FROM question'
        ' WHERE user_id = ?',
        (user_id,)
    )

    answers = db.execute(
        'SELECT q.text, q.id, a.text, a.id'
        ' FROM answer a JOIN question q on(a.question_id = q.question_id)'
        ' WHERE user_id = ?',
        (user_id,)
    )
    
    return render_template('profile/index.html', questions = questions, answers = answers)
