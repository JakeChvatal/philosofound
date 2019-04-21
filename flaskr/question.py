from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.queries import has_duplicate_question, get_question_answers, create_answer, create_question

import random

bp = Blueprint('question', __name__)
# gets an initial question page with a random question; the main view of our website
@bp.route('/')
@login_required
def index():
    db = get_db()

    # gets all of the questions a user hasn't answered yet
    questions = db.execute(
        'SELECT question.question_id, question.text'
        ' FROM question'
        ' WHERE question.question_id NOT IN'
        ' (SELECT q.question_id FROM question q join answer a on(q.question_id = a.question_id)'
        ' join choose c on (a.answer_id = c.answer_id)'
        ' WHERE c.user_id = ?);',
        (g.user['user_id'],)
    ).fetchall()

    question = None
    answers = None
    # gets random question if possible
    if questions != None and len(questions) != 0:
        question = questions[random.randint(0, len(questions) - 1)]
        answers = get_question_answers(db, question['question_id'], g.user['user_id'])

    return render_template('questions/index.html', question = question, answers = answers)

# allows the user to create a question by bringing up a create page and allowing submissions
# notable that the user creating the question is also required to provide an answer to the question
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        question_text = request.form['question_text']
        answer_text = request.form['answer_text']
        error = None
        db = get_db()

        # errors if a question is not supplied or if question already exists
        if not question_text:
            error = 'Question is required.'

        if not answer_text:
            error = 'Answer is required.'

        if has_duplicate_question(db, question_text):
            error = "This question has already been asked by another user."

        if error is not None:
            flash(error)

        # if no error, adds a question to the database
        else:
            question_id = create_question(db, question_text, g.user['user_id'])
            # if the question id was found, create an answer with it
            create_answer(db, question_id, g.user['user_id'], answer_text)
            db.commit()

            return redirect(url_for('question.index'))

    return render_template('questions/create.html')