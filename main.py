import pymysql
from app import app
import json
from banco import mysql
from flask import jsonify
from flask import flash, redirect, request, render_template, has_request_context
from nbis import identify
from nbis import mindtct_from_image


@app.route('/')
def render_index(text=""):
    return render_template("index.html", message=text)


@app.route('/add', methods=['GET', 'POST'])
def add_pessoa():
    if request.method == "POST":
        try:
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
                    conn = mysql.connect()
                    cursor = conn.cursor()
                    cursor.execute(sqlQuery, bindData)
                    conn.commit()
                    response = jsonify('Registrado com sucesso!')
                    response.status_code = 200
                    return render_index('Registrado com sucesso!')
                else:
                    response = jsonify('Nome já existe')
                    response.status_code = 404
                    return render_index('Nome já existe')
            else:
                return not_found()
        except Exception as e:
            print(e)
        finally:
            try:
                cursor.close()
                conn.close()
            except Exception as ex:
                print(ex)
    else:
        return redirect('/')

@app.route('/search')
def search():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * from pessoa')
        rows = cursor.fetchall()
        response = jsonify(rows)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/register')
def render_register():
    return redirect("/")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        try:
            if(has_request_context()):
                if(request.method == "POST" and request.form['nome'] and request.form['digital']):
                    _nome = request.form['nome']
                    _digital = "./fingers/"+request.form['digital']
                    conn = mysql.connect()
                    cursor = conn.cursor(pymysql.cursors.DictCursor)
                    cursor.execute('SELECT * from pessoa where nome=%s', _nome)
                    account = cursor.fetchone()
                    mindtct_from_image(account["digital"], "./banco/")
                    if identify(mindtct_from_image(_digital, "./")):
                        if(account['nivel_acesso'] < 3):
                            response = getInfos(account['nivel_acesso'])
                            return render_template("infos.html",infos=response.get_data(as_text=True))
                        else:
                            return render_template("users.html")
                    else:
                        return render_index('Nome de usuário ou digital incorretos')
        except:
            return render_index('Nome de usuário ou digital incorretos!')
    else:
        return redirect("/")


@app.route('/get-info/<int:nivel_acesso>')
def getInfos(nivel_acesso):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            'SELECT * from infos where nivel_acesso=%s order by id desc', nivel_acesso)
        rows = cursor.fetchall()
        response = jsonify(rows)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/search/<int:id>')
def searchById(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * from pessoa where id=%s', id)
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
        cursor.close()
        conn.close()


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
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            response = jsonify('Pessoa updated')
            response.status_code = 200
            return response
        else:
            return not_found()
    except Exception as e:
        print(e)
        return not_found()
    finally:
        cursor.close()
        conn.close()


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pessoa WHERE id=%s", (id))
        conn.commit()
        response = jsonify("Pessoa aniquilada")
        response.status_code = 200
        return response
    except Exception as ex:
        print(ex)
        return not_found()
    finally:
        cursor.close()
        conn.close()


@app.errorhandler(405)
def not_allowed(error=None):
    return render_index()


@app.errorhandler(404)
def not_found(error=None):
    return render_template('404.html')


def searchByName(name):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * from pessoa where nome=%s', name)
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
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
        return not_found()
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
