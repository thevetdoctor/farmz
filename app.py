from flask import Flask, request, jsonify, make_response
from flask import Flask, flash, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from flask_cors import CORS
import os

# print(os.environ['USERNAME'])

app = Flask(__name__)

CORS(app)

# if os.environ.get('USERNAME') == 'ACER':
#     ENV = 'dev'
# else:
ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:animalworld@localhost/flaskrest'
else:
    app.debug = False 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vxjxpdpdiwnrqw:55e5e567b888401056b662421a387e5e830a0a30fce8d64046f112d37b04135b@ec2-18-210-51-239.compute-1.amazonaws.com:5432/d5obp1t1cedffb'

print(ENV)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
marsh = Marshmallow(app)


UPLOAD_FOLDER = 'C:\\Users\\ACER\\Desktop\\projects'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4'}

# app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file',
                                    filename=filename))
    return render_template('upload.html')
    # return '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
    #   <input type=file name=file>
    #   <input type=submit value=Click2Upload>
    # </form>
    # '''


class PenRecord(db.Model):
    __tablename__ = 'penrecord'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    population = db.Column(db.Integer)
    mortality = db.Column(db.Integer)
    consumption = db.Column(db.Integer)
    production = db.Column(db.Integer)
    medication = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, name, population, mortality, consumption, production, medication, date=None):
        self.name = name
        self.population = population
        self.mortality = mortality
        self.consumption = consumption
        self.production = production
        self.medication = medication
        self.date = date

 
# Report Schema
class ReportSchema(marsh.Schema):
    class Meta:
        fields = ('id', 'name', 'population', 'mortality', 'consumption', 'production', 'medication', 'date')

# Init schema
# report_schema = ReportSchema(strict=True)
# reports_schema = ReportSchema(many=True, strict=True)
report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)

c = datetime.utcnow()
# d = datetime(2020, 3, 12)
# print(c, d, c.replace(day=9), d.replace(day=9))

# Root URL
@app.route('/')
def index():
    return jsonify({'message' : 'Welcome to Bafot Farms'}), 200


# Create new report
@app.route('/report', methods=['POST'])
def add_report():
    name = request.json['name']
    # population = request.json['population']
    mortality = request.json['mortality']
    consumption = request.json['consumption']
    production = request.json['production']
    medication = request.json['medication']
    if 'date' in request.json:
        date = request.json['date']
        population = request.json['population']
        report_found = PenRecord.query.filter(PenRecord.name==name).order_by(PenRecord.date.desc()).all()
        report_found_dump = reports_schema.dump(report_found)
        for rep in report_found_dump:
            date_exist = rep['date'][8:10]
            print(date_exist)
            if date == date_exist:
                return jsonify({'message' : 'record exist already'}), 404

        report = PenRecord(name, population, mortality, consumption, production, medication, date=c.replace(day=int(date)))
        db.session.add(report)
        db.session.commit()
        print(report)
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
            report = PenRecord(name, population, mortality, consumption, production, medication)
            db.session.add(report)
            db.session.commit()
            new_report = PenRecord.query.order_by(PenRecord.date.desc()).first()

            # print(report, new_report)
        return jsonify(report_schema.dump(new_report)), 201
        # return jsonify({'message' : 'pen already has a record2'}), 404


# Get all reports
@app.route('/report', methods=['GET'])
def get_reports():
    reports = PenRecord.query.order_by(PenRecord.date.desc()).all()
    result = reports_schema.dump(reports)
    # print(reports, result)
    if len(result) == 0:
        return jsonify({ 'message' : 'No report available' }), 200

    return jsonify(result), 200

 
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
    return jsonify({'message' : 'report successfully updated'}, 204)
    return make_response({'message' : 'report successfully updated'}, 204)


# Delete single report
@app.route('/report/<id>', methods=['DELETE'])
def delete_report(id):
    report = PenRecord.query.get(id)
    if report is None:
        return jsonify({'message' : 'report not found'}), 404

    db.session.delete(report)
    db.session.commit()
    # print(report)

    return jsonify({'message' : 'report successfully deleted'}), 200

if __name__ == '__main__':
    app.run(debug = True)
