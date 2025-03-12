import os
import random
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# States for the conversation
PICKING_NUMBERS = 1

# Store user game data
user_games = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Welcome to the 5-Number Lottery Game! 🎲\n\n"
        "Rules:\n"
        "1. Pick exactly 5 different numbers between 1-20\n"
        "2. Submit your numbers\n"
        "3. Check if you won!\n\n"
        "Commands:\n"
        "/play - Start a new lottery game\n"
        "/cancel - Cancel current game"
    )
    await update.message.reply_text(welcome_message)

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        # Check if user is already in a game
        if user_id in user_games:
            await update.message.reply_text("You already have a game in progress! Send your numbers or use /cancel to stop it.")
            return PICKING_NUMBERS
            
        # Start new game
        user_games[user_id] = {
            "numbers": set(),
            "message_id": None
        }
        
        message = (
            f"🎮 Welcome to the game, {user_name}!\n\n"
            "Please send me your numbers one by one (1-20).\n"
            "You need to pick exactly 5 different numbers.\n\n"
            "Your numbers so far: none\n\n"
            "Send /cancel to stop the game"
        )
        await update.message.reply_text(message)
        return PICKING_NUMBERS
    except Exception as e:
        print(f"Error in play: {e}")
        await update.message.reply_text("Something went wrong. Please try /play again.")
        return ConversationHandler.END

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        
        if user_id not in user_games:
            await update.message.reply_text("No active game found. Please use /play to start a new game!")
            return ConversationHandler.END
            
        text = update.message.text.strip()
        
        if not text.isdigit():
            await update.message.reply_text("Please send only numbers between 1 and 20!")
            return PICKING_NUMBERS
            
        number = int(text)
        
        if number < 1 or number > 20:
            await update.message.reply_text("Please pick a number between 1 and 20!")
            return PICKING_NUMBERS
            
        if number in user_games[user_id]["numbers"]:
            await update.message.reply_text("You already picked this number! Choose a different one.")
            return PICKING_NUMBERS
            
        user_games[user_id]["numbers"].add(number)
        numbers_left = 5 - len(user_games[user_id]["numbers"])
        
        if numbers_left > 0:
            message = (
                f"✅ Number {number} added!\n"
                f"Your numbers so far: {sorted(user_games[user_id]['numbers'])}\n"
                f"You need to pick {numbers_left} more number{'s' if numbers_left > 1 else ''}.\n\n"
                f"Send /cancel to stop the game"
            )
            await update.message.reply_text(message)
            return PICKING_NUMBERS
        else:
            # Generate winning numbers
            winning_numbers = set(random.sample(range(1, 21), 5))
            user_numbers = user_games[user_id]["numbers"]
            matches = len(winning_numbers.intersection(user_numbers))
            
            result_message = (
                f"🎯 Your final numbers: {sorted(user_numbers)}\n"
                f"🎲 Winning numbers: {sorted(winning_numbers)}\n\n"
                f"Matches: {matches}\n"
            )
            
            if matches == 5:
                result_message += "🎉 JACKPOT! You matched all numbers! Congratulations! 🎉"
            elif matches == 4:
                result_message += "🎊 Amazing! You matched 4 numbers! 🎊"
            elif matches == 3:
                result_message += "👏 Good job! You matched 3 numbers!"
            elif matches == 2:
                result_message += "👍 Not bad! You matched 2 numbers."
            else:
                result_message += "Better luck next time! 🍀"
                
            await update.message.reply_text(result_message)
            del user_games[user_id]
            
            # Ask if they want to play again
            await update.message.reply_text(
                "🌟 Want to try your luck again? 🌟\n"
                "Use /play to start a new game!"
            )
            return ConversationHandler.END
    except Exception as e:
        print(f"Error in handle_number: {e}")
        await update.message.reply_text("Something went wrong. Please use /play to start a new game.")
        if user_id in user_games:
            del user_games[user_id]
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        if user_id in user_games:
            del user_games[user_id]
            
        end_message = (
            "╔══════════════════╗\n"
            "║   🎮 Game Over   ║\n"
            "╚══════════════════╝\n\n"
            f"👋 Thanks for playing, {user_name}!\n"
            "We hope you enjoyed the game.\n\n"
            "🌟 Remember, every end is a new beginning! 🌟\n\n"
            "Want to try again? Just hit /play\n"
            "and test your luck once more! 🎲"
        )
        
        await update.message.reply_text(end_message)
        return ConversationHandler.END
    except Exception as e:
        print(f"Error in cancel: {e}")
        return ConversationHandler.END

def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("play", play)],
        states={
            PICKING_NUMBERS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number),
                CommandHandler("cancel", cancel)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    
    # Start the bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 