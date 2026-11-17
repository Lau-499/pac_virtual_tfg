
import os
from functools import wraps
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, jsonify
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from pymongo.errors import DuplicateKeyError

from controllers.chat_controller import chat_bp
from services.mongo_service import (
    usuarios, preparar_indices, crear_conversacion
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

preparar_indices()


def requiere_login(funcion):
    @wraps(funcion)
    def protegida(*args, **kwargs):
        if "usuario_id" not in session:
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
    if "usuario_id" in session:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        password = request.form.get("password", "")

        usuario = usuarios.find_one({"nombre": nombre})

        if usuario and check_password_hash(
            usuario["password_hash"], password
        ):
            session.clear()
            session["usuario_id"] = str(usuario["_id"])
            session["usuario"] = usuario["nombre"]
            return redirect(url_for("inicio"))

        flash("Identificación o contraseña incorrecta.")

    return render_template("login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if "usuario_id" in session:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        password = request.form.get("password", "")
        confirmar = request.form.get("confirmar", "")

        if not 3 <= len(nombre) <= 50:
            flash("La identificación debe tener entre 3 y 50 caracteres.")

        elif password != confirmar:
            flash("Las contraseñas no coinciden.")

        else:
            try:
                resultado = usuarios.insert_one({
                    "nombre": nombre,
                    "password_hash": generate_password_hash(password),
                    "fecha_registro": datetime.now(timezone.utc)
                })

                session.clear()
                session["usuario_id"] = str(resultado.inserted_id)
                session["usuario"] = nombre

                return redirect(url_for("inicio"))

            except DuplicateKeyError:
                flash("Esa identificación ya existe.")

    return render_template("registro.html")


@app.route("/nueva-conversacion", methods=["POST"])
@requiere_login
def nueva_conversacion():
    conversacion_id = crear_conversacion(
        session["usuario_id"]
    )
    return jsonify({"conversacion_id": conversacion_id})


@app.route("/logout", methods=["POST"])
@requiere_login
def logout():
    session.clear()
    return redirect(url_for("login"))


app.register_blueprint(chat_bp)

if __name__ == "__main__":
    app.run(debug=False)
