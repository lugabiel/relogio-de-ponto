import re
from flask import Flask, Response, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import mysql.connector
import json

# from flask_marshmallow import Marshmallow
from flask.wrappers import Response
from markupsafe import escape
from datetime import date,datetime
import time
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
        return {"id": self.id, "nome": self.nome,"cpf": self.cpf,"data de cadastro": self.dataCadastro,"mail": self.mail }

class controleDePonto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usu = db.Column(db.Integer)
    data_hora = db.Column(db.String(30))
    entrada_saida = db.Column(db.Boolean)
    def to_json(self):
        return {"id": self.id,"id_usu":self.id_usu,"data_hora": self.data_hora,"entrada_saida": self.entrada_saida}



# Listar todos usuário
@app.route("/usuarios",methods=["GET"])
def listar_usuarios():
    obj_usuarios = Usuario.query.all()
    json_usuarios = [usuario.to_json() for usuario in obj_usuarios]
    return gera_response(200,"usuarios",json_usuarios,"ok")

# Selecionar Usuarios por <id>
@app.route("/usuario/<id>", methods=["GET"])
def selecionar_usuario(id):
    obj_usuarios = Usuario.query.filter_by(id=id).first()
    json_usuarios = obj_usuarios.to_json()
    return gera_response(200,"usuarios",json_usuarios)

# Cadastrar novo usuario
@app.route("/usuario",methods=["POST"])
def criar_usuario():
    body = request.get_json()
    try:
        usu = Usuario(
            nome=body["nome"],
            cpf=body["cpf"],
            mail=body["mail"],
            dataCadastro=str(date.today()))
        db.session.add(usu)
        db.session.commit()
        return gera_response(201,"usuario", usu.to_json(),"Criado com sucesso")
    except Exception as e:
        print('Erro:',e)
        return gera_response(400,"",{},"Erro no cadastro")
        ...

# Atualizar dados de usuario com <id>
@app.route("/usuario/<id>",methods=["PUT"])
def atualizar_usuario(id):
    # get usu by id
    obj_usuario = Usuario.query.filter_by(id=id).first()
    # get novos dados para usu
    body = request.get_json()
    try:
        if('nome' in body):
            obj_usuario.nome = body['nome']
        if('cpf' in body):
            obj_usuario.cpf = body['cpf']
        if('mail' in body):
            obj_usuario.mail = body['mail']
        db.session.add(obj_usuario)
        db.session.commit()
        return gera_response(200,"usuario", obj_usuario.to_json(),"Atualizado com sucesso")
    except Exception as e:
        print('Erro:',e)
        return gera_response(400,"",{},"Erro na atualização")

# Bater o ponto com <id> do usuario
@app.route("/usuario/<id>/ponto",methods=["POST"])
def bater_ponto(id):
    # existe usuario <id>?
    obj_usuario = Usuario.query.filter_by(id=id).first()
    if(obj_usuario != None): # sim
        # usuario <id> ja bateu ponto alguma vez?
        list_obj_ponto = controleDePonto.query.filter_by(id_usu=id).all()
        list_json_ponto = [obj.to_json() for obj in list_obj_ponto]
        obj_ponto = None
        try:
            obj_ponto = list_json_ponto.pop()
            print(obj_ponto)
        except:
            ...
        if (obj_ponto != None): # sim
            try:
                # bate ponto (de entrada ou saída)
                pt = controleDePonto(
                    id_usu = id,
                    data_hora = str(datetime.now()),
                    entrada_saida = not obj_ponto["entrada_saida"]
                    )
                db.session.add(pt)
                db.session.commit()
                return gera_response(201,"usuario id:", id,"Ponto batido com sucesso")
            except Exception as e:
                print('Erro:',e)
                return gera_response(400,"",{},"Erro na atualização")
        else: # nao
            try:
                # bate primeiro ponto do usuario (ponto de entrada) 
                pt = controleDePonto(
                    id_usu=id,
                    data_hora=str(datetime.now()),
                    entrada_saida = True
                    )
                db.session.add(pt)
                db.session.commit()
                return gera_response(201,"usuario id:", id,"Ponto batido com sucesso")
            except Exception as e:
                print('Erro:',e)
                return gera_response(400,"",{},"Erro ao bater ponto")
    else: # nao
        return gera_response(400,"",{},"Erro ao bater ponto")

# Gera response para todos
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