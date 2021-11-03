import mariadb
import dbcreds
from flask import request, Response
import json
from endpoints.dbConnect import dbConnection
from myapp import app

def dbConnect():
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

@app.route('/api/jobs', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def jobs():
# Get job post
    if (request.method == "GET"):
        cursor = None
        conn = None
        job_id = request.args.get('jobId')

        try:
            (cursor, conn) = dbConnection()
            cursor.execute("SELECT * from jobs where id=?", [job_id])
            result = cursor.fetchall()
            if cursor.rowcount > 0:
                job_post_data = []
                for post in result:
                    postings = {
                       "jobId": job_id,
                       "recruiterId": post[1],
                       "workingTitle": post[5],
                       "organizationName": post[4],
                       "location": post[6],
                       "SalaryRange": post[13],
                       "ftStatus": post[7],
                       "permStatus": post[8],
                       "duration": post[9],
                       "closingDate": post[14],
                       "createdAt": post[15],
                       "about": post[10],
                       "responsibilities": post[11],
                       "qualifications": post[12],
                       "recruiterName": post[16],
                       "recruiterTitle": post[19],
                       "recruiterEmail": post[17],
                       "recruiterPhoneNumber": post[18],
                    }
                    job_post_data.append(postings)
                return Response(json.dumps(job_post_data),
                                mimetype="application/json",
                                status=200)
            else:
                msg = {
                    "message": "Job ID not found"
                }
                return Response (json.dumps(msg),
                                mimetype="application/json",
                                status=400)

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

# Create job post
    elif (request.method == "POST"):
        cursor = None
        conn = None
        data = request.json
        login_token = data.get('loginToken')
        working_title = data.get('workingTitle')
        organization_name = data.get('organizationName')
        location = data.get('location')
        salary_range = data.get('salaryRange')
        ft_status = data.get('ftStatus')
        perm_status = data.get('permStatus') 
        duration = data.get('duration') 
        closing_date = data.get('closingDate')
        created_at = data.get('createdAt')
        about = data.get('about')
        responsibilities = data.get('responsibilities')
        qualifications = data.get('qualifications')
        recruiter_name = data.get('recruiterName')
        recruiter_title = data.get('recruiterTitle') 
        recruiter_email = data.get('recruiterEmail') 
        recruiter_phone_number = data.get('recruiterPhoneNumber')

        try: 
            (cursor, conn) = dbConnection()
            cursor.execute("SELECT user_id, login_token FROM user_session INNER JOIN users ON users.id = user_session.user_id WHERE login_token=?", [login_token,])
            result = cursor.fetchall()
            recruiter_id = result[0][0]
            if result[0][1] == login_token:
                cursor.execute("INSERT INTO jobs(user_id, working_title, organization_name, location, ft_status, perm_status, salary_range, duration, closing_date, created_at, about, responsibilities, qualifications, \
                                recruiter_name, recruiter_title, recruiter_email, recruiter_phone_number) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", \
                                [recruiter_id, working_title, organization_name, location, ft_status, perm_status, salary_range, duration, closing_date, created_at, about, responsibilities, qualifications, recruiter_name, recruiter_title, recruiter_email, recruiter_phone_number])
            cursor.commit()
            job_id = cursor.lastrowid
            createPosting = {
                "jobId": job_id,
                "recruiterId": result[0][0],
                "workingTitle": result[0][5],
                "organizationName": result[0][4],
                "location": result[0][6],
                "SalaryRange": result[0][13],
                "ftStatus": result[0][7],
                "permStatus": result[0][8],
                "duration": result[0][9],
                "closingDate": result[0][14],
                "createdAt": result[0][15],
                "about": result[0][10],
                "responsibilities": result[0][11],
                "qualifications": result[0][12],
                "recruiterName": result[0][16],
                "recruiterTitle": result[0][19],
                "recruiterEmail": result[0][17],
                "recruiterPhoneNumber": result[0][18],
            }
            return Response(json.dumps(createPosting, default=str),
                            mimetype="application/json",
                            status=200)

        except ConnectionError:
            print("Error occured trying to connect to database")
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

            