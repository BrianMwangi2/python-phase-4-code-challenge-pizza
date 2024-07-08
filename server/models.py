from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Define custom naming convention for foreign keys
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initialize SQLAlchemy with the custom metadata
db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Relationship to RestaurantPizza
    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan")
    # Association proxy to access pizzas directly from restaurant
    pizzas = association_proxy("restaurant_pizzas", "pizza")
    # Serialization rules to exclude pizzas field
    serialize_rules = ("-pizzas",)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Relationship to RestaurantPizza
    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates="pizza", cascade="all, delete-orphan")
    # Association proxy to access restaurants directly from pizza
    restaurants = association_proxy("restaurant_pizzas", "restaurant")
    # Serialization rules to exclude restaurants field
    serialize_rules = ("-restaurants",)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, ForeignKey("pizzas.id"))
    restaurant_id = db.Column(db.Integer, ForeignKey("restaurants.id"))

    # Relationships to Pizza and Restaurant
    pizza = relationship("Pizza", back_populates="restaurant_pizzas")
    restaurant = relationship("Restaurant", back_populates="restaurant_pizzas")
    # Serialization rules to exclude circular references
    serialize_rules = ("-pizza.restaurant_pizzas", "-restaurant.restaurant_pizzas")

    # Validate price to ensure it's between 1 and 30
    @validates("price")
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("price must be between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
