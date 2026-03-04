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
            parse_mode="html",           # HTML — <b>, <code> tags, no escaping issues
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"[Logger] Send failed: {e}")


def _ulink(user_id: int, username: str) -> str:
    return f'<a href="tg://user?id={user_id}">{username}</a>'


def _count_line(member_count) -> str:
    return f"├ 👥 Members: <b>{member_count:,}</b>\n" if member_count else ""


# ══════════════════════════════════════════════════════
#  BOT EVENTS
# ══════════════════════════════════════════════════════

async def log_bot_started(username: str):
    await _send(
        f"╔═══════════════════╗\n"
        f"║  🚀  BOT STARTED   ║\n"
        f"╚═══════════════════╝\n\n"
        f"🤖 <b>@{username}</b> is now online\n"
        f"🕐 {_now()}"
    )


async def log_bot_stopped(username: str):
    await _send(
        f"⛔ <b>Bot Stopped</b>\n"
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
    uname = f"@{username}" if username else f"<code>{chat_id}</code>"
    count = _count_line(member_count)
    await _send(
        f"📢 <b>Channel Added</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 <b>{title}</b>\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 <code>{chat_id}</code>\n"
        f"{count}"
        f"├ ⏰ Remove after: <b>{days} day(s)</b>\n"
        f"├ {icon} Method: <b>{label}</b>\n"
        f"└ 🕐 {_now()}"
    )


async def log_channel_removed(chat_id: int, title: str,
                               username: str = "", removed_by: int = None):
    uname   = f"@{username}" if username else f"<code>{chat_id}</code>"
    by_line = f"├ 👤 By: {_ulink(removed_by, str(removed_by))}\n" if removed_by else ""
    await _send(
        f"🗑 <b>Channel Removed</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 <b>{title}</b>\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 <code>{chat_id}</code>\n"
        f"{by_line}"
        f"└ 🕐 {_now()}"
    )


async def log_channel_bot_kicked(chat_id: int, title: str, username: str = ""):
    uname = f"@{username}" if username else f"<code>{chat_id}</code>"
    await _send(
        f"⚠️ <b>Bot Kicked from Channel!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 <b>{title}</b>\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 <code>{chat_id}</code>\n"
        f"├ 🔴 Monitoring stopped\n"
        f"└ 🕐 {_now()}"
    )


async def log_channel_days_changed(chat_id: int, title: str, username: str,
                                    old_days: int, new_days: int, changed_by: int):
    arrow = "⬆️" if new_days > old_days else "⬇️"
    uname = f"@{username}" if username else f"<code>{chat_id}</code>"
    await _send(
        f"⏰ <b>Remove Days Updated</b> {arrow}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 <b>{title}</b>\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 <code>{chat_id}</code>\n"
        f"├ 📊 <b>{old_days}d  →  {new_days}d</b>\n"
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
        f"🟢 <b>Member Joined</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 👤 {_ulink(user_id, username)}\n"
        f"├ 🆔 <code>{user_id}</code>\n"
        f"├ 📢 <b>{channel_name}</b>\n"
        f"{count}"
        f"├ 🗓 Remove at: <b>{remove_at.strftime('%d %b %Y')}</b>\n"
        f"└ 🕐 {_now()}"
    )


async def log_member_removed(user_id: int, username: str, channel_name: str,
                              joined_at: datetime = None, member_count=None):
    joined_str = joined_at.strftime("%d %b %Y") if joined_at else "—"
    count      = _count_line(member_count)
    await _send(
        f"🔴 <b>Member Removed</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 👤 {_ulink(user_id, username)}\n"
        f"├ 🆔 <code>{user_id}</code>\n"
        f"├ 📢 <b>{channel_name}</b>\n"
        f"{count}"
        f"├ 📅 Joined: <b>{joined_str}</b>\n"
        f"└ 🕐 {_now()}"
    )


async def log_member_remove_failed(user_id: int, username: str,
                                    channel_name: str, reason: str):
    await _send(
        f"⚠️ <b>Remove Failed</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 👤 {_ulink(user_id, username)}\n"
        f"├ 🆔 <code>{user_id}</code>\n"
        f"├ 📢 <b>{channel_name}</b>\n"
        f"├ ❌ <code>{reason}</code>\n"
        f"└ 🕐 {_now()}"
    )


async def log_member_left(user_id: int, username: str,
                           channel_name: str, member_count=None):
    count = _count_line(member_count)
    await _send(
        f"🚶 <b>Member Left</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 👤 {_ulink(user_id, username)}\n"
        f"├ 🆔 <code>{user_id}</code>\n"
        f"├ 📢 <b>{channel_name}</b>\n"
        f"{count}"
        f"├ ℹ️ Left on their own\n"
        f"└ 🕐 {_now()}"
    )


# ══════════════════════════════════════════════════════
#  IMPORT EVENTS
# ══════════════════════════════════════════════════════

async def log_import_started(chat_id: int, title: str,
                              username: str, member_count=None):
    uname = f"@{username}" if username else f"<code>{chat_id}</code>"
    count = _count_line(member_count)
    await _send(
        f"📥 <b>Import Started</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 <b>{title}</b>\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 <code>{chat_id}</code>\n"
        f"{count}"
        f"├ ⏳ Fetching members...\n"
        f"└ 🕐 {_now()}"
    )


async def log_import_complete(chat_id: int, title: str, username: str,
                               imported: int, skipped: int, remove_at: datetime):
    uname = f"@{username}" if username else f"<code>{chat_id}</code>"
    await _send(
        f"✅ <b>Import Complete</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 <b>{title}</b>\n"
        f"├ 🔗 {uname}\n"
        f"├ 🆔 <code>{chat_id}</code>\n"
        f"├ ✅ Imported: <b>{imported:,}</b>\n"
        f"├ ⏭ Skipped:  <b>{skipped:,}</b> (bots/admins)\n"
        f"├ 🗓 Remove at: <b>{remove_at.strftime('%d %b %Y')}</b>\n"
        f"└ 🕐 {_now()}"
    )


async def log_import_failed(chat_id: int, title: str, reason: str):
    await _send(
        f"❌ <b>Import Failed</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 📛 <b>{title}</b>\n"
        f"├ 🆔 <code>{chat_id}</code>\n"
        f"├ ❌ <code>{reason}</code>\n"
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
        f"{status} <b>Removal Batch Done</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 🔴 Removed: <b>{removed:,}</b>\n"
        f"├ ❌ Failed:  <b>{failed:,}</b>\n"
        f"└ 🕐 {_now()}"
    )


# ══════════════════════════════════════════════════════
#  ADMIN ACTIONS
# ══════════════════════════════════════════════════════

async def log_admin_action(user_id: int, action: str, detail: str = ""):
    detail_line = f"├ 📝 {detail}\n" if detail else ""
    await _send(
        f"👤 <b>Admin Action</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"┌ 🔧 <b>{action}</b>\n"
        f"{detail_line}"
        f"├ 👤 By: {_ulink(user_id, str(user_id))}\n"
        f"└ 🕐 {_now()}"
    )
