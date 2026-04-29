# Expense Tracker Bot 💰

A Telegram bot for tracking daily expenses with automatic categorization and spending summaries.

## Features

- ✅ Log expenses via WhatsApp-like messages
- ✅ View daily, weekly, and monthly spending
- ✅ Category-wise breakdown
- ✅ Persistent storage in SQLite
- ✅ Multi-user support (each user's data isolated)
- ✅ No app needed (Telegram only)

## How to Use

### Commands
- `/start` - Welcome message
- `/today` - Today's total spending
- `/week` - Last 7 days summary
- `/stats` - Category-wise breakdown (30 days)
- `/help` - Show help message

### Log Expense
Send message in format: `category amount description`

**Examples:**
lunch 280 swiggy
fuel 500 petrol
shopping 150 groceries

## Tech Stack

- **Language:** Python 3.13
- **Bot Framework:** python-telegram-bot
- **Database:** SQLite3
- **Deployment:** Render 

## Installation

1. Clone repo
```bash
git clone https://github.com/Ruturaj-Creates/Expense_tracker.git
cd Expense_tracker
```

2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create `.env` file
TELEGRAM_BOT_TOKEN=your_bot_token_here

5. Run bot
```bash
python main.py
```

## Find the Bot

Search for **@cash_trackerbot** on Telegram and start using!

## Future Features
- [ ] Budget alerts
- [ ] Monthly export to CSV
- [ ] Receipt uploads

## Author

Ruturaj - [GitHub](https://github.com/Ruturaj-Creates)

## License

MIT License - feel free to use and modify
