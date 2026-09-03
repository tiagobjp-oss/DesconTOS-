import logging
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Configuração de logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = "8659241051:AAE_ephuJdNdi-D2vWMaINGZiHX9iTJw5aw"


# 1. Boas-vindas automáticas
async def boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for membro in update.message.new_chat_members:
        # Ignora se o novo membro for o próprio bot
        if membro.id == context.bot.id:
            continue

        mensagem = (
            f"👋 Olá, {membro.first_name}! Seja bem-vindo(a) ao grupo de ofertas!\n\n"
            "📌 **Regras do grupo:**\n"
            "• Proibido enviar links de afiliados de terceiros.\n"
            "• Respeite os demais membros.\n\n"
            "Aproveite as melhores promoções diárias! 🚀"
        )
        await update.message.reply_text(mensagem, parse_mode="Markdown")


# 2. Moderação Antispam (Exclui links enviados por membros normais)
async def moderar_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = update.message.from_user.id
    chat_id = update.message.chat_id

    # Verifica se quem mandou a mensagem é Administrador
    membros_admin = await context.bot.get_chat_administrators(chat_id)
    ids_admins = [admin.user.id for admin in membros_admin]

    # Se for Admin, ignora e permite a postagem
    if usuario_id in ids_admins:
        return

    # Se for membro comum e contiver link, apaga a mensagem
    if update.message.entities:
        for entity in update.message.entities:
            if entity.type in ["url", "text_link"]:
                await update.message.delete()
                print(
                    f"Link não autorizado removido do usuário {update.message.from_user.first_name}"
                )
                break


# 3. Postagem Automática de Ofertas (Comando exclusivo do Admin)
async def postar_oferta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Exemplo de comando: /oferta https://amzn.to/link | Notebook Lenovo | R$ 2.499
    try:
        texto = " ".join(context.args)
        partes = texto.split("|")

        link = partes[0].strip()
        titulo = partes[1].strip()
        preco = partes[2].strip()

        mensagem_formatada = (
            f"🔥 **OFERTA IMPERDÍVEL!** 🔥\n\n"
            f"📦 **{titulo}**\n"
            f"💰 Por apenas: **{preco}**\n\n"
            f"🛒 **Compre agora:** {link}\n\n"
            f"⚠️ *Preços sujeitos a alteração a qualquer momento.*"
        )

        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=mensagem_formatada,
            parse_mode="Markdown",
        )
        await update.message.delete()  # Apaga o comando /oferta original
    except Exception:
        await update.message.reply_text(
            "❌ Formato incorreto. Use: `/oferta LINK | TÍTULO | PREÇO`",
            parse_mode="Markdown",
        )


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Registra os manipuladores
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, boas_vindas)
    )
    app.add_handler(CommandHandler("oferta", postar_oferta))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, moderar_links))

    print("🤖 Bot autônomo está rodando...")
    app.run_polling()