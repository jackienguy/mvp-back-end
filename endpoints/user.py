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
 # get user data
    if (request.method == 'GET'):
        conn = None
        cursor = None
        user_id = request.args.get('userId')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT id, first_name, last_name, organization_name, location, working_title, email, phone_number FROM users WHERE id=?", [user_id,])
            result = cursor.fetchone()
            if result != None:
                user = {
                    "userId": result[0],
                    "email": result[6],
                    "firstName": result[1],
                    "lastName": result[2],
                    "organizationName": result[3],
                    "location": result[4],
                    "workingTitle": result[5],
                    "phoneNumber": result[7]
                }
                return Response(json.dumps(user),
                                mimetype="application/json",
                                status=200)
            else:
                msg = {
                    "message": "User ID not found"
                }
                return Response (json.dumps(msg),
                                mimetype="application/json",
                                status=400)

        except mariadb.DataError as e:
            print(e)
        except mariadb.OperationalError as e:
            print(e)
        except mariadb.ProgrammingError as e:
            print(e)
        except mariadb.IntegrityError as e:
            print(e)
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
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(13))
            cursor.execute("INSERT INTO users(first_name, last_name, email, password, role) VALUES(?,?,?,?,?)", [first_name, last_name, email, hashed, role])
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
        except mariadb.DataError as e:
            print(e)
        except mariadb.OperationalError as e:
            print(e)
        except mariadb.ProgrammingError as e:
            print(e)
        except mariadb.IntegrityError as e:
            print(e)
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
        phone_number =data.get('phoneNumber')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token, role FROM user_session INNER JOIN users on user_session.user_id = users.id WHERE login_token=?", [login_token])
            user = cursor.fetchone()
            user_id = user[0]
            if (first_name != None and user[1] == login_token):
                cursor.execute("UPDATE users SET first_name=? WHERE id=?", [first_name, user_id])
            if (last_name != None and user[1] == login_token):
                cursor.execute("UPDATE users SET last_name=? WHERE id=?", [last_name, user_id])
            if (email != None and user[1] == login_token):
                cursor.execute("UPDATE users SET email=? WHERE id=?", [email, user_id])
            if (organization_name != None and user[1] == login_token):
                cursor.execute("UPDATE users SET organization_name=? WHERE id=?", [organization_name, user_id])
            if (location != None and user[1] == login_token):
                cursor.execute("UPDATE users SET location=? WHERE id=?", [location, user_id])
            if (company_website != None and user[1] == login_token):
                cursor.execute("UPDATE users SET company_website=? WHERE id=?", [company_website, user_id])
            if (working_title != None and user[1] == login_token):
                cursor.execute("UPDATE users SET working_title=? WHERE id=?", [working_title, user_id])
            if (phone_number != None and user[1] == login_token):
                    cursor.execute("UPDATE users SET phone_number=? WHERE id=?", [phone_number, user_id])
            conn.commit()
            updatedUser = {
                "userId": user_id,
                "role": user[2]
            }
            return Response(json.dumps(updatedUser),
                            mimetype="application/json",
                            status=200)

        except ValueError as error:
            print("Error" +str(error))
        except mariadb.DataError as e:
            print(e)
        except mariadb.OperationalError as e:
            print(e)
        except mariadb.ProgrammingError as e:
            print(e)
        except mariadb.IntegrityError as e:
            print(e)
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

        except mariadb.DataError as e:
            print(e)
        except mariadb.OperationalError as e:
            print(e)
        except mariadb.ProgrammingError as e:
            print(e)
        except mariadb.IntegrityError as e:
            print(e)
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

   



    

   