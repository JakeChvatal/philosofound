import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

# g : unique object for every request

def get_db():
    if 'db' not in g:
        # connects to file pointed at by DATABASE
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # returns a row (like a dict) - can now access cols by name
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # opens file relative to flaskr package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# defines command like command that calls the function it decorates
@click.command('init-db')
@with_appcontext
def init_db_command():
    # clears db and creates new tables
    init_db()
    click.echo('Database has been initialized.')

def init_app(app):
    # calls close_db when app is torn down; cleaning up
    app.teardown_appcontext(close_db)
    # adds command to be called with flask
    app.cli.add_command(init_db_command)