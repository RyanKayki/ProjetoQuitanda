from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import uuid


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
    conexao = sql.connect("db_quitanda.db")
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
    produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
    if verifica_sessao():    
        login = True
    else:
        login = False
    return render_template("home.html", produtos=produtos,login=login)


@app.route("/cadprodutos")
def cadprodutos():
    if verifica_sessao():
        title = "Cadastro de produtos"
        return render_template("cadastro.html",title=title)
    else:
        return redirect("/login")

@app.route('/index')
def indexx():
    return render_template("index.html")

@app.route("/cadastro",methods=["post"])
def cadastro():
	if verifica_sessao():
		nome_prod=request.form['nome_prod']
		desc_prod=request.form['desc_prod']
		preco_prod=request.form['preco_prod']
		img_prod=request.files['img_prod']
		id_foto=str(uuid.uuid4().hex)
		filename=id_foto+nome_prod+'.png'
		img_prod.save("static/img/produtos/"+filename )
		conexao = conecta_database()
		conexao.execute('INSERT INTO produtos (nome_prod, desc_prod, preco_prod,img_prod) VALUES (?, ?, ?, ?)', (nome_prod, desc_prod, preco_prod, filename))
		conexao.commit()
		conexao.close()
		return redirect("/adm")
	else:
		return redirect("/login")

@app.route ("/adm")
def adm():
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute( 'SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
        conexao.close()
        title = "Administração"
        return render_template("adm.html" , produtos=produtos , title=title)
    else:
        return redirect("/login")
    
@app.route('/excluir/<id>')
def excluir(id):
    if verifica_sessao():
        id = int(id)
        conexao = conecta_database()
        conexao.execute('DELETE FROM produtos WHERE id_prod = ?',(id,))
        conexao.commit()
        conexao.close()
        return redirect('/adm')
    else:
        return redirect ("/login")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route("/acesso", methods=['post'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha == senha_informada:

        session["login"] = True
        return redirect('/adm')
    else:
        return render_template("login.html",msg="Usuário/Senha estão incorretos!")

@app.route("/logout")
def logout():
    global login
    login = False
    session.clear()
    return redirect("/")

def excluir(id):
    conexao = conecta_database()
    conexao.execute('DELETE FROM produtos WHERE id = ?',(id))
    conexao.commit()
    conexao.close()
    return redirect('/')

@app.route("/editprodutos/<id_prod>")
def editar(id_prod):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos WHERE id_prod = ?',(id_prod,)).fetchall()
        conexao.close()
        title = "Edição De Produtos"
        return render_template("editprodutos.html", produtos=produtos, title=title)
    else:
        return redirect ("/login")

@app.route("/editarprodutos", methods=['POST'])
def editpost():
    id_prod = request.form['id_prod']
    nome_prod = request.form['nome_prod']
    desc_prod = request.form['desc_prod']
    preco_prod = request.form['preco_prod']
    img_prod = request.files['img_prod']
    id_foto=str(uuid.uuid4().hex)
    filename =id_foto+nome_prod+'.png'
    img_prod.save("/static/img/produto/"+filename)
    conexao = conecta_database()
    conexao.execute('UPDATE produtos SET nome_prod = ?, desc_prod = ?, preco_prod = ?, img_prod = ? WHERE id_prod = ?',(nome_prod,desc_prod,preco_prod,filename,id_prod))  
    conexao.commit()
    conexao.close()
    return redirect('/adm')

@app.route("/busca", methods=["post"])
def busca():
    busca = request.form['buscar']
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos WHERE nome_prod LIKE "%" || ? || "%"',(busca,)).fetchall()
    title = "Home"
    return render_template("home.html", produtos=produtos, title=title)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
