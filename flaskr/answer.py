from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db

# answer.answer_id -> [question.question_id, question.text]
# Accesses the question data associated with an Answer ID
def get_question(db, answerId):
    question = db.execute(
        'SELECT q.question_id, q.text'
        ' FROM question q JOIN answer a on(q.question_id = a.question_id)'
        ' WHERE a.answer_id = ?',
        (answerId,)
    ).fetchone()

# question.question_id -> [answer_id, answer.text, num_respondents]
# retrieves all of the answers to a given question id
def get_question_answers(db, questionId):
    return db.execute(
        'SELECT a.answer_id as answer_id, a.text, COUNT(c.answer_id) as num_respondents'
        ' FROM answer a JOIN choose c on(a.answer_id = c.answer_id)'
        ' WHERE a.question_id = ?'
        ' GROUP BY c.answer_id',
        (questionId,)
    ).fetchall()

# question.question_id -> Number
# counts all of the answers associated with a given question
def count_answers(db, questionId):
    return db.execute(
        'SELECT COUNT(c.user_id) as answer_count'
        ' FROM answer a JOIN choose c on(a.answer_id == c.answer_id)'
        ' WHERE a.question_id == ?'
        ' GROUP BY a.answer_id',
        (questionId,)
    ).fetchone()['answer_count']

# answer.answer_id -> Number
# counts the number of times this answer was chosen
def times_answer_chosen(db, answerId):
    return db.execute(
        'SELECT COUNT(user_id) as count'
        ' FROM choose'
        ' WHERE answer_id = ?',
        (answerId,)
    ).fetchone()['count']

# answer.answer_id, demographic -> [demographic, num_responses, num_chose, percent_chose, answer_selected]
# computes user statistics by demographic information for some answer and chosen demographic
def get_demographic_info(answerId, demographic):
    db = get_db()
    num_responses = times_answer_chosen(db, answerId)
    if demographic in ["gender", "income", "party", "geography"]:
        return db.execute(
            'SELECT {} as demographic, ? as num_responses, COUNT(c.user_id) as num_chose, ((COUNT(c.user_id) * 100) / ?) as percent_chose, ? as answer_selected'.format(demographic) +
            ' FROM choose c JOIN user u on(c.user_id = u.user_id)'
            ' WHERE answer_id = ?'
            ' GROUP BY gender'
            ' ORDER BY gender',
            (num_responses, num_responses, answerId, answerId)
        ).fetchall()
    else:
        return None

# question.question_id, answer.answer_text -> Boolean
# determines whether a question has a duplicate answer in the database
def has_duplicate_answer(db, questionId, answer_text):
    return db.execute(
        'SELECT *'
        ' FROM answer'
        ' WHERE answer.question_id = ? AND answer.text LIKE ?;',
        (questionId, answer_text,)
    ).fetchone() != None

# answer.answer_id -> Boolean
# determines whether the current user has already voted for an answer
def has_duplicate_vote(db, answer_id):
    return db.execute(
        'SELECT *'
        ' FROM choose'
        '  WHERE answer_id == ? AND user_id == ?',
        (answer_id, g.user['user_id'])).fetchall() != None


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
