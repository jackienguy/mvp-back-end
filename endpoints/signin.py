import mariadb
import dbcreds
from flask import request, Response
import json
from myapp import app
import secrets
import bcrypt

def dbConnect():
    conn = None
    cursor = None

    try:
        conn = mariadb.connect(
                                user=dbcreds.user,
                                password=dbcreds.password,
                                host=dbcreds.host,
                                port=dbcreds.port,
                                database=dbcreds.database)
        cursor = conn.cursor()
    
    except:
        if (cursor != None):
            cursor.close()
        if (conn != None):
            conn.close()
        else:
            raise ConnectionError("Connection failed")
    
    return (conn, cursor)

@app.route('/api/signin', methods=['POST', 'DELETE'])
def login_session():
# logging in
    if (request.method == 'POST'):
        conn = None
        cursor = None
        email = request.json.get('email')
        password = request.json.get('password')
        
        try:
            (conn, cursor) = dbConnect()
            cursor.execute("SELECT id, password, role FROM users WHERE email=?",[email,]) 
            user = cursor.fetchone()
            login_token = secrets.token_hex(16)
            if bcrypt.checkpw(password.encode(), user[1].encode()):
                if user != None: 
                    user_id = user[0]
                    cursor.execute("INSERT INTO user_session(user_id, login_token) VALUES(?,?)", [user_id, login_token]) 
                    conn.commit()
                    resp = {
                        "userId" : user[0],
                        "loginToken": login_token,
                        "role": user[2]
                    }
                    return Response(json.dumps(resp),
                                    mimetype="application/json",
                                    status=200)  
                else:
                    msg = { 
                        "message": "password incorrect"
                      }
                    return Response (json.dumps(msg),
                                    mimetype="application/json",
                                    status=400)
            else: 
                msg = {
                    "message": "Email or password inccorect, please try again"
                }
                return Response (json.dumps(msg),
                                mimetype="application/json",
                                status=400)

        except ValueError as error:
            print("Error" +str(error))
        except mariadb.DataError:
            print("something went wrong with your data")
        except mariadb.OperationalError:
            print("opertational error on the connection")
        except mariadb.ProgrammingError:
            print("apparently, you don't know how to code")
        except mariadb.IntegrityError:
            print("Error with DB integrity. most likelu constraint failure")
        except:
            print("Something went wrong")

        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            else:
                print("Failed to read data")

        return Response("Error something went wrong",
                        mimetype="text/plain",
                        status=500)
# logging out 
    elif (request.method == 'DELETE'):
        conn = None
        cursor = None
        login_token = request.json.get('loginToken')

        try:
            (conn, cursor) = dbConnect()
            cursor.execute("DELETE from user_session WHERE login_token=?",[login_token])
            conn.commit()
            msg = {
                "message": "Successfully loged out"
            }
            return Response(json.dumps(msg),
                            mimetype="text/html",
                            status=200)
        
        except mariadb.DataError:
            print("something went wrong with your data")
        except mariadb.OperationalError:
            print("opertational error on the connection")
        except mariadb.ProgrammingError:
            print("apparently, you don't know how to code")
        except mariadb.IntegrityError:
            print("Error with DB integrity. most likely constraint failure")
        except:
            print("Something went wrong")

        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            else:
                print("Failed to read data")

        return Response("Error something went wrong",
                        mimetype="text/plain",
                        status=500)