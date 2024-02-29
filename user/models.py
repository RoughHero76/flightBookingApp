import bcrypt
import jwt
import time
from pymongo import MongoClient


class Admin:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def authenticate(self):
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        admins = db.admins

        # Check if admin exists and password matches
        admin_data = admins.find_one({"username": self.username})
        if admin_data and bcrypt.checkpw(
            self.password.encode("utf-8"), admin_data["password"]
        ):
            return True
        else:
            return False

    def authenticate_with_token(self):
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        admins = db.admins

        # Check if admin exists
        admin_data = admins.find_one({"username": self.username})
        if admin_data:
            return True
        else:
            return False

    def generate_token(self):
        payload = {
            "username": self.username,
            "exp": int(time.time()) + 3600,  # Token expires in 1 hour (3600 seconds)
        }
        token = jwt.encode(payload, "myKey", algorithm="HS256")
        return token

    def register(self):
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        admins = db.admins

        # Check if admin already exists
        if admins.find_one({"username": self.username}):
            return {
                "error": "Admin already exists"
            }, 400  # Returning error in JSON format

        # Hash the password
        hashed_password = bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt())

        # Insert new admin into the database
        admin_data = {"username": self.username, "password": hashed_password}
        admins.insert_one(admin_data)

        return {"message": "Admin registered successfully"}, 201

    def add_flight(self, flight_data):
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        flights = db.flights

        flight_number = flight_data.get("flight_number")
        # Check if flight already exists
        if flights.find_one({"flight_number": flight_number}):
            return {
                "error": "Flight already exists"
            }, 400  # Return status code 400 and error message

        # Insert new flight into the database
        flights.insert_one(flight_data)

        return {"message": "Flight added successfully"}, 201  # Return status code 201

    def remove_flight(self, flight_id):
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        flights = db.flights
        bookings = db.bookings

        # Check if there are any bookings for the specified flight ID
        existing_bookings_count = bookings.count_documents({"flight_number": flight_id})
        if existing_bookings_count > 0:
            # Remove all bookings for the specified flight ID
            bookings.delete_many({"flight_number": flight_id})

        # Remove the flight from the database
        result = flights.delete_one({"flight_number": flight_id})
        if result.deleted_count == 1:
            return {
                "message": "Flight and associated bookings removed successfully"
            }, 200
        else:
            return {"error": "Flight not found"}, 404

    def fetch_bookings_by_flight(flight_number):
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        bookings_collection = db["bookings"]

        # Query the database for bookings with the specified flight number
        bookings = list(bookings_collection.find({"flight_number": flight_number}))

        return bookings


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def authenticate(self):
        print("Authenticating user:", self.username)  # Debug statement
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        users = db.users

        # Check if user exists and password matches
        user_data = users.find_one({"username": self.username})
        if user_data:
            print("User found in database:", user_data)  # Debug statement
            if bcrypt.checkpw(self.password.encode("utf-8"), user_data["password"]):
                print("Password matched")  # Debug statement
                return True
            else:
                print("Password did not match")  # Debug statement
        else:
            print("User not found")  # Debug statement
        return False

    def generate_token(self):
        payload = {
            "username": self.username,
            "exp": int(time.time()) + 3600,  # Token expires in 1 hour (3600 seconds)
        }
        token = jwt.encode(payload, "myKey", algorithm="HS256")
        return token

    def register(self):
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        users = db.users

        # Check if user already exists
        if users.find_one({"username": self.username}):
            return {
                "error": "User already exists"
            }, 400  # Returning error in JSON format

        # Hash the password
        hashed_password = bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt())

        # Insert new user into the database
        user_data = {"username": self.username, "password": hashed_password}
        users.insert_one(user_data)

        return {"message": "User registered successfully"}, 201

    def user_authenticate_with_token(token):
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        users = db.users

        # Decode the token to extract the username
        try:
            decoded_token = jwt.decode(token, "myKey", algorithms=["HS256"])
            username = decoded_token["username"]
        except jwt.ExpiredSignatureError:
            return False  # Token expired
        except jwt.InvalidTokenError:
            return False  # Invalid token

        # Check if the user exists in the database
        user_data = users.find_one({"username": username})
        if user_data:
            return user_data
        else:
            return False

    def search_flights(flight_data):
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        flights = db.flights

        # Prepare the query
        query = {"date": flight_data["date"]}
        if flight_data.get("time"):
            query["time"] = flight_data["time"]

        # Search for flights
        result = flights.find(query)
        result_list = list(result)  # Convert the cursor to a list

        if not result_list:
            return {"message": "No flights found"}, 404

        return result_list, 200  # Return the list instead of the cursor

    def book_flight(username, flight_id):
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        bookings = db.bookings
        flights = db.flights

        # Check if the user has already booked the same flight
        existing_booking = bookings.find_one(
            {"username": username, "flight_number": flight_id}
        )
        if existing_booking:
            return {"error": "You have already booked this flight"}, 400

        # Get the flight data
        flight_data = flights.find_one({"flight_number": flight_id})
        if not flight_data or flight_data["seats"] <= 0:
            return {"error": "This flight is fully booked or does not exist"}, 400

        # Decrease the seat number
        flights.update_one({"flight_number": flight_id}, {"$inc": {"seats": -1}})

        # Create the booking data
        booking_data = {
            "username": username,
            "flight_number": flight_id,
            "departure": flight_data["departure"],
            "destination": flight_data["destination"],
            "date": flight_data["date"],
            "time": flight_data["time"],
        }

        # Insert the booking data into the database
        result = bookings.insert_one(booking_data)

        if result.inserted_id:
            booking_data["_id"] = str(result.inserted_id)  # Convert ObjectId to string
            return {
                "message": "Flight booked successfully",
                "booking": booking_data,
            }, 200
        else:
            return {"error": "Failed to book flight"}, 500

    def fetch_bookings(username):
        # Connect to MongoDB
        client = MongoClient("mongodb://127.0.0.1:27017")
        db = client["flightBooking"]
        bookings = db.bookings

        # Fetch the bookings for the user
        user_bookings = bookings.find({"username": username})

        # Convert the bookings to a list of dictionaries
        return list(user_bookings)
