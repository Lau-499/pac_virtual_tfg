
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

cliente = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def obtener_respuesta(historial):
    respuesta = cliente.chat.completions.create(
        model="deepseek-chat",
        messages=historial
    )

    return respuesta.choices[0].message.content
