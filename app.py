from flask import Flask, request, render_template
# from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow
from flask.wrappers import Response
from markupsafe import escape
import git


app = Flask(__name__)

# # SQL setup
# connString = "mysql+mysqlconnector://<user>:<password>@<localhost[:3306/klipfolio"
# app.config["SQLALCHEMY_DATABASE_URI"] = connString

@app.route('/git_update', methods = ['GET','POST'])
def git_update():
    repo = git.Repo('./relogio-de-ponto')
    origin = repo.remotes.origin
    repo.create_head('main',
    origin.refs.main).set_tracking_branch(origin.refs.main).checkout()
    origin.pull()
    return '', 200

@app.route('/')
def index():
    return render_template("index.html")