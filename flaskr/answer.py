from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.queries import get_question, get_question_answers, count_answers, get_demographic_info, has_duplicate_answer, has_duplicate_vote

bp = Blueprint('answer', __name__)
# accepts a chosen answer, retrieving all of the associated questions and answers for it
@bp.route('/<int:chosen_answer>', methods = ('POST','GET'))
@login_required
def index(chosen_answer):
    db = get_db()
    demographic_info = None
    
    question = get_question(chosen_answer)
    question_id = question['question_id']
    answers = get_question_answers(question_id)
    answer_count = count_answers(question_id)
    
    db.commit()

    return render_template('answer/index.html', question = question, answers = answers, demographic_info = demographic_info, answer_count = answer_count)


@bp.route('/<int:chosen_answer>/reload', methods = ('POST','GET'))
@login_required
def index_reloaded(chosen_answer):
    db = get_db()
    
    question = get_question(chosen_answer)
    answers = get_question_answers(question['question_id'])
    answer_count = count_answers(question['question_id'])

    demographic = None
    demographic_info = None
    
    try:
        demographic = request.form[str(chosen_answer)]
    except:
        demographic = None

    if demographic is not None and demographic != "Choose an option...":
       demographic_info = get_demographic_info(chosen_answer, demographic)

    return render_template('answer/index.html', question = question, answers = answers, demographic = demographic, demographic_info = demographic_info, answer_count = answer_count)


@bp.route('/<int:questionId>/createAnswer', methods=('POST',))
@login_required
def create(questionId):
    answer_text = request.form['answer_text']
    db = get_db()
    error = None
    
    # error message displayed if a question is not supplied
    if not answer_text:
        error = 'Answer is required.'

    # error message displayed if a very similar answer already exists in the db 
    if has_duplicate_answer(db, questionId, answer_text):
        error = "This answer already exists for this question! Your vote has been registered for that answer."
    # if no error, adds an answer to the database
    else:
        # creates a new answer
        db.execute(
            'INSERT INTO answer (text, question_id, author_id)'
            ' VALUES (?, ?, ?)',
            (answer_text, questionId, g.user['user_id'])
        )

    if error is not None:
        flash(error)

    answer_id = db.execute(
        'SELECT answer.answer_id'
        ' FROM answer'
        ' WHERE answer.text = ? AND answer.question_id = ?',
        (answer_text, questionId)
    ).fetchone()['answer_id']

    if not has_duplicate_vote(db, answer_id):
        # user automatically chooses an answer they create
        db.execute(
            'INSERT INTO choose (user_id, answer_id)'
            ' VALUES (?, ?)',
            (g.user['user_id'], answer_id)
        )

    question = get_question(db, answer_id)
    answers = get_question_answers(db, question['question_id'])
    
    db.commit()

    return render_template('answer/index.html', question = question, answers = answers, demographic_info = None)
