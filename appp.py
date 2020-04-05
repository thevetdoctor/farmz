from flask import Flask, flash, request, jsonify,render_template, redirect, url_for, make_response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from functools import wraps
from datetime import datetime, timedelta
from flask_cors import CORS
import jwt
import math
import os
from seed import record as data, auth

# print(os.environ['USERNAME'])

app = Flask(__name__)

CORS(app)

# if os.environ.get('USERNAME') == 'ACER':
#     ENV = 'dev'
# else:
ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:animalworld@localhost/flaskrest'
else:
    app.debug = False 
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vxjxpdpdiwnrqw:55e5e567b888401056b662421a387e5e830a0a30fce8d64046f112d37b04135b@ec2-18-210-51-239.compute-1.amazonaws.com:5432/d5obp1t1cedffb'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://snnemmtjbvdsls:40e156cf3c697687901f8569071deff7cf0c307ad827f1f1ae24914fe73f49a5@ec2-18-235-20-228.compute-1.amazonaws.com:5432/da9h6v89t4t3u3'

print(ENV)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['secret'] = 'jwtsecret'

db = SQLAlchemy(app)
marsh = Marshmallow(app)


class PenRecord(db.Model):
    __tablename__ = 'penrecord'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    population = db.Column(db.Integer)
    mortality = db.Column(db.Integer, default=0)
    dressed = db.Column(db.Integer, default=0)
    consumption = db.Column(db.Integer)
    feedbrand = db.Column(db.String(20), default='olam')
    production = db.Column(db.Integer)
    jumbo = db.Column(db.Integer, default=0)
    extra = db.Column(db.Integer, default=0)
    large = db.Column(db.Integer, default=0)
    small = db.Column(db.Integer, default=0)
    pullet = db.Column(db.Integer, default=0)
    crack = db.Column(db.Integer, default=0)
    wastage = db.Column(db.Integer, default=0)
    medication = db.Column(db.String(200), default='none')
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, name, population, mortality, dressed, consumption, feedbrand, production, jumbo, extra, large, small, pullet, crack, wastage, medication, date=None):
        self.name = name
        self.population = population
        self.mortality = mortality
        self.dressed = dressed
        self.consumption = consumption
        self.feedbrand = feedbrand
        self.production = production
        self.jumbo = jumbo
        self.extra = extra
        self.large = large
        self.small = small
        self.pullet = pullet
        self.crack = crack
        self.wastage = wastage
        self.medication = medication
        self.date = date


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean(), default=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, name, password, admin = False):
        self.name = name
        self.password = password
        self.admin = admin

 
# Report Schema
class ReportSchema(marsh.Schema):
    class Meta:
        fields = ('id', 'name', 'population', 'mortality', 'dressed', 'consumption', 'feedbrand', 'production', 'jumbo', 'extra', 'large', 'small', 'pullet', 'crack', 'wastage', 'medication', 'date')

# user Schema
class UserSchema(marsh.Schema):
    class Meta:
        fields = ('id', 'name', 'password', 'admin', 'date')

# Init schema
# report_schema = ReportSchema(strict=True)
# reports_schema = ReportSchema(many=True, strict=True)
report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

c = datetime.utcnow()
d = datetime(2020, 3, 12)

# Root URL
@app.route('/')
def index():
    return jsonify({'message' : 'Welcome to Bafot Farms'}), 200

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # token = request.args.get('token')
        header = request.headers['Authorization']
        token = header[2:(len(header)-1)]

        if not token:
            return jsonify({ 'message' : 'missing authorization'}), 403
        try:
            data = jwt.decode(token, app.config['secret'])
        except:
            return jsonify({'message' : 'invalid authorization'}), 403
        print('data', data)
        return f(*args, **kwargs)
    return decorated
 
# Create new user
@app.route('/auth/createuser', methods=['POST'])
def create_user():
    name = request.json['name']
    password = request.json['password']
    password1 = request.json['password1']
    if password != password1:
          return jsonify({'message' : 'Different password(s) supplied'}), 404
    for attr in request.json:
        request.json[attr] = request.json[attr].replace('/', '')
        if request.json[attr] == '':
          return jsonify({'message' : '{} not supplied'.format(attr)}), 404
    user_found = User.query.filter(User.name==name).first()
    user_found_dump = user_schema.dump(user_found)
    # print(user_found_dump)
    if len(user_found_dump):
        return jsonify({'message' : 'user exist already'}), 404

    hashed = generate_password_hash(password)
    print(hashed)
    user = User(name, hashed)
    db.session.add(user)
    db.session.commit()
    print(user_schema.dump(user))
    return jsonify({ 'data' : user_schema.dump(user), 'user' : user_schema.dump(user)['name'], 'message' : 'new user created'}), 201


# Sign in user
@app.route('/auth/signin', methods=['POST'])
def user_signin():
    # auth = request.get_json()
    # print(auth)
    name = request.json['name']
    password = request.json['password']
    for attr in request.json:
        request.json[attr] = request.json[attr].replace('/', '')
        if request.json[attr] == '':
          return jsonify({'message' : '{} not supplied'.format(attr)}), 404
    user_found = User.query.filter(User.name==name).first()
    user_found_dump = user_schema.dump(user_found)
    # print(len(user_found_dump), user_found_dump)
    if len(user_found_dump):
        pw = check_password_hash(user_found_dump['password'], password)
        if pw:
            print(user_found_dump)
            user_found_dump['password'] = ''
            print(user_found_dump)

            token = jwt.encode({'user' : user_found_dump, 'exp' : datetime.utcnow() +  timedelta(minutes=60)}, app.config['secret']) 
            # print('yes') if not token else print('no') 
            print(str(token))
            return jsonify({'user' : user_found_dump['name'], 'message' : 'user signed in', 'token' : str(token)}), 200
        return jsonify({'message' : 'invalid password'}), 404
    return jsonify({'message' : 'user not found'}), 404

    
#Get all users
@app.route('/auth/users', methods=['GET'])
# @token_required
def get_users():
    user_list = User.query.all()
    user_list_dump = users_schema.dump(user_list)
    # print(user_list_dump)
    if len(user_list_dump):
        return jsonify({'users' : user_list_dump, 'number_of_users' : len(user_list_dump) }), 200
    return jsonify({'message' : 'No user found'}), 404
    

# Create new report
@app.route('/report', methods=['POST'])
def add_report():
    name = request.json['name']
    mortality = request.json['mortality']
    dressed = request.json['dressed']
    consumption = request.json['consumption']
    feedbrand = request.json['feedbrand']
    jumbo = request.json['jumbo']
    extra = request.json['extra']
    large = request.json['large']
    small = request.json['small']
    pullet = request.json['pullet']
    crack = request.json['crack']
    wastage = request.json['wastage']
    medication = request.json['medication']
    for attr in request.json:
        request.json[attr] = request.json[attr].replace('/', '')
        if request.json[attr] == '':
          return jsonify({'message' : '{} not supplied'.format(attr)}), 404
    if 'date' in request.json:
        date = request.json['date']
        population = request.json['population']
        report_found = PenRecord.query.filter(PenRecord.name==name).order_by(PenRecord.date.desc()).all()
        report_found_dump = reports_schema.dump(report_found)
        for rep in report_found_dump:
            date_exist = rep['date'][8:10]
            # print(date_exist)

            if date == date_exist:
                return jsonify({'message' : 'record exist already'}), 404

        production = int(jumbo) + int(extra) + int(large) + int(small) + int(pullet) + int(crack) + int(wastage)
        report = PenRecord(name, population, mortality, dressed, consumption, feedbrand, production, jumbo, extra, large, small, pullet, crack, wastage, medication, date=c.replace(day=int(date)))
        db.session.add(report)
        db.session.commit()
        # print(report)
        return jsonify(report_schema.dump(report)), 201

    report_exist = PenRecord.query.filter(PenRecord.name==name).order_by(PenRecord.date.desc()).first()
    report_previous = PenRecord.query.filter(PenRecord.name==name).order_by(PenRecord.date.desc()).limit(2).all()
    report_exist_dump = report_schema.dump(report_exist)
    report_prev_dump = reports_schema.dump(report_previous)
    # print(report_prev_dump, report_prev_dump[0]['population'])
    x = datetime.now()
    
    if len(report_exist_dump) == 0:
        print('No previous day report to get population!')
        return jsonify({'message' : 'No previous day report to get population!'}), 404
    else:
        # print(report_exist_dump['date'], x)
        print(report_exist_dump['date'][8:10], x.strftime('%d'))
        if report_exist_dump['date'][8:10] == x.strftime('%d'):
            return jsonify({'message' : 'pen already has a record'}), 404
        # if len(report_prev_dump) == 2:
        elif int(x.strftime('%d')) - int(report_exist_dump['date'][8:10]) > int(1):
            return jsonify({'message' : 'Previous day report not available!'}), 404
        else:
            prev_pop = report_prev_dump[0]['population']
            prev_mort = report_prev_dump[0]['mortality']
            population = int(prev_pop) - int(prev_mort)
            production = int(jumbo) + int(extra) + int(large) + int(small) + int(pullet) + int(crack) + int(wastage)
             
            new_report = PenRecord.query.order_by(PenRecord.date.desc()).first()

            # print(report, new_report)
        return jsonify({ 'data' : report_schema.dump(new_report), 'message' : 'New report created!'}), 201


# Get all reports
@app.route('/report', methods=['GET'])
@app.route('/report/page/<int:page>/<int:pp>', methods=['GET'])
# @token_required
def get_reports(page=1, pp=3):
    # try:
    #     # reports = PenRecord.query.order_by(PenRecord.date.desc()).all()
    #     reports = PenRecord.query.order_by(PenRecord.date.desc()).paginate(page, per_page=6)
    #     result = reports_schema.dump(reports)
    # except e:
    #     flash('No report found!')
    #     reports = None
    #     result = reports_schema.dump(reports)

    reportAll = PenRecord.query.order_by(PenRecord.date.desc()).all()
    reportCount = len(reports_schema.dump(reportAll))
 
   
    if reportCount == 0:
        return jsonify({ 'message' : 'No report available' }), 404
    if reportCount % pp == 0:
        limit = math.floor(reportCount / pp)
    else:
        limit = math.floor(reportCount / pp) + 1

    print('report count {}, page {}, perPage {}, pages {} last page report count {}'.format(reportCount, page, pp, limit, reportCount - ((limit - 1) * pp)))
    if(page > limit):
        return jsonify({ 'message' : 'No report available beyond this point', 'prev' : bool(1), 'next': bool(0) }), 400
  
    reports = PenRecord.query.order_by(PenRecord.date.desc()).paginate(page, per_page=pp).items
    # print(page, limit, pp)
    result = reports_schema.dump(reports)
    
    return jsonify({ 'data' : result, 'page' : page, 'pages' : limit, 'prev' : bool(page > 1), 'next': bool(limit - page) }), 200

 
# Get all reports (by tag)
@app.route('/report/tag/<tag>', methods=['GET'])
@app.route('/report/tag/<tag>/<int:page>/<int:pp>', methods=['GET'])
def get_report_by_tag(tag, page = 1, pp = 6):
    report_tag = PenRecord.query.filter(PenRecord.name==str(tag)).order_by(PenRecord.date.desc())
    report_tag_dump = reports_schema.dump(report_tag)
    # print(report_tag_dump)
    reportCount = len(report_tag_dump)
    if reportCount == 0:
        return jsonify({ 'message' : 'No report available for {}'.format(tag) }), 404

    
    reports = report_tag.paginate(page, per_page=pp).items
    result = reports_schema.dump(reports)
    if reportCount % pp == 0:
        limit = math.floor(reportCount / pp)
    else:
        limit = math.floor(reportCount / pp) + 1
    return jsonify({ 'message' : 'reports for {}'.format(tag), 'data' : result, 'page' : page, 'pages' : limit, 'prev' : bool(page > 1), 'next': bool(limit - page) }), 200


# Get details of reports (by tag & days)
@app.route('/report/detail/<tag>', methods=['GET'])
@app.route('/report/detail/<tag>/<int:days>', methods=['GET'])
def get_report_by_details(tag = 'crack', days = 1):
    # report_tag = PenRecord.query.filter(PenRecord.crack).limit(int(days))
    reportCount = PenRecord.query.group_by(PenRecord.id, PenRecord.crack)
    report_count_dump = reports_schema.dump(reportCount)
    # print(report_tag_dump) 
    # print(reportCount)
    # reportCount = len(report_tag_dump)
    if reportCount == 0:
        return jsonify({ 'message' : 'No report available for {}'.format(tag) }), 404
    return jsonify({ 'message' : 'reportCount', 'data' : report_count_dump}), 200
  
    # reports = report_tag.paginate(page, per_page=pp).items
    # result = reports_schema.dump(reports)
    # if reportCount % pp == 0:
    #     limit = math.floor(reportCount / pp)
    # else:
    #     limit = math.floor(reportCount / pp) + 1
    # return jsonify({ 'message' : 'reports for {}'.format(tag), 'data' : result, 'page' : page, 'pages' : limit, 'prev' : bool(page > 1), 'next': bool(limit - page) }), 200

 
# Get single report
@app.route('/report/<id>', methods=['GET'])
def get_report(id):
    report = PenRecord.query.get(id)
    # print(report)
    if report is None:
        return jsonify({'message' : 'report not available!'}), 404
    
    return jsonify(report_schema.dump(report)), 200


# Update single report
@app.route('/report/<id>', methods=['PUT'])
def update_report(id):
    report = PenRecord.query.get(id)

    name = request.json['name']
    population = request.json['population']
    mortality = request.json['mortality']
    consumption = request.json['consumption']
    production = request.json['production']
    medication = request.json['medication']

    if report is None:
        return jsonify({'message' : 'report not available!'}), 404
    report.name = name
    report.population = population
    report.mortality = mortality
    report.consumption = consumption
    report.production = production
    report.medication = medication

    db.session.commit()

    # print(report)

    # return report_schema.jsonify(report)
    return jsonify({'message' : 'report successfully updated'}), 204
    # return make_response({'message' : 'report successfully updated'}, 204) 


# Delete single report
@app.route('/report/<id>', methods=['DELETE'])
@token_required
def delete_report(id):
    report = PenRecord.query.get(id)
    if report is None:
        return jsonify({'message' : 'report not found'}), 404

    db.session.delete(report)
    db.session.commit()
    # print(report)

    return jsonify({'message' : 'report successfully deleted'}), 200

print(len(data))
@app.route('/seed', methods=['GET', 'POST'])
def seed():
    record_exist = PenRecord.query.all()
    record_dump = reports_schema.dump(record_exist)
    # print(record_dump)
    if len(record_dump):
        return jsonify({ 'message' : 'DB already seeded!'})
   
    for rep in data:
        production = int(rep['jumbo'] + rep['extra'] + rep['large'] + rep['small'] + rep['pullet'] + rep['crack'] + rep['wastage'])
        
        consumption = math.floor(rep['population'] * .11 / 25)
        # print('day {}, mortality {}, production {}, population {}, consumption {}, '.format(rep['date'][8:10], rep['mortality'], production, rep['population'], consumption))

        dat = PenRecord(rep['name'], rep['population'], rep['mortality'], rep['dressed'], consumption, rep['feedbrand'], production, rep['jumbo'], rep['extra'], rep['large'], rep['small'], rep['pullet'], rep['crack'], rep['wastage'], rep['medication'], c.replace(day=int(rep['date'][8:10])))
        db.session.add(dat)
        db.session.commit()
    return jsonify({ 'message' : 'seeding completed'})


@app.route('/auth', methods=['GET'])
def seed_auth():
    auth_exist = User.query.filter(User.name == 'oba').first()
    if auth_exist:
        return jsonify({ 'message' : 'auth already seeded'})
    print(auth)
    auth_pass = generate_password_hash('pass')
    create_auth = User(auth['name'], auth_pass, auth['admin'])
    db.session.add(create_auth)
    db.session.commit()

    return jsonify({ 'message' : 'auth seeding completed'})

@app.route('/refresh', methods=['GET'])
def refresh_db():
    db.drop_all()
    print('dropped')
    db.create_all()
    print('created')
    seed()
    seed_auth()
    print('seeded')

    return jsonify({ 'message' : 'refresh completed'})

if __name__ == '__main__':
    app.run(debug = True)
