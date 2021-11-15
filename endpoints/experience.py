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

@app.route('/api/user/experience', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def experience():
    if (request.method == 'GET'):
        cursor = None
        conn = None
        user_id = request.args.get('userId')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, title, company_name, work_location, description, start_date, end_date from work_experience INNER JOIN users on work_experience.user_id = users.id WHERE user_id=?", [user_id,])
            result = cursor.fetchone()
            if result != None:
                experienceInfo = {
                    "userId": result[0],
                    "title": result[1],
                    "companyName": result[2],
                    "workLocation": result[3],
                    "description": result[4],
                    "startDate": result[5],
                    "endDate": result[6],      
                }
                return Response(json.dumps(experienceInfo, default=str),
                                mimetype="application/json",
                                status=200)
            else:
                msg = {
                    "message": "section empty"
                }
                return Response(json.dumps(msg),
                                mimetype="application/json",
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

    elif (request.method == 'POST'):
        cursor = None
        conn = None
        data = request.json
        login_token = data.get('loginToken')
        title = data.get('title')
        company_name = data.get('companyName')
        work_location = data.get('workLocation')
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        description = data.get('description')
       
        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token from user_session INNER JOIN users ON user_session.user_id = users.id WHERE login_token=?", [login_token,])
            result = cursor.fetchone()
            user_id = result[0]
            cursor.execute("INSERT INTO work_experience(user_id, title ,company_name, work_location, start_date, end_date, description) VALUES(?,?,?,?,?,?,?)",[user_id, title, company_name, work_location, start_date, end_date, description])
            conn.commit()
            experience = {
                "userId": user_id,
                "title": title,
                "workLocation": work_location,
                "description": description,
                "endDate": end_date,
                "startDate": start_date,
                "companyName": company_name
            }
            return Response (json.dumps(experience),
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
        title = data.get('title')
        company_name = data.get('companyName')
        work_location = data.get('workLocation')
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        description = data.get('description')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token FROM user_session INNER JOIN users on user_session.user_id = users.id WHERE login_token=?", [login_token])
            user = cursor.fetchone()
            user_id = user[0]
            if (user !=None):
                if (title !="" and user[1] == login_token ):
                    cursor.execute("UPDATE work_experience SET title=? WHERE user_id=?", [title, user_id])
                if (company_name !="" and user[1] == login_token):
                    cursor.execute("UPDATE work_experience SET company_name=? WHERE user_id=?", [company_name, user_id])
                if (work_location !="" and user[1] == login_token):
                    cursor.execute("UPDATE work_experience SET work_location=? WHERE user_id=?", [work_location, user_id])
                if (start_date !="" and user[1] == login_token):
                    cursor.execute("UPDATE work_experience SET start_date=? WHERE user_id=?", [start_date, user_id])
                if (end_date !="" and user[1] == login_token):
                    cursor.execute("UPDATE work_experience SET end_date=? WHERE user_id=?", [end_date, user_id])
                if (description !="" and user[1] == login_token):
                    cursor.execute("UPDATE work_experience SET description=? WHERE user_id=?", [description, user_id])
                conn.commit()
                cursor.execute("SELECT user_id, title, company_name, work_location, start_date, end_date, description FROM work_experience INNER JOIN users ON users.id = work_experience.user_id WHERE user_id=?", [user_id,])
                result = cursor.fetchall()
                updatedExperience = {
                    "userId": user_id,
                    "loginToken": login_token,
                    "title": title,
                    "companyName": company_name,
                    "workLocation": work_location,
                    "startDate": start_date,
                    "endDate": end_date,
                    "description": description
                }
                return Response(json.dumps(updatedExperience, default=str),
                                mimetype="application/json",
                                status=200)
            else:
                msg = {
                    "message": "Denied, authentication not verified"
                }
                return Response(json.dumps(msg),
                                mimetype="application/json",
                                status=400)

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
                cursor.execute("SELECT * FROM work_expereince WHERE user_id=?",[user_id,])
                experience = cursor.fetchone()
                if result[1] == login_token and user_id == experience[0]:
                    cursor.execute("DELETE FROM work_expereince WHERE user_id=?",[user_id,])
                    conn.commit()
                    msg = {
                        "message": "work experience deleted"
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


           