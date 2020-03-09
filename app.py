from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from db_config import *

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:animalworld@localhost/flaskrest'
else:
    app.debug = False 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vxjxpdpdiwnrqw:55e5e567b888401056b662421a387e5e830a0a30fce8d64046f112d37b04135b@ec2-18-210-51-239.compute-1.amazonaws.com:5432/d5obp1t1cedffb'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
marsh = Marshmallow(app)


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

    def __init__(self, name, population, mortality, consumption, production, medication):
        self.name = name
        self.population = population
        self.mortality = mortality
        self.consumption = consumption
        self.production = production
        self.medication = medication


# Report Schema
class ReportSchema(marsh.Schema):
    class Meta:
        fields = ('id', 'name', 'population', 'mortality', 'consumption', 'production', 'medication', 'date')

# Init schema
# report_schema = ReportSchema(strict=True)
# reports_schema = ReportSchema(many=True, strict=True)
report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)


# Root URL
@app.route('/')
def index():
    return jsonify({'message' : 'Welcome to Bafot Farms'})


# Create new report
@app.route('/report', methods=['POST'])
def add_report():
    name = request.json['name']
    population = request.json['population']
    mortality = request.json['mortality']
    consumption = request.json['consumption']
    production = request.json['production']
    medication = request.json['medication']
  
    report_exist = PenRecord.query.filter(PenRecord.name==name).first()
    report_dump = report_schema.dump(report_exist)
    x = datetime.now()
    if len(report_dump) != 0:
        # print(report_dump['date'][8:10], x.strftime('%d'))
        if report_dump['date'][8:10] == x.strftime('%d'):
            return jsonify({'message' : 'pen already has a record'})

    report = PenRecord(name, population, mortality, consumption, production, medication)
    db.session.add(report)
    db.session.commit()
    new_report = PenRecord.query.order_by(PenRecord.date.desc()).first()

    # print(report, new_report)
    return report_schema.jsonify(new_report)


# Get all reports
@app.route('/report', methods=['GET'])
def get_reports():
    reports = PenRecord.query.all()
    result = reports_schema.dump(reports)
    # print(reports, result)
    if len(result) == 0:
        return jsonify({ 'message' : 'No report available' })

    return jsonify(result)


# Get single report
@app.route('/report/<id>', methods=['GET'])
def get_report(id):
    report = PenRecord.query.get(id)
    # print(report)

    return report_schema.jsonify(report)


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
        return jsonify({'message' : 'report not available!'})
    report.name = name
    report.population = population
    report.mortality = mortality
    report.consumption = consumption
    report.production = production
    report.medication = medication

    db.session.commit()

    # print(report)

    # return report_schema.jsonify(report)
    return jsonify({'message' : 'report successfully updated'})


# Delete single report
@app.route('/report/<id>', methods=['DELETE'])
def delete_report(id):
    report = PenRecord.query.get(id)
    if report is None:
        return jsonify({'message' : 'report not found'})

    db.session.delete(report)
    db.session.commit()
    # print(report)

    return jsonify({'message' : 'report successfully deleted'})

if __name__ == '__main__':
    app.run(debug = True)
