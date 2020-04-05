from flask import request, jsonify,render_template, redirect, url_for, make_response
from flaskresty import app, db
from flaskresty.models import PenRecord, User, FeedStock, reports_schema, report_schema, users_schema, user_schema, feedstock_schema
from functools import wraps
from datetime import datetime, timedelta
from flaskresty.seed import auth, dbase, feed_seed
from werkzeug.security import generate_password_hash, check_password_hash
import jwt, math

c = datetime.utcnow()

# Root URL
@app.route('/')
def index():
    return jsonify({'message' : 'Welcome to Bafot Farms'}), 200

# decorator function
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
        # print('data', data)
        return f(data, *args, **kwargs)
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
    if len(user_found_dump):
        pw = check_password_hash(user_found_dump['password'], password)
        if pw:
            user_found_dump['password'] = ''
            token = jwt.encode({'user' : user_found_dump, 'exp' : datetime.utcnow() +  timedelta(minutes=60)}, app.config['secret']) 
            return jsonify({'user' : user_found_dump['name'], 'isAdmin': user_found_dump['admin'], 'message' : 'user signed in', 'token' : str(token)}), 200
        return jsonify({'message' : 'invalid password'}), 404
    return jsonify({'message' : 'user not found'}), 404
    
#Get all users
@app.route('/auth/users', methods=['GET'])
# @token_required
def get_users():
    user_list = User.query.all()
    user_list_dump = users_schema.dump(user_list)
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
        if len(date) <= 2:
            return jsonify({ 'message': 'Date should be minimum of 2 digits!'}), 404
        population = request.json['population']
        report_found = PenRecord.query.filter(PenRecord.name==name).order_by(PenRecord.date.desc()).all()
        report_found_dump = reports_schema.dump(report_found)
        for rep in report_found_dump:
            date_exist = rep['date'][8:10]

            if date == date_exist:
                return jsonify({'message' : 'Record exist already'}), 404

        production = int(jumbo) + int(extra) + int(large) + int(small) + int(pullet) + int(crack) + int(wastage)
        print(date, c.replace(month=3))
        report = PenRecord(name, population, mortality, dressed, consumption, feedbrand, production, jumbo, extra, large, small, pullet, crack, wastage, medication, date=c.replace(day=int(date)))
        db.session.add(report)
        db.session.commit()
        # print(report)
        return jsonify({ 'data' : report_schema.dump(report), 'message' : 'New report created!'}), 201

    report_exist = PenRecord.query.filter(PenRecord.name==name).order_by(PenRecord.date.desc()).first()
    report_previous = PenRecord.query.filter(PenRecord.name==name).order_by(PenRecord.date.desc()).limit(2).all()
    report_exist_dump = report_schema.dump(report_exist)
    report_prev_dump = reports_schema.dump(report_previous)
    print(len(report_prev_dump), len(report_prev_dump))
    x = datetime.now()
    
    if len(report_exist_dump) == 0:
        print('No existing report to get population!')
        return jsonify({'message' : 'No existing report to get population!'}), 404
    else:
        print(report_exist_dump['date'][8:10], report_exist_dump['date'][5:7], x.strftime('%d'), x.strftime('%m'))
        if report_exist_dump['date'][5:7] != x.strftime('%m'):
            return jsonify({'message' : 'Please fill missing records'}), 404
        if report_exist_dump['date'][8:10] == x.strftime('%d'):
            print('pen already has a record')
            return jsonify({'message' : 'Pen already has a record'}), 404
        # if len(report_prev_dump) == 2:
        elif int(x.strftime('%d')) - int(report_exist_dump['date'][8:10]) > int(1):
            return jsonify({'message' : 'Previous day report not available!'}), 404
        else:
            prev_pop = report_prev_dump[0]['population']
            prev_mort = report_prev_dump[0]['mortality']
            population = int(prev_pop) - int(prev_mort)
            production = int(jumbo) + int(extra) + int(large) + int(small) + int(pullet) + int(crack) + int(wastage)
             
            new_report = PenRecord(name, population, mortality, dressed, consumption, feedbrand, production, jumbo, extra, large, small, pullet, crack, wastage, medication)
            db.session.add(new_report)
            db.session.commit()

            print(new_report)
        return jsonify({ 'data' : report_schema.dump(new_report), 'message' : 'New report created!'}), 201

# Get all reports
@app.route('/report', methods=['GET'])
@app.route('/report/page/<int:page>/<int:pp>', methods=['GET'])
# @token_required
def get_reports(page=1, pp=3):
    # print(data, 'hey')
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
    return jsonify({'message' : 'report successfully updated'}), 204

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

@app.route('/seed/', methods=['GET', 'POST'])
def seed():
    record_exist = PenRecord.query.all()
    record_dump = reports_schema.dump(record_exist)
    # print(record_dump)
    if len(record_dump):
        return jsonify({ 'message' : 'DB already seeded!'})
   
    print('dbase :', len(dbase['data'])) 
    # for rep in data:
    for rep in dbase['data']:
        production = int(rep['jumbo'] + rep['extra'] + rep['large'] + rep['small'] + rep['pullet'] + rep['crack'] + rep['wastage'])
        
        consumption = math.floor(rep['population'] * .11 / 25)

        month_input = int(rep['date'][5:7])
        day_input = int(rep['date'][8:10])
        current_date = c.replace(month=month_input, day=day_input)
        # current_date = c.replace(day=day_input)
        # print('day:', day_input,'month:', month_input, current_date)
        data_unit = PenRecord(rep['name'], rep['population'], rep['mortality'], rep['dressed'], consumption, rep['feedbrand'], production, rep['jumbo'], rep['extra'], rep['large'], rep['small'], rep['pullet'], rep['crack'], rep['wastage'], rep['medication'], current_date)
        db.session.add(data_unit)
        db.session.commit()
    return jsonify({ 'message' : 'seeding completed'})

@app.route('/auth', methods=['GET'])
def seed_auth():
    auth_exist = User.query.filter(User.name == 'oba').first()
    if auth_exist:
        return jsonify({ 'message' : 'auth already seeded'})
    # print(auth)
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

@app.route('/clear', methods=['GET'])
def clear_db():
    print('clearing')
    db.drop_all()
    print('dropped')
    db.create_all()
    return jsonify({ 'message' : 'DB cleared'})

@app.route('/clearfeed', methods=['GET'])
def clear_feed():
    print('clearing feed table')
    db.session.query(FeedStock).delete()
    db.session.commit()
    return jsonify({ 'message' : 'Feed table cleared'})

#Get all feedstock
@app.route('/feed', methods=['GET'])
# @token_required
def get_feedstock():
    last_feed_received = db.session.query(FeedStock.name, FeedStock.quantity, FeedStock.date).group_by(FeedStock.quantity, FeedStock.name, FeedStock.date).order_by(FeedStock.name, FeedStock.date.desc()).all()
    feed_received = db.session.query(FeedStock.name, db.func.sum(FeedStock.quantity)).group_by(FeedStock.name).all()
    feed_consumed_tilldate = db.session.query(PenRecord.feedbrand, db.func.sum(PenRecord.consumption) * 25).group_by(PenRecord.feedbrand).all()
    feed_consumed_daily = db.session.query(PenRecord.feedbrand, PenRecord.consumption, PenRecord.date).order_by(PenRecord.date.desc()).limit(6).all()
    # print(feed_consumed_daily)
    filtered = []
    daily_feed = []
    for f in feed_consumed_daily:
        if f[0] not in filtered:
            filtered.append(f[0])
            daily_feed.append(f)
    # print(daily_feed, filtered.index('olam layer1'))
    list = []  
    check = []
    count = 0
    for l in last_feed_received:
        if l[0] not in check:
            list.append(last_feed_received[count])
            check.append(l[0])
        count += 1
    # print(list, check)
    output = []
    for i in feed_received:
        x = { 'name': i[0], 'feed received': i[1], 'feed consumed': 0, 'daily consumption': 0 }
        if i[0] in filtered:
            x['daily consumption'] = daily_feed[filtered.index(i[0])][1]
        for j in feed_consumed_tilldate:
            if i[0] == j[0]:
                x['feed consumed'] = j[1]
            
        output.append(x)
    for r in output:
        for p in list: 
            if p[0] == r['name']:
                obj = { 'quantity' : p[1], 'date': p[2] }
                r['supplied'] = obj
    # print(output)
    if len(output):
        return jsonify({'feedstock' : output}), 200
    return jsonify({'message' : 'No feed in stock'}), 404

@app.route('/feed/seed', methods=['GET'])
def seed_feed():
    feed_exist = FeedStock.query.all()
    feed_exist_dump = feedstock_schema.dump(feed_exist)
    if feed_exist_dump:
        return jsonify({ 'message' : 'feedstock already seeded'})
    for feed in feed_seed:
        if 'date' not in feed:
            seed_feedstock = FeedStock(feed['name'], feed['quantity'])
            db.session.add(seed_feedstock)
            db.session.commit()
        else:
            seed_feedstock = FeedStock(feed['name'], feed['quantity'], feed['date'])
            db.session.add(seed_feedstock)
            db.session.commit()
    return jsonify({ 'message' : 'feedstock seeding completed', 'feedstock' : feed_exist_dump })
    
