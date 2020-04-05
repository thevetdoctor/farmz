from flaskresty import db, marsh
from datetime import datetime

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

class FeedStock(db.Model):
    __tablename__ = 'feedstock'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, quantity, date=None):
        self.name = name
        self.quantity = quantity
        self.date = date

 
# Report Schema
class ReportSchema(marsh.Schema):
    class Meta:
        fields = ('id', 'name', 'population', 'mortality', 'dressed', 'consumption', 'feedbrand', 'production', 'jumbo', 'extra', 'large', 'small', 'pullet', 'crack', 'wastage', 'medication', 'date')

# User Schema
class UserSchema(marsh.Schema):
    class Meta:
        fields = ('id', 'name', 'password', 'admin', 'date')

# FeedStock Schema
class FeedStockSchema(marsh.Schema):
    class Meta:
        fields = ('id', 'name', 'quantity', 'date')

# Init schema
# report_schema = ReportSchema(strict=True)
# reports_schema = ReportSchema(many=True, strict=True)
report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

feedstock_schema = FeedStockSchema(many=True)