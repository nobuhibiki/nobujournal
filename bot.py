from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json
from datetime import datetime
import os

# Load or create journal
def load_journal():
    try:
        with open('journal.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"entries": []}

# Save journal
def save_journal(data):
    with open('journal.json', 'w') as f:
        json.dump(data, f, indent=2)

# Command handlers
async def start(update, context):
    await update.message.reply_text(
        "Welcome to your Journal Bot! 📝\n"
        "Just send me any message to save it as a journal entry.\n"
        "Use /mood [emotion] to log your mood"
    )

async def save_message(update, context):
    journal = load_journal()
    entry = {
        "type": "entry",
        "content": update.message.text,
        "timestamp": datetime.now().isoformat(),
        "user_id": update.message.from_user.id
    }
    journal["entries"].append(entry)
    save_journal(journal)
    await update.message.reply_text("Entry saved! 📝")

async def add_mood(update, context):
    if not context.args:
        await update.message.reply_text("Please specify your mood: /mood [emotion]")
        return
    
    mood = ' '.join(context.args)
    journal = load_journal()
    entry = {
        "type": "mood",
        "content": mood,
        "timestamp": datetime.now().isoformat(),
        "user_id": update.message.from_user.id
    }
    journal["entries"].append(entry)
    save_journal(journal)
    await update.message.reply_text(f"Mood '{mood}' recorded! 🎭")

def main():
    # Get bot token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("No token found! Set TELEGRAM_BOT_TOKEN in repository secrets")
    
    # Create application and add handlers
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mood", add_mood))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_message))
    
    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()