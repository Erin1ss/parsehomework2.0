from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Authorized user IDs
AUTHORIZED_USERS = [userID]  # Replace with the actual Telegram user ID(s)

# Function to read the content of a file
def read_homework(day_file):
    try:
        with open(day_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Нет домашних заданий на этот день."  # "No homework for this day." in Russian

# Function to write content to a file
def write_homework(day_file, content):
    with open(day_file, "w", encoding="utf-8") as file:
        file.write(content)

# Function to generate the main menu keyboard
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(day, callback_data=day)] for day in [
            "Понедельник",  # Monday
            "Вторник",      # Tuesday
            "Среда",        # Wednesday
            "Четверг",      # Thursday
            "Пятница",      # Friday
            "Суббота",      # Saturday
        ]
    ])

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = main_menu_keyboard()
    await update.message.reply_text("Выберите день недели:", reply_markup=reply_markup)

# Callback handler for day selection
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "main_menu":
        reply_markup = main_menu_keyboard()
        await query.edit_message_text("Выберите день недели:", reply_markup=reply_markup)
    else:
        day = query.data
        day_file = f"{day}.txt"
        homework = read_homework(day_file)

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад в главное меню", callback_data="main_menu")]
        ])

        await query.edit_message_text(text=homework, reply_markup=reply_markup)

# Command to update homework
async def rem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("У вас нет прав на выполнение этой команды.")  # "You don't have permission to use this command."
        return

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /rem <день недели> <текст>")  # "Usage: /rem <day of the week> <text>"
        return

    day = context.args[0].capitalize()
    content = " ".join(context.args[1:])
    day_file = f"{day}.txt"

    write_homework(day_file, content)
    await update.message.reply_text(f"Домашнее задание для {day} обновлено.")  # "Homework for <day> updated."

# Main function to set up the bot
def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your bot token
    application = ApplicationBuilder().token("KEY").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("rem", rem))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()

