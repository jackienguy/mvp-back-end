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

@app.route('/api/users/skills', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def skills():
    if (request.method == 'GET'):
        cursor = None
        conn = None
        user_id = request.args.get('userId')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT * from users INNER JOIN skills ON skills.user_id = users.id WHERE user_id=?", [user_id,])
            result = cursor.fetchone()
            if result != None:
                skillsInfo = {
                    "userId": result[0],
                    "skillType": result[1],
                    "proficiencyLevel": result[2],   
                }
            return Response(json.dumps(skillsInfo),
                            mimetype="application/json",
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

    elif (request.method == 'POST'):
        cursor = None
        conn = None
        data = request.json
        login_token = data.get('loginToken')
        skill_type = data.get('skillType')
        proficiency_level = data.get('proficiencyLevel')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token from user_session INNER JOIN users ON user_session.user_id = users.id WHERE login_token=?", [login_token,])
            result = cursor.fetchone()
            user_id = result[0]
            cursor.execute("INSERT INTO skills(user_id, skill_type, proficiency_level) VALUES(?,?,?)",[user_id, skill_type, proficiency_level])
            conn.commit()
            skills = {
                "userId": user_id,
                "skillType": result[1],
                "proficiencyLevel": result[2],          
            }
            return Response (json.dumps(skills),
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
        skill_type = data.get('skillType')
        proficiency_level = data.get('proficiencyLevel')
        
        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token FROM user_session INNER JOIN users on user_session.user_id = users.id WHERE login_token=?", [login_token])
            user = cursor.fetchone()
            user_id = user[0]
            if (skill_type != None and user[1] == login_token):
                cursor.execute("UPDATE skills SET skill_type=? WHERE user_id=?", [skill_type, user_id])
            if (proficiency_level != None and user[1] == login_token):
                cursor.execute("UPDATE skills SET proficiency_level=? WHERE user_id=?", [proficiency_level, user_id])
            conn.commit()
            updatedSkills = {
                "userId": user_id
            }
            return Response(json.dumps(updatedSkills),
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
                cursor.execute("SELECT * FROM skills WHERE user_id=?",[user_id,])
                skills = cursor.fetchone()
                if result[1] == login_token and user_id == skills[0]:
                    cursor.execute("DELETE FROM skills WHERE user_id=?",[user_id,])
                    conn.commit()
                    msg = {
                        "message": "skills deleted"
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




