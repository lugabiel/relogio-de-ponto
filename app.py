from flask import Flask, Response, request, render_template
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json

# from flask_marshmallow import Marshmallow
from flask.wrappers import Response
from markupsafe import escape
import git


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:gato.preto@localhost/relogiodeponto'


db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))
    cpf = db.Column(db.String(50))
    dataCadastro = db.Column(db.String(10))
    mail = db.Column(db.String(100))
    def to_json(self):
        return {"id": self.id, "nome": self.nome,"cpf": self.cpf,"data de cadastro": self.dataCadastro,"e-mail": self.mail }


# Lista todos usuário
@app.route("/usuarios",methods=["GET"])
def listar_usuarios():
    obj_usuarios = Usuario.query.all()
    json_usuarios = [usuario.to_json() for usuario in obj_usuarios]
    return gera_response(200,"usuarios",json_usuarios,"ok")

def gera_response(status, nome_dado, conteudo, mensagem=False):
    body = {}
    body[nome_dado] = conteudo
    if(mensagem):
        body["mensagem"] = mensagem
    return Response(json.dumps(body),status=status, mimetype="application/json")
#app.run()
# CRUD 
# Select *
# Select 1
# ADD
# Update
# Delete

# rota para integração contínua (github + pythonanywhere)
@app.route('/git_update', methods = ['POST'])
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