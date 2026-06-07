from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app():
    app = Flask(
        __name__,
        static_url_path="/chromatic-matroids/static",
    )
    app.secret_key = "change-me-in-production"
    # Trust X-Forwarded-* headers from nginx
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    from .routes import bp
    app.register_blueprint(bp, url_prefix="/chromatic-matroids")

    from flask import redirect
    @app.route("/")
    def _root():
        return redirect("/chromatic-matroids/")

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5001)
