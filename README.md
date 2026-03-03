# 🤖 Telegram Auto-Remove Bot

Channel join ചെയ്ത members-നെ X days കഴിഞ്ഞ് automatically remove ചെയ്യുന്ന Telegram Bot.

Built with **Pyrogram (Kurigram)** + **MongoDB**

---

## ✨ Features

- 📢 Multiple channels support
- ⏰ Per-channel custom remove days
- 🤖 Auto-detect (bot admin ആക്കിയാൽ auto add)
- ✍️ Manual channel add (ID input)
- 📥 Existing members import
- 📊 Stats & pending members view
- 📋 Log channel support (formatted cards)
- 🎛 Inline button UI (no commands needed)

---

## 📁 Project Structure

```
tg-autoremove-bot/
├── bot.py          # Main bot logic + handlers
├── config.py       # Configuration (API keys etc.)
├── database.py     # MongoDB database handler
├── logger.py       # Log channel formatted messages
├── requirements.txt
├── .env.example    # Environment variables template
└── README.md
```

---

## 🚀 Setup

### Step 1: Clone
```bash
git clone https://github.com/yourusername/tg-autoremove-bot.git
cd tg-autoremove-bot
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure
```bash
cp .env.example .env   # edit .env with your values
```

`config.py` edit ചെയ്യുക:
```python
API_ID    = 123456           # my.telegram.org/apps
API_HASH  = "xxxx"
BOT_TOKEN = "xxxx"           # @BotFather
ADMIN_IDS = [123456789]      # @userinfobot
DEFAULT_DAYS = 30
MONGO_URI = "mongodb+srv://..." # MongoDB Atlas URI
LOG_CHANNEL = -100xxxxxxxxx  # Log channel ID
```

### Step 4: Telegram Setup
1. **@BotFather** → `/newbot` → Token copy ചെയ്യുക
2. **my.telegram.org/apps** → `api_id`, `api_hash` copy ചെയ്യുക
3. **@userinfobot** → നിങ്ങളുടെ User ID copy ചെയ്യുക
4. Log channel ഉണ്ടാക്കി → Bot-നെ admin ആക്കുക (Post Messages ✅)

### Step 5: Run
```bash
python bot.py
```

---

## 📱 Bot Usage

**Admin Commands (Private chat):**

| Command | Description |
|---|---|
| `/start` | Main menu open ചെയ്യുക |

**Inline Buttons:**

| Button | Action |
|---|---|
| 📢 My Channels | Channel list കാണുക |
| ➕ Add Channel | Channel add ചെയ്യുക |
| 📊 Stats | Overall statistics |
| ⏳ Pending | Pending removal list |
| ⏰ Change Days | Per-channel days set |
| 👥 Members | Channel member list |
| 🗑 Remove | Channel monitoring stop |

---

## 📢 Channel Add — 2 Methods

**Method 1 — Auto Detect:**
Bot-നെ channel-ൽ admin ആക്കിയ ഉടനെ automatically detect ആകും ✅

**Method 2 — Manual:**
`/start` → ➕ Add Channel → ✍️ Manual → Channel ID send ചെയ്യുക

---

## 📋 Log Channel Previews

```
🟢 Member Joined
━━━━━━━━━━━━━━━━
┌ 👤 John Doe
├ 🆔 123456789
├ 📢 My Channel
├ 👥 Members: 4,521
├ 🗓 Remove at: 02 Apr 2025
└ 🕐 03 Mar 2025 • 19:31:22

🔴 Member Removed
━━━━━━━━━━━━━━━━
┌ 👤 Jane Smith
├ 🆔 987654321
├ 📢 My Channel
├ 👥 Members: 4,520
├ 📅 Joined: 03 Mar 2025
└ 🕐 02 Apr 2025 • 00:01:05
```

---

## ☁️ Deploy (24/7)

**Railway.app (Free):**
```bash
railway login
railway init
railway up
```

**VPS:**
```bash
nohup python bot.py &
# or use systemd service
```

---

## 📦 Requirements

- Python 3.9+
- MongoDB (local or Atlas)
- Telegram API credentials

---

## 📄 License

MIT License
