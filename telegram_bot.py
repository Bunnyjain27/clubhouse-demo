#!/usr/bin/env python3
"""
Telegram Bot - User Information Display
This bot shows the LIMITED user information available through the Telegram Bot API.

IMPORTANT: This bot CANNOT access private information like:
- Phone numbers
- Email addresses
- Private messages
- Contact lists

It can only access publicly available information that users share with the bot.
"""

import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system environment variables

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token - You need to get this from @BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    welcome_message = f"""
🤖 **Telegram User Info Bot**

Hello {user.mention_html()}!

This bot can show you the LIMITED information available through the Telegram Bot API.

**What this bot CAN show:**
✅ User ID
✅ First name
✅ Last name (if set)
✅ Username (if set)
✅ Language code
✅ Profile photo status
✅ Bot status

**What this bot CANNOT access:**
❌ Phone numbers
❌ Email addresses
❌ Private messages
❌ Contact lists
❌ Location (unless shared)

Use /info to see your available information.
    """
    
    keyboard = [
        [InlineKeyboardButton("📋 Get My Info", callback_data='get_info')],
        [InlineKeyboardButton("ℹ️ About Privacy", callback_data='privacy_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(welcome_message, reply_markup=reply_markup)

async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display available user information."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Get user information
    user_info = f"""
👤 **User Information**

🆔 **User ID:** `{user.id}`
👋 **First Name:** {user.first_name or 'Not set'}
👤 **Last Name:** {user.last_name or 'Not set'}
🔗 **Username:** @{user.username or 'Not set'}
🌐 **Language:** {user.language_code or 'Not set'}
🤖 **Is Bot:** {'Yes' ✅' if user.is_bot else 'No ❌'}
💎 **Premium User:** {'Yes ✅' if user.is_premium else 'No ❌'}
📸 **Has Profile Photo:** {'Yes ✅' if user.has_profile_photo else 'No ❌'}

📊 **Chat Information**
🆔 **Chat ID:** `{chat.id}`
📝 **Chat Type:** {chat.type}
📅 **Request Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ **Privacy Note:** This is ALL the information available through the Telegram Bot API. 
Phone numbers and emails are NOT accessible for privacy reasons.
    """
    
    await update.message.reply_html(user_info)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'get_info':
        user = query.from_user
        chat = query.message.chat
        
        user_info = f"""
👤 **User Information**

🆔 **User ID:** `{user.id}`
👋 **First Name:** {user.first_name or 'Not set'}
👤 **Last Name:** {user.last_name or 'Not set'}
🔗 **Username:** @{user.username or 'Not set'}
🌐 **Language:** {user.language_code or 'Not set'}
🤖 **Is Bot:** {'Yes ✅' if user.is_bot else 'No ❌'}
💎 **Premium User:** {'Yes ✅' if user.is_premium else 'No ❌'}
📸 **Has Profile Photo:** {'Yes ✅' if user.has_profile_photo else 'No ❌'}

📊 **Chat Information**
🆔 **Chat ID:** `{chat.id}`
📝 **Chat Type:** {chat.type}
📅 **Request Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ **Privacy Note:** This is ALL the information available through the Telegram Bot API.
        """
        
        await query.edit_message_text(user_info, parse_mode='HTML')
    
    elif query.data == 'privacy_info':
        privacy_info = """
🔒 **Privacy Information**

**Why can't this bot access phone numbers/emails?**

1. **Telegram Privacy Policy**: Telegram protects user privacy by not exposing sensitive data to bots
2. **Bot API Limitations**: The Bot API intentionally limits access to public information only
3. **Security**: This prevents malicious bots from harvesting personal data
4. **User Consent**: Users must explicitly share contact info if they choose to

**What bots CAN access:**
✅ Basic profile info (name, username, ID)
✅ Messages sent to the bot
✅ Shared contact/location (if user chooses)
✅ Public chat interactions

**What bots CANNOT access:**
❌ Phone numbers (unless shared via contact)
❌ Email addresses
❌ Private messages with other users
❌ Contact lists
❌ Private group messages (unless bot is added)

This is by design to protect user privacy! 🛡️
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(privacy_info, parse_mode='HTML', reply_markup=reply_markup)
    
    elif query.data == 'back_to_main':
        await start(update, context)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle when user shares their contact voluntarily."""
    if update.message.contact:
        contact = update.message.contact
        response = f"""
📞 **Contact Information Shared**

Thank you for sharing your contact information voluntarily!

👤 **Name:** {contact.first_name} {contact.last_name or ''}
📱 **Phone:** {contact.phone_number}
🆔 **User ID:** {contact.user_id}

⚠️ **Note:** This information was shared because YOU chose to share it, 
not because the bot accessed it automatically.
        """
        await update.message.reply_html(response)
    else:
        await update.message.reply_text("No contact information found in this message.")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle when user shares their location voluntarily."""
    if update.message.location:
        location = update.message.location
        response = f"""
📍 **Location Information Shared**

Thank you for sharing your location voluntarily!

🌍 **Latitude:** {location.latitude}
🌍 **Longitude:** {location.longitude}
📅 **Shared at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ **Note:** This information was shared because YOU chose to share it,
not because the bot accessed it automatically.
        """
        await update.message.reply_html(response)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🆘 **Help - Available Commands**

/start - Welcome message and main menu
/info - Show your available user information
/help - Show this help message
/privacy - Show privacy information

**What you can do:**
• Share your contact voluntarily (use attachment menu)
• Share your location voluntarily (use attachment menu)
• View your basic profile information

**Remember:** This bot respects your privacy and only shows information that's publicly available or voluntarily shared by you.
    """
    await update.message.reply_html(help_text)

async def privacy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show privacy information."""
    privacy_info = """
🔒 **Privacy & Security**

**What this bot does:**
✅ Shows only publicly available information
✅ Respects Telegram's privacy policies
✅ Only accesses data you voluntarily share
✅ Does not store your personal information

**What this bot does NOT do:**
❌ Access your phone number automatically
❌ Access your email address
❌ Read your private messages
❌ Access your contacts
❌ Share your data with third parties

**Your rights:**
• You control what information you share
• You can block the bot anytime
• You can report abuse to @BotSupport
• Your data is protected by Telegram's privacy policy

Stay safe online! 🛡️
    """
    await update.message.reply_html(privacy_info)

def main() -> None:
    """Start the bot."""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logger.error("Please set your bot token! Get it from @BotFather on Telegram.")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", get_user_info))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("privacy", privacy_command))
    
    # Handle button callbacks
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Handle shared contact and location
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()