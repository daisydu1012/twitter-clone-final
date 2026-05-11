from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object("project.config.Config")
    db.init_app(app)

    @app.route("/")
    def home():
        sql = text("""
            SELECT
                tweets.id,
                users.username,
                tweets.body,
                tweets.created_at
            FROM tweets
            JOIN users
              ON tweets.user_id = users.id
            ORDER BY tweets.created_at DESC
            LIMIT 20;
        """)

        rows = db.session.execute(sql).fetchall()

        html = """
        <h1>Twitter Clone</h1>
        <p>
            <a href="/login">Login</a> |
            <a href="/create_account">Create Account</a> |
            <a href="/search">Search</a>
        </p>
        <hr>
        """

        for row in rows:
            html += f"""
            <div>
                <strong>@{row.username}</strong><br>
                {row.body}<br>
                <small>{row.created_at}</small>
            </div>
            <hr>
            """

        return html

    @app.route("/create_account", methods=["GET", "POST"])
    def create_account():
        if request.method == "GET":
            return """
            <h1>Create Account</h1>
            <form method="post">
                Username:<br>
                <input type="text" name="username"><br><br>

                Password:<br>
                <input type="password" name="password1"><br><br>

                Confirm Password:<br>
                <input type="password" name="password2"><br><br>

                <input type="submit" value="Create Account">
            </form>
            """

        username = request.form["username"].strip()
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if username == "":
            return "Username cannot be empty."

        if password1 != password2:
            return "Passwords do not match."

        # Check if username already exists
        sql = text("""
            SELECT id
            FROM users
            WHERE username = :username
        """)
        existing_user = db.session.execute(
            sql,
            {"username": username}
        ).fetchone()

        if existing_user:
            return "Username already exists."

        # Insert new user
        sql = text("""
            INSERT INTO users (username)
            VALUES (:username)
            RETURNING id
        """)
        user_id = db.session.execute(
            sql,
            {"username": username}
        ).fetchone()[0]

        # Store password (plain text for now)
        sql = text("""
            INSERT INTO credentials (user_id, password_hash)
            VALUES (:user_id, :password_hash)
        """)
        db.session.execute(
            sql,
            {
                "user_id": user_id,
                "password_hash": password1
            }
        )

        db.session.commit()

        return redirect("/")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            return """
            <h1>Login</h1>
            <form method="post">
                Username:<br>
                <input type="text" name="username"><br><br>

                Password:<br>
                <input type="password" name="password"><br><br>

                <input type="submit" value="Login">
            </form>
            """

        username = request.form["username"].strip()
        password = request.form["password"]

        sql = text("""
            SELECT credentials.password_hash
            FROM users
            JOIN credentials
              ON users.id = credentials.user_id
            WHERE users.username = :username
        """)

        row = db.session.execute(
            sql,
            {"username": username}
        ).fetchone()

        if row is None:
            return "Invalid username or password."

        if row.password_hash != password:
            return "Invalid username or password."

        return redirect("/")

    return app
