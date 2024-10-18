from meta_ai_api import MetaAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

# Initialize MetaAI instance outside the loop for efficiency
meta = MetaAI()
load_dotenv()

TOKEN = os.getenv("TOKEN")
BOT = os.getenv("BOT")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your Meta AI-powered Telegram bot. Send me a message to start our conversation.")

# Handling Responses (Consider including error handling)
async def handle_response(text: str) -> str:
    try:
        return meta.prompt(text)
    
    except Exception as e:
        print(f"Error in handle_response: {e}")
        return "An error occurred. Please try again later."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text

    if message_type == 'group':
        if BOT in text:
            new_text = text.replace(BOT, '').strip()
            response = await handle_response(new_text)
        else:
            return
    else:
        response = await handle_response(text)

    if 'message' in response:
            await update.message.reply_text(response['message'])

    if 'sources' in response:
        for source in response['sources']:
            if 'link' in source and source['link']:
                await update.message.reply_text({source['title']})
                await update.message.reply_text({source['link']})

def main():
    print('Starting...')
    application = Application.builder().token(TOKEN).build()
    # commands
    application.add_handler(CommandHandler("start", start_command))
    # Messages
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    # polling
    print('Polling...')
    application.run_polling()

if __name__ == "__main__":
    main()