import os
from flask import Flask

def create_app(test_config=None):
    # creates the flask instance
    #name: name of current python module
    # config: tells us config is relative to instance folder
    app = Flask(__name__, instance_relative_config=True)

    # secret key: keeps db data safe

    #database, sqllite database path
    app.config.from_mapping(
        SECRET_KEY='dev',
        # TODO: db path: how to replace with mysql??
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )

    if test_config is None:
        # imports config from config.py file
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    #ensures app.instance_path exists for db to be made
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # creates a route for the app  
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import question
    app.register_blueprint(question.bp)
    app.add_url_rule('/', endpoint='index')

    from . import choose
    app.register_blueprint(choose.bp)

    from . import answer
    app.register_blueprint(answer.bp)

    return app