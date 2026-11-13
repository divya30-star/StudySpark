import os
import sqlite3
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "platform.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key-for-deployment")


# ---------------- DATABASE ----------------

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT NOT NULL,
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
    );

    CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        quiz_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        total INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
    );

    CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        subject TEXT NOT NULL,
        front TEXT NOT NULL,
        back TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # Add starter content only the first time the database is created.
    quiz_count = db.execute("SELECT COUNT(*) FROM quizzes").fetchone()[0]
    if quiz_count == 0:
        db.execute(
            "INSERT INTO quizzes (title, subject, description) VALUES (?, ?, ?)",
            ("Python Basics", "Programming", "A beginner-friendly Python quiz.")
        )
        quiz_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        starter_questions = [
            ("Which keyword is used to define a function in Python?", "func", "def", "function", "define", "B"),
            ("Which data type stores True or False?", "String", "Integer", "Boolean", "List", "C"),
            ("What is the output of 3 ** 2?", "6", "9", "5", "8", "B"),
            ("Which brackets are used to create a Python list?", "()", "{}", "[]", "<>", "C"),
            ("Which function displays output in Python?", "input()", "show()", "print()", "display()", "C"),
            ("Which symbol starts a comment in Python?", "//", "#", "/*", "--", "B"),
            ("Which method adds an item to the end of a list?", "append()", "add_end()", "insert_end()", "push()", "A"),
            ("Which loop repeats while a condition is true?", "for", "repeat", "while", "loop", "C"),
            ("Which operator checks equality?", "=", "==", "!=", ":=", "B"),
            ("Which keyword is used for a conditional branch?", "when", "if", "check", "case", "B"),
        ]
        db.executemany("""
            INSERT INTO questions
            (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [(quiz_id, *q) for q in starter_questions])

    card_count = db.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0]
    if card_count == 0:
        starter_cards = [
            (None, "Python", "What is Python?", "A high-level, general-purpose programming language."),
            (None, "Python", "What is a variable?", "A named place used to store a value."),
            (None, "Python", "What does len() do?", "It returns the number of items in an object."),
            (None, "Python", "What is a list?", "An ordered, changeable collection of items."),
            (None, "Web", "What does HTML stand for?", "HyperText Markup Language."),
            (None, "Web", "What is CSS used for?", "Styling and laying out web pages."),
        ]
        db.executemany(
            "INSERT INTO flashcards (user_id, subject, front, back) VALUES (?, ?, ?, ?)",
            starter_cards
        )

    db.commit()
    db.close()


# ---------------- LOGIN HELPERS ----------------

def login_required(view_function):
    @wraps(view_function)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "info")
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)
    return wrapped


# ---------------- WEBSITE PAGES ----------------

@app.route("/")
def home():
    db = get_db()
    quizzes = db.execute("SELECT * FROM quizzes ORDER BY id").fetchall()
    db.close()
    return render_template("index.html", quizzes=quizzes)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 3:
            flash("Username must contain at least 3 characters.", "error")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "error")
            return render_template("register.html")

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            db.commit()
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That username is already taken.", "error")
        finally:
            db.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        db.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))

        flash("Incorrect username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    attempts = db.execute("""
        SELECT attempts.*, quizzes.title
        FROM attempts JOIN quizzes ON attempts.quiz_id = quizzes.id
        WHERE attempts.user_id = ?
        ORDER BY attempts.created_at DESC LIMIT 5
    """, (session["user_id"],)).fetchall()
    summary = db.execute("""
        SELECT COUNT(*) AS count, COALESCE(AVG(score * 100.0 / total), 0) AS average
        FROM attempts WHERE user_id = ?
    """, (session["user_id"],)).fetchone()
    db.close()
    return render_template("dashboard.html", attempts=attempts, summary=summary)


@app.route("/quiz/<int:quiz_id>")
@login_required
def quiz_page(quiz_id):
    db = get_db()
    quiz = db.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    db.close()
    if not quiz:
        abort(404)
    return render_template("quiz.html", quiz=quiz)


@app.route("/result")
@login_required
def result_page():
    return render_template("result.html")


@app.route("/flashcards")
@login_required
def flashcards_page():
    return render_template("flashcards.html")


# ---------------- JSON API ROUTES ----------------

@app.route("/api/quizzes", methods=["GET"])
def api_quizzes():
    db = get_db()
    quizzes = db.execute("SELECT id, title, subject, description FROM quizzes ORDER BY id").fetchall()
    db.close()
    return jsonify([dict(row) for row in quizzes])


@app.route("/api/quiz/<int:quiz_id>", methods=["GET"])
@login_required
def api_quiz_questions(quiz_id):
    db = get_db()
    quiz = db.execute("SELECT id, title FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if not quiz:
        db.close()
        return jsonify({"error": "Quiz not found"}), 404

    questions = db.execute("""
        SELECT id, question_text, option_a, option_b, option_c, option_d
        FROM questions WHERE quiz_id = ? ORDER BY id
    """, (quiz_id,)).fetchall()
    db.close()

    return jsonify({
        "quiz": dict(quiz),
        "questions": [dict(row) for row in questions]
    })


@app.route("/api/submit", methods=["POST"])
@login_required
def api_submit_quiz():
    data = request.get_json(silent=True) or {}
    quiz_id = data.get("quiz_id")
    answers = data.get("answers", {})

    if not isinstance(answers, dict):
        return jsonify({"error": "Answers must be sent as an object."}), 400

    db = get_db()
    quiz = db.execute("SELECT id FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    if not quiz:
        db.close()
        return jsonify({"error": "Quiz not found"}), 404

    questions = db.execute(
        "SELECT id, correct_option FROM questions WHERE quiz_id = ?", (quiz_id,)
    ).fetchall()

    if not questions:
        db.close()
        return jsonify({"error": "This quiz has no questions."}), 400

    score = 0
    for question in questions:
        submitted = str(answers.get(str(question["id"]), "")).upper()
        if submitted == question["correct_option"]:
            score += 1

    total = len(questions)
    percentage = round((score / total) * 100, 1)

    db.execute(
        "INSERT INTO attempts (user_id, quiz_id, score, total) VALUES (?, ?, ?, ?)",
        (session["user_id"], quiz_id, score, total)
    )
    db.commit()
    db.close()

    return jsonify({
        "score": score,
        "total": total,
        "percentage": percentage
    })


@app.route("/api/flashcards", methods=["GET", "POST"])
@login_required
def api_flashcards():
    if request.method == "GET":
        db = get_db()
        cards = db.execute("""
            SELECT id, subject, front, back FROM flashcards
            WHERE user_id IS NULL OR user_id = ?
            ORDER BY id DESC
        """, (session["user_id"],)).fetchall()
        db.close()
        return jsonify([dict(card) for card in cards])

    data = request.get_json(silent=True) or {}
    subject = str(data.get("subject", "General")).strip()
    front = str(data.get("front", "")).strip()
    back = str(data.get("back", "")).strip()

    if not front or not back:
        return jsonify({"error": "Both question and answer are required."}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO flashcards (user_id, subject, front, back) VALUES (?, ?, ?, ?)",
        (session["user_id"], subject or "General", front, back)
    )
    db.commit()
    card_id = cursor.lastrowid
    db.close()

    return jsonify({
        "id": card_id, "subject": subject or "General",
        "front": front, "back": back
    }), 201


@app.route("/api/flashcards/<int:card_id>", methods=["DELETE"])
@login_required
def delete_flashcard(card_id):
    db = get_db()
    cursor = db.execute(
        "DELETE FROM flashcards WHERE id = ? AND user_id = ?",
        (card_id, session["user_id"])
    )
    db.commit()
    db.close()
    if cursor.rowcount == 0:
        return jsonify({"error": "Card not found or it is a shared starter card."}), 404
    return jsonify({"message": "Flashcard deleted."})


@app.route("/api/my-stats", methods=["GET"])
@login_required
def api_my_stats():
    db = get_db()
    stats = db.execute("""
        SELECT COUNT(*) AS attempts,
               COALESCE(ROUND(AVG(score * 100.0 / total), 1), 0) AS average
        FROM attempts WHERE user_id = ?
    """, (session["user_id"],)).fetchone()
    db.close()
    return jsonify(dict(stats))


# Create the database tables and sample content when the app starts.
init_db()

if __name__ == "__main__":
    app.run(debug=True)
