from meta_ai_api import MetaAI
from telegram import Update, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

# Initialize MetaAI instance outside the loop for efficiency
meta = MetaAI()
load_dotenv()

TOKEN = os.getenv("TOKEN")
BOT = os.getenv("BOT")  # Bot username should include '@' in group mentions

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your Meta AI-powered Telegram bot. Send me a message to start our conversation.")

# Handling Responses (Consider including error handling)
async def handle_response(text: str) -> str:
    try:
        return meta.prompt(text)
    except Exception as e:
        return "An error occurred. Please try again later."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text
    await update.message.reply_chat_action(action=constants.ChatAction.TYPING)

    if message_type in ['group', 'supergroup']:  # Updated to check for both group types
        if BOT in text:  # Ensuring bot is mentioned
            new_text = text.replace(BOT, '').strip()
            response = await handle_response(new_text)
        else:
            return  # Ignore messages without bot mention
    else:
        response = await handle_response(text)

    if isinstance(response, dict):  # Ensure response is in expected format
        if 'message' in response:
            await update.message.reply_text(response['message'])
        
        if 'sources' in response:
            for source in response['sources']:
                if 'link' in source and source['link']:
                    await update.message.reply_text(source['title'])  # Fixed incorrect curly brackets
                    await update.message.reply_text(source['link'])
    else:
        await update.message.reply_text(response)  # Handle plain text responses

def main():
    application = Application.builder().token(TOKEN).build()
    # Commands
    application.add_handler(CommandHandler("start", start_command))
    # Messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Prevents responding to commands
    # Polling
    application.run_polling()

if __name__ == "__main__":
    print('Server started running')
    main()
