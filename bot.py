import asyncio
from telegram import Bot, Update, MenuButtonWebApp, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# Telegram Bot Token (get from @BotFather)
BOT_TOKEN = "8378933501:AAFsevPpIj8CVnJKzE4S20NEY0nwtBPTkB8"
# Your deployed web app URL
WEB_APP_URL = "https://your-server.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    await update.message.reply_html(
        f"👋 Hello {user.mention_html()}!\n\n"
        f"Welcome to Mining Controller Bot!\n\n"
        f"Use /control to open the mining dashboard\n"
        f"Use /status to check mining status"
    )

async def control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open the mining control panel"""
    keyboard = [[
        {
            "text": "⛏️ Open Mining Dashboard",
            "web_app": {"url": WEB_APP_URL}
        }
    ]]
    
    await update.message.reply_text(
        "Click below to open the mining control panel:",
        reply_markup={
            "inline_keyboard": keyboard
        }
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check mining status via command"""
    # You can integrate with your backend API here
    await update.message.reply_text(
        "🔍 Checking mining status...\n"
        "Opening dashboard for detailed information..."
    )
    
    # Open web app
    await control(update, context)

async def setup_menu_button():
    """Set up the menu button for the bot"""
    bot = Bot(BOT_TOKEN)
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="⛏️ Mining Control",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("control", control))
    application.add_handler(CommandHandler("status", status))
    
    # Set up menu button
    asyncio.run(setup_menu_button())
    
    # Start bot
    print("🤖 Mining Control Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
