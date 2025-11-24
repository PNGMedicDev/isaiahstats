#!/usr/bin/env python3
"""
IsaiahStats - Real-time Gambling Statistics Tracker
A Flask + Socket.IO application for tracking Isaiah's casino statistics
"""

from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, session, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sqlite3
import json
import time
from datetime import datetime, timedelta
from threading import Lock, Thread
import os
import requests
from urllib.parse import urlencode
from cryptography.fernet import Fernet
import discord_config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'isaiah-stats-secret-key-change-in-production'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Encryption for Discord tokens
try:
    cipher_suite = Fernet(discord_config.ENCRYPTION_KEY.encode())
except:
    print("WARNING: Invalid or missing ENCRYPTION_KEY. Generate one with:")
    print("python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
    cipher_suite = None

# Database setup
DB_PATH = 'database/isaiah_stats.db'
db_lock = Lock()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with schema"""
    os.makedirs('database', exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    # Players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            total_bets INTEGER DEFAULT 0,
            total_wagered BIGINT DEFAULT 0,
            total_won BIGINT DEFAULT 0,
            total_lost BIGINT DEFAULT 0,
            net_profit BIGINT DEFAULT 0,
            win_count INTEGER DEFAULT 0,
            loss_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Bets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            amount BIGINT NOT NULL,
            multiplier REAL DEFAULT 0,
            payout BIGINT DEFAULT 0,
            profit BIGINT NOT NULL,
            result TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players(id)
        )
    ''')

    # Daily stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL UNIQUE,
            total_bets INTEGER DEFAULT 0,
            total_wagered BIGINT DEFAULT 0,
            house_profit BIGINT DEFAULT 0,
            unique_players INTEGER DEFAULT 0
        )
    ''')

    # Discord users table (OAuth authenticated users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discord_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT NOT NULL UNIQUE,
            discord_username TEXT NOT NULL,
            discord_discriminator TEXT,
            discord_avatar TEXT,
            minecraft_username TEXT,
            access_token_encrypted TEXT NOT NULL,
            refresh_token_encrypted TEXT,
            token_expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Discord VC status table (current voice channel status)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discord_vc_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT NOT NULL UNIQUE,
            guild_id TEXT NOT NULL,
            guild_name TEXT,
            channel_id TEXT,
            channel_name TEXT,
            is_connected BOOLEAN DEFAULT 1,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (discord_id) REFERENCES discord_users(discord_id)
        )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bets_timestamp ON bets(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bets_username ON bets(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_players_username ON players(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_discord_users_discord_id ON discord_users(discord_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_discord_vc_discord_id ON discord_vc_status(discord_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_discord_vc_connected ON discord_vc_status(is_connected)')

    conn.commit()
    conn.close()

def format_money(amount):
    """Format money amount with K/M/B suffixes"""
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.2f}K"
    else:
        return f"${amount}"

def get_global_stats():
    """Get global statistics"""
    conn = get_db()
    cursor = conn.cursor()

    # Total bets
    cursor.execute('SELECT COUNT(*) as total FROM bets')
    total_bets = cursor.fetchone()['total']

    # Total wagered
    cursor.execute('SELECT COALESCE(SUM(amount), 0) as total FROM bets')
    total_wagered = cursor.fetchone()['total']

    # House profit (total wagered - total payouts)
    cursor.execute('SELECT COALESCE(SUM(profit), 0) as profit FROM bets')
    house_profit = -cursor.fetchone()['profit']  # Negative of player profit

    # Average house edge
    avg_edge = (house_profit / total_wagered * 100) if total_wagered > 0 else 0

    conn.close()

    return {
        'total_bets': total_bets,
        'total_bets_formatted': f"{total_bets / 1000:.2f}K" if total_bets >= 1000 else str(total_bets),
        'total_wagered': total_wagered,
        'total_wagered_formatted': format_money(total_wagered),
        'house_profit': house_profit,
        'house_profit_formatted': format_money(house_profit),
        'house_edge': f"{avg_edge:.2f}%"
    }

def get_leaderboard(order_by='total_wagered', limit=10):
    """Get leaderboard data"""
    conn = get_db()
    cursor = conn.cursor()

    valid_orders = {
        'wagered': 'total_wagered',
        'won': 'total_won',
        'lost': 'total_lost'
    }

    order_col = valid_orders.get(order_by, 'total_wagered')

    cursor.execute(f'''
        SELECT username, total_bets, total_wagered, total_won, total_lost, net_profit
        FROM players
        WHERE total_bets > 0
        ORDER BY {order_col} DESC
        LIMIT ?
    ''', (limit,))

    players = []
    for row in cursor.fetchall():
        players.append({
            'username': row['username'],
            'total_bets': row['total_bets'],
            'total_wagered': row['total_wagered'],
            'total_wagered_formatted': format_money(row['total_wagered']),
            'total_won': row['total_won'],
            'total_won_formatted': format_money(row['total_won']),
            'total_lost': row['total_lost'],
            'total_lost_formatted': format_money(row['total_lost']),
            'net_profit': row['net_profit'],
            'net_profit_formatted': format_money(abs(row['net_profit'])),
            'is_profitable': row['net_profit'] > 0
        })

    conn.close()
    return players

def get_recent_bets(limit=20):
    """Get recent bets"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT username, amount, multiplier, payout, result, timestamp
        FROM bets
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))

    bets = []
    for row in cursor.fetchall():
        timestamp = datetime.fromisoformat(row['timestamp'])
        time_str = timestamp.strftime('%H:%M:%S')

        bets.append({
            'username': row['username'],
            'amount': row['amount'],
            'amount_formatted': format_money(row['amount']),
            'multiplier': f"{row['multiplier']}x",
            'payout': row['payout'],
            'payout_formatted': format_money(row['payout']),
            'result': row['result'],
            'timestamp': time_str
        })

    conn.close()
    return bets

def get_player_stats(username):
    """Get detailed player statistics"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM players WHERE username = ?
    ''', (username,))

    player = cursor.fetchone()
    if not player:
        conn.close()
        return None

    # Get bet history
    cursor.execute('''
        SELECT amount, multiplier, payout, profit, result, timestamp
        FROM bets
        WHERE username = ?
        ORDER BY timestamp DESC
        LIMIT 100
    ''', (username,))

    history = []
    for row in cursor.fetchall():
        timestamp = datetime.fromisoformat(row['timestamp'])
        history.append({
            'amount': row['amount'],
            'amount_formatted': format_money(row['amount']),
            'multiplier': row['multiplier'],
            'payout': row['payout'],
            'payout_formatted': format_money(row['payout']),
            'profit': row['profit'],
            'profit_formatted': format_money(abs(row['profit'])),
            'result': row['result'],
            'timestamp': timestamp.strftime('%H:%M:%S')
        })

    win_rate = (player['win_count'] / player['total_bets'] * 100) if player['total_bets'] > 0 else 0

    stats = {
        'username': player['username'],
        'total_bets': player['total_bets'],
        'total_wagered': format_money(player['total_wagered']),
        'win_rate': f"{win_rate:.1f}%",
        'net_profit': player['net_profit'],
        'net_profit_formatted': format_money(abs(player['net_profit'])),
        'is_profitable': player['net_profit'] > 0,
        'history': history
    }

    conn.close()
    return stats

def record_bet(username, amount, multiplier=0, result='loss'):
    """Record a new bet"""
    with db_lock:
        conn = get_db()
        cursor = conn.cursor()

        # Get or create player
        cursor.execute('SELECT id FROM players WHERE username = ?', (username,))
        player = cursor.fetchone()

        if not player:
            cursor.execute('INSERT INTO players (username) VALUES (?)', (username,))
            player_id = cursor.lastrowid
        else:
            player_id = player['id']

        # Calculate payout and profit
        payout = int(amount * multiplier) if result == 'win' else 0
        profit = payout - amount

        # Insert bet
        cursor.execute('''
            INSERT INTO bets (player_id, username, amount, multiplier, payout, profit, result)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (player_id, username, amount, multiplier, payout, profit, result))

        # Update player stats
        if result == 'win':
            cursor.execute('''
                UPDATE players
                SET total_bets = total_bets + 1,
                    total_wagered = total_wagered + ?,
                    total_won = total_won + ?,
                    net_profit = net_profit + ?,
                    win_count = win_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (amount, payout, profit, player_id))
        else:
            cursor.execute('''
                UPDATE players
                SET total_bets = total_bets + 1,
                    total_wagered = total_wagered + ?,
                    total_lost = total_lost + ?,
                    net_profit = net_profit + ?,
                    loss_count = loss_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (amount, amount, profit, player_id))

        # Update daily stats
        today = datetime.now().date()
        cursor.execute('''
            INSERT INTO daily_stats (date, total_bets, total_wagered, house_profit)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                total_bets = total_bets + 1,
                total_wagered = total_wagered + ?,
                house_profit = house_profit + ?
        ''', (today, amount, -profit, amount, -profit))

        conn.commit()
        conn.close()

        # Emit socket event
        socketio.emit('new_bet', {
            'username': username,
            'amount': amount,
            'amount_formatted': format_money(amount),
            'multiplier': multiplier,
            'payout': payout,
            'payout_formatted': format_money(payout),
            'result': result
        })

        # Emit stats update
        socketio.emit('stats_update', get_global_stats())

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def api_stats():
    return jsonify(get_global_stats())

@app.route('/api/leaderboard/<category>')
def api_leaderboard(category):
    return jsonify(get_leaderboard(category, 10))

@app.route('/api/recent')
def api_recent():
    return jsonify(get_recent_bets(20))

@app.route('/api/player/<username>')
def api_player(username):
    stats = get_player_stats(username)
    if stats:
        return jsonify(stats)
    return jsonify({'error': 'Player not found'}), 404

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '').lower()
    if len(query) < 2:
        return jsonify([])

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username FROM players
        WHERE LOWER(username) LIKE ?
        ORDER BY total_wagered DESC
        LIMIT 10
    ''', (f'%{query}%',))

    results = [row['username'] for row in cursor.fetchall()]
    conn.close()

    return jsonify(results)

@app.route('/api/bet', methods=['POST'])
def api_bet():
    """Record a new bet (for testing or mod integration)"""
    data = request.json

    username = data.get('username')
    amount = data.get('amount')
    multiplier = data.get('multiplier', 0)
    result = data.get('result', 'loss')

    if not username or not amount:
        return jsonify({'error': 'Missing required fields'}), 400

    record_bet(username, amount, multiplier, result)
    return jsonify({'success': True})

@app.route('/static/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory('static/downloads', filename)

def encrypt_token(token):
    """Encrypt a Discord token"""
    if not cipher_suite or not token:
        return None
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token):
    """Decrypt a Discord token"""
    if not cipher_suite or not encrypted_token:
        return None
    try:
        return cipher_suite.decrypt(encrypted_token.encode()).decode()
    except:
        return None

def get_discord_voice_state(access_token):
    """Get user's voice state from Discord API"""
    headers = {'Authorization': f'Bearer {access_token}'}

    # Get user's guilds
    response = requests.get(f'{discord_config.DISCORD_API_BASE}/users/@me/guilds', headers=headers)
    if response.status_code != 200:
        return None

    guilds = response.json()

    # Check voice state in each whitelisted guild
    for guild in guilds:
        guild_id = guild['id']

        # Only check whitelisted guilds
        if guild_id not in discord_config.WHITELISTED_GUILDS:
            continue

        # Get voice state for this guild
        # Note: We need to get this from the gateway, but we can use a workaround
        # by checking the user's connections or using a different approach

        # For now, we'll use a simplified approach - checking guild channels
        channels_response = requests.get(
            f'{discord_config.DISCORD_API_BASE}/guilds/{guild_id}/channels',
            headers=headers
        )

        if channels_response.status_code == 200:
            channels = channels_response.json()
            voice_channels = [ch for ch in channels if ch.get('type') == 2]  # Type 2 = Voice Channel

            # Check if user is in any voice channel
            for channel in voice_channels:
                # This would require WebSocket connection for real-time data
                # For this implementation, we'll use a different approach
                pass

    return None

def check_all_voice_states():
    """Check voice states for all authenticated users"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT discord_id, discord_username, minecraft_username, access_token_encrypted
        FROM discord_users
    ''')

    users = cursor.fetchall()

    for user in users:
        discord_id = user['discord_id']
        access_token = decrypt_token(user['access_token_encrypted'])

        if not access_token:
            continue

        # Get current voice state from Discord
        voice_state = get_user_voice_state_via_api(access_token, discord_id)

        if voice_state:
            # Update or insert voice state
            cursor.execute('''
                INSERT INTO discord_vc_status
                (discord_id, guild_id, guild_name, channel_id, channel_name, is_connected, joined_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(discord_id) DO UPDATE SET
                    guild_id = ?,
                    guild_name = ?,
                    channel_id = ?,
                    channel_name = ?,
                    is_connected = 1,
                    updated_at = CURRENT_TIMESTAMP
            ''', (discord_id, voice_state['guild_id'], voice_state['guild_name'],
                  voice_state['channel_id'], voice_state['channel_name'],
                  voice_state['guild_id'], voice_state['guild_name'],
                  voice_state['channel_id'], voice_state['channel_name']))
        else:
            # User not in VC, mark as disconnected
            cursor.execute('''
                UPDATE discord_vc_status
                SET is_connected = 0, updated_at = CURRENT_TIMESTAMP
                WHERE discord_id = ?
            ''', (discord_id,))

    conn.commit()
    conn.close()

    # Emit update to all connected clients
    socketio.emit('vc_update', {'refresh': True})

def get_user_voice_state_via_api(access_token, user_id):
    """
    Get user's voice state from Discord API
    Note: This requires checking voice states via WebSocket Gateway or bot token
    This is a simplified version that checks user connections
    """
    headers = {'Authorization': f'Bearer {access_token}'}

    # Get user's current connections/sessions
    response = requests.get(f'{discord_config.DISCORD_API_BASE}/users/@me/connections', headers=headers)

    if response.status_code != 200:
        return None

    # For actual voice state, we would need WebSocket Gateway connection
    # This is a limitation of OAuth-only approach without a bot
    # Alternative: Use user's client to report their own VC state
    return None

@app.route('/auth/discord')
def discord_login():
    """Redirect to Discord OAuth"""
    params = {
        'client_id': discord_config.DISCORD_CLIENT_ID,
        'redirect_uri': discord_config.DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify guilds guilds.members.read'
    }
    return redirect(f'{discord_config.DISCORD_OAUTH_URL}?{urlencode(params)}')

@app.route('/auth/discord/callback')
def discord_callback():
    """Handle Discord OAuth callback"""
    code = request.args.get('code')
    if not code:
        return 'Error: No code provided', 400

    # Exchange code for access token
    data = {
        'client_id': discord_config.DISCORD_CLIENT_ID,
        'client_secret': discord_config.DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': discord_config.DISCORD_REDIRECT_URI
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(discord_config.DISCORD_TOKEN_URL, data=data, headers=headers)

    if response.status_code != 200:
        return 'Error exchanging code for token', 400

    token_data = response.json()
    access_token = token_data['access_token']
    refresh_token = token_data.get('refresh_token')
    expires_in = token_data['expires_in']

    # Get user info
    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get(discord_config.DISCORD_USER_URL, headers=headers)

    if user_response.status_code != 200:
        return 'Error fetching user info', 400

    user_data = user_response.json()
    discord_id = user_data['id']
    discord_username = f"{user_data['username']}#{user_data['discriminator']}"

    # Store user in database
    with db_lock:
        conn = get_db()
        cursor = conn.cursor()

        expires_at = datetime.now() + timedelta(seconds=expires_in)

        cursor.execute('''
            INSERT INTO discord_users
            (discord_id, discord_username, discord_discriminator, discord_avatar,
             access_token_encrypted, refresh_token_encrypted, token_expires_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(discord_id) DO UPDATE SET
                discord_username = ?,
                discord_discriminator = ?,
                discord_avatar = ?,
                access_token_encrypted = ?,
                refresh_token_encrypted = ?,
                token_expires_at = ?,
                updated_at = CURRENT_TIMESTAMP
        ''', (discord_id, discord_username, user_data['discriminator'], user_data.get('avatar'),
              encrypt_token(access_token), encrypt_token(refresh_token), expires_at,
              discord_username, user_data['discriminator'], user_data.get('avatar'),
              encrypt_token(access_token), encrypt_token(refresh_token), expires_at))

        conn.commit()
        conn.close()

    # Store in session
    session['discord_id'] = discord_id
    session['discord_username'] = discord_username

    return redirect('/?discord_linked=true')

@app.route('/api/discord/link', methods=['POST'])
def link_minecraft():
    """Link Minecraft username to Discord account"""
    if 'discord_id' not in session:
        return jsonify({'error': 'Not logged in with Discord'}), 401

    data = request.json
    minecraft_username = data.get('minecraft_username')

    if not minecraft_username:
        return jsonify({'error': 'Minecraft username required'}), 400

    with db_lock:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE discord_users
            SET minecraft_username = ?, updated_at = CURRENT_TIMESTAMP
            WHERE discord_id = ?
        ''', (minecraft_username, session['discord_id']))

        conn.commit()
        conn.close()

    return jsonify({'success': True, 'minecraft_username': minecraft_username})

@app.route('/api/discord/user')
def get_discord_user():
    """Get current Discord user info"""
    if 'discord_id' not in session:
        return jsonify({'logged_in': False})

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT discord_username, minecraft_username, discord_avatar
        FROM discord_users
        WHERE discord_id = ?
    ''', (session['discord_id'],))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({'logged_in': False})

    return jsonify({
        'logged_in': True,
        'discord_username': user['discord_username'],
        'minecraft_username': user['minecraft_username'],
        'discord_avatar': user['discord_avatar']
    })

@app.route('/api/discord/vc', methods=['GET'])
def api_discord_vc():
    """Get all users currently in voice channels (from whitelisted guilds only)"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            u.discord_username,
            u.minecraft_username,
            v.guild_name,
            v.channel_name,
            v.joined_at
        FROM discord_vc_status v
        JOIN discord_users u ON v.discord_id = u.discord_id
        WHERE v.is_connected = 1
        ORDER BY v.joined_at ASC
    ''')

    users = []
    for row in cursor.fetchall():
        joined_time = datetime.fromisoformat(row['joined_at']) if row['joined_at'] else None
        duration = ''
        if joined_time:
            delta = datetime.now() - joined_time
            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            if hours > 0:
                duration = f"{hours}h {minutes}m"
            else:
                duration = f"{minutes}m"

        users.append({
            'discord_username': row['discord_username'],
            'minecraft_username': row['minecraft_username'] or 'Unknown',
            'guild_name': row['guild_name'],
            'channel_name': row['channel_name'],
            'duration': duration
        })

    conn.close()
    return jsonify(users)

@app.route('/api/discord/report_vc', methods=['POST'])
def report_vc_status():
    """Allow logged-in users to report their own VC status"""
    if 'discord_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.json
    guild_id = data.get('guild_id')
    channel_id = data.get('channel_id')
    channel_name = data.get('channel_name')
    guild_name = data.get('guild_name')
    in_vc = data.get('in_vc', False)

    # Only track whitelisted guilds
    if guild_id and guild_id not in discord_config.WHITELISTED_GUILDS:
        return jsonify({'success': True, 'tracked': False})

    with db_lock:
        conn = get_db()
        cursor = conn.cursor()

        if in_vc and guild_id:
            cursor.execute('''
                INSERT INTO discord_vc_status
                (discord_id, guild_id, guild_name, channel_id, channel_name, is_connected, joined_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(discord_id) DO UPDATE SET
                    guild_id = ?,
                    guild_name = ?,
                    channel_id = ?,
                    channel_name = ?,
                    is_connected = 1,
                    updated_at = CURRENT_TIMESTAMP
            ''', (session['discord_id'], guild_id, guild_name, channel_id, channel_name,
                  guild_id, guild_name, channel_id, channel_name))
        else:
            cursor.execute('''
                UPDATE discord_vc_status
                SET is_connected = 0, updated_at = CURRENT_TIMESTAMP
                WHERE discord_id = ?
            ''', (session['discord_id'],))

        conn.commit()
        conn.close()

    # Emit update
    socketio.emit('vc_update', {'refresh': True})

    return jsonify({'success': True, 'tracked': True})

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('stats_update', get_global_stats())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_stats')
def handle_request_stats():
    emit('stats_update', get_global_stats())

if __name__ == '__main__':
    init_db()
    print("Isaiah Stats Server starting...")
    print("Visit http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
