from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    user_favorite = db.relationship("Favorite", uselist=True, backref="user")

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planet_name = db.Column(db.String(50), unique=False, nullable=False)
    population = db.Column(db.Integer, unique=False, nullable=False)
    planets_favorite = db.relationship("Favorite", uselist=True, backref="planets")

class Characters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_name = db.Column(db.String(50), unique=False, nullable=False)
    character_age = db.Column(db.Integer, unique=False, nullable=True)
    characters_favorite = db.relationship("Favorite", uselist=True, backref="characters")

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    planets_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    characters_id = db.Column(db.Integer, db.ForeignKey('characters.id'))



   
    