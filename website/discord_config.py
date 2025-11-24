"""
Discord OAuth and VC Tracking Configuration
"""
import os

# Discord OAuth Settings
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', 'YOUR_DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', 'YOUR_DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5000/auth/discord/callback')

# Discord API endpoints
DISCORD_API_BASE = 'https://discord.com/api/v10'
DISCORD_OAUTH_URL = f'{DISCORD_API_BASE}/oauth2/authorize'
DISCORD_TOKEN_URL = f'{DISCORD_API_BASE}/oauth2/token'
DISCORD_USER_URL = f'{DISCORD_API_BASE}/users/@me'
DISCORD_VOICE_STATE_URL = f'{DISCORD_API_BASE}/users/@me/guilds'

# Whitelisted Guild IDs (only track VCs from these Discord servers)
# Add your Discord server IDs here
WHITELISTED_GUILDS = [
    # Example: '123456789012345678',  # Your Minecraft Server
    # Example: '987654321098765432',  # Another allowed server
]

# You can get Guild IDs by:
# 1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
# 2. Right-click on a server icon
# 3. Click "Copy Server ID"

# Voice state check interval (seconds)
VC_CHECK_INTERVAL = 30  # Check every 30 seconds

# Encryption key for storing Discord tokens
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'GENERATE_A_KEY_HERE')
