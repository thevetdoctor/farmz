from app import app, db

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