
from flask import Blueprint, request, jsonify, session

from services.deepseek_service import obtener_respuesta
from services.mongo_service import (
    obtener_conversacion,
    guardar_intercambio
)

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():

    if "usuario_id" not in session:
        return jsonify({
            "error": "Debes identificarte primero."
        }), 401

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Solicitud JSON no válida."
        }), 400

    conversacion_id = datos.get("conversacion_id")
    pregunta = datos.get("mensaje")

    if not isinstance(conversacion_id, str):
        return jsonify({
            "error": "Identificador de conversación no válido."
        }), 400

    if not isinstance(pregunta, str):
        return jsonify({
            "error": "El mensaje no es válido."
        }), 400

    pregunta = pregunta.strip()

    if not pregunta or len(pregunta) > 4000:
        return jsonify({
            "error": "El mensaje debe tener entre 1 y 4000 caracteres."
        }), 400

    try:
        conversacion = obtener_conversacion(
            conversacion_id,
            session["usuario_id"]
        )

        if conversacion is None:
            return jsonify({
                "error": "Conversación no encontrada."
            }), 404

        # Historial guardado en MongoDB
        historial = conversacion["mensajes"]

        # Enviamos los últimos 28 mensajes anteriores,
        # más la nueva pregunta.
        mensajes = historial[-28:] + [
            {
                "role": "user",
                "content": pregunta
            }
        ]

        # Obtener respuesta de DeepSeek
        respuesta = obtener_respuesta(mensajes)

        if not isinstance(respuesta, str) or not respuesta:
            raise ValueError("Respuesta vacía de DeepSeek")

        # Guardar ambos mensajes en MongoDB
        guardado = guardar_intercambio(
            conversacion_id,
            session["usuario_id"],
            pregunta,
            respuesta
        )

        if not guardado:
            return jsonify({
                "error": "No se pudo guardar la conversación."
            }), 500

        return jsonify({
            "respuesta": respuesta,
            "conversacion_id": conversacion_id
        })

    except Exception:
        return jsonify({
            "error": "No se pudo procesar o guardar el mensaje."
        }), 500
