from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.queries import get_question, get_question_answers, count_answers, get_demographic_info, has_duplicate_answer, has_duplicate_vote, create_answer

bp = Blueprint('answer', __name__)
# accepts a chosen answer, retrieving all of the associated questions and answers for it
@bp.route('/<int:chosen_answer>', methods = ('POST','GET'))
@login_required
def index(chosen_answer):
    db = get_db()
    
    question = get_question(db, chosen_answer)
    answers = get_question_answers(db, question['question_id'])
    answer_count = count_answers(db, question['question_id'])

    demographic = None
    demographic_info = None
    
    if request.method == 'POST':        
        try:
            demographic = request.form[str(chosen_answer)]
        except:
            demographic = None

        if demographic is not None and demographic != "Choose an option...":
            demographic_info = get_demographic_info(db, chosen_answer, demographic)

    return render_template('answer/index.html', question = question, answers = answers, demographic = demographic, demographic_info = demographic_info, answer_count = answer_count)


@bp.route('/<int:questionId>/create', methods=('POST',))
@login_required
def create(questionId):
    answer_text = request.form['answer_text']
    db = get_db()
    error = None

    question = None
    answers = None
    
    # error message displayed if a question is not supplied
    if not answer_text:
        error = 'Answer is required.'

    # error message displayed if a very similar answer already exists in the db 
    elif has_duplicate_answer(db, questionId, answer_text):
        error = "This answer already exists for this question! Your vote has been registered for that answer."
    
    # if no error, adds an answer to the database
    else:
        answer_id = create_answer(db, questionId, g.user['user_id'], answer_text)    
        question = get_question(db, answer_id)
        answers = get_question_answers(db, question['question_id'], g.user['user_id'])
    if error is not None:
        flash(error)

    db.commit()

    return render_template('answer/index.html', question = question, answers = answers, demographic_info = None)
