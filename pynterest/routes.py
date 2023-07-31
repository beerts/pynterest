# criar as rotas do nosso site (os links)
from flask import render_template, url_for, redirect
from pynterest import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from pynterest.forms import FormLogin, FormCriarConta, FormFoto
from pynterest.models import Usuario, Foto
import os
from werkzeug.utils import  secure_filename

@app.route("/", methods=["GET", "POST"])
def homepage():
    formlogin = FormLogin() # formulário de login
    if formlogin.validate_on_submit():
        usuario = Usuario.query.filter_by(email=formlogin.email.data).first() #confirmando se o email do usuario coincide com o banco de dados
        if usuario and bcrypt.check_password_hash(usuario.senha, formlogin.senha.data): # confirmando se a senha coincide com a criptografada e a colocada no login
            login_user(usuario) # logando o usuario no perfil
            return redirect(url_for("perfil", id_usuario=usuario.id)) #redirecionando o usuario para o perfil

    return render_template("homepage.html", form=formlogin)

@app.route("/criar_conta", methods=["GET", "POST"])
def criarconta():  # criando a conta do usuario
    formcriarconta = FormCriarConta() # formulario de criar conta
    if formcriarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(formcriarconta.senha.data) # criptografando a senha da conta criada
        usuario = Usuario(nome=formcriarconta.nome.data,
                          senha=senha,
                          email=formcriarconta.email.data)
        database.session.add(usuario) # adicionando o usuario no banco de dados
        database.session.commit()
        login_user(usuario, remember=True) # fazendo login quando cria a conta direto
        return redirect(url_for("perfil", id_usuario=usuario.id)) # redirecionando para o perfil quando cria conta
    return render_template("criarconta.html", form=formcriarconta) # carregando o template de criar conta


@app.route("/perfil/<id_usuario>", methods=["GET","POST"]) #perfil o usuario
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id): # se o id do usuario for o mesmo do banco de dados
        form_foto = FormFoto()
        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro = secure_filename(arquivo.filename)

            # salvar arquivo na pasta foto post
            caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              app.config["UPLOAD_FOLDER"], nome_seguro)

            arquivo.save(caminho)

            # registrar arquivo no banco de dados
            foto = Foto(imagem=nome_seguro, id_usuario=current_user.id)
            database.session.add(foto)
            database.session.commit()

        return render_template("perfil.html", usuario=current_user, form=form_foto) # ele tem acesso ao perfil dele
    else:
        usuario = Usuario.query.get(int(id_usuario)) # caso contrario ele pode apenas visualizar outros perfis
        return render_template("perfil.html", usuario=usuario, form=None) # carregando o perfil html


@app.route("/logout") #fazendo logout e nao deixando conectar na conta através da url
@login_required
def logout():
    logout_user() # deslogando o usuario
    return redirect(url_for("homepage"))


@app.route("/feed")
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.data_criacao).all()
    return render_template("feed.html", fotos=fotos )