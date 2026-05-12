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
            SELECT tweets.id, users.username, tweets.body, tweets.created_at
            FROM tweets
            JOIN users ON tweets.user_id = users.id
            ORDER BY tweets.created_at DESC
            LIMIT 20;
        """)
        rows = db.session.execute(sql).fetchall()

        html = """
        <h1>Twitter Clone</h1>
        <p>
            <a href="/login">Login</a> |
            <a href="/logout">Logout</a> |
            <a href="/create_account">Create Account</a> |
            <a href="/create_message">Create Message</a> |
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

        existing_user = db.session.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()

        if existing_user:
            return "Username already exists."

        user_id = db.session.execute(
            text("INSERT INTO users (username) VALUES (:username) RETURNING id"),
            {"username": username}
        ).fetchone()[0]

        db.session.execute(
            text("""
                INSERT INTO credentials (user_id, password_hash)
                VALUES (:user_id, :password_hash)
            """),
            {"user_id": user_id, "password_hash": password1}
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

        row = db.session.execute(
            text("""
                SELECT users.id, credentials.password_hash
                FROM users
                JOIN credentials ON users.id = credentials.user_id
                WHERE users.username = :username
            """),
            {"username": username}
        ).fetchone()

        if row is None or row.password_hash != password:
            return "Invalid username or password."

        return redirect("/")

    @app.route("/logout")
    def logout():
        return redirect("/")

    @app.route("/create_message", methods=["GET", "POST"])
    def create_message():
        if request.method == "GET":
            return """
            <h1>Create Message</h1>
            <form method="post">
                Username:<br>
                <input type="text" name="username"><br><br>
                Message:<br>
                <textarea name="body" rows="4" cols="50"></textarea><br><br>
                <input type="submit" value="Post Message">
            </form>
            """

        username = request.form["username"].strip()
        body = request.form["body"].strip()

        if username == "":
            return "Username cannot be empty."

        if body == "":
            return "Message cannot be empty."

        user = db.session.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()

        if user is None:
            return "User does not exist. Please create an account first."

        db.session.execute(
            text("""
                INSERT INTO tweets (user_id, body)
                VALUES (:user_id, :body)
            """),
            {"user_id": user.id, "body": body}
        )

        db.session.commit()
        return redirect("/")

    @app.route("/search", methods=["GET", "POST"])
    def search():
        if request.method == "GET":
            return """
            <h1>Search Tweets</h1>
            <form method="post">
                Search Term:<br>
                <input type="text" name="query"><br><br>
                <input type="submit" value="Search">
            </form>
            """

        query = request.form["query"].strip()

        if query == "":
            return "Search query cannot be empty."

        rows = db.session.execute(
            text("""
                SELECT tweets.id, users.username, tweets.body, tweets.created_at
                FROM tweets
                JOIN users ON tweets.user_id = users.id
                WHERE to_tsvector('english', tweets.body)
                      @@ plainto_tsquery('english', :query)
                ORDER BY tweets.created_at DESC;
            """),
            {"query": query}
        ).fetchall()

        html = f"""
        <h1>Search Results for: {query}</h1>
        <p><a href="/">Back to Home</a></p>
        <hr>
        """

        if len(rows) == 0:
            html += "<p>No matching tweets found.</p>"

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

    return app
