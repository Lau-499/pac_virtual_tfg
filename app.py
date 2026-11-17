
import os
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)

from controllers.chat_controller import chat_bp

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ["DEEPSEEK_API_KEY"]
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Usuarios temporales en memoria.
# Se borran cuando se reinicia el servidor.
usuarios = {}


def requiere_login(funcion):
    @wraps(funcion)
    def protegida(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))

        return funcion(*args, **kwargs)

    return protegida


@app.route("/")
@requiere_login
def inicio():
    return render_template(
        "index.html",
        usuario=session["usuario"]
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        password = request.form.get("password", "")

        if nombre in usuarios and usuarios[nombre] == password:
            session.clear()
            session["usuario"] = nombre

            return redirect(url_for("inicio"))

        flash("Identificación o contraseña incorrecta.")

    return render_template("login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if "usuario" in session:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        password = request.form.get("password", "")
        confirmar = request.form.get("confirmar", "")

        if len(nombre) < 3:
            flash("La identificación debe tener al menos 3 caracteres.")

        elif len(nombre) > 50:
            flash("La identificación es demasiado larga.")

        elif not password:
            flash("Debes introducir una contraseña.")

        elif password != confirmar:
            flash("Las contraseñas no coinciden.")

        elif nombre in usuarios:
            flash("Esa identificación ya existe.")

        else:
            usuarios[nombre] = password

            session.clear()
            session["usuario"] = nombre

            return redirect(url_for("inicio"))

    return render_template("registro.html")


@app.route("/logout", methods=["POST"])
@requiere_login
def logout():
    session.clear()
    return redirect(url_for("login"))


# Registrar el controlador del chatbot
app.register_blueprint(chat_bp)


if __name__ == "__main__":
    app.run(debug=False)
