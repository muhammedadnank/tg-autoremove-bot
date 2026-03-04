"""
logger.py — Telegram Log Channel Handler
bot.py-ൽ set_bot(app) call ചെയ്യുക
"""

from datetime import datetime
from config import LOG_CHANNEL

_bot = None


def set_bot(bot):
    global _bot
    _bot = bot


def _now() -> str:
    return datetime.now().strftime("%d %b %Y • %H:%M:%S")


async def _send(text: str):
    if not _bot or not LOG_CHANNEL:
        return
    try:
        await _bot.send_message(
            LOG_CHANNEL,
            text,
            parse_mode="markdown",
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"[Logger] Send failed: {e}")


def _ulink(user_id: int, username: str) -> str:
    return f"[{username}](tg://user?id={user_id})"


def _count_line(member_count) -> str:
    return f"├ 👥 Members: **{member_count:,}**\n" if member_count else ""


# ══════════════════════════════════════════════════════
#  BOT EVENTS
# ══════════════════════════════════════════════════════

async def log_bot_started(username: str):
    await _send(
        f"╔═══════════════════╗\n"
        f"║  🚀  BOT STARTED   ║\n"
        f"╚═══════════════════╝\n\n"
        f"🤖 **@{username}** is now online\n"
        f"🕐 {_now()}"
    )


async def log_bot_stopped(username: str):
    await _send(
        f"⛔ **Bot Stopped**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 🤖 @{username}\n"
        f"└ 🕐 {_now()}"
    )


# ══════════════════════════════════════════════════════
#  CHANNEL EVENTS
# ══════════════════════════════════════════════════════

async def log_channel_added(chat_id: int, title: str, username: str,
                             days: int, member_count=None, method: str = "auto"):
    icon  = "🤖" if method == "auto" else "✍️"
    label = "Auto Detect" if method == "auto" else "Manual"
    uname = f"@{username}" if username else f"`{chat_id}`"
    count = _count_line(member_count)
    await _send(
        f"📢 **Channel Added**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 **{title}**\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 `{chat_id}`\n"
        f"{count}"
        f"├ ⏰ Remove after: **{days} day(s)**\n"
        f"├ {icon} Method: **{label}**\n"
        f"└ 🕐 {_now()}"
    )


async def log_channel_removed(chat_id: int, title: str,
                               username: str = "", removed_by: int = None):
    uname   = f"@{username}" if username else f"`{chat_id}`"
    by_line = (f"├ 👤 By: {_ulink(removed_by, str(removed_by))}\n"
               if removed_by else "")
    await _send(
        f"🗑 **Channel Removed**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 **{title}**\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 `{chat_id}`\n"
        f"{by_line}"
        f"└ 🕐 {_now()}"
    )


async def log_channel_bot_kicked(chat_id: int, title: str, username: str = ""):
    uname = f"@{username}" if username else f"`{chat_id}`"
    await _send(
        f"⚠️ **Bot Kicked from Channel!**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 **{title}**\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 `{chat_id}`\n"
        f"├ 🔴 Monitoring stopped\n"
        f"└ 🕐 {_now()}"
    )


async def log_channel_days_changed(chat_id: int, title: str, username: str,
                                    old_days: int, new_days: int, changed_by: int):
    arrow = "⬆️" if new_days > old_days else "⬇️"
    uname = f"@{username}" if username else f"`{chat_id}`"
    await _send(
        f"⏰ **Remove Days Updated** {arrow}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 **{title}**\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 `{chat_id}`\n"
        f"├ 📊 **{old_days}d  →  {new_days}d**\n"
        f"├ 👤 By: {_ulink(changed_by, str(changed_by))}\n"
        f"└ 🕐 {_now()}"
    )


# ══════════════════════════════════════════════════════
#  MEMBER EVENTS
# ══════════════════════════════════════════════════════

async def log_member_joined(user_id: int, username: str, channel_name: str,
                             remove_at: datetime, member_count=None):
    count = _count_line(member_count)
    await _send(
        f"🟢 **Member Joined**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 👤 {_ulink(user_id, username)}\n"
        f"├ 🆔 `{user_id}`\n"
        f"├ 📢 **{channel_name}**\n"
        f"{count}"
        f"├ 🗓 Remove at: **{remove_at.strftime('%d %b %Y')}**\n"
        f"└ 🕐 {_now()}"
    )


async def log_member_removed(user_id: int, username: str, channel_name: str,
                              joined_at: datetime = None, member_count=None):
    joined_str = joined_at.strftime("%d %b %Y") if joined_at else "—"
    count      = _count_line(member_count)
    await _send(
        f"🔴 **Member Removed**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 👤 {_ulink(user_id, username)}\n"
        f"├ 🆔 `{user_id}`\n"
        f"├ 📢 **{channel_name}**\n"
        f"{count}"
        f"├ 📅 Joined: **{joined_str}**\n"
        f"└ 🕐 {_now()}"
    )


async def log_member_remove_failed(user_id: int, username: str,
                                    channel_name: str, reason: str):
    await _send(
        f"⚠️ **Remove Failed**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 👤 {_ulink(user_id, username)}\n"
        f"├ 🆔 `{user_id}`\n"
        f"├ 📢 **{channel_name}**\n"
        f"├ ❌ `{reason}`\n"
        f"└ 🕐 {_now()}"
    )


async def log_member_left(user_id: int, username: str,
                           channel_name: str, member_count=None):
    count = _count_line(member_count)
    await _send(
        f"🚶 **Member Left**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 👤 {_ulink(user_id, username)}\n"
        f"├ 🆔 `{user_id}`\n"
        f"├ 📢 **{channel_name}**\n"
        f"{count}"
        f"├ ℹ️ Left on their own\n"
        f"└ 🕐 {_now()}"
    )


# ══════════════════════════════════════════════════════
#  IMPORT EVENTS
# ══════════════════════════════════════════════════════

async def log_import_started(chat_id: int, title: str,
                              username: str, member_count=None):
    uname = f"@{username}" if username else f"`{chat_id}`"
    count = _count_line(member_count)
    await _send(
        f"📥 **Import Started**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 **{title}**\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 `{chat_id}`\n"
        f"{count}"
        f"├ ⏳ Fetching members...\n"
        f"└ 🕐 {_now()}"
    )


async def log_import_complete(chat_id: int, title: str, username: str,
                               imported: int, skipped: int, remove_at: datetime):
    uname = f"@{username}" if username else f"`{chat_id}`"
    await _send(
        f"✅ **Import Complete**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 **{title}**\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 `{chat_id}`\n"
        f"├ ✅ Imported: **{imported:,}**\n"
        f"├ ⏭ Skipped:  **{skipped:,}** _(bots/admins)_\n"
        f"├ 🗓 Remove at: **{remove_at.strftime('%d %b %Y')}**\n"
        f"└ 🕐 {_now()}"
    )


async def log_import_failed(chat_id: int, title: str, reason: str):
    await _send(
        f"❌ **Import Failed**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 **{title}**\n"
        f"├ 🆔 `{chat_id}`\n"
        f"├ ❌ `{reason}`\n"
        f"└ 🕐 {_now()}"
    )


# ══════════════════════════════════════════════════════
#  REMOVAL BATCH  (every 30 min job summary)
# ══════════════════════════════════════════════════════

async def log_removal_batch(removed: int, failed: int):
    if removed == 0 and failed == 0:
        return
    status = "✅" if failed == 0 else "⚠️"
    await _send(
        f"{status} **Removal Batch Done**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 🔴 Removed: **{removed:,}**\n"
        f"├ ❌ Failed:  **{failed:,}**\n"
        f"└ 🕐 {_now()}"
    )


# ══════════════════════════════════════════════════════
#  ADMIN ACTIONS
# ══════════════════════════════════════════════════════

async def log_admin_action(user_id: int, action: str, detail: str = ""):
    detail_line = f"├ 📝 {detail}\n" if detail else ""
    await _send(
        f"👤 **Admin Action**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 🔧 **{action}**\n"
        f"{detail_line}"
        f"├ 👤 By: {_ulink(user_id, str(user_id))}\n"
        f"└ 🕐 {_now()}"
    )
