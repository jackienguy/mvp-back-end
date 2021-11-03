from myapp import app
from flask_cors import CORS

CORS(app)

app.run(debug=True)
