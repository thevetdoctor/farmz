from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
 
ENV = 'dev'

if ENV == 'prod':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:animalworld@localhost/flaskrest'
else:
    app.debug = False 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://snnemmtjbvdsls:40e156cf3c697687901f8569071deff7cf0c307ad827f1f1ae24914fe73f49a5@ec2-18-235-20-228.compute-1.amazonaws.com:5432/da9h6v89t4t3u3'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://khowojaj:QexvLciyprZqe0m8ofzx2lbBSyMh61ho@drona.db.elephantsql.com:5432/khowojaj'

print(ENV)
 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['secret'] = 'jwtsecret'

db = SQLAlchemy(app)
marsh = Marshmallow(app)

from flaskresty import routes
