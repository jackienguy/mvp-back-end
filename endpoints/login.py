import mariadb
from myapp import dbcreds
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

@app.route('/api/signin', methods=['POST','DELETE'])
def login_session():
    if (request.method == 'POST'):
        conn = None
        cursor = None
        email = request.json.get('email')
        password = request.json.get('password')
        
        try:
            (conn, cursor) = dbConnect()
            cursor.execute("SELECT * FROM users WHERE email=? AND password=?",[email, password]) #If combination matches, will return rowcount 1, if combination do not match, will return 0
            user = cursor.fetchall()
            login_token = secrets.token_hex(16)
            
            if cursor.rowcount == 1: #If user exist will = 1
                user_id = user[0][0]
                cursor.execute("INSERT INTO user_session(user_id, loginToken) VALUES(?,?)", [user_id, login_token]) #insert the created login token into user session table
                conn.commit()
                # fetchall returns dictionaries with tuples. Indexes reflect dictionary index and indexes of the tuples 
                resp = {
                    "userId" : user[0][0],
                    "firstName": user[0][1],
                    "lastName": user[0][1],
                    "email" : user[0][3],
                    "phoneNumber": user[0][2],
                    "loginToken ": login_token
                }
                return Response(json.dumps(resp),
                                mimetype="application/json",
                                status=200)  
            else: 
                return ("Username or password inccorect, please try again")
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

    elif (request.method == 'DELETE'):
        conn = None
        cursor = None
        login_token = request.json.get('loginToken')

        try:
            (conn, cursor) = dbConnect()
            cursor.execute("DELETE from user_session WHERE loginToken=?",[login_token])
            conn.commit()
            return Response("Sucessfully logged out",
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