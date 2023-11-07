from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql


app = Flask(__name__)
app.secret_key = "vendinhaze"

usuario = "ze"
senha = "venda"
login = False

def verifica_sessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False
    

def conecta_database():
    conexao = sql.connect("db_blog.db")
    conexao.row_factory = sql.Row
    return conexao


def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()


@app.route('/')
def index():
    iniciar_db()
    conexao = conecta_database()
    posts = conexao.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conexao.close()
    if verifica_sessao():    
        login = True
    else:
        login = False
    return render_template("home.html", posts=posts,login=login)


@app.route('/novopost')
def novopost():
    if verifica_sessao():
        return render_template("novopost.html")
    else:
        return render_template("login.html")

@app.route('/cadpost', methods=['post'])
def cadpost():
    titulo = request.form['titulo']
    conteudo = request.form['conteudo']
    conexao = conecta_database()
    conexao.execute('INSERT INTO posts (titulo,conteudo) VALUES (?,?)',(titulo,conteudo))
    conexao.commit()
    conexao.close()
    return redirect('/')

@app.route('/excluir/<id>')
def excluir(id):
    conexao = conecta_database()
    conexao.execute('DELETE FROM posts WHERE id = ?',(id))
    conexao.commit()
    conexao.close()
    return redirect('/')

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/acesso', methods=['POST'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informado = request.form["senha"]

    if usuario == usuario_informado and senha == senha_informado:
        session["login"] = True
        return redirect('/')
    else:
        return render_template("login.html", msg="Usuario/Senha estão incorretos")

@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect("/")

def excluir(id):
    conexao = conecta_database()
    conexao.execute('DELETE FROM posts WHERE id = ?',(id))
    conexao.commit()
    conexao.close()
    return redirect('/')

@app.route("/editar/<id>")
def editar(id):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        posts = conexao.execute('SELECT * FROM posts WHERE id = ?',(id,)).fetchall()
        conexao.close()
        return render_template("editar.html", posts=posts)

@app.route("/editpost", methods=['POST'])
def editpost():
    id = request.form['id']
    titulo = request.form['titulo']
    conteudo = request.form['conteudo']
    conexao = conecta_database()
    conexao.execute('UPDATE posts SET titulo = ?, conteudo = ? WHERE id = ?',(titulo,conteudo,id))  
    conexao.commit()
    conexao.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
