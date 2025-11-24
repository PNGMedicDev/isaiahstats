# Discord Voice Channel Tracking Setup

## Overview

The IsaiahStats website tracks which users are in Discord voice channels, but **ONLY** for whitelisted Discord servers. This ensures privacy - users won't be tracked when they're in unrelated servers (like Rust servers, private servers, etc.).

## How It Works

1. **User Authentication**: Users log in with Discord OAuth
2. **Guild Whitelist**: Only specific Discord server IDs are tracked
3. **Client-Side Reporting**: Users' browsers report their VC status via Discord RPC
4. **Real-Time Updates**: Website shows who's in voice channels on whitelisted servers

## Setup Steps

### 1. Create a Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name it (e.g., "IsaiahStats")
4. Go to "OAuth2" section
5. Add redirect URL: `http://localhost:5000/auth/discord/callback`
   - For production, use your domain: `https://yourdomain.com/auth/discord/callback`
6. Copy your **Client ID** and **Client Secret**

### 2. Configure Environment Variables

Create a `.env` file in the `website` directory:

```bash
# Discord OAuth Credentials
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
DISCORD_REDIRECT_URI=http://localhost:5000/auth/discord/callback

# Encryption Key (generate with command below)
ENCRYPTION_KEY=your_encryption_key_here
```

Generate an encryption key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Add Whitelisted Guild IDs

Edit `website/discord_config.py` and add your Discord server IDs:

```python
WHITELISTED_GUILDS = [
    '1234567890123456789',  # Your Minecraft Server
    '9876543210987654321',  # Another allowed server
]
```

**How to get Guild IDs:**
1. Enable Developer Mode in Discord: `User Settings → Advanced → Developer Mode`
2. Right-click on a server icon
3. Click "Copy Server ID"

### 4. Install Dependencies

```bash
cd website
pip install -r requirements.txt
```

### 5. Run the Server

```bash
python app.py
```

## For Users: How to Get Tracked

### Step 1: Login with Discord

1. Go to the IsaiahStats website
2. Click the "Discord VC" tab
3. Click "Login with Discord"
4. Authorize the application

### Step 2: Link Minecraft Username (Optional)

1. After logging in, you'll see your Discord profile
2. Enter your Minecraft username in the input field
3. Click "Link"
4. Your Minecraft avatar will now show in the VC tracker

### Step 3: Install Discord RPC Bridge (Required for VC Tracking)

Since Discord doesn't allow OAuth apps to access voice state, users need to run a small script that reports their VC status.

**Option A: Browser Extension (Recommended)**

We need to create a browser extension that uses Discord RPC to detect voice channel status.

**Option B: Python Script**

Run this script while Discord is open:

```python
# discord_vc_reporter.py
import requests
import time
import discord_rpc  # pip install discord-rpc.py

# Your session token (get from browser cookies after logging in)
SESSION_TOKEN = "your_session_token"

# Website URL
WEBSITE_URL = "http://localhost:5000"

def report_vc_status():
    # Get Discord voice state via RPC
    # Send to website API
    pass

while True:
    report_vc_status()
    time.sleep(30)  # Report every 30 seconds
```

## Privacy & Security

✅ **Only Whitelisted Servers**: Your VC status is only tracked in servers you've explicitly whitelisted

✅ **Opt-In**: Users must log in with Discord to be tracked

✅ **Encrypted Tokens**: Discord access tokens are encrypted in the database

✅ **No Bot Required**: This doesn't use a Discord bot, so it doesn't have access to all your servers

❌ **Not Real-Time via OAuth**: Discord OAuth doesn't provide voice state access. Users must report their own status via RPC or extension.

## Troubleshooting

### "Could not authorize" Error

- Check your `DISCORD_CLIENT_ID` and `DISCORD_CLIENT_SECRET`
- Verify the redirect URI matches exactly (including http:// or https://)

### VC Status Not Updating

- Make sure the user is in a **whitelisted guild**
- Check that the RPC bridge/script is running
- Verify guild IDs in `discord_config.py`

### "Invalid Encryption Key" Warning

- Generate a new key with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- Add it to your `.env` file or `discord_config.py`

## Alternative: Discord Bot Approach

If you prefer automatic VC tracking without user scripts, consider using a Discord bot instead:

1. Bot can access voice states automatically
2. No RPC bridge needed
3. See `mod/BUILD_INSTRUCTIONS.md` for bot approach (deprecated in current version)

## Production Deployment

1. Update `DISCORD_REDIRECT_URI` to your production URL
2. Add production redirect URL to Discord Developer Portal
3. Use HTTPS for production
4. Set strong `ENCRYPTION_KEY`
5. Consider rate limiting on OAuth endpoints
6. Use environment variables instead of config file

## Example Workflow

1. User "Steve" logs into IsaiahStats with Discord
2. Steve links their Minecraft username "Steve123"
3. Steve joins a voice channel in whitelisted server "Minecraft Community"
4. Steve's browser/RPC script detects the VC join
5. Script sends update to IsaiahStats API
6. Website updates to show "Steve123" in "Minecraft Community" → "General Voice"
7. Steve joins a Rust server voice channel (not whitelisted)
8. Script detects VC but sees guild ID is not whitelisted
9. Script does **NOT** report this to the website
10. Steve appears as "Not in VC" on IsaiahStats

This ensures Steve's Rust server activity remains private!
