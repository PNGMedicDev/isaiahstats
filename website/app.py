#!/usr/bin/env python3
"""
IsaiahStats - Real-time Gambling Statistics Tracker
A Flask + Socket.IO application for tracking Isaiah's casino statistics
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sqlite3
import json
import time
from datetime import datetime, timedelta
from threading import Lock
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'isaiah-stats-secret-key-change-in-production'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

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

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bets_timestamp ON bets(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bets_username ON bets(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_players_username ON players(username)')

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
