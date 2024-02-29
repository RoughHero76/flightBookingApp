from flask import Flask, render_template
from user.routes import auth_bp

app = Flask(__name__)
app.register_blueprint(auth_bp)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


if __name__ == "__main__":
    app.run(debug=True)
