from flask import Flask, render_template, request
from flaskr.__init__ import create_app
import os
from flask import Flask
import flaskr
from flaskr.db import get_db, init_db, init_db_command
import os
# creates the flask instance
#name: name of current python module
# config: tells us config is relative to instance folder

os.environ["FLASK_APP"] = "flaskr"
os.environ["FLASK_ENV"] = "development"

app = create_app()
app.run()