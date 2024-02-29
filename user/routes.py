import jwt
from flask import Blueprint, request, jsonify, render_template, Response
from .models import User, Admin
from bson import json_util
import json

auth_bp = Blueprint("auth", __name__)

# Registration routes


@auth_bp.route("/register/user", methods=["POST"])
def user_register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User(username, password)
    result, status_code = user.register()
    if status_code == 201:
        return jsonify(result), status_code
    else:
        return jsonify(result), status_code


@auth_bp.route("/register/admin", methods=["POST"])
def admin_register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    admin = Admin(username, password)
    result, status_code = admin.register()
    if status_code == 201:
        return jsonify(result), status_code
    else:
        return jsonify(result), status_code


# Login routes


@auth_bp.route("/login/admin", methods=["POST"])
def admin_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    admin = Admin(username, password)
    if admin.authenticate():
        token = admin.generate_token()
        print("Generated token:", token)  # Debug statement
        try:
            decoded_token = jwt.decode(token, "myKey", algorithms=["HS256"])
            print("Decoded token payload:", decoded_token)  # Debug statement
            return jsonify({"message": "Admin authenticated", "token": token}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@auth_bp.route("/login/user", methods=["POST"])
def user_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User(username, password)
    if user.authenticate():
        token = user.generate_token()
        return jsonify({"message": "User authenticated", "token": token}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@auth_bp.route("/admin_dashboard", methods=["GET"])
def admin_dashboard():
    token = request.args.get("token")
    if token:
        try:
            decoded_token = jwt.decode(token, "myKey", algorithms=["HS256"])
            username = decoded_token["username"]
            return render_template("admin_dashboard.html", username=username)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    else:
        return jsonify({"error": "Token not provided"}), 401


@auth_bp.route("/user_dashboard", methods=["GET"])
def user_dashboard():
    token = request.args.get("token")
    if token:
        try:
            decoded_token = jwt.decode(token, "myKey", algorithms=["HS256"])
            username = decoded_token["username"]
            return render_template("user_dashboard.html", username=username)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    else:
        return jsonify({"error": "Token not provided"}), 401

    # add flights and remove flights


@auth_bp.route("/add_flight", methods=["POST"])
def add_flight():
    data = request.get_json()
    flight_data = {
        "flight_number": data.get("flight_number"),
        "departure": data.get("departure"),
        "destination": data.get("destination"),
        "date": data.get("date"),
        "time": data.get("time"),
        "seats": 60,  # Default seat value
        # Add other flight details as needed
    }
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Authorization header not provided"}), 401

    # Split the auth_header into 'Bearer' and the token
    parts = auth_header.split()

    if parts[0].lower() != "bearer":
        return jsonify({"error": "Invalid token header"}), 401
    if len(parts) == 1:
        return jsonify({"error": "Token not found"}), 401
    if len(parts) > 2:
        return jsonify({"error": "Token header must not contain spaces"}), 401

    token = parts[1]

    try:
        decoded_token = jwt.decode(token, "myKey", algorithms=["HS256"])
        username = decoded_token["username"]
        admin = Admin(username, None)
        if admin.authenticate_with_token():
            if (
                not flight_data["flight_number"]
                or not flight_data["departure"]
                or not flight_data["destination"]
                or not flight_data["date"]
                or not flight_data["time"]
            ):
                return jsonify({"error": "Flight details not provided"}), 400

            result, status_code = admin.add_flight(flight_data)
            return jsonify(result), status_code
        else:
            return jsonify({"error": "Unauthorized"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401


@auth_bp.route("/remove_flight", methods=["POST"])
def remove_flight():
    data = request.get_json()
    flight_id = data.get("flight_id")
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Authorization header not provided"}), 401

    # Split the auth_header into 'Bearer' and the token
    parts = auth_header.split()

    if parts[0].lower() != "bearer":
        return jsonify({"error": "Invalid token header"}), 401
    if len(parts) == 1:
        return jsonify({"error": "Token not found"}), 401
    if len(parts) > 2:
        return jsonify({"error": "Token header must not contain spaces"}), 401

    token = parts[1]

    try:
        decoded_token = jwt.decode(token, "myKey", algorithms=["HS256"])
        username = decoded_token["username"]
        admin = Admin(username, None)  # No need for password to perform admin actions
        if admin.authenticate_with_token():
            result, status_code = admin.remove_flight(flight_id)
            return jsonify(result), status_code
        else:
            return jsonify({"error": "Unauthorized"}), status_code
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), status_code
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), status_code


# Other routes for user actions


@auth_bp.route("/search_flights", methods=["POST"])
def search_flights():
    # Get the JWT token from the Authorization header
    token = request.headers.get("Authorization").split(" ")[1]

    # Verify the JWT token and get the user
    user = User.user_authenticate_with_token(token)
    if not user:
        print("Invalid token")
        return jsonify({"message": "Invalid token"}), 401

    # Get the date and time from the request body
    data = request.get_json()
    date = data.get("date")
    time = data.get("time")

    print(f"Date: {date}, Time: {time}")  # Debugging line

    # Prepare the flight data
    flight_data = {"date": date}
    if time:
        flight_data["time"] = time

    # Search for flights
    flights, status_code = User.search_flights(flight_data)

    # If no flights were found, return the message
    if status_code == 404:
        return jsonify(flights), status_code

    # Convert the cursor to a list of dictionaries
    flight_list = [json.loads(json_util.dumps(flight)) for flight in flights]

    print(f"Flights: {flight_list}")  # Debugging line

    return jsonify(flight_list), status_code


@auth_bp.route("/book_flight", methods=["POST"])
def book_flight():
    token = request.headers.get("Authorization").split(" ")[1]
    user_data = User.user_authenticate_with_token(token)

    if not user_data:
        print("Invalid token")
        return jsonify({"message": "Invalid token"}), 401

    data = request.get_json()
    print(f"Data: {data}")  # Debugging line
    flight_id = data.get("flight_id")

    if user_data and flight_id:
        result, status_code = User.book_flight(user_data["username"], flight_id)
        return jsonify(result), status_code
    else:
        return jsonify({"error": "Missing user or flight id"}), 400


@auth_bp.route("/fetch_bookings", methods=["GET"])
def fetch_bookings():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 401

    token = auth_header.split(" ")[1]
    user_data = User.user_authenticate_with_token(token)

    # Fetch the bookings for the current user
    bookings = User.fetch_bookings(user_data["username"])

    # Convert the bookings to a list of dictionaries
    bookings_list = [booking for booking in bookings]

    # Check if the list is empty
    if not bookings_list:
        return jsonify({"message": "No bookings found"}), 200

    # Convert ObjectId to string
    for booking in bookings_list:
        booking["_id"] = str(booking["_id"])

    return jsonify(bookings_list), 200


@auth_bp.route("/view_bookings_by_flight", methods=["GET"])
def view_bookings_by_flight():
    flight_number = request.args.get("flight_number")
    if not flight_number:
        return jsonify({"error": "Missing flight_number parameter"}), 400

    bookings = Admin.fetch_bookings_by_flight(flight_number)
    # Convert ObjectId to string for JSON serialization
    for booking in bookings:
        booking["_id"] = str(booking["_id"])

    # Serialize bookings to JSON
    serialized_bookings = json_util.dumps(bookings)

    return Response(serialized_bookings, mimetype="application/json")
