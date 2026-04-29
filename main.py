import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import ExpenseDB

# Load environment variables
load_dotenv()

# Get token from environment
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Validate token exists
if not BOT_TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN environment variable not found!")
    print("Make sure you set it in Render's Environment settings.")
    exit(1)

print("✅ Bot token loaded successfully")

# Initialize database
db = ExpenseDB()

def parse_expense(text):
    """
    Parse expense from text like: 'lunch 280 swiggy'
    Returns: (amount, category, description) or (None, None, None)
    """
    parts = text.strip().split(maxsplit=2)

    if len(parts) < 2:
        return None, None, None
    
    try:
        category = parts[0].lower()
        amount = float(parts[1])
        description = parts[2] if len(parts) > 2 else category
        return amount, category, description
    except ValueError:
        return None, None, None

# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    telegram_id = str(user.id)

    user_id = db.get_or_create_user(telegram_id, user.first_name)

    welcome_text = f"""
welcome to Cash Tracker, {user.first_name}   
📝 How to use:
Send expenses like: `lunch 280 swiggy`
- First word: category (food, travel, etc)
- Second word: amount
- Rest: description

📊 Commands:
/today - Today's total
/week - Last 7 days summary
/help - Show help
/stats - Spending statistics
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get today's total"""
    user = update.effective_user
    telegram_id = str(user.id)

    user_id = db.get_or_create_user(telegram_id, user.first_name)
    total = db.get_daily_total(user_id)

    await update.message.reply_text(f"Today's total: ₹{total:.2f}")

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get last 7 days summary"""
    user = update.effective_user
    telegram_id = str(user.id)
    
    user_id = db.get_or_create_user(telegram_id, user.first_name)
    expenses = db.get_all_expenses(user_id, days=7)
    
    if not expenses or len(expenses) == 0:
        await update.message.reply_text("📊 No expenses in last 7 days")
        return
    
    summary = "📊 Last 7 days:\n\n"
    total = 0
    for expense in expenses:
        date, category, amount, desc = expense
        summary += f"• {date} | {category.upper()} | ₹{amount:.2f} ({desc})\n"
        total += amount
    
    summary += f"\n💵 Total: ₹{total:.2f}"
    await update.message.reply_text(summary)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    help_text = """
📖 *Cash Tracker Help*

*Format:* `category amount description`

*Examples:*
- `food 280 swiggy lunch`
- `travel 500 uber to office`
- `fuel 1000 petrol`
- `shopping 150 groceries`

*Commands:*
/start - Start the bot
/today - Today's spending
/week - Last 7 days
/stats - Statistics
/last - Show last expense
/delete - Delete last expense
/edit amount category desc - Edit last expense
/help - This help message

*Tips:*
✓ Amount must be a number
✓ Category can be any word
✓ Description is optional
✓ Your data is private!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle expense messages"""
    user = update.effective_user
    telegram_id = str(user.id)
    text = update.message.text

    user_id = db.get_or_create_user(telegram_id, user.first_name)

    amount, category, description = parse_expense(text)

    if amount is None:
        await update.message.reply_text(
            "❌ Invalid format!\n\nUse: `category amount description`\n"
            "Example: `food 280 swiggy`\n\n"
            "Type /help for more info",
            parse_mode='Markdown'
        )
        return
    
    db.add_expense(user_id, amount, category, description)
    total = db.get_daily_total(user_id)

    response = f"""
✅ *Expense Added!*

📝 {category.upper()} | ₹{amount:.2f}
📌 {description}

💰 Today's total: ₹{total:.2f}
"""
    await update.message.reply_text(response, parse_mode='Markdown')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show spending statistics"""
    user = update.effective_user
    telegram_id = str(user.id)
    
    user_id = db.get_or_create_user(telegram_id, user.first_name)
    expenses = db.get_all_expenses(user_id, days=30)
    
    if not expenses or len(expenses) == 0:
        await update.message.reply_text("📊 No expenses yet!")
        return
    
    categories = {}
    total = 0
    for expense in expenses:
        date, category, amount, desc = expense
        categories[category] = categories.get(category, 0) + amount
        total += amount
    
    stats_text = "📊 *Last 30 Days Statistics*\n\n"
    for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        stats_text += f"• {cat.upper()}: ₹{amount:.2f}\n"
    
    stats_text += f"\n💵 Total: ₹{total:.2f}"
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def delete_last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete last expense: /delete"""
    user = update.effective_user
    telegram_id = str(user.id)

    user_id = db.get_or_create_user(telegram_id, user.first_name)
    last_expense = db.get_last_expense(user_id)

    if not last_expense:
        await update.message.reply_text("❌ No expenses to delete")
        return
    
    expense_id, date, category, amount, description = last_expense
    db.delete_expense(expense_id, user_id)

    response = f"""
🗑️ *Deleted Last Expense*

📝 {category.upper()} | ₹{amount:.2f}
📌 {description}
📅 {date}

Use /undo if this was a mistake
"""
    await update.message.reply_text(response, parse_mode='Markdown')

async def edit_last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edit last expense: /edit amount category description"""   
    user = update.effective_user
    telegram_id = str(user.id)

    user_id = db.get_or_create_user(telegram_id, user.first_name)
    last_expense = db.get_last_expense(user_id)

    if not last_expense:
        await update.message.reply_text("❌ No expenses to edit")
        return
    
    expense_id, date, category, amount, description = last_expense

    try:
        args = update.message.text.split(maxsplit=3)

        if len(args) < 2:
            await update.message.reply_text(
                "❌ Format: `/edit amount category description`\n" 
                "Example: `/edit 300 food lunch`",
                parse_mode='Markdown'
            )
            return
        
        new_amount = float(args[1])
        new_category = args[2] if len(args) > 2 else category
        new_description = args[3] if len(args) > 3 else description

        db.update_expense(expense_id, user_id, new_amount, new_category, new_description)

        response = f"""
✏️ *Expense Updated!*

📝 {new_category.upper()} | ₹{new_amount:.2f}
📌 {new_description}
📅 {date}

Old value: ₹{amount:.2f}
"""
        await update.message.reply_text(response, parse_mode='Markdown')

    except ValueError:
        await update.message.reply_text(
            "❌ Invalid format!\n\n"
            "Use: `/edit amount category description`\n"
            "Example: `/edit 300 food lunch`",
            parse_mode='Markdown'
        )

async def show_last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show last expense: /last"""
    user = update.effective_user
    telegram_id = str(user.id)

    user_id = db.get_or_create_user(telegram_id, user.first_name)
    last_expense = db.get_last_expense(user_id)

    if not last_expense:
        await update.message.reply_text("❌ No expenses yet")
        return
    
    expense_id, date, category, amount, description = last_expense

    response = f"""
📋 *Last Expense*

📝 {category.upper()} | ₹{amount:.2f}
📌 {description}
📅 {date}

Commands:
/delete - Delete this
/edit amount category desc - Edit this
"""
    await update.message.reply_text(response, parse_mode='Markdown')

def main():
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(CommandHandler("week", week))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("delete", delete_last))
    application.add_handler(CommandHandler("edit", edit_last))
    application.add_handler(CommandHandler("last", show_last))

    # Handle all text messages (expenses)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_expense))

    print("🤖 Bot started! Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == '__main__':
    main()