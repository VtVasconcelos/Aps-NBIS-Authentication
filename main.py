import pymysql
from app import app
from banco import mysql
from flask import jsonify
from flask import flash, request
from nbis import identify

@app.route('/add', methods=['POST'])
def add_pessoa():
    try:
        # aqui eu pego o json
        _json = request.json
        # pego uma parte do json que no caso é o nome
        _nome = _json['nome']
        _digital = _json['digital']
        _nivel_acesso = _json['nivel_acesso']
        # se nome existe e se a req é POST
        if(_nome and request.method == 'POST'):
            # eu guardo o comando que o banco de dados vai receber
            sqlQuery = 'insert into pessoa(nome,digital,nivel_acesso) values(%s,%s,%s)'
            # eu guardo os valores do json que eu peguei
            bindData = (_nome,_digital,_nivel_acesso)
            # crio uma conexao com o banco
            conn = mysql.connect()
            # guardo essa conexao em uma variavel
            cursor = conn.cursor()
            # executo o comando, passando o comando e os valores
            cursor.execute(sqlQuery, bindData)
            conn.commit()

            # respondo se conseguir
            response = jsonify('Pessoa added')
            response.status_code = 200
            return response
        else:
            return not_found()
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


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
        with open("search.xyt","w") as fxyt:
            fxyt.write(rows['digital'])
        print(identify("search.xyt"))
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
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
    finally:
        cursor.close()
        conn.close()


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': "Not found" + request.url
    }
    response = jsonify(message)
    response.status_code = 404
    return response


if __name__=='__main__':
    app.run()
