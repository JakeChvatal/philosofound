from flask import Flask, render_template, request
from flaskr.__init__ import create_app
import os
from flask import Flask
import flaskr
# creates the flask instance
#name: name of current python module
# config: tells us config is relative to instance folder

app = create_app()
app.run()
'''app = Flask(__name__, instance_relative_config=True)

# secret key: keeps db data safe

#database, sqllite database path
app.config.from_mapping(
    SECRET_KEY='dev',
    # TODO: db path: how to replace with mysql??
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
)

#ensures app.instance_path exists for db to be made
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# creates a route for the app  
from flaskr import db
db.init_app(app)

from flaskr import auth
app.register_blueprint(auth.bp)

from flaskr import question
app.register_blueprint(question.bp)
app.add_url_rule('/', endpoint='index')

from flaskr import choose
app.register_blueprint(choose.bp)

from flaskr import answer
app.register_blueprint(answer.bp)

from flaskr import report
app.register_blueprint(report.bp)

from flaskr import profile
app.register_blueprint(profile.bp)

app.run()'''