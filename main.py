from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from distutils.util import strtobool
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # 1st option
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

        # 2nd option
        # dictionary = {}
        # for column in self.__table__.columns:
        #     dictionary[column.name] = getattr(self, column.name)
        #
        # return dictionary


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random", methods=['GET'])
def get_request():
    all_the_cafes = Cafe.query.all()
    random_cafe = random.choice(all_the_cafes)

    # THE MOST EASIEST OPTION
    # cafe_dict = vars(random_cafe)
    # del cafe_dict["_sa_instance_state"]

    # TUTOR'S OPTION
    return random_cafe.to_dict()

    # THE MOST CUSTOMIZABLE OPTION
    # return jsonify(cafe={
    #     # Omit the id from the response
    #     # "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #
    #     # Put some properties in a sub-category
    #     "amenities": {
    #         "seats": random_cafe.seats,
    #         "has_toilet": random_cafe.has_toilet,
    #         "has_wifi": random_cafe.has_wifi,
    #         "has_sockets": random_cafe.has_sockets,
    #         "can_take_calls": random_cafe.can_take_calls,
    #         "coffee_price": random_cafe.coffee_price,
    #     }
    # })


@app.route("/all", methods=["GET"])
def second_get_request():
    all_cafes = Cafe.query.all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])  # DON'T FORGET ABOUT THE COMPREHENSION


@app.route("/search", methods=["GET"])
def third_get_request():
    user_query_parameter = request.args.get("loc")

    # FIRST METHOD
    # all_cafes = Cafe.query.all()
    # found_cafes = []
    # for cafe in all_cafes:
    #     if cafe.location == user_query_parameter:
    #         found_cafes.append(cafe.to_dict())
    #

    # SECOND METHOD
    # all_cafes = Cafe.query.all()
    # found_cafes = [cafe.to_dict() for cafe in all_cafes if cafe.location == user_query_parameter]

    # THIRD METHOD
    search_result = Cafe.query.filter_by(location=user_query_parameter).all()
    found_cafes = [cafe.to_dict() for cafe in search_result]

    if found_cafes:
        return jsonify(found_cafes=found_cafes)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_request():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=strtobool(request.form.get("has_sockets")),
        has_toilet=strtobool(request.form.get("has_toilet")),
        has_wifi=strtobool(request.form.get("has_wifi")),
        can_take_calls=strtobool(request.form.get("can_take_calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price")
    )

    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={"success": "Successfully added the new cafe."}), 200


## HTTP PUT/PATCH - Update Record

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_request(cafe_id):
    cafe_to_patch = Cafe.query.get(cafe_id)
    if cafe_to_patch:
        new_price = request.args.get("new_price")
        cafe_to_patch.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully updated the price"), 200
    else:
        return jsonify(fail="Sorry, a cafe with that id wasn't found in the database."), 404


## HTTP DELETE - Delete Record

@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_request(cafe_id):
    cafe_to_delete = Cafe.query.get(cafe_id)
    api_key_provided = request.args.get("api-key")
    if cafe_to_delete:
        if api_key_provided == "TopSecretAPIKey":
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(success="Successfully deleted the cafe from the database."), 200
        else:
            return jsonify(fail="Sorry, that's not allowed. Make sure you have the correct api_key."), 403

    else:
        return jsonify(fail="Sorry, a cafe with that id wasn't found in the database."), 404


if __name__ == '__main__':
    app.run(debug=True)
