from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "volunteer_ai_secret"

DB_NAME = "database.db"

# -------------------------------------------------
# DATABASE INITIALIZATION (AUTO)
# -------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS opportunities (
        opportunity_id INTEGER PRIMARY KEY AUTOINCREMENT,
        required_skills TEXT,
        domain TEXT,
        location TEXT,
        duration TEXT
    )
    """)

    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect(DB_NAME)

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form["role"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (role, email, password) VALUES (?, ?, ?)",
                (role, email, password)
            )
            db.commit()
        except:
            pass
        db.close()
        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["role"] = request.form["role"]

        if session["role"] == "student":
            return redirect("/student")
        else:
            return redirect("/ngo")

    return render_template("login.html")

# ---------------- STUDENT DASHBOARD ----------------
@app.route("/student", methods=["GET", "POST"])
def student_dashboard():
    recommendations = []

    if request.method == "POST":
        skill = request.form["skill"]
        interest = request.form["interest"]
        location = request.form["location"]

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM opportunities")
        opportunities = cur.fetchall()

        # AI Recommendation (Content-Based Filtering)
        for opp in opportunities:
            score = 0
            if skill.lower() in opp[1].lower():
                score += 50
            if interest.lower() in opp[2].lower():
                score += 30
            if location.lower() in opp[3].lower():
                score += 20

            if score > 0:
                recommendations.append({
                    "skill": opp[1],
                    "domain": opp[2],
                    "location": opp[3],
                    "score": score
                })

        db.close()

    return render_template("student_dashboard.html", rec=recommendations)

# ---------------- NGO DASHBOARD ----------------
@app.route("/ngo", methods=["GET", "POST"])
def ngo_dashboard():
    if request.method == "POST":
        db = get_db()
        db.execute("""
        INSERT INTO opportunities (required_skills, domain, location, duration)
        VALUES (?, ?, ?, ?)
        """, (
            request.form["skills"],
            request.form["domain"],
            request.form["location"],
            request.form["duration"]
        ))
        db.commit()
        db.close()

    return render_template("ngo_dashboard.html")

# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)