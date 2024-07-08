#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):

    def get(self):

        response_dict_list = [n.to_dict() for n in Restaurant.query.all()]

        response = make_response(
            response_dict_list,
            200,
        )

        return response

class RestaurantByID(Resource):

    def get(self, id):

        response_dict = Restaurant.query.filter_by(id=id).first()

        if response_dict:
            response = make_response(
                response_dict.to_dict(),
                200,
            )
        else:
            response = make_response(
                {"error": "restaurant not found"},
                404
            )

        return response
    
    def delete(self, id):

        record = Restaurant.query.filter(Restaurant.id == id).first()

        if record:
            db.session.delete(record)
            db.session.commit()

            response_dict = {"message": "record successfully deleted"}

            response = make_response(
                response_dict,
                200
            )
        else:
            response = make_response(
                {"error": "restaurant not found"},
                404
            )

        return response
    
class Pizzas(Resource):

    def get(self):

        response_dict_list = [n.to_dict() for n in Pizza.query.all()]

        response = make_response(
            response_dict_list,
            200,
        )

        return response
    
class RestaurantPizzas(Resource):
     def post(self):
        try:            
            new_record = RestaurantPizza(
                price=request.form["price"],
                restaurant_id=request.form["restaurant_id"],
                pizza_id=request.form["pizza_id"]
            )

            db.session.add(new_record)
            db.session.commit()
            response = new_record.to_dict()
            response['pizza'] = new_record.pizza.to_dict(only=('id', 'name', 'ingredients'))
            response['restaurant'] = new_record.restaurant.to_dict(only=('id', 'name', 'address'))
            #return jsonify(response), 201

            return make_response(jsonify(response), 201)

        except Exception as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)

api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantByID, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")




if __name__ == "__main__":
    app.run(port=5555, debug=True)
