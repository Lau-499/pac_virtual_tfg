
from flask import Blueprint, request, jsonify, session
from services.deepseek_service import obtener_respuesta

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():

    # Comprobar que el usuario está identificado
    if "usuario" not in session:
        return jsonify({
            "error": "Debes identificarte primero."
        }), 401

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Solicitud JSON no válida."
        }), 400

    historial = datos.get("historial")

    # Comprobar que recibimos una lista de mensajes
    if not isinstance(historial, list) or not historial:
        return jsonify({
            "error": "El historial no es válido."
        }), 400

    # Limitar el tamaño de las solicitudes
    if len(historial) > 30:
        return jsonify({
            "error": "Demasiados mensajes en el historial."
        }), 400

    for mensaje in historial:
        if not isinstance(mensaje, dict):
            return jsonify({
                "error": "Mensaje no válido."
            }), 400

        if set(mensaje.keys()) != {"role", "content"}:
            return jsonify({
                "error": "Formato de mensaje incorrecto."
            }), 400

        if mensaje["role"] not in ("user", "assistant"):
            return jsonify({
                "error": "Rol no permitido."
            }), 400

        contenido = mensaje["content"]

        if not isinstance(contenido, str) or not contenido.strip():
            return jsonify({
                "error": "Contenido no válido."
            }), 400

        if len(contenido) > 4000:
            return jsonify({
                "error": "Mensaje demasiado largo."
            }), 400

    if historial[-1]["role"] != "user":
        return jsonify({
            "error": "El último mensaje debe ser del usuario."
        }), 400

    try:
        respuesta = obtener_respuesta(historial)

        return jsonify({
            "respuesta": respuesta
        })

    except Exception:
        return jsonify({
            "error": "No se pudo obtener respuesta de DeepSeek."
        }), 500
