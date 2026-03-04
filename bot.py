"""
bot.py — Main Bot
Auto-Remove Bot | Pyrogram (Kurigram) + MongoDB
"""

import asyncio
import logging
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from pyrogram.enums import ChatMemberStatus, ChatType

from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS, DEFAULT_DAYS
import database as db
import logger as log_ch

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ── Pyrogram Client ────────────────────────────────────────────────────────────
app = Client(
    "autoremove_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def time_left(iso_or_dt) -> str:
    dt = iso_or_dt if isinstance(iso_or_dt, datetime) else datetime.fromisoformat(iso_or_dt)
    secs = (dt - datetime.now()).total_seconds()
    if secs <= 0:
        return "Expired"
    h = int(secs / 3600)
    return f"{h // 24}d {h % 24}h" if h >= 24 else f"{h}h"


async def get_member_count(chat_id: int) -> int | None:
    try:
        return await app.get_chat_members_count(chat_id)
    except Exception:
        return None


def channel_text(ch: dict, cs: dict) -> str:
    uname = f"@{ch['username']}" if ch.get("username") else f"`{ch['chat_id']}`"
    return (
        f"📢 **{ch['title']}**\n"
        f"🔗 {uname}\n\n"
        f"⏰ Remove after: **{ch['remove_days']} day(s)**\n"
        f"👥 Total: **{cs['total']:,}**  •  "
        f"⏳ Pending: **{cs['pending']:,}**  •  "
        f"✅ Removed: **{cs['removed']:,}**"
    )


# ══════════════════════════════════════════════════════
#  KEYBOARDS
# ══════════════════════════════════════════════════════

def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 എന്റെ Channels", callback_data="channels_list")],
        [InlineKeyboardButton("➕ Channel Add ചെയ്യുക", callback_data="add_channel_menu")],
        [InlineKeyboardButton("📊 Stats",              callback_data="global_stats"),
         InlineKeyboardButton("⏳ Pending",             callback_data="pending_all")],
    ])


def kb_add_channel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Auto Detect", callback_data="add_auto_help")],
        [InlineKeyboardButton("✍️ Manual (Channel ID)", callback_data="add_manual")],
        [InlineKeyboardButton("◀️ Back", callback_data="main_menu")],
    ])


def kb_channels(channels: list) -> InlineKeyboardMarkup:
    rows = []
    for ch in channels:
        rows.append([InlineKeyboardButton(
            f"📢 {ch['title']}  [{ch['remove_days']}d]",
            callback_data=f"ch_{ch['chat_id']}"
        )])
    rows.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)


def kb_channel_detail(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏰ Days മാറ്റുക", callback_data=f"setdays_{chat_id}"),
         InlineKeyboardButton("👥 Members",       callback_data=f"members_{chat_id}")],
        [InlineKeyboardButton("🗑 Remove Channel", callback_data=f"delch_{chat_id}")],
        [InlineKeyboardButton("◀️ Back",           callback_data="channels_list")],
    ])


def kb_days(chat_id: int) -> InlineKeyboardMarkup:
    opts = [1, 3, 7, 14, 30, 60, 90]
    rows, row = [], []
    for d in opts:
        row.append(InlineKeyboardButton(f"{d}d", callback_data=f"days_{chat_id}_{d}"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("◀️ Back", callback_data=f"ch_{chat_id}")])
    return InlineKeyboardMarkup(rows)


def kb_back(cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data=cb)]])


def kb_cancel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]])


# ══════════════════════════════════════════════════════
#  /start
# ══════════════════════════════════════════════════════

@app.on_message(filters.command("start") & filters.private)
async def cmd_start(client: Client, msg: Message):
    if not is_admin(msg.from_user.id):
        await msg.reply("⛔ You are not authorized.")
        return
    db.clear_state(msg.from_user.id)
    s   = db.total_stats()
    chs = db.get_channels()
    await msg.reply(
        f"👋 **Auto-Remove Bot**\n\n"
        f"📢 Channels: **{len(chs)}**\n"
        f"⏳ Pending: **{s['pending']:,}**  •  "
        f"✅ Removed: **{s['removed']:,}**\n\n"
        f"_Channel join ചെയ്ത members-നെ X days കഴിഞ്ഞ് auto remove ചെയ്യും_ ✨",
        reply_markup=kb_main(),
    )


# ══════════════════════════════════════════════════════
#  CALLBACKS
# ══════════════════════════════════════════════════════

@app.on_callback_query()
async def on_callback(client: Client, cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        await cb.answer("⛔ Not authorized", show_alert=True)
        return

    d   = cb.data
    uid = cb.from_user.id

    # ── Main Menu ──────────────────────────────────────
    if d == "main_menu":
        db.clear_state(uid)
        s   = db.total_stats()
        chs = db.get_channels()
        await cb.message.edit_text(
            f"👋 **Auto-Remove Bot**\n\n"
            f"📢 Channels: **{len(chs)}**\n"
            f"⏳ Pending: **{s['pending']:,}**  •  "
            f"✅ Removed: **{s['removed']:,}**",
            reply_markup=kb_main(),
        )

    # ── Channels List ──────────────────────────────────
    elif d == "channels_list":
        chs = db.get_channels()
        if not chs:
            await cb.message.edit_text(
                "📢 **Channels ഒന്നും ഇല്ല!**\n\n"
                "Bot-നെ ഒരു channel-ൽ admin ആക്കൂ — auto detect ആകും.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Channel Add ചെയ്യുക",
                                          callback_data="add_channel_menu")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
                ]),
            )
            return
        await cb.message.edit_text(
            f"📢 **Your Channels** ({len(chs)})\n\nManage ചെയ്യാൻ select ചെയ്യൂ:",
            reply_markup=kb_channels(chs),
        )

    # ── Add Channel Menu ───────────────────────────────
    elif d == "add_channel_menu":
        await cb.message.edit_text(
            "➕ **Channel Add ചെയ്യുക**\n\nഏത് രീതി?",
            reply_markup=kb_add_channel(),
        )

    # ── Auto Detect Help ───────────────────────────────
    elif d == "add_auto_help":
        await cb.message.edit_text(
            "🤖 **Auto Detect**\n\n"
            "1️⃣ Channel → Settings → Administrators\n"
            "2️⃣ Bot-നെ Add ചെയ്യുക\n"
            "3️⃣ **'Ban users'** ✅ permission on\n"
            "4️⃣ Save → Bot automatically detect ചെയ്യും ✅\n\n"
            "_Notification കിട്ടും + list-ൽ appear ആകും_",
            reply_markup=kb_back("add_channel_menu"),
        )

    # ── Manual Add ────────────────────────────────────
    elif d == "add_manual":
        db.set_state(uid, "waiting_channel_id")
        await cb.message.edit_text(
            "✍️ **Manual Channel Add**\n\n"
            "Channel ID send ചെയ്യൂ:\n\n"
            "**ID എങ്ങനെ കണ്ടുപിടിക്കും?**\n"
            "• @userinfobot open ചെയ്യൂ\n"
            "• Channel-ൽ നിന്ന് ഒരു message forward ചെയ്യൂ\n"
            "• കിട്ടുന്ന ID (`-100XXXXXXXXXX`) ഇവിടെ send ചെയ്യൂ\n\n"
            "⚠️ _Bot-നെ ആ channel-ൽ admin ആക്കിയിരിക്കണം_",
            reply_markup=kb_cancel(),
        )

    # ── Global Stats ───────────────────────────────────
    elif d == "global_stats":
        s   = db.total_stats()
        chs = db.get_channels()
        lines = [
            "📊 **Overall Stats**\n",
            f"📢 Active channels: **{len(chs)}**",
            f"👥 Total tracked:   **{s['total']:,}**",
            f"⏳ Pending removal: **{s['pending']:,}**",
            f"✅ Already removed: **{s['removed']:,}**",
        ]
        if chs:
            lines.append("\n**Per-channel:**")
            for ch in chs:
                cs = db.channel_stats(ch["chat_id"])
                lines.append(
                    f"• **{ch['title']}** [{ch['remove_days']}d] — "
                    f"⏳ {cs['pending']:,} pending · ✅ {cs['removed']:,} removed"
                )
        await cb.message.edit_text(
            "\n".join(lines), reply_markup=kb_back("main_menu")
        )

    # ── Pending All ────────────────────────────────────
    elif d == "pending_all":
        pending = db.get_pending()
        if not pending:
            await cb.message.edit_text(
                "✅ Pending removals ഒന്നും ഇല്ല!",
                reply_markup=kb_back("main_menu"),
            )
            return
        lines = [f"⏳ **Pending Removals** ({len(pending):,})\n"]
        for p in pending[:30]:
            lines.append(
                f"• **{p['username']}**  |  {p['channel_name']}  |  ⏰ {time_left(p['remove_at'])}"
            )
        if len(pending) > 30:
            lines.append(f"\n_...and {len(pending) - 30:,} more_")
        await cb.message.edit_text(
            "\n".join(lines), reply_markup=kb_back("main_menu")
        )

    # ── Channel Detail ─────────────────────────────────
    elif d.startswith("ch_"):
        chat_id = int(d[3:])
        ch = db.get_channel(chat_id)
        if not ch:
            await cb.answer("Channel not found", show_alert=True)
            return
        await cb.message.edit_text(
            channel_text(ch, db.channel_stats(chat_id)),
            reply_markup=kb_channel_detail(chat_id),
        )

    # ── Set Days Menu ──────────────────────────────────
    elif d.startswith("setdays_"):
        chat_id = int(d[8:])
        ch = db.get_channel(chat_id)
        await cb.message.edit_text(
            f"⏰ **{ch['title']}**\n\n"
            f"Remove days select ചെയ്യൂ:\n"
            f"_(ഇപ്പോൾ: **{ch['remove_days']} day(s)**)_",
            reply_markup=kb_days(chat_id),
        )

    # ── Days Selected ──────────────────────────────────
    elif d.startswith("days_"):
        _, cid_s, days_s = d.split("_")
        chat_id, new_days = int(cid_s), int(days_s)
        ch       = db.get_channel(chat_id)
        old_days = ch["remove_days"]
        db.set_channel_days(chat_id, new_days)
        await cb.answer(f"✅ {new_days} day(s) set!", show_alert=False)

        # Log
        await log_ch.log_channel_days_changed(
            chat_id, ch["title"], ch.get("username", ""),
            old_days, new_days, uid
        )
        await log_ch.log_admin_action(
            uid, "Days Changed",
            f"{ch['title']}: {old_days}d → {new_days}d"
        )

        ch = db.get_channel(chat_id)
        await cb.message.edit_text(
            channel_text(ch, db.channel_stats(chat_id)),
            reply_markup=kb_channel_detail(chat_id),
        )

    # ── Members List ───────────────────────────────────
    elif d.startswith("members_"):
        chat_id = int(d[8:])
        ch      = db.get_channel(chat_id)
        pending = db.get_pending(chat_id)
        if not pending:
            await cb.message.edit_text(
                f"📢 **{ch['title']}**\n\n✅ Pending members ഒന്നും ഇല്ല.",
                reply_markup=kb_back(f"ch_{chat_id}"),
            )
            return
        lines = [f"👥 **{ch['title']}** — Pending ({len(pending):,})\n"]
        for p in pending[:25]:
            lines.append(f"• **{p['username']}**  ⏰ {time_left(p['remove_at'])}")
        if len(pending) > 25:
            lines.append(f"\n_...and {len(pending) - 25:,} more_")
        await cb.message.edit_text(
            "\n".join(lines), reply_markup=kb_back(f"ch_{chat_id}")
        )

    # ── Delete Channel ─────────────────────────────────
    elif d.startswith("delch_"):
        chat_id = int(d[6:])
        ch      = db.get_channel(chat_id)
        await cb.message.edit_text(
            f"🗑 **'{ch['title']}'** monitoring-ൽ നിന്ന് remove ചെയ്യണോ?\n\n"
            f"_Existing tracked members-നെ kick ചെയ്യില്ല._",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Yes, Remove",
                                      callback_data=f"confirmdelch_{chat_id}"),
                 InlineKeyboardButton("❌ Cancel",
                                      callback_data=f"ch_{chat_id}")],
            ]),
        )

    elif d.startswith("confirmdelch_"):
        chat_id = int(d[13:])
        ch      = db.get_channel(chat_id)
        db.remove_channel(chat_id)
        await cb.answer(f"✅ {ch['title']} removed!", show_alert=True)

        # Log
        await log_ch.log_channel_removed(
            chat_id, ch["title"], ch.get("username", ""), removed_by=uid
        )
        await log_ch.log_admin_action(uid, "Channel Removed", ch["title"])

        chs = db.get_channels()
        if chs:
            await cb.message.edit_text(
                f"📢 **Your Channels** ({len(chs)})",
                reply_markup=kb_channels(chs),
            )
        else:
            await cb.message.edit_text(
                "📢 Channels ഒന്നും ഇല്ല!", reply_markup=kb_back("main_menu")
            )

    await cb.answer()


# ══════════════════════════════════════════════════════
#  MANUAL CHANNEL ID INPUT
# ══════════════════════════════════════════════════════

@app.on_message(filters.private & ~filters.command(["start"]))
async def on_text(client: Client, msg: Message):
    if not is_admin(msg.from_user.id):
        return
    uid          = msg.from_user.id
    state, _     = db.get_state(uid)

    if state != "waiting_channel_id":
        return

    text = msg.text.strip() if msg.text else ""
    try:
        chat_id = int(text)
    except ValueError:
        await msg.reply(
            "❌ Invalid! `-100XXXXXXXXXX` format-ൽ send ചെയ്യൂ.",
            reply_markup=kb_cancel(),
        )
        return

    # Fetch chat info
    try:
        chat = await client.get_chat(chat_id)
    except Exception:
        await msg.reply(
            "❌ Channel കണ്ടുപിടിക്കാൻ കഴിഞ്ഞില്ല!\n\n"
            "• Bot-നെ admin ആക്കിയോ?\n"
            "• ID correct ആണോ?",
            reply_markup=kb_cancel(),
        )
        return

    # Check bot is admin
    try:
        bm = await client.get_chat_member(chat_id, "me")
        if bm.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            raise Exception()
    except Exception:
        await msg.reply(
            f"❌ Bot-നെ **{chat.title}**-ൽ admin ആക്കിയിട്ടില്ല!\n"
            f"Admin ആക്കിയ ശേഷം try ചെയ്യൂ.",
            reply_markup=kb_cancel(),
        )
        return

    db.clear_state(uid)
    db.add_channel(chat_id, chat.title, chat.username, DEFAULT_DAYS)

    member_count = await get_member_count(chat_id)
    await log_ch.log_channel_added(
        chat_id, chat.title, chat.username,
        DEFAULT_DAYS, member_count, method="manual"
    )
    await log_ch.log_admin_action(uid, "Channel Added (Manual)", chat.title)

    uname = f"@{chat.username}" if chat.username else str(chat_id)
    await msg.reply(
        f"✅ **Channel Added!**\n\n"
        f"📛 **{chat.title}**\n"
        f"🔗 {uname}\n"
        f"⏰ Default: **{DEFAULT_DAYS} day(s)**\n\n"
        f"⏳ _Existing members import ചെയ്യുന്നു..._",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Manage", callback_data=f"ch_{chat_id}")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
        ]),
    )

    await import_existing_members(client, chat_id)


# ══════════════════════════════════════════════════════
#  AUTO DETECT  (bot added as admin to channel)
# ══════════════════════════════════════════════════════

@app.on_chat_member_updated(filters.my_chat_member)
async def on_bot_status(client: Client, update):
    chat = update.chat
    new  = update.new_chat_member

    if chat.type not in [ChatType.CHANNEL, ChatType.SUPERGROUP]:
        return

    # Bot became admin ───────────────────────────────
    if new.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        db.add_channel(chat.id, chat.title, chat.username, DEFAULT_DAYS)
        log.info(f"Auto-detected: {chat.title} ({chat.id})")

        member_count = await get_member_count(chat.id)
        await log_ch.log_channel_added(
            chat.id, chat.title, chat.username,
            DEFAULT_DAYS, member_count, method="auto"
        )

        uname = f"@{chat.username}" if chat.username else str(chat.id)
        count_str = f"\n👥 Members: **{member_count:,}**" if member_count else ""
        for aid in ADMIN_IDS:
            try:
                await client.send_message(
                    aid,
                    f"✅ **New Channel Detected!**\n\n"
                    f"📛 **{chat.title}**\n"
                    f"🔗 {uname}{count_str}\n"
                    f"⏰ Default: **{DEFAULT_DAYS} days**\n\n"
                    f"⏳ _Existing members import ചെയ്യുന്നു..._",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⚙️ Manage",
                                              callback_data=f"ch_{chat.id}")]
                    ]),
                )
            except Exception as e:
                log.error(f"Notify admin failed: {e}")

        await import_existing_members(client, chat.id)

    # Bot kicked / left ──────────────────────────────
    elif new.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
        db.remove_channel(chat.id)
        log.info(f"Bot removed from: {chat.title} ({chat.id})")
        await log_ch.log_channel_bot_kicked(chat.id, chat.title, chat.username or "")
        for aid in ADMIN_IDS:
            try:
                await client.send_message(
                    aid,
                    f"⚠️ Bot removed from **{chat.title}**\n_Monitoring stopped._",
                )
            except Exception:
                pass


# ══════════════════════════════════════════════════════
#  TRACK NEW MEMBERS JOINING
# ══════════════════════════════════════════════════════

@app.on_chat_member_updated()
async def on_member_updated(client: Client, update):
    chat_id = update.chat.id
    if not db.channel_active(chat_id):
        return

    old = update.old_chat_member
    new = update.new_chat_member
    left_statuses = {ChatMemberStatus.LEFT, ChatMemberStatus.BANNED}

    # Member joined ──────────────────────────────────
    joined = (
        (old is None or old.status in left_statuses) and
        new is not None and
        new.status == ChatMemberStatus.MEMBER
    )
    if joined:
        user  = new.user
        ch    = db.get_channel(chat_id)
        days  = ch["remove_days"] if ch else DEFAULT_DAYS
        now   = datetime.now()
        remove_at = now + timedelta(days=days)

        db.add_member(
            user.id,
            user.username or user.first_name,
            chat_id,
            update.chat.title or str(chat_id),
            now,
            remove_at,
        )
        log.info(
            f"Tracked: {user.username or user.first_name} "
            f"in '{update.chat.title}' → remove {remove_at.date()}"
        )

        member_count = await get_member_count(chat_id)
        await log_ch.log_member_joined(
            user.id,
            user.username or user.first_name,
            update.chat.title or str(chat_id),
            remove_at,
            member_count,
        )
        return

    # Member left on own ─────────────────────────────
    left_own = (
        old is not None and
        old.status == ChatMemberStatus.MEMBER and
        new is not None and
        new.status == ChatMemberStatus.LEFT
    )
    if left_own:
        user = new.user
        db.mark_left(user.id, chat_id)
        member_count = await get_member_count(chat_id)
        await log_ch.log_member_left(
            user.id,
            user.username or user.first_name,
            update.chat.title or str(chat_id),
            member_count,
        )


# ══════════════════════════════════════════════════════
#  IMPORT EXISTING MEMBERS
# ══════════════════════════════════════════════════════

async def import_existing_members(client: Client, chat_id: int):
    ch = db.get_channel(chat_id)
    if not ch:
        return

    days      = ch["remove_days"]
    now       = datetime.now()
    remove_at = now + timedelta(days=days)
    imported  = 0
    skipped   = 0

    member_count = await get_member_count(chat_id)
    await log_ch.log_import_started(
        chat_id, ch["title"], ch.get("username", ""), member_count
    )

    try:
        async for member in client.get_chat_members(chat_id):
            try:
                user = member.user
                if user.is_bot or user.is_deleted:
                    skipped += 1
                    continue
                if member.status in [ChatMemberStatus.ADMINISTRATOR,
                                      ChatMemberStatus.OWNER]:
                    skipped += 1
                    continue

                db.add_member(
                    user.id,
                    user.username or user.first_name,
                    chat_id,
                    ch["title"],
                    now,
                    remove_at,
                )
                imported += 1

            except Exception as e:
                log.error(f"Import member error: {e}")
                skipped += 1

    except Exception as e:
        log.error(f"get_chat_members failed ({chat_id}): {e}")
        await log_ch.log_import_failed(chat_id, ch["title"], str(e))
        return

    log.info(
        f"Import done: {imported} imported, {skipped} skipped — '{ch['title']}'"
    )
    await log_ch.log_import_complete(
        chat_id, ch["title"], ch.get("username", ""),
        imported, skipped, remove_at
    )

    # Notify admins
    for aid in ADMIN_IDS:
        try:
            await app.send_message(
                aid,
                f"📥 **Import Complete!**\n\n"
                f"📛 **{ch['title']}**\n"
                f"✅ Imported: **{imported:,}**\n"
                f"⏭ Skipped: **{skipped:,}** _(bots/admins)_\n"
                f"🗓 Remove at: **{remove_at.strftime('%d %b %Y')}**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👥 View Members",
                                          callback_data=f"members_{chat_id}")]
                ]),
            )
        except Exception:
            pass


# ══════════════════════════════════════════════════════
#  REMOVAL BACKGROUND JOB  (every 30 minutes)
# ══════════════════════════════════════════════════════

async def removal_job():
    await asyncio.sleep(20)
    while True:
        removed_count = 0
        failed_count  = 0
        try:
            expired = db.get_expired(datetime.now())
            if expired:
                log.info(f"Removal job: processing {len(expired)} expired members")

            for rec in expired:
                try:
                    await app.ban_chat_member(rec["chat_id"], rec["user_id"])
                    await asyncio.sleep(0.5)
                    await app.unban_chat_member(rec["chat_id"], rec["user_id"])
                    db.mark_removed(rec["user_id"], rec["chat_id"])

                    joined_at = rec.get("joined_at")
                    if isinstance(joined_at, str):
                        joined_at = datetime.fromisoformat(joined_at)

                    member_count = await get_member_count(rec["chat_id"])
                    await log_ch.log_member_removed(
                        rec["user_id"],
                        rec["username"],
                        rec["channel_name"],
                        joined_at,
                        member_count,
                    )
                    removed_count += 1
                    log.info(
                        f"Removed: {rec['username']} from '{rec['channel_name']}'"
                    )

                except Exception as e:
                    failed_count += 1
                    await log_ch.log_member_remove_failed(
                        rec["user_id"], rec["username"],
                        rec["channel_name"], str(e)
                    )
                    log.error(f"Remove failed ({rec['username']}): {e}")

            await log_ch.log_removal_batch(removed_count, failed_count)

        except Exception as e:
            log.error(f"Removal job error: {e}")

        await asyncio.sleep(1800)  # 30 minutes


# ══════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════

async def main():
    await app.start()
    me = await app.get_me()
    log.info(f"Bot started: @{me.username}")

    log_ch.set_bot(app)
    await log_ch.log_bot_started(me.username)

    for aid in ADMIN_IDS:
        try:
            await app.send_message(
                aid,
                f"🚀 **Bot started!**\n"
                f"@{me.username} is online ✅\n\n"
                f"/start ചെയ്ത് manage ചെയ്യൂ.",
            )
        except Exception:
            pass

    asyncio.create_task(removal_job())
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
