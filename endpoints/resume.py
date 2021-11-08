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

@app.route('/api/resume', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def resume():
    if (request.method == 'POST'):
        cursor = None
        conn = None
        data = request.json
        login_token = data.get('loginToken')
        certificate_name = data.get('certificateName')
        major = data.get('major')
        institution_name = data.get('institutionName')
        completion_date = data.get('completitionDate')
        location = data.get('location')
        other = data.get('other')
        skill_type = data.get('skillType')
        proficiency_level = data.get('proficiencyLevel')
        working_title = data.get('workingTitle')
        company_name = data.get('companyName')
        work_location = data.get('workLocation')
        start_date = data.get('startDate')
        end_date = data.get('endData')
        description = data.get('description')
       
        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token from user_session INNER JOIN users ON user_session.user_id = users.id WHERE login_token=?", [login_token,])
            result = cursor.fetchone()
            user_id = result[0]
            cursor.execute("SELECT users.id FROM users INNER JOIN education ON education.user_id = users.id WHERE users.id=?", [user_id,])
            education = cursor.fetchone()
            if user_id == education[0]
                cursor.execute("INSERT INTO education(user_id, certificate_name, major, institution_name, completion_date, location, other) VALUES(?,?,?,?,?,?,?)",[user_id, certificate_name, major, institution_name, completion_date, location, other])
       
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
           
           
           
           
            



