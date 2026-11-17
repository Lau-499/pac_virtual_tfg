
import os #Para leer la clave secreta
from functools import wraps #Para conservar metadatos de una función "decorada"
from datetime import datetime, timezone #Para registrar la fecha de creación del usuario en UTC

from dotenv import load_dotenv #Para cargar variables de entorno desde .env
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, jsonify
)
 # Flask: para crear la aplicación web
 # render_template: para mostrar archivos HTML
 # request: leer datos enviados por el navegador
 # redirect: redirigir a otra página
 # url_for: generar URLs para rutas
 # session: mantener el estado de identificación
 # flash: mostrar mensajes de notificación
 # jsonify: devolver respuestas JSON


from werkzeug.security import (
    generate_password_hash,
    check_password_hash
) 
# generate_password_hash: para crear un hash seguro de la contraseña
# check_password_hash: para verificar la contraseña ingresada con el hash almacenado

from pymongo.errors import DuplicateKeyError #Para gestionar identificaciones duplicadas en la base de datos

from controllers.chat_controller import chat_bp #Para registrar las rutas del chat
from services.mongo_service import (
    usuarios, preparar_indices, crear_conversacion
)
# usuarios: Acceder a la colección de usuarios en la base de datos
# preparar_indices: Crear índices en la colección de usuarios
# crear_conversacion: Crear una nueva conversación

load_dotenv() #Buscamos un archivo .env y cargamos las variables de entorno en el sistema operativo

app = Flask(__name__) #Crear la aplicación Flask, app es un objeto que podemos configurar y registrar rutas para él
app.secret_key = os.environ["SECRET_KEY"] #Clave secreta para firmar cookies de sesión y proteger contra ataques de falsificación

app.config["SESSION_COOKIE_HTTPONLY"] = True #Impide que JavaScript acceda directamente a la cookie.
app.config["SESSION_COOKIE_SAMESITE"] = "Lax" #Restringe el envío de cookies en determinadas peticiones entre sitios.

preparar_indices() #Prepara los índices en la colección de usuarios en mongoDB


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


app.register_blueprint(chat_bp) # En flask, un "blueprint" permite organizar rutas en diferentes archivos. Aquí, incorporamos las rutas definidas en el controlador a la aplicación chat.

if __name__ == "__main__":
    app.run(debug=False)
