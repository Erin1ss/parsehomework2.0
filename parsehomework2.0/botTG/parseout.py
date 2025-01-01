from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Function to read the content of a file
def read_homework(day_file):
    try:
        with open(day_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "Нет домашних заданий на этот день."  # "No homework for this day." in Russian

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
    await update.message.reply_text("Выберите день недели:", reply_markup=reply_markup)  # "Choose a day of the week." in Russian

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

# Main function to set up the bot
def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your bot token
    application = ApplicationBuilder().token("7901658924:AAHvoH3jpA9iuAgMPq3_sHP4WS7RgQTvf50").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
