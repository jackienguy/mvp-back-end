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

@app.route('/api/applicants', methods=['GET'])
def applicants():
    if (request.method == 'GET'):
        cursor = None
        conn = None
        job_id = request.args.get('jobId')
        login_token = request.headers.get('loginToken')
        
        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token FROM user_session INNER JOIN users ON users.id = user_session.user_id WHERE login_token=?", [login_token,])
            result = cursor.fetchone()
            user_id = result[0]
            cursor.execute("SELECT recruiter_id FROM job INNER JOIN users ON users.id = job.recruiter_id WHERE users.id=?", [user_id])
            recruiter = cursor.fetchone()
            recruiter_id = recruiter[0]
            if result[1] == login_token and recruiter_id == user_id:
                cursor.execute("SELECT job_id, applicant_id, first_name, last_name, job_title from application INNER JOIN job on job.id = application.job_id INNER JOIN users ON application.applicant_id = users.id WHERE job_id=?",[job_id,])
                applicant_result = cursor.fetchall()
                if cursor.rowcount > 0:
                    applicant_list = []
                    for applicant in applicant_result:
                        applicants = {
                            "jobId": applicant[0],
                            "applicantId": applicant[1],
                            "firstName": applicant[2],
                            "lastName":  applicant[3],
                            "jobTItle":  applicant[4]
                        }
                        applicant_list.append(applicants)
                    return Response(json.dumps(applicant_list),
                                    mimetype="application/json",
                                    status=200)
                else:
                    msg = {
                        "message": "No applicants"
                    }
                    return Response(json.dumps(msg),
                            mimetype="application/json",
                            status=400)
            else:
                msg = {
                    "message": "Denied, authentication not verified"
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
        