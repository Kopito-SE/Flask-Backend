from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy.sql.functions import user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:osama4545@localhost/flask_auth"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

# Remove the users dictionary - we'll use the database instead

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password required!") 
            return redirect(url_for("register"))
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!")
            return redirect(url_for("register"))
        
        # Create new user in database
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
       
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful!")
            return redirect(url_for("login"))
        except:
            db.session.rollback()
            flash("An error occurred during registration!")
            return redirect(url_for("register"))
            
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Query user from database
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful!")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!")
            return redirect(url_for("login"))
            
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first!")
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    return f"Welcome {user.username} to your dashboard!"
@app.route("/logout")
def logout():
    session.pop("user_id",None)
    flash("You have been logged out!")
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)