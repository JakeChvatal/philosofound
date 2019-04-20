from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import sys

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('question', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    # gets the questions a user hasn't answered yet
    question = db.execute(
        'SELECT q.id, question' # a.id , a.answer'
        ' FROM question q;' # JOIN answer a on a.question_id = q.id ',
        #' WHERE v.user_id NOT LIKE ?' ;;;; JOIN vote v on a.id = v.answer_id;,
        #(g.user['id'],)
    ).fetchone()


    return render_template('questions/index.html', question = question)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        question = request.form['question']
        error = None

        # errors if a question is not supplied
        if not question:
            error = 'Question is required.'
        
        if error is not None:
            flash(error)

        # if no error, adds a question to the database
        else:
            db = get_db()
            db.execute(
                'INSERT INTO question (question, author_id)'
                ' VALUES (?, ?)',
                (question, g.user['id'])
            )
            db.commit()
            return redirect(url_for('question.index'))

    return render_template('questions/create.html')

# gets a question without checking its author?? 
def get_question(id, check_author=True):
    # makes query for post matching user and post id
    question = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if question is None:
        abort(404, "Question id {0} doesn't exist".format(id))
    
    # raises exception, returning http status code
    if check_author and question['author_id'] != g.user['id']:
        abort(403)
    
    return question

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_question(id)
    db = get_db()
    db.execute('DELETE FROM question WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('questions.index'))
