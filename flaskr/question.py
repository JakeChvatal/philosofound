from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import random

bp = Blueprint('question', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    # gets the questions a user hasn't answered yet
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

    if questions != None and len(questions) != 0:
        # gets random question
        question = questions[random.randint(0, len(questions) - 1)]

        answers = db.execute(
            'SELECT a.answer_id, a.text'
            ' FROM answer a'
            ' WHERE a.question_id = ?;',
            (question['question_id'],)
        )

    return render_template('questions/index.html', question = question, answers = answers)

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

        duplicate_question = db.execute(
            'SELECT *'
            ' FROM question'
            ' WHERE question.text = ?',
            (question_text,)
        ).fetchone()

        if duplicate_question is not None:
            error = "This question has already been asked by another user."

        if error is not None:
            flash(error)

        # if no error, adds a question to the database
        else:
            db.execute(
                'INSERT INTO question (text, author_id)'
                ' VALUES (?, ?)',
                (question_text, g.user['user_id']),
            )

            #TODO: see if we can do better
            # gets the id of the just-generated question
            question_id = db.execute(
                'SELECT question.question_id'
                ' FROM question'
                ' WHERE question.text = ?',
                (question_text,)
            ).fetchone()['question_id']

            # if the question id was found, create an answer with it
            if question_id is not None:
                db.execute(
                    'INSERT INTO answer (text, question_id, author_id)'
                    ' VALUES (?, ?, ?)',
                    (answer_text, question_id, g.user['user_id']),
                )

                print("added an answer to the database")

                answer_id = db.execute(
                    'SELECT answer.answer_id'
                    ' FROM answer'
                    ' WHERE answer.text = ? AND answer.question_id = ?',
                    (answer_text, question_id)
                ).fetchone()['answer_id']

                # user automatically chooses an answer they create
                db.execute(
                    'INSERT INTO choose (user_id, answer_id)'
                    ' VALUES (?, ?)',
                    (g.user['user_id'], answer_id)
                )

                db.commit()
            else:
                print("could not find a question id")
            
            return redirect(url_for('question.index'))

    return render_template('questions/create.html')
