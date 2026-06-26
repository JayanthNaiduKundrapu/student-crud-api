from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from .otel import init_otel
from .config import Config
from .extensions import db, migrate
from .routes.student_routes import student_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    PrometheusMetrics(app) # Initialize Prometheus metrics for monitoring

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        init_otel(app, db)
    app.register_blueprint(student_bp)

    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.exception("Unhandled exception")
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/healthcheck")
    def healthcheck():
        return {"status": "healthy"}, 200

    return app
