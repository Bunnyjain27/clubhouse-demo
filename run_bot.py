#!/usr/bin/env python3
"""
Simple runner script for the Telegram Bot with better error handling.
"""

import os
import sys

def check_requirements():
    """Check if all requirements are met."""
    try:
        import telegram
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements with: pip install -r requirements.txt")
        return False
    
    return True

def check_bot_token():
    """Check if bot token is configured."""
    token = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    
    if not token or token == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Bot token not configured!")
        print("\nTo set up your bot token:")
        print("1. Message @BotFather on Telegram")
        print("2. Send /newbot and follow the instructions")
        print("3. Copy the bot token")
        print("4. Set it as environment variable: export BOT_TOKEN='your_token_here'")
        print("5. Or create a .env file with: BOT_TOKEN=your_token_here")
        return False
    
    return True

def main():
    """Run the bot with proper checks."""
    print("🤖 Telegram User Info Bot")
    print("=" * 30)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check bot token
    if not check_bot_token():
        sys.exit(1)
    
    # Import and run the bot
    try:
        from telegram_bot import main as run_bot
        print("✅ Starting bot...")
        run_bot()
    except KeyboardInterrupt:
        print("\n⚠️ Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        print("Check the logs above for more details")
        sys.exit(1)

if __name__ == '__main__':
    main()