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

@app.router('/api/requisition', methods=['GET'])
def requisition():
    if (request.method == "GET"):
        cursor = None
        conn = None
        job_id = request.args.get('jobId')
        
        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT job_id, job_title, num_applicants, closing_date, status FROM jobs INNER JOIN users on jobs.recruiter_id = users.id WHERE job_id=", [job_id])
            result = cursor.fetchall()
            if cursor.rowcount > 0:
                for requisition in result:
                    requisition_list = []
                    requisitions = {
                        "jobId": result[0][0],
                        "jobTitle": result[0][1],
                        "numApplicants": result[0][2],
                        "closingDate": result[0][3],
                        "status": result[0][4],
                    }
                    requisition_list.append(requisitions)
            return Response(json.dumps(requisition_list, default=str),
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