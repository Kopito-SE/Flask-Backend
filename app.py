from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import pymysql
import sys

app = Flask(__name__)
app.secret_key = "supersecretkey"

# MySQL configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:osama4545@localhost/flask_auth"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

# Test database connection
def test_db_connection():
    try:
        with app.app_context():
            db.engine.connect()
        print("✅ Database connection successful!")
        return True
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required!") 
            return redirect(url_for("register"))
        
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("Username already exists!")
                return redirect(url_for("register"))
            
            # Create new user in database
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))
            
        except OperationalError:
            flash("Database connection error. Please try again later.")
            return redirect(url_for("register"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred during registration: {str(e)}")
            return redirect(url_for("register"))
            
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                session["user_id"] = user.id
                flash("Login successful!")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid credentials!")
                return redirect(url_for("login"))
                
        except OperationalError:
            flash("Database connection error. Please try again later.")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login first!")
        return redirect(url_for("login"))

    try:
        user = User.query.get(session["user_id"])
        if not user:
            session.pop("user_id", None)
            flash("User not found!")
            return redirect(url_for("login"))
        return render_template("dashboard.html", user=user)
    except OperationalError:
        flash("Database connection error.")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully!")
    return redirect(url_for("login"))

if __name__ == "__main__":
    # Test database connection before starting
    if test_db_connection():
        with app.app_context():
            try:
                db.create_all()
                print("✅ Database tables created successfully!")
            except Exception as e:
                print(f"❌ Error creating tables: {e}")
        app.run(debug=True)
    else:
        print("\n❌ Cannot start application due to database connection issues.")
        print("Please fix the database connection and try again.")