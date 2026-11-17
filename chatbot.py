
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

cliente = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

while True:
    pregunta = input("Tú: ")

    if pregunta.lower() == "salir":
        print("Chat finalizado.")
        break

    respuesta = cliente.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": pregunta}
        ]
    )

    print("DeepSeek:", respuesta.choices[0].message.content)
