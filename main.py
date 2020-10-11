# IMPORTS
import json
import flask_login
import pymysql
from flask import (flash, has_request_context, jsonify,
                   redirect, render_template, request)
# arquivos
from app import app
from banco import mysql
from nbis import identify, mindtct_from_image

# ROUTES ------------------------------------------
# render
@app.route('/')
def render_login(text=""):
    return render_template("login.html", message=text)
@app.route('/register')
def render_register():
    return render_template("register.html")

# api
@app.route('/add', methods=['GET', 'POST'])
def add_pessoa():
    try:
        if request.method == 'POST':
            _json = request.json

            _nome = _json['nome']
            _digital = _json['digital']
            _nivel_acesso = _json['nivel_acesso']

            if(_nome):
                response_search = searchByName(_nome)
                if(response_search.status_code == 404):
                    sqlQuery = 'insert into pessoa(nome,digital,nivel_acesso) values(%s,%s,%s)'
                    #_digital = mindtct_from_image(_digital)
                    bindData = (_nome, _digital, _nivel_acesso)
                    cursor, conn = sqlCmdCommit(sqlQuery, bindData)
                    response = resposta("Usuário Criado!")
                    return response
                else:
                    response = jsonify('Nome já existe')
                    response.status_code = 405
                    return response
            else:
                return not_found()
        else:
            print(request)
    except Exception as e:
        print(e)
    finally:
        try:
            closeConnection(cursor, conn)
        except Exception as ex:
            print(ex)
@app.route('/search')
def search():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * from pessoa')
        conn.commit()
        rows = cursor.fetchall()
        response = jsonify(rows)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
    finally:
        closeConnection(cursor, conn)
@app.route('/login', methods=['POST'])
def login():
    try:
        if(has_request_context()):
            if(request.method == "POST" and request.form['nome'] and request.form['digital']):
                _nome = request.form['nome']
                _digital = "./fingers/"+request.form['digital']
                cursor, conn = sqlCmd(
                    'SELECT * from pessoa where nome=%s', _nome)
                account = cursor.fetchone()
                mindtct_from_image(account["digital"], "./banco/")
                if identify(mindtct_from_image(_digital, "./")):
                    if(account['nivel_acesso'] < 3):
                        return render_login('Boa filho de uma égua, agora se fode ai')
                    else:
                        return render_template("users.html")
                else:
                    return render_login('Nome de usuário ou digital incorretos')
    except:
        return render_login('Nome de usuário ou digital incorretos!')
@app.route('/get-info/<int:nivel_acesso>')
def getInfos(nivel_acesso):
    try:
        cursor, conn = sqlCmd(
            'SELECT * from info where nivel_acesso=%s', nivel_acesso)
        rows = cursor.fetchall()
        response = jsonify(rows)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
    finally:
        closeConnection(cursor, conn)
@app.route('/search/<int:id>')
def searchById(id):
    try:
        sqlCommand = 'SELECT * from pessoa where id=%s'
        bindCommand = id
        cursor, conn = sqlCmd(sqlCommand, bindCommand)
        rows = cursor.fetchone()
        if(rows == None):
            return not_found
        response = jsonify(rows)
        # with open("digital_busca.xyt", "w") as fxyt:
        #    fxyt.write(rows['digital'])
        # identify("digital_busca.xyt")
        response.status_code = 200
        return response
    except:
        return not_found()
    finally:
        closeConnection(cursor, conn)
# ta errado essa porra
@app.route('/update', methods=['PUT'])
def update():
    try:
        _json = request.json
        _id = _json['id']
        _nome = _json['nome']
        _digital = _json['digital']
        _nivel_acesso = _json['nivel_acesso']

        if _nome and _digital and _nivel_acesso and _id and request.method == 'PUT':
            sqlQuery = "UPDATE pessoa SET nome=%s, digital=%s, nivel_acesso=%s WHERE id=%s"
            bindData = (_nome, _digital, _nivel_acesso, _id,)
            cursor, conn = sqlCmdCommit(sqlQuery, bindData)
            response = resposta('Pessoa atualizada!')
            return response
        else:
            return not_found()
    except Exception as e:
        print(e)
        return not_found()
    finally:
        closeConnection(cursor, conn)
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        cursor, conn = sqlCmdCommit("DELETE FROM pessoa WHERE id=%s", id)
        response = resposta('Pessoa Deletada!')
        return response
    except Exception as ex:
        print(ex)
        return not_found()
    finally:
        closeConnection(cursor, conn)

# error
@app.errorhandler(405)
def not_allowed(error=None):
    return render_login()
@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': "Not found" + request.url
    }
    response = jsonify(message)
    response.status_code = 404
    return response

# FUNCTIONS ------------------------------------------
def resposta(text):
    response = jsonify(text)
    response.status_code = 200
    return response
def closeConnection(cursor, conn):
    cursor.close()
    conn.close()
def sqlCmdCommit(sqlQuery, bindData):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sqlQuery, bindData)
    conn.commit()
    return cursor, conn
def sqlCmd(sqlCommand, bindCommand):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sqlCommand, bindCommand)
    return cursor, conn
def searchByName(name):
    try:
        cursor, conn = sqlCmd('SELECT * from pessoa where nome=%s', name)
        rows = cursor.fetchone()
        if(rows == None):
            message = {
                'status': 404,
                'message': "Not found"
            }
            response = jsonify(message)
            response.status_code = 404
            return response
        response = jsonify(rows)
        # with open("digital_busca.xyt", "w") as fxyt:
        #    fxyt.write(rows['digital'])
        # identify("digital_busca.xyt")
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
        return not_found()
    finally:
        closeConnection(cursor, conn)


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True)
