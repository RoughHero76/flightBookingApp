# Flight Booking System

This project is a simple flight booking system implemented using Flask, MongoDB, and JWT for authentication.

## Features

- User registration and authentication
- Admin registration and authentication
- Adding, removing, and searching for flights

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/RoughHero76/flightBookingApp.git
   ```

2. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MongoDB:**
   - Install MongoDB on your local machine or use a cloud-based MongoDB service.
   - Update the MongoDB connection URI in the code to point to your MongoDB instance.

4. **Run the Flask application:**

   ```bash
   python app.py
   ```

## Usage

1. Register as a user or admin using the provided registration endpoints.
2. Log in with your credentials to obtain a JWT token.
3. Use the token to access protected endpoints such as adding, removing, or searching for flights.
4. Log out by deleting or invalidating the token.

## Endpoints

- `POST /register/user`: Register a new user.
- `POST /register/admin`: Register a new admin.
- `POST /login/user`: Log in as a user.
- `POST /login/admin`: Log in as an admin.
- `GET /admin_dashboard`: Admin dashboard (requires admin authentication).
- `GET /user_dashboard`: User dashboard (requires user authentication).
- `POST /add_flight`: Add a new flight (requires admin authentication).
- `POST /remove_flight`: Remove a flight (requires admin authentication).
- `POST /search_flights`: Search for flights (requires user authentication).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
