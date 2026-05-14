from flask import Flask
from .config import Config
from .extensions import db, migrate
from .models.student import Student
from .routes.student_routes import student_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(student_bp)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/healthcheck")
    def healthcheck():
        return {"status": "healthy"}, 200

    return app