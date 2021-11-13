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
        
        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT job_id, applicant_id, first_name, last_name, job_title from application INNER JOIN job on job.id = application.job_id INNER JOIN users ON application.applicant_id = users.id WHERE job_id=?",[job_id,])
            result = cursor.fetchall()
            if cursor.rowcount > 0:
                applicant_list = []
                for applicant in result:
                    applicants = {
                        "jobId": result[0][0],
                        "applicantId": result[0][1],
                        "firstName": result[0][2],
                        "lastName": result[0][3],
                        "jobTItle": result[0][4]
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
        