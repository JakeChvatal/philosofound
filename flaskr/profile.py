from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.queries import get_question, get_question_answers, count_answers, get_demographic_info, has_duplicate_answer, has_duplicate_vote, create_answer

bp = Blueprint('profile', __name__)
# provides a way to view the current user's profile with all of their questions and answers
@login_required
@bp.route('/profile/<int:user_id>', methods = ('POST','GET'))
def index(user_id):
    db = get_db()
    
    questions = db.execute(
        'SELECT *'
        ' FROM question'
        ' WHERE author_id = ?',
        (user_id,)
    )

    answers = db.execute(
        'SELECT q.text as question_text, q.question_id, a.text as answer_text, a.answer_id'
        ' FROM answer a JOIN question q on(a.question_id = q.question_id)'
        ' WHERE a.author_id = ?',
        (user_id,)
    )
    
    return render_template('profile/index.html', questions = questions, answers = answers)
