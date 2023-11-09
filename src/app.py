"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/test', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def list_characters():
    people = People.query.all()
    people_list =[]
    for item in people:
        people_list.append(item.serialize())
    return jsonify(people_list), 200 

@app.route('/people/<int:theid>', methods=['GET'])
def characters_by_id(theid=None):
    people = People.query.get(theid)
    if people is None:
        return jsonify({"Menssage": "People does not exist yet"}), 404 

    return jsonify(people.serialize(), 200)

@app.route('/planets', methods=['GET'])
def planets_list():
    planet = Planets.query.all()
    planet_list = []
    for item in planet:
        planet_list.append(item.serialize())
    return jsonify(planet_list), 200

# planets_id
@app.route('/planets/<int:theid>', methods=['GET'])
def planets_by_id(theid=None):
    planet = Planets.query.get(theid)
    if planet is None:
        return jsonify({"Menssage":"Planet does not exist yet"}), 404
    else:
        return jsonify(planet.serialize()), 200
    
@app.route('/user', methods=['GET'])
def all_users():
    user = User.query.all()
    user_list = []
    for item in user:
        user_list.append(item.serialize())
    return jsonify(user_list), 200

@app.route('/user/favorites/<int:theid>', methods=['GET'])
def get_user_favorites(theid=None):
    if theid is None:
        return jsonify({"Menssage":"User not found"}), 404
     
    
    favorites = Favorite.query.filter_by(user_id=theid).all()
    if favorites is None:
        return jsonify({"Menssage":"This user has no favorites"})
    favorites_list = []
    for item in favorites:
        favorites_list.append(item.serialize())
    return jsonify(favorites_list), 200

@app.route('/favorites/planets/<int:planets_number>/<int:user_number>', methods=['POST'])
def add_planets_favorites(planets_number, user_number): 
    favorite = Favorite.query.filter_by(planets_id = planets_number, user_id = user_number).first()

    user = User.query.get(user_number)

    if user is None:
        return jsonify({"Message":"User does not exist yet"}), 404

    if favorite is not None:
        return jsonify({"Message":"This favorite already exist"})

    add_favorite = Favorite(user_id = user_number, planets_id = planets_number)
    db.session.add(add_favorite)
    

    try:
        db.session.commit()
        return jsonify({"Menssage":"The favorite was added"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"Menssage":f"{error}"})
    
@app.route('/favorites/people/<int:people_number>/<int:user_number>', methods=['POST'])
def add_people_favorites(people_number, user_number):
    favorite = Favorite.query.filter_by(user_id = user_number, people_id = people_number).first()

    user = User.query.get(user_number)

    if user is None:
        return jsonify({"Menssge":"User does not exist yet"})
    
    if favorite is not None:
        return jsonify({"Menssage":"This favorite already exist"})
    
    add_favorite = Favorite(user_id = user_number, people_id = people_number)
    db.session.add(add_favorite)

    try:
        db.session.commit()
        return jsonify({"Message":"Favorite was added"})
    except Exception as error:
        db.session.rollback()
        return jsonify({"Message":f"{error}"}), 500

@app.route('/favorites/planets/<int:planets_number>/<int:user_number>', methods=['DELETE'])
def delete_favorite(planets_number, user_number):
    favorite = Favorite.query.filter_by(user_id = user_number, planets_id = planets_number).first()

    if favorite is None:
        return jsonify({"Message":"Favorite does not exist"}), 404

    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"Message":"This favorite was deleted"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"Message":f"{error}"}), 500
    
@app.route('/favorites/people/<int:people_number>/<int:user_number>', methods=['DELETE'])
def delete_people_favorite(people_number, user_number):
    favorite = Favorite.query.filter_by(user_id = user_number, people_id = people_number).first()

    if favorite is None:
        return jsonify({"Menssage":"Favorite does not exist"}), 404
    
    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"Message":"This favorite was deleted"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"Message":f"{error}"}, 500)



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
