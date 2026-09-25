from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import time
import config
from context_injector import build_system_prompt
from response_parser import parse_response
from task_executor import execute_commands

# /start command just to test if the bot is alive
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("NOVA online. Send me /prompt to get the system prompt, or just paste your commands.")


# /prompt command to manually trigger the system prompt generation
async def get_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text="Generating prompt from Notion DB...")
    prompt = build_system_prompt()
    await context.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=prompt)

# The main listener for pasted text
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    
    # Parse the pasted text for commands
    conversational_text, commands = parse_response(raw_text)
    
    if commands:
        # Execute the commands silently
        execute_commands(commands)
        reply = f"✅ Executed {len(commands)} command(s) successfully."
        await update.message.reply_text(reply)
    else:
        # If no commands found, just acknowledge
        await update.message.reply_text("No commands found in that message. Just talking?")

# The 8 AM morning routine
async def morning_routine(context: ContextTypes.DEFAULT_TYPE):
    placeholder = "🌅 Wake up Nonchy! Your coffee is waiting. Here's your system prompt for the morning:"
    prompt = build_system_prompt()
    await context.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=f"{placeholder}\n\n{prompt}")

# The 4 PM check-in
async def afternoon_checkin(context: ContextTypes.DEFAULT_TYPE):
    placeholder = "⚙️ 4 PM Check-in: How's the deep work going? If you need to reschedule, talk to your voice app and send me the commands. Here's your updated state:"
    prompt = build_system_prompt()
    await context.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=f"{placeholder}\n\n{prompt}")

# The 10 PM debrief
async def evening_debrief(context: ContextTypes.DEFAULT_TYPE):
    placeholder = "🌙 10 PM Debrief: Time to wrap up. Did you finish what you planned? Talk to your voice app, generate the check commands, and paste them here. Here's your final state:"
    prompt = build_system_prompt()
    await context.bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text=f"{placeholder}\n\n{prompt}")

def run_bot():
    # Create the Application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("prompt", get_prompt))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Schedule the routines using Telegram's built-in JobQueue
    job_queue = application.job_queue
    
    # Note: Times are in UTC. 8 AM Chicago = 13:00 UTC (assuming CDT, adjust if needed)
    job_queue.run_daily(morning_routine, time=time(hour=13, minute=0))
    job_queue.run_daily(afternoon_checkin, time=time(hour=21, minute=0)) # 4 PM Chicago = 21:00 UTC
    job_queue.run_daily(evening_debrief, time=time(hour=3, minute=0))   # 10 PM Chicago = 03:00 UTC next day

    print("🚀 NOVA Telegram Bot is running...")
    application.run_polling()