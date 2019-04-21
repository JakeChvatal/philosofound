from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('answer', __name__)
@bp.route('/<int:chosen_answer>', methods = ('POST','GET'))
@login_required
def index(chosen_answer):
    db = get_db()
    demographic_info = None
    
    question = db.execute(
        'SELECT q.question_id, q.text'
        ' FROM question q JOIN answer a on(q.question_id = a.question_id)'
        ' WHERE a.answer_id = ?',
        (chosen_answer,)
    ).fetchone()

    answers = db.execute(
        'SELECT a.answer_id, a.text'
        ' FROM answer a'
        ' WHERE a.question_id = ?;',
        (question['question_id'],)
    )

    return render_template('answer/index.html', question = question, answers = answers, demographic_info = demographic_info)

@bp.route('/<int:chosen_answer>/reload', methods = ('POST','GET'))
@login_required
def index_reloaded(chosen_answer):
    db = get_db()
    demographic_info = None
    
    question = db.execute(
        'SELECT q.question_id, q.text'
        ' FROM question q JOIN answer a on(q.question_id = a.question_id)'
        ' WHERE a.answer_id = ?',
        (chosen_answer,)
    ).fetchone()

    answers = db.execute(
        'SELECT a.answer_id, a.text'
        ' FROM answer a'
        ' WHERE a.question_id = ?;',
        (question['question_id'],)
    )

    demographic = request.form[str(chosen_answer)]
    
    if demographic is not None and demographic != "Choose an option...":
       demographic_info = get_demographic_info(chosen_answer, demographic)

    return render_template('answer/index.html', question = question, answers = answers, demographic = demographic, demographic_info = demographic_info)


def get_demographic_info(answerId, demographic):
    db = get_db()
    
    num_responses = db.execute(
        'SELECT COUNT(user_id) as count'
        ' FROM choose'
        ' WHERE answer_id = ?',
        (answerId,)
    ).fetchone()['count']

    if demographic == "gender":
        return db.execute(
            'SELECT gender as demographic, ? as num_responses, COUNT(c.user_id) as num_chose, ((COUNT(c.user_id) * 100) / ?) as percent_chose, ? as answer_selected'
            ' FROM choose c JOIN user u on(c.user_id = u.user_id)'
            ' WHERE answer_id = ?'
            ' GROUP BY ?'
            ' ORDER BY ?',
            (num_responses, num_responses, answerId, answerId, demographic, demographic)
        ).fetchall()
    elif demographic == "income":
        return db.execute(
            'SELECT income as demographic, ? as num_responses, COUNT(c.user_id) as num_chose, ((COUNT(c.user_id) * 100) / ?) as percent_chose, ? as answer_selected'
            ' FROM choose c JOIN user u on(c.user_id = u.user_id)'
            ' WHERE answer_id = ?'
            ' GROUP BY ?'
            ' ORDER BY ?',
            (num_responses, num_responses, answerId, answerId, demographic, demographic)
        ).fetchall()
    elif demographic == "party":
        return db.execute(
            'SELECT party as demographic, ? as num_responses, COUNT(c.user_id) as num_chose, ((COUNT(c.user_id) * 100) / ?) as percent_chose, ? as answer_selected'
            ' FROM choose c JOIN user u on(c.user_id = u.user_id)'
            ' WHERE answer_id = ?'
            ' GROUP BY ?'
            ' ORDER BY ?',
            (num_responses, num_responses, answerId, answerId, demographic, demographic)
        ).fetchall()
    elif demographic == "geography":
        return db.execute(
            'SELECT geography as demographic, ? as num_responses, COUNT(c.user_id) as num_chose, ((COUNT(c.user_id) * 100) / ?) as percent_chose, ? as answer_selected'
            ' FROM choose c JOIN user u on(c.user_id = u.user_id)'
            ' WHERE answer_id = ?'
            ' GROUP BY ?'
            ' ORDER BY ?',
            (num_responses, num_responses, answerId, answerId, demographic, demographic)
        ).fetchall()
    else:
        return None

@bp.route('/<int:questionId>/createAnswer', methods=('POST',))
@login_required
def create(questionId):
    answer_text = request.form['answer_text']
    error = None
    db = get_db()
    
    question = None
    answers = None
    

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

        question = db.execute(
            'SELECT q.question_id, q.text'
            ' FROM question q JOIN answer a on(q.question_id = a.question_id)'
            ' WHERE a.answer_id = ?',
            (answer_id,)
        ).fetchone()

        answers = db.execute(
            'SELECT a.answer_id, a.text'
            ' FROM answer a'
            ' WHERE a.question_id = ?;',
            (question['question_id'],)
        ).fetchall()
        
        db.commit()

    return render_template('answer/index.html', question = question, answers = answers)
