from flask import Flask 


app = Flask(__name__)

from endpoints import user
from endpoints import signin
from endpoints import jobs
from endpoints import education
from endpoints import experience
from endpoints import skills
from endpoints import applicants
from endpoints import application
from endpoints.dbConnect import dbConnection