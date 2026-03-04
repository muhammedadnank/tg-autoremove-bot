# 🤖 Telegram Auto-Remove Bot

Channel join ചെയ്ത members-നെ X days കഴിഞ്ഞ് automatically remove ചെയ്യുന്ന Telegram Bot.

Built with **Kurigram (Pyrogram fork)** + **MongoDB** + **Python 3.11**

---

## ✨ Features

- 📢 Multiple channels support
- ⏰ Per-channel custom remove days (1 / 3 / 7 / 14 / 30 / 60 / 90)
- 📅 Per-member custom remove date (extend by +1d / +3d / +7d / +14d / +30d)
- 👤 Member info view (joined date, remove date, time left)
- 🤖 Auto-detect (bot-നെ admin ആക്കിയാൽ auto add ആകും)
- ✍️ Manual channel add (Channel ID input)
- 📥 Existing members import (channel add ചെയ്യുമ്പോൾ)
- 📊 Global stats & per-channel stats
- ⏳ Pending removals list (paginated)
- 🗑 Channel remove / monitoring stop
- 📋 Log channel — formatted HTML cards (all events)
- 🔁 Bot restart notification → log channel
- 🎛 Full Inline button UI (commands ഇല്ല, /start മാത്രം)
- 🌐 Render.com Web Service compatible (built-in health-check server)

---

## 📁 Project Structure

```
tg-autoremove-bot/
├── bot.py            # Main bot logic + all handlers
├── config.py         # Environment variable config
├── database.py       # MongoDB handler (lazy init)
├── logger.py         # Log channel — HTML formatted cards
├── requirements.txt  # Python dependencies
├── .env.example      # Environment variables template
├── .python-version   # Python 3.11.9 (for Render)
└── README.md
```

---

## ⚙️ Environment Variables

| Variable | Description | Example |
|---|---|---|
| `API_ID` | Telegram API ID | `12345678` |
| `API_HASH` | Telegram API Hash | `abcdef1234...` |
| `BOT_TOKEN` | Bot token from @BotFather | `123456:ABC-DEF...` |
| `ADMIN_IDS` | Admin user IDs (comma separated) | `123456789,987654321` |
| `MONGO_URI` | MongoDB connection URI | `mongodb+srv://...` |
| `DB_NAME` | MongoDB database name | `autoremove_bot` |
| `DEFAULT_DAYS` | Default remove days | `30` |
| `LOG_CHANNEL` | Log channel ID | `-1001234567890` |

---

## 🚀 Local Setup

### 1. Clone
```bash
git clone https://github.com/yourusername/tg-autoremove-bot.git
cd tg-autoremove-bot
```

### 2. Python 3.11 install
```bash
# pyenv ഉപയോഗിച്ച്
pyenv install 3.11.9
pyenv local 3.11.9
```

### 3. Dependencies install
```bash
pip install -r requirements.txt
```

### 4. Environment configure
`.env` file create ചെയ്യുക (`.env.example` നോക്കൂ):
```env
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=autoremove_bot
DEFAULT_DAYS=30
LOG_CHANNEL=-1001234567890
```

### 5. Run
```bash
python bot.py
```

---

## 🔧 Telegram Setup

1. **@BotFather** → `/newbot` → Bot token copy ചെയ്യുക
2. **my.telegram.org/apps** → `API_ID`, `API_HASH` copy ചെയ്യുക
3. **@userinfobot** → നിങ്ങളുടെ User ID copy ചെയ്യുക (`ADMIN_IDS`)
4. Log channel create ചെയ്ത് Bot-നെ admin ആക്കുക → **Post Messages ✅** permission on
5. Log channel ID copy ചെയ്യുക (`LOG_CHANNEL`) — `-100` prefix ഉള്ളത്

---

## ☁️ Deploy — Render.com (Free)

> Bot-ൽ built-in health-check HTTP server ഉണ്ട് — Render Web Service-ൽ timeout ഇല്ലാതെ run ആകും.

### Steps:

1. GitHub-ൽ repo push ചെയ്യുക
2. [render.com](https://render.com) → **New → Web Service**
3. Repo connect ചെയ്യുക
4. Settings:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. **Environment Variables** tab-ൽ എല്ലാ vars add ചെയ്യുക
6. **Deploy** ക്ലിക്ക് ചെയ്യുക ✅

> ⚠️ **Note:** `.python-version` file (3.11.9) project root-ൽ ഉണ്ടെന്ന് ഉറപ്പാക്കൂ. Python 3.12+ ൽ kurigram-ന് compatibility issues ഉണ്ട്.

---

## 📱 Bot Usage

`/start` → Main Menu

### Inline Buttons

| Button | Action |
|---|---|
| 📢 എന്റെ Channels | Channel list കാണുക |
| ➕ Channel Add ചെയ്യുക | Channel add menu |
| 📊 Stats | Global statistics |
| ⏳ Pending | All pending removals |

### Channel Detail

| Button | Action |
|---|---|
| ⏰ Days മാറ്റുക | Remove days select ചെയ്യുക |
| 👥 Members | Member list + custom date |
| 🗑 Remove Channel | Monitoring stop ചെയ്യുക |

### Member List

| Button | Action |
|---|---|
| 👤 Username | Member info (joined, remove date, time left) |
| 📅 Date | Remove date extend ചെയ്യുക (+1d/+3d/+7d/+14d/+30d) |
| ◀️ ▶️ | Pagination (10 members per page) |

---

## 📢 Channel Add — 2 Methods

**Method 1 — Auto Detect (Recommended):**
1. Channel → Settings → Administrators
2. Bot-നെ add ചെയ്യുക
3. **Ban users** ✅ permission on ആക്കുക
4. Save → Bot automatically detect ആകും ✅

**Method 2 — Manual:**
`/start` → ➕ Add Channel → ✍️ Manual (Channel ID) → ID send ചെയ്യുക

---

## 📋 Log Channel Events

| Event | Trigger |
|---|---|
| 🚀 Bot Started | Bot restart / deploy |
| 📢 Channel Added | Auto detect / manual add |
| 🗑 Channel Removed | Admin removes channel |
| ⚠️ Bot Kicked | Bot removed from channel |
| ⏰ Days Updated | Admin changes remove days |
| 📥 Import Started | New channel add |
| ✅ Import Complete | Import finish |
| 🟢 Member Joined | New member joins channel |
| 🔴 Member Removed | Auto removal (expired) |
| 🚶 Member Left | Member leaves on own |
| ⚠️ Remove Failed | Removal error |
| ✅ Removal Batch | Every 30 min job summary |
| 👤 Admin Action | Any admin action |

---

## 📦 Requirements

```
kurigram
pymongo
tgcrypto
```

- Python **3.11.x** (3.12+ avoid ചെയ്യുക)
- MongoDB Atlas (free tier sufficient)

---

## 🗄️ Database Collections

| Collection | Purpose |
|---|---|
| `channels` | Monitored channels list |
| `members` | Tracked members + remove dates |
| `user_states` | Admin conversation state (manual add flow) |

---

## 📄 License

MIT License
