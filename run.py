import os

from flask import Flask, render_template

from tienda.routes import tienda
from admin.routes import admin

from config.settings import (
    SECRET_KEY,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE,
    SESSION_COOKIE_SECURE
)


app = Flask(__name__)

app.secret_key = SECRET_KEY


# ==========================================================
# SEGURIDAD DE SESIONES
# ==========================================================

app.config["SESSION_COOKIE_HTTPONLY"] = (
    SESSION_COOKIE_HTTPONLY
)

app.config["SESSION_COOKIE_SAMESITE"] = (
    SESSION_COOKIE_SAMESITE
)

app.config["SESSION_COOKIE_SECURE"] = (
    SESSION_COOKIE_SECURE
)


# ==========================================================
# BLUEPRINTS
# ==========================================================

app.register_blueprint(tienda)

app.register_blueprint(admin)


# ==========================================================
# PÁGINA 404
# ==========================================================

@app.errorhandler(404)
def pagina_no_encontrada(error):

    return render_template(
        "404.html"
    ), 404


# ==========================================================
# INICIAR SERVIDOR
# ==========================================================

if __name__ == "__main__":

    debug = (
        os.environ.get(
            "FLASK_DEBUG",
            "false"
        ).lower()
        == "true"
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=debug
    )