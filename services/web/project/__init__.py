from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

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

        result = db.session.execute(sql)
        rows = result.fetchall()

        html = """
        <h1>Twitter Clone</h1>
        <p><a href="/login">Login</a> |
        <a href="/create_account">Create Account</a> |
        <a href="/search">Search</a></p>
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

    return app
