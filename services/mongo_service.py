
import os
from datetime import datetime, timezone

from bson import ObjectId
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

cliente = MongoClient(
    os.environ["MONGO_URI"],
    serverSelectionTimeoutMS=5000
)

db = cliente["pac_virtual_tfg"]

usuarios = db["usuarios"]
conversaciones = db["conversaciones"]


def preparar_indices():
    usuarios.create_index("nombre", unique=True)
    conversaciones.create_index([
        ("usuario_id", ASCENDING),
        ("fecha", ASCENDING)
    ])


def crear_conversacion(usuario_id):
    ahora = datetime.now(timezone.utc)

    resultado = conversaciones.insert_one({
        "usuario_id": ObjectId(usuario_id),
        "fecha": ahora,
        "fecha_actualizacion": ahora,
        "mensajes": []
    })

    return str(resultado.inserted_id)


def obtener_conversacion(conversacion_id, usuario_id):
    if not ObjectId.is_valid(conversacion_id):
        return None

    return conversaciones.find_one({
        "_id": ObjectId(conversacion_id),
        "usuario_id": ObjectId(usuario_id)
    })


def guardar_intercambio(conversacion_id, usuario_id,
                        pregunta, respuesta):
    resultado = conversaciones.update_one(
        {
            "_id": ObjectId(conversacion_id),
            "usuario_id": ObjectId(usuario_id)
        },
        {
            "$push": {
                "mensajes": {
                    "$each": [
                        {
                            "role": "user",
                            "content": pregunta
                        },
                        {
                            "role": "assistant",
                            "content": respuesta
                        }
                    ]
                }
            },
            "$set": {
                "fecha_actualizacion":
                    datetime.now(timezone.utc)
            }
        }
    )

    return resultado.matched_count == 1
