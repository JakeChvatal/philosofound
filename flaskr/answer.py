from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('answer', __name__)
@bp.route('/<int:questionId>', methods = ('POST','GET'))
@login_required
def index(questionId):
    db = get_db()
    demographic = request.form['demographic']
    demographic_info = None
    
    chosen_answer = db.execute(
        'SELECT a.answer_id'
        ' FROM answer a JOIN choose c on(a.answer_id = c.answer_id)'
        ' WHERE a.question_id = ? AND c.user_id = ?',
        (questionId, g.user['user_id'])
    ).fetchone()['answer_id']

    question = db.execute(
        'SELECT *'
        ' from question'
        ' WHERE question_id = ?',
        (questionId,)
    ).fetchone()

    answers = db.execute(
        'SELECT a.answer_id, a.text'
        ' FROM answer a'
        ' WHERE a.question_id = ?;',
        (question['question_id'],)
    )
    
    if demographic is not None and demographic != "Choose an option...":
        demographic_info = get_demographic_info(chosen_answer, demographic)

    return render_template('answer/index.html', question = question, answers = answers, demographic_info = demographic_info)

def get_demographic_info(answerId, demographic):
    db = get_db()
    
    num_responses = db.execute(
        'SELECT COUNT(user_id) as count'
        ' FROM choose'
        ' WHERE answer_id = ?',
        (answerId,)
    ).fetchone()['count']

    return db.execute(
        'SELECT ?, ?, COUNT(c.user_id) as num_chose, ((COUNT(c.user_id) * 100) / ?) as percent_chose'
        ' FROM choose c JOIN user u on(c.user_id = u.user_id)'
        ' WHERE answer_id = ?'
        ' GROUP BY ?'
        ' ORDER BY ?',
        (demographic, num_responses, num_responses, answerId, demographic, demographic)
    ).fetchall()

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
        error = "This answer already exists for this question! Vote for that answer."

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
    return redirect(url_for('answer.index'))