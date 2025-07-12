# Telegram User Info Bot 🤖

A legitimate Telegram bot that demonstrates what user information is **actually available** through the official Telegram Bot API, while respecting user privacy.

## 🔒 Important Privacy Notice

**This bot CANNOT and WILL NOT access:**
- ❌ Phone numbers (unless voluntarily shared)
- ❌ Email addresses
- ❌ Private messages
- ❌ Contact lists
- ❌ Private user data

**This bot CAN only access:**
- ✅ Basic profile information (name, username, user ID)
- ✅ Messages sent directly to the bot
- ✅ Information voluntarily shared by users
- ✅ Publicly available profile data

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.7 or higher
- A Telegram account

### 2. Create a Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` to create a new bot
3. Follow the instructions to choose a name and username
4. Save the bot token that BotFather provides

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure the Bot
Set your bot token as an environment variable:

**On Linux/macOS:**
```bash
export BOT_TOKEN="your_bot_token_here"
```

**On Windows:**
```cmd
set BOT_TOKEN=your_bot_token_here
```

**Or create a `.env` file:**
```
BOT_TOKEN=your_bot_token_here
```

### 5. Run the Bot

**Option 1: Using the runner script (recommended)**
```bash
python run_bot.py
```

**Option 2: Direct execution**
```bash
python telegram_bot.py
```

The runner script provides better error checking and setup validation.

## 📋 Features

### Available Commands
- `/start` - Welcome message and main menu
- `/info` - Show your available user information
- `/help` - Show help message
- `/privacy` - Show privacy information

### What Information Can Be Shown
- 🆔 User ID
- 👋 First name
- 👤 Last name (if set)
- 🔗 Username (if set)
- 🌐 Language code
- 🤖 Bot status
- 💎 Premium user status
- 📸 Profile photo status
- 📊 Chat information

### Voluntary Information Sharing
Users can choose to share:
- 📞 Contact information (phone number)
- 📍 Location data

**Note:** This information is only shown when users explicitly choose to share it.

## 🔒 Privacy & Security

### Why This Bot Is Safe
1. **API Limitations**: Uses only official Telegram Bot API endpoints
2. **No Data Storage**: Does not store user information
3. **Transparent**: Shows exactly what information is available
4. **Educational**: Demonstrates Telegram's privacy protections

### What Makes This Different from Malicious Bots
- ✅ Shows only publicly available information
- ✅ Respects Telegram's privacy policies
- ✅ Educational and transparent
- ✅ No data harvesting or storage
- ✅ No unauthorized access attempts

## 🛡️ Telegram's Privacy Protection

Telegram Bot API is designed with privacy in mind:
- Bots cannot access phone numbers or emails automatically
- Private messages remain private
- Contact lists are not accessible
- Location data requires explicit user consent
- Profile information is limited to public data

## 📝 Code Structure

```
telegram_bot.py       # Main bot code
requirements.txt      # Python dependencies
README.md            # This documentation
```

## 🤝 Contributing

This bot is designed for educational purposes to demonstrate:
1. What information is legitimately available to Telegram bots
2. How Telegram protects user privacy
3. Best practices for bot development

## ⚖️ Legal & Ethical Use

This bot is intended for:
- ✅ Educational purposes
- ✅ Demonstrating API capabilities
- ✅ Understanding privacy protections
- ✅ Learning bot development

**Do NOT use this code for:**
- ❌ Attempting to bypass privacy protections
- ❌ Harvesting user data
- ❌ Malicious purposes
- ❌ Violating Telegram's Terms of Service

## 📞 Support

If you encounter issues:
1. Check that your bot token is correct
2. Ensure all dependencies are installed
3. Verify your Python version (3.7+)
4. Check the logs for error messages

## 🔗 Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [python-telegram-bot Library](https://github.com/python-telegram-bot/python-telegram-bot)
- [Telegram Privacy Policy](https://telegram.org/privacy)

---

**Remember:** Always respect user privacy and follow Telegram's Terms of Service! 🛡️
