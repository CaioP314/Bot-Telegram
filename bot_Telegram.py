import telebot
import requests
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID_HARDWARE = os.getenv("ADMIN_ID_HARDWARE")
ADMIN_ID_SOFTWARE = os.getenv("ADMIN_ID_SOFTWARE")
NIFI_URL = "http://localhost:8080/telegram"

bot = telebot.TeleBot(TOKEN)

usuarios = {}

ADMINS = {ADMIN_ID_HARDWARE, ADMIN_ID_SOFTWARE}

@bot.message_handler(func=lambda message: True)
def handle(message):
    chat_id = message.chat.id
    texto = message.text

    if chat_id in ADMINS:
        if texto.startswith("/responder"):
            partes = texto.split(maxsplit=2)
            if len(partes) < 3:
                bot.send_message(
                    chat_id,
                    "Uso:\n/responder CHAT_ID mensagem"
                )
                return
            
            try:
                usuario_id = int(partes[1])
            except ValueError:
                bot.send_message(
                    chat_id,
                    "CHAT_ID inválido."
                )
                return

            resposta = partes[2]

            try:
                bot.send_message(
                    usuario_id,
                    f"Resposta do suporte:\n\n{resposta}"
                )
                bot.send_message(
                    chat_id,
                    "Resposta enviada com sucesso."
                )
            except Exception as e:
                bot.send_message(
                    chat_id,
                    f"Erro ao enviar resposta: {e}"
                )
        else:
            bot.send_message(
                chat_id,
                "Modo administrador.\nUse:\n/responder CHAT_ID mensagem"
            )
        return

    if chat_id not in usuarios:
        usuarios[chat_id] = {
            "estado": "nome",
            "dados": {}
        }
        bot.send_message(
            chat_id,
            "Olá! Qual é o seu nome?"
        )
        return

    estado = usuarios[chat_id]["estado"]
    dados = usuarios[chat_id]["dados"]

    if estado == "nome":
        dados["nome"] = texto
        usuarios[chat_id]["estado"] = "mensagem"
        bot.send_message(
            chat_id,
            "Em que posso ajudar?"
        )
        return

    if estado == "mensagem":
        dados["mensagem"] = texto
        dados["chat_id"] = chat_id
        bot.send_message(
            chat_id,
            f"Recebemos sua solicitação, {dados['nome']}!"
        )

        try:
            requests.post(
                NIFI_URL,
                json=dados
            )
        except Exception as e:
            bot.send_message(
                chat_id,
                f"Erro ao enviar para NiFi: {e}"
            )
        usuarios.pop(chat_id, None)

bot.polling(none_stop=True,interval=3)