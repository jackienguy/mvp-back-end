import mariadb
from flask import request, Response
import json
from myapp import app

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

@app.route('/api/user/education', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def education():
    if (request.method == 'GET'):
        cursor = None
        conn = None
        user_id = request.args.get('userId')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, certificate_name, major, institution_name, completion_date, institution_location, other from education INNER JOIN users ON education.user_id = users.id WHERE user_id=?", [user_id,])
            result = cursor.fetchone()
            if result != None:
                eduInfo = {
                    "userId": result[0],
                    "certificateName": result[1],
                    "major": result[2],
                    "institutionName": result[3],
                    "completionDate": result[4],
                    "institutionLocation": result[5],
                    "other": result[6]  
                }
                return Response(json.dumps(eduInfo),
                                mimetype="application/json",
                                status=200)
            else:
                msg = {
                    "message": "section empty"
                }
                return Response(json.dumps(msg),
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

    elif (request.method == 'POST'):
        cursor = None
        conn = None
        data = request.json
        login_token = data.get('loginToken')
        certificate_name = data.get('certificateName')
        major = data.get('major"')
        institution_name = data.get('institutionName')
        completion_date = data.get('completionDate')
        institution_location = data.get('institutionLocation')
        other = data.get('other')
       
        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token from user_session INNER JOIN users ON user_session.user_id = users.id WHERE login_token=?", [login_token,])
            result = cursor.fetchone()
            user_id = result[0]
            cursor.execute("INSERT INTO education(user_id, certificate_name, major, institution_name, completion_date, institution_location, other) VALUES(?,?,?,?,?,?,?)",[user_id, certificate_name, major, institution_name, completion_date, institution_location, other])
            conn.commit()
            education = {
                "userId": user_id,
                "certificateName": certificate_name,
                "major": major,
                "institutionName": institution_name,
                "completionDate": completion_date,
                "institutionLocation": institution_location,
                "other": other          
            }
            return Response (json.dumps(education),
                            mimetype="application/json",
                            status=201)

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

    elif (request.method == "PATCH"):
        data = request.json 
        conn = None
        cursor = None
        login_token = data.get('loginToken')
        certificate_name = data.get('certificateName')
        major = data.get('major"')
        institution_name = data.get('institutionName')
        completion_date = data.get('completionDate')
        institution_location = data.get('institutionLocation')
        other = data.get('other')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token FROM user_session INNER JOIN users on user_session.user_id = users.id WHERE login_token=?", [login_token])
            user = cursor.fetchone()
            user_id = user[0]
            if (user != None):
                if (certificate_name != "" and user[1] == login_token):
                    cursor.execute("UPDATE education SET certificate_name=? WHERE user_id=?", [certificate_name, user_id])
                if (major != "" and user[1] == login_token):
                    cursor.execute("UPDATE education SET major=? WHERE user_id=?", [major, user_id])
                if (institution_name != "" and user[1] == login_token):
                    cursor.execute("UPDATE education SET institution_name=? WHERE user_id=?", [institution_name, user_id])
                if (completion_date != "" and user[1] == login_token):
                    cursor.execute("UPDATE education SET completion_date=? WHERE user_id=?", [completion_date, user_id])
                if (institution_location != "" and user[1] == login_token):
                    cursor.execute("UPDATE education SET institution_location=? WHERE user_id=?", [institution_location, user_id])
                if (other != "" and user[1] == login_token):
                    cursor.execute("UPDATE education SET other=? WHERE user_id=?", [other, user_id])
                conn.commit()
                cursor.execute("SELECT user_id, certificate_name, major, institution_name, completion_date, institution_location, other FROM education INNER JOIN users ON users.id = education.user_id WHERE user_id=?", [user_id,])
                result = cursor.fetchall()
                updatedEducation = {
                    "userId": user_id,
                    "certificateName": certificate_name,
                    "major": major,
                    "institutionName": institution_name,
                    "completetionDate": completion_date,
                    "institutionLocation": institution_location,
                    "other": other
                }
                return Response(json.dumps(updatedEducation, default=str),
                                mimetype="application/json",
                                status=200)
            else:
                msg = {
                    "message": "section empty"
                }
                return Response(json.dumps(msg),
                                mimetype="application/json",
                                status=401)

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

    elif (request.method == 'DELETE'):
            cursor = None
            conn = None
            login_token = request.json.get('loginToken')
            user_id = request.json.get('userId')

            try:
                (conn, cursor) = dbConnection()
                cursor.execute("SELECT user_id, loginToken FROM user_session INNER JOIN users ON user_session.user_id = users.id WHERE loginToken=?", [ login_token,])
                result = cursor.fetchone()
                user_id = result[0]
                cursor.execute("SELECT * FROM education WHERE user_id=?",[user_id,])
                education = cursor.fetchone()
                if result[1] == login_token and user_id == education[0]:
                    cursor.execute("DELETE FROM education WHERE user_id=?",[user_id,])
                    conn.commit()
                    msg = {
                        "message": "education deleted"
                    }
                    return Response(json.dumps(msg),
                                    mimetype="application/json",
                                    status=200)
                else:
                    return Response("Action denied, you are not authenticated user",
                                mimetype="text/plain",
                                status=401)

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


           