from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.queries import get_question, get_question_answers, count_answers, get_demographic_info, has_duplicate_answer, has_duplicate_vote, create_answer

bp = Blueprint('answer', __name__)
# accepts a chosen answer, retrieving all of the associated questions and answers for it
@bp.route('/<int:chosen_answer>', methods = ('POST','GET'))
@login_required
def index(chosen_answer):
    db = get_db()
    
    #question = get_question(db, chosen_answer)
    #answers = get_question_answers(db, question['question_id'])
    #answer_count = count_answers(db, question['question_id'])

    demographic = None
    demographic_info = None
    db = get_db()
    demographic_info = None
    
    question = db.execute(
        'SELECT q.question_id, q.text'
        ' FROM question q JOIN answer a on(q.question_id = a.question_id)'
        ' WHERE a.answer_id = ?',
        (chosen_answer,)
    ).fetchone()

    answers = db.execute(
        'SELECT a.answer_id as answer_id, a.text, COUNT(c.answer_id) as num_respondents'
        ' FROM answer a JOIN choose c on(a.answer_id = c.answer_id)'
        ' WHERE a.question_id = ?'
        ' GROUP BY c.answer_id',
        (question['question_id'],)
    ).fetchall()

    answer_count = db.execute(
        'SELECT COUNT(c.user_id) as answer_count'
        ' FROM answer a JOIN choose c on(a.answer_id == c.answer_id)'
        ' WHERE a.question_id == ?'
        ' GROUP BY a.answer_id',
        (question['question_id'],)
    ).fetchone()['answer_count']

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
    #elif has_duplicate_answer(db, questionId, answer_text):
    #    error = "This answer already exists for this question! Your vote has been registered for that answer."
    duplicate_answer = db.execute(
        'SELECT *'
        ' FROM answer'
        ' WHERE answer.question_id = ? AND answer.text = ?;',
        (questionId, answer_text,)
    ).fetchone()

    if duplicate_answer is not None:
        error = "This answer already exists for this question! Your vote has been registered for that answer."
    # if no error, adds an answer to the database
    else:
        #answer_id = create_answer(db, questionId, g.user['user_id'], answer_text)    
        #question = get_question(db, answer_id)
        #answers = get_question_answers(db, question['question_id'], g.user['user_id'])
        
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

    if db.execute(
        'SELECT *'
        ' FROM choose'
        '  WHERE answer_id == ? AND user_id == ?',
        (answer_id, g.user['user_id'])
    ) is not None:
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

    return render_template('answer/index.html', question = question, answers = answers, demographic_info = None)
