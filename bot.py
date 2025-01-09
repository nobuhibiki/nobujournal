from telegram.ext import Application, CommandHandler, MessageHandler, filters
import json
from datetime import datetime
import os
import asyncio

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

async def process_updates(application):
    # Get updates and process them
    updates = await application.bot.get_updates()
    
    for update in updates:
        if update.message:
            # Process commands
            if update.message.text.startswith('/start'):
                await update.message.reply_text(
                    "Welcome to your Journal Bot! 📝\n"
                    "Just send me any message to save it as a journal entry.\n"
                    "Use /mood [emotion] to log your mood"
                )
            
            elif update.message.text.startswith('/mood'):
                # Handle mood command
                mood = update.message.text.replace('/mood', '').strip()
                if mood:
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
                else:
                    await update.message.reply_text("Please specify your mood: /mood [emotion]")
            
            # Handle regular messages
            elif not update.message.text.startswith('/'):
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
        
        # Mark this update as processed
        if updates:
            await application.bot.get_updates(offset=update.update_id + 1)

async def main():
    # Get bot token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("No token found! Set TELEGRAM_BOT_TOKEN in repository secrets")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Process updates once
    await application.initialize()
    await process_updates(application)
    await application.shutdown()

if __name__ == '__main__':
    asyncio.run(main())