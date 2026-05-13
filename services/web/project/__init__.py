from flask import Flask, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from urllib.parse import quote_plus
import html

db = SQLAlchemy()


def safe_page(value):
    try:
        page = int(value)
    except (TypeError, ValueError):
        return 0
    return max(page, 0)


def safe_highlight(value):
    escaped = html.escape(value or "")
    escaped = escaped.replace("[[[", "<mark>")
    escaped = escaped.replace("]]]", "</mark>")
    return escaped


def create_app():
    app = Flask(__name__)
    app.config.from_object("project.config.Config")
    app.secret_key = "dev-secret-key"
    db.init_app(app)

    def menu():
        if "user_id" in session:
            return """
            <p>
                <a href="/">Home</a> |
                <a href="/logout">Logout</a> |
                <a href="/create_message">Create Message</a> |
                <a href="/search">Search</a>
            </p>
            <hr>
            """
        return """
        <p>
            <a href="/">Home</a> |
            <a href="/login">Login</a> |
            <a href="/create_account">Create Account</a> |
            <a href="/search">Search</a>
        </p>
        <hr>
        """

    @app.route("/")
    def home():
        page = safe_page(request.args.get("page", 0))
        offset = page * 20

        rows = db.session.execute(
            text("""
                SELECT users.username, tweets.body, tweets.created_at
                FROM tweets
                JOIN users ON tweets.user_id = users.id
                ORDER BY tweets.created_at DESC
                LIMIT 20 OFFSET :offset
            """),
            {"offset": offset}
        ).fetchall()

        output = "<h1>Twitter Clone</h1>" + menu()

        for row in rows:
            output += f"""
            <p>
                <strong>@{html.escape(row.username)}</strong><br>
                {html.escape(row.body)}<br>
                {row.created_at}
            </p>
            <hr>
            """

        output += "<p>"
        if page > 0:
            output += f'<a href="/?page={page - 1}">Newer messages</a> '
        if len(rows) == 20:
            output += f'<a href="/?page={page + 1}">Older messages</a>'
        output += "</p>"

        return output

    @app.route("/create_account", methods=["GET", "POST"])
    def create_account():
        if "user_id" in session:
            return redirect("/")

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
        return redirect("/login")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if "user_id" in session:
            return redirect("/")

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

        session["user_id"] = row.id
        session["username"] = username

        return redirect("/")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/")

    @app.route("/create_message", methods=["GET", "POST"])
    def create_message():
        if "user_id" not in session:
            return redirect("/login")

        if request.method == "GET":
            return """
            <h1>Create Message</h1>
            <form method="post">
                Message:<br>
                <textarea name="body" rows="4" cols="50"></textarea><br><br>
                <input type="submit" value="Post Message">
            </form>
            """

        body = request.form["body"].strip()

        if body == "":
            return "Message cannot be empty."

        db.session.execute(
            text("""
                INSERT INTO tweets (user_id, body)
                VALUES (:user_id, :body)
            """),
            {"user_id": session["user_id"], "body": body}
        )

        db.session.commit()
        return redirect("/")

    @app.route("/search", methods=["GET", "POST"])
    def search():
        if request.method == "POST":
            query = request.form["query"].strip()

            if query == "":
                return "Search query cannot be empty."

            return redirect(f"/search?query={quote_plus(query)}&page=0")

        query = request.args.get("query", "").strip()

        if query == "":
            return """
            <h1>Search Tweets</h1>
            <form method="post">
                Search Term:<br>
                <input type="text" name="query"><br><br>
                <input type="submit" value="Search">
            </form>
            """

        page = safe_page(request.args.get("page", 0))
        offset = page * 20

        rows = db.session.execute(
            text("""
                SELECT
                    users.username,
                    tweets.body,
                    tweets.created_at,
                    ts_headline(
                        'english',
                        tweets.body,
                        plainto_tsquery('english', :query),
                        'StartSel="[[[", StopSel="]]]"'
                    ) AS highlighted
                FROM tweets
                JOIN users ON tweets.user_id = users.id
                WHERE to_tsvector('english', tweets.body)
                      @@ plainto_tsquery('english', :query)
                ORDER BY ts_rank(
                    to_tsvector('english', tweets.body),
                    plainto_tsquery('english', :query)
                ) DESC
                LIMIT 20 OFFSET :offset
            """),
            {"query": query, "offset": offset}
        ).fetchall()

        escaped_query = html.escape(query)
        encoded_query = quote_plus(query)

        output = f"<h1>Search Results for: {escaped_query}</h1>"
        output += '<p><a href="/">Back to Home</a></p><hr>'

        if len(rows) == 0:
            output += "<p>No matching tweets found.</p>"

            suggestion = db.session.execute(
                text("""
                    WITH words AS (
                        SELECT DISTINCT lower(clean_word) AS word
                        FROM (
                            SELECT regexp_replace(
                                regexp_split_to_table(body, '\\s+'),
                                '[^a-zA-Z0-9]',
                                '',
                                'g'
                            ) AS clean_word
                            FROM tweets
                            LIMIT 100000
                        ) split_words
                        WHERE length(clean_word) > 2
                    )
                    SELECT word
                    FROM words
                    WHERE similarity(word, :query) > 0.2
                    ORDER BY similarity(word, :query) DESC
                    LIMIT 1
                """),
                {"query": query.lower()}
            ).fetchone()

            if suggestion is not None:
                safe_suggestion = html.escape(suggestion.word)
                encoded_suggestion = quote_plus(suggestion.word)
                output += f"""
                <p>
                    Did you mean:
                    <a href="/search?query={encoded_suggestion}&page=0">{safe_suggestion}</a>?
                </p>
                """

        for row in rows:
            output += f"""
            <p>
                <strong>@{html.escape(row.username)}</strong><br>
                {safe_highlight(row.highlighted)}<br>
                {row.created_at}
            </p>
            <hr>
            """

        output += "<p>"
        if page > 0:
            output += (
                f'<a href="/search?query={encoded_query}&page={page - 1}">'
                'Previous'
                '</a> '
            )
        if len(rows) == 20:
            output += (
                f'<a href="/search?query={encoded_query}&page={page + 1}">'
                'Next'
                '</a>'
            )
        output += "</p>"

        return output

    return app
