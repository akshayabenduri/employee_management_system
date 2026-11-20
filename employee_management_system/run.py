"""Start the application:  python run.py"""
from flask import Flask, render_template
from config import Config
from app.routes import main


def create_app():
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
    app.config.from_object(Config)
    app.register_blueprint(main)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500, message="Something went wrong"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
