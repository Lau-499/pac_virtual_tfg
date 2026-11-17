
import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Cargar la clave API desde el archivo .env
load_dotenv()

# 2. Crear el cliente para conectarnos a DeepSeek
cliente = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 3. Enviar un mensaje a la inteligencia artificial
respuesta = cliente.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "user",
            "content": "Hola, ¿qué es un paciente virtual?"
        }
    ]
)

# 4. Mostrar la respuesta en la terminal
print(respuesta.choices[0].message.content)
