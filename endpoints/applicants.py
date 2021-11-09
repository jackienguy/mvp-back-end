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

@app.route('/api/applicant', methods=['GET'])
def applicants():
    if (request.method == 'GET'):
        cursor = None
        conn = None
        login_token = request.headers.get('loginToken')
        job_id = request.args.get('jobId')
        
        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token, role FROM user_session INNER JOIN users ON users.id = user_session.user_id WHERE login_token=?", [login_token,])
            user = cursor.fetchone()
            if user[3] == "recruiter":
                cursor.execute("SELECT * from application INNER JOIN jobs on jobs.id = application.job_id INNER JOIN users ON jobs.recruiter_id = users.id WHERE job_id=?",[job_id])
                result = cursor.fetchall()
                if cursor.rowcount > 0:
                    applicant_list = []
                    for applicant in result:
                        applicants = {
                            "jobId": result[0],
                            "applicantId": result[1],
                            "firstName": result[5],
                            "lastName": result[6] 
                        }
                        applicant_list.append(applicants)
                return Response(json.dumps(applicant_list),
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
        