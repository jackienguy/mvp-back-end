import mariadb
from flask import request, Response
import json
from myapp import app
import secrets
import dbcreds
import bcrypt

def dbConnection():
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

@app.route('/api/user', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def user():
    # creating user
    if (request.method == 'POST'):
        conn = None
        cursor = None
        first_name = request.json.get("firstName")
        last_name = request.json.get("lastName")
        password = request.json.get("password")
        email= request.json.get("email")
        phone_number = request.json.get("phoneNumber")
        role = request.json.get("role")
      
        try:
            (conn, cursor) = dbConnection()
            cursor.execute("INSERT INTO users(first_name, last_name, password, email, phone_number, role) VALUES(?,?,?,?,?,?)", [first_name, last_name, password, email, phone_number, role])
            user_id = cursor.lastrowid #cursor.lastrowid is a read-only property which returns the value generated for the auto increment column user_id by the INSERT statement above
            login_token = secrets.token_hex(16)
            salt = bcrypt.gensalt(15)
            hashed = bcrypt.hashpw(password.encode(), salt)
            print(hashed)
            cursor.execute("INSERT INTO user_session(user_id, loginToken) VALUES(?,?)",[user_id, login_token])
            conn.commit()
            newUser = {
                "userId": user_id,
                "firstName": first_name,
                "lastName": last_name,
                "password": password,
                "email": email,
                "phoneNumber": phone_number,
                "role": role,
                "loginToken": login_token
            }
            return Response(json.dumps(newUser),
                        mimetype="application/json",
                        status=200)
                        
        except ValueError as error:
            print("ValueError" +str(error))
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

    elif (request.method == 'GET'):
        cursor = None
        conn = None
        conn = None
        cursor = None
        user_id = request.args.get('userId')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT * FROM user WHERE id=?", [user_id,])
            result = cursor.fetchall()
            if cursor.rowcount > 0:
                user_data = []
                for user in result:
                    users = {
                       " userId": user_id,
                       " email": user[3],
                       " firstName": user[1],
                       " lastName": user[1],
                       " phoneNumber": user[2],
                    }
                    user_data.append(users)
                return Response(json.dumps(user_data, default=str),
                                mimetype="application/json",
                                status=200)
            else:
                return Response("User id not found",
                                mimetype="text/html",
                                status=400)

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
  