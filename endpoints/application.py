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

@app.route('/api/application', methods=['POST'])
def application ():
    if (request.method == 'POST'):
        cursor = None
        conn = None
        data = request.json
        login_token = data.get('loginToken')
        job_id = data.get('jobId')
        
        
        try: 
            (conn, cursor) = dbConnection()
            (cursor.execute("SELECT user_id, login_token from user_session INNER JOIN users ON user_session.user_id = users.id WHERE login_token=?", [login_token,]))
            result = cursor.fetchall()
            applicant_id = result [0][0]
            if result[0][1] == login_token:
                cursor.execute("INSERT INTO application(applicant_id, job_id) VALUES(?,?)", [applicant_id, job_id])
                application_id = cursor.lastrowid
                conn.commit()
                applications = {
                    "applicantId": applicant_id,
                    "jobId": job_id,
                    "applicationId": application_id
                }
                return Response (json.dumps(applications),
                                mimetype="application/json",
                                status=200)
            else:
                msg = {
                    "message": "Action denied, you are not authenticated user"
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