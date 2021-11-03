import mariadb
from flask import request, Response
import json
from myapp import app
import secrets
import dbcreds


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
 # get user data
    if (request.method == 'GET'):
        conn = None
        cursor = None
        user_id = request.args.get('userId')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT users.id, first_name, last_name, email, phone_number FROM users WHERE id=?", [user_id])
            result = cursor.fetchall()
            if cursor.rowcount > 0:
                user_data = []
                for user in result:
                    users = {
                        "userId": user_id,
                        "email": user[3],
                        "firstName": user[1],
                        "lastName": user[2],
                        "phone_number": user[4]
                    }
                    user_data.append(users)
                return Response(json.dumps(user_data),
                                mimetype="application/json",
                                status=200)
            else:
                msg = {
                    "message": "User ID not found"
                }
                return Response (json.dumps(msg),
                                mimetype="application/json",
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
#create new user
    elif (request.method == 'POST'):
        cursor = None
        conn = None
        first_name = request.json.get('firstName')
        last_name = request.json.get('lastName')
        email = request.json.get('email')
        password = request.json.get('password')
        role = request.json.get('role')

        try: 
            (conn, cursor) = dbConnection()
            cursor.execute("INSERT INTO users(first_name, last_name, email, password, role) VALUES(?,?,?,?,?)", [first_name, last_name, email, password, role])
            if (len(password) < 6):
                return ("Password need to be at least 8 characters long")
            user_id = cursor.lastrowid
            login_token = secrets.token_hex(16)
            cursor.execute("INSERT INTO user_session(user_id, login_token) VALUES(?,?)", [user_id, login_token]) 
            conn.commit()
            newUser = {
                "userId": user_id,
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "password": password,
                "role": role,
                "loginToken": login_token
            }
            return Response(json.dumps(newUser),
                            mimetype="application/json",
                            status=200)
                            
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
# edit user
    elif (request.method == "PATCH"):
        data = request.json 
        conn = None
        cursor = None
        login_token = data.get('loginToken')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')
        organization_name = data.get('organizationName')
        location = data.get('location')
        company_website = data.get('companyWebsite')
        working_title =data.get('workingTitle')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token FROM user_session INNER JOIN users on user_session.user_id = users.id WHERE login_token=?", [login_token])
            user = cursor.fetchall()
            user_id = user[0][0]
            if (first_name != None and user[0][1] == login_token):
                cursor.execute("UPDATE users SET first_name=? WHERE id=?", [first_name, user_id])
            elif (last_name != None and user[0][1] == login_token):
                cursor.execute("UPDATE users SET last_name=? WHERE id=?", [last_name, user_id])
            elif (email != None and user[0][1] == login_token):
                cursor.execute("UPDATE users SET email=? WHERE id=?", [email, user_id])
            elif (organization_name != None and user[0][1] == login_token):
                cursor.execute("UPDATE users SET organization_name=? WHERE id=?", [organization_name, user_id])
            elif (location != None and user[0][1] == login_token):
                cursor.execute("UPDATE users SET location=? WHERE id=?", [location, user_id])
            elif (company_website != None and user[0][1] == login_token):
                cursor.execute("UPDATE users SET company_website=? WHERE id=?", [company_website, user_id])
            elif (working_title != None and user[0][1] == login_token):
                cursor.execute("UPDATE users SET working_title=? WHERE id=?", [working_title, user_id])
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE id=?", [user_id])
            updated_user_data = cursor.fetchall()
            if cursor.rowcount == 1:
                user_update = {
                    "userId": updated_user_data[0][0],
                    "firstName": updated_user_data[0][2],
                    "lastName": updated_user_data[0][3],
                    "email": updated_user_data[0][1],
                    "phoneNumber": updated_user_data[0][6],
                    "profilePicture": updated_user_data[0][7],
                    "organizationName": updated_user_data[0][9],
                    "location": updated_user_data[0][10],
                    "companyWebsite": updated_user_data[0][11],
                    "workingTitle": updated_user_data[0][12]
                }
            return Response(json.dumps(user_update),
            mimetype="application/json",
                status=200)

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
# Delete user
    elif (request.method == 'DELETE'):
        conn = None
        cursor = None
        login_token = request.json.get("loginToken")
        password = request.json.get('password')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, password, login_token FROM users INNER JOIN user_session ON user_session.user_id = users.id WHERE login_token=?", [login_token,])
            user = cursor.fetchall()
            if user[0][1] == password and user[0][2] == login_token:
                cursor.execute("DELETE FROM users WHERE password=?",[password,])
                conn.commit()
                msg = {
                    "message": "User successfully deleted"
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





    

   