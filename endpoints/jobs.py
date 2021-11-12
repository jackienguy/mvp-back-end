import mariadb
import dbcreds
from flask import request, Response
import json
from endpoints.dbConnect import dbConnection
from myapp import app
import datetime


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
        recruiter_id = request.args.get('recruiterId')
        recruiter_post = True
        not_recruiter = True

        try:
            (conn, cursor) = dbConnection()
            if recruiter_post:
                cursor.execute("SELECT * from job WHERE recruiter_id=?", [recruiter_id])
                result = cursor.fetchall()
                if result != None:
                    job_post_data = []
                    for post in result:
                        postings = {
                        "jobId": post[0],
                        "recruiterId": post[1],
                        "jobTitle": post[5],
                        "orgName": post[4],
                        "jobLocation": post[6],
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
                    return Response (json.dumps(job_post_data, default=str),
                                    mimetype="application/json",
                                    status=200)
            elif not_recruiter:
                cursor.execute("SELECT * from user INNER JOIN job on job.recruiter_id = users.id")
                result = cursor.fetchall()
                if result != None:
                    all_post = []
                    for post in result:
                        postings = {
                        "jobId": post[0],
                        "recruiterId": post[1],
                        "jobTitle": post[5],
                        "orgName": post[4],
                        "jobLocation": post[6],
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
                        all_post.append(postings)
                return Response (json.dumps(all_post, default=str),
                                mimetype="application/json",
                                status=200)
            else:
                msg = {
                    "message": "ID not found"
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

# Create job post
    elif (request.method == "POST"):
        cursor = None
        conn = None
        data = request.json
        login_token = data.get('loginToken')
        job_title = data.get('jobTitle')
        org_name = data.get('orgName')
        job_location = data.get('jobLocation')
        salary_range = data.get('salaryRange')
        ft_status = data.get('ftStatus')
        perm_status = data.get('permStatus') 
        duration = data.get('duration') 
        closing_date = data.get('closingDate')
        about = data.get('about')
        responsibilities = data.get('responsibilities')
        qualifications = data.get('qualifications')
        recruiter_name = data.get('recruiterName')
        recruiter_title = data.get('recruiterTitle') 
        recruiter_email = data.get('recruiterEmail') 
        recruiter_phone_number = data.get('recruiterPhoneNumber')

        try: 
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token FROM user_session INNER JOIN users ON users.id = user_session.user_id WHERE login_token=?", [login_token,])
            result = cursor.fetchone()
            created_at = datetime.datetime.now()
            recruiter_id = result[0]
            if result[1] == login_token:
                cursor.execute("INSERT INTO job(recruiter_id, job_title, org_name, job_location, ft_status, perm_status, salary_range, duration, closing_date, created_at, about, responsibilities, qualifications, recruiter_name, recruiter_title, recruiter_email, recruiter_phone_number) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [recruiter_id, job_title, org_name, job_location, ft_status, perm_status, salary_range, duration, closing_date, created_at, about, responsibilities, qualifications, recruiter_name, recruiter_title, recruiter_email, recruiter_phone_number])
            conn.commit()
            job_id = cursor.lastrowid
            createPosting = {
                "jobId": job_id,
                "recruiterId": recruiter_id,
                "login_token": result[1]
            }
            return Response(json.dumps(createPosting, default=str),
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

# Edit job post
    elif (request.method == "PATCH"):
        cursor = None
        conn = None
        data = request.json
        login_token = data.get('loginToken')
        job_title = data.get('jobTitle')
        org_name = data.get('orgName')
        job_location = data.get('jobLocation')
        salary_range = data.get('salaryRange')
        ft_status = data.get('ftStatus')
        perm_status = data.get('permStatus') 
        duration = data.get('duration') 
        closing_date = data.get('closingDate')
        about = data.get('about')
        responsibilities = data.get('responsibilities')
        qualifications = data.get('qualifications')
        recruiter_name = data.get('recruiterName')
        recruiter_title = data.get('recruiterTitle') 
        recruiter_email = data.get('recruiterEmail') 
        recruiter_phone_number = data.get('recruiterPhoneNumber')

        try: 
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, login_token FROM user_session INNER JOIN users ON users.id = user_session.user_id WHERE login_token=?", [login_token,])
            result = cursor.fetchone()
            recruiter_id = result[0]
            cursor.execute("SELECT job_id FROM job INNER JOIN users ON users.id = job.recruiter_id WHERE recruiter_id=?", [recruiter_id])
            job = cursor.fetchone()
            job_id = job[0]
            if result[1] == login_token:
                if (job_title != None):
                    cursor.execute("UPDATE job SET job_title=? WHERE id=?", [job_title, job_id])
                if (org_name != None):
                    cursor.execute("UPDATE job SET  org_name=? WHERE id=?", [org_name, job_id])
                if (job_location != None):
                   cursor.execute("UPDATE job SET job_location=? WHERE id=?", [job_title, job_id])
                if (salary_range != None):
                    cursor.execute("UPDATE job SET salary_range=? WHERE id=?", [salary_range, job_id])
                if (ft_status != None):
                    cursor.execute("UPDATE job SET ft_status=? WHERE id=?", [ft_status, job_id])
                if (perm_status != None):
                    cursor.execute("UPDATE job SET perm_status=? WHERE id=?", [perm_status, job_id])
                if (duration != None):
                    cursor.execute("UPDATE job SET duration=? WHERE id=?", [duration, job_id])
                if (closing_date != None):
                    cursor.execute("UPDATE job SET closing_date=? WHERE id=?", [closing_date, job_id])
                if (about != None):
                    cursor.execute("UPDATE job SET about=? WHERE id=?", [about, job_id])
                if (responsibilities != None):
                    cursor.execute("UPDATE job SET responsibilities=? WHERE id=?", [responsibilities, job_id])
                if (qualifications != None):
                    cursor.execute("UPDATE job SET qualifications=? WHERE id=?", [qualifications, job_id])
                if (recruiter_name != None):
                    cursor.execute("UPDATE job SET recruiter_name=? WHERE id=?", [recruiter_name, job_id])
                if (recruiter_title != None):
                    cursor.execute("UPDATE job SET recruiter_title=? WHERE id=?", [recruiter_title, job_id])
                if (recruiter_email != None):
                    cursor.execute("UPDATE job SET recruiter_email=? WHERE id=?", [recruiter_email, job_id])
                if (recruiter_phone_number != None):
                    cursor.execute("UPDATE job SET recruiter_phone_number=? WHERE id=?", [recruiter_phone_number, job_id])
                conn.commit()  
                    
                updatedJob = {
                    "jobId": job_id,
                }
                return Response(json.dumps(updatedJob),
                                mimetype="application/json",
                                status=200)
            else:
                msg = {
                    "message": "Action denied, you do not have the verified credentials to complete action"
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

# Delete job post
    elif (request.method == "DELETE"):
        cursor = None
        conn = None
        login_token = request.json.get('loginToken')
        recruiter_id = request.json.get('recruiterId')

        try:
            (conn, cursor) = dbConnection()
            cursor.execute("SELECT user_id, loginToken FROM user_session INNER JOIN users ON user_session.user_id = users.id WHERE loginToken=?", [ login_token,])
            result = cursor.fetchone()
            recruiter_id = result[0]
            if result[1] == login_token:
                cursor.execute("DELETE FROM job WHERE recruiter_id=?",[recruiter_id,])
                conn.commit()
                msg = {
                    "message": "job ad deleted"
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
