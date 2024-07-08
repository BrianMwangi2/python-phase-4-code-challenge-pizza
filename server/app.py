from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

# Set up base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize Flask-Migrate for database migrations
migrate = Migrate(app, db)

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-RESTful API
api = Api(app)

# Define a route for the home page
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Resource for handling requests to /restaurants
class RestaurantsResource(Resource):
    def get(self):
        # Get all restaurants and serialize the response
        restaurants = Restaurant.query.all()
        response = [restaurant.to_dict(only=("id", "name", "address")) for restaurant in restaurants]
        return make_response(jsonify(response), 200)

# Resource for handling requests to /restaurants/<id>
class RestaurantResource(Resource):
    def get(self, id):
        # Get a restaurant by ID and serialize the response
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return make_response(jsonify(restaurant.to_dict()), 200)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    def delete(self, id):
        # Delete a restaurant by ID
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response(jsonify({"message": "Restaurant deleted"}), 204)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

# Resource for handling requests to /pizzas
class PizzasResource(Resource):
    def get(self):
        # Get all pizzas and serialize the response
        pizzas = Pizza.query.all()
        response = [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas]
        return make_response(jsonify(response), 200)

# Resource for handling requests to /restaurant_pizzas
class RestaurantPizzasResource(Resource):
    def post(self):
        # Handle POST request to create a new restaurant-pizza relationship
        data = request.get_json()
        try:
            price = data['price']
            # Validate price
            if price < 1 or price > 30:
                return make_response(jsonify({"errors": ["validation errors"]}), 400)
            # Create new RestaurantPizza object
            new_restaurant_pizza = RestaurantPizza(**data)
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)
        except KeyError as e:
            # Handle missing keys in the request data
            return make_response(jsonify({"errors": [f"Missing key: {str(e)}"]}), 400)
        except Exception as e:
            # Handle other exceptions
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 400)
        finally:
            db.session.close()

# Add resources to the API
api.add_resource(RestaurantsResource, "/restaurants")
api.add_resource(RestaurantResource, "/restaurants/<int:id>")
api.add_resource(PizzasResource, "/pizzas")
api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")

# Run the app
if __name__ == "__main__":
    app.run(port=5555, debug=True)
