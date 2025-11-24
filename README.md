# IsaiahStats - Complete Casino Statistics System

A comprehensive gambling statistics tracking system featuring:
- **Real-time Web Dashboard** - Live statistics, leaderboards, and bet tracking
- **Enhanced Minecraft Mod** - Advanced in-game bet management with sound notifications and web sync
- **Automated Build Scripts** - One-click compilation and deployment

## 🎯 Features

### Website (IsaiahStats Dashboard)
- ✨ Real-time bet tracking with Socket.IO
- 📊 Interactive leaderboards (Most Wagered, Top Winners, Top Losers)
- 🔍 Player search and detailed statistics
- 📈 Live bet feed
- 🎨 Beautiful dark theme with neon accents
- 📱 Fully responsive design
- 🔄 Auto-updating statistics

### Minecraft Mod (IsaiahUtils v2.0)
- 🎮 **Enhanced Bet Tracking** - Automatically detects payments in chat
- 🔔 **Sound Notifications** - Audio feedback for wins, losses, and bets
- 📊 **Statistics Dashboard** - In-game HUD showing active bets
- 💾 **CSV Export** - Export all bet data for analysis
- 🌐 **Web Sync** - Real-time synchronization with IsaiahStats website
- ⚙️ **Customizable GUI** - Move, scale, and customize colors
- 🎯 **Min/Max Bet Filtering** - Automatic bet range validation
- 📝 **Lifetime Totals** - Track total payments per player
- 🎨 **Modern UI** - Clean interface with smooth animations

## 📦 Installation

### Quick Start (Windows)

1. **Clone or download this repository**
   ```bash
   cd isaiahstats
   ```

2. **Build Everything**
   ```batch
   cd scripts
   build-all.bat
   ```

   This will:
   - Compile the Minecraft mod
   - Prepare the website files
   - Create a `build/` folder with everything ready

### Website Setup

1. **Install Python dependencies**
   ```batch
   cd scripts
   setup-website.bat
   ```

2. **Start the website**
   ```batch
   start-website.bat
   ```

3. **Visit** `http://localhost:5000`

### Minecraft Mod Installation

1. **Install Fabric Loader**
   - Download from [fabricmc.net](https://fabricmc.net/)
   - Install for Minecraft 1.21.3

2. **Install the Mod**
   - Copy `build/mod/isaiahutils-2.0.0.jar` to `.minecraft/mods/`
   - Launch Minecraft with Fabric profile

3. **Configure the Mod**
   - In-game, press `Right Ctrl` to open config
   - Set your username, bet limits, and preferences

## 🎮 Mod Usage

### Keybinds
- `Left Ctrl` - Toggle bet tracker ON/OFF
- `Left Alt` - Toggle move mode (reposition GUI)
- `Right Ctrl` - Open configuration screen
- `Right Shift` - Export bet data to CSV

### Move Mode
When in move mode:
- `Arrow Keys` - Move GUI position
- `Shift + Plus/Minus` - Scale GUI size
- Press `Left Alt` again to save and exit

### Configuration
- **Username**: Your display name
- **Min Bet**: Minimum bet amount (e.g., `100K`)
- **Max Bet**: Maximum bet amount (e.g., `25M`)
- **Default Multiplier**: Default multiplier for wins
- **Server URL**: IsaiahStats website URL
- **Sound Effects**: Enable/disable audio notifications
- **Web Sync**: Auto-sync bets to website

### How It Works

1. **Detecting Bets**: The mod monitors chat for payment messages:
   ```
   PlayerName paid you $100M
   You received $100M from PlayerName
   ```

2. **Managing Bets**: Click buttons in the HUD:
   - `Win` - Mark as won (prompts for multiplier)
   - `Lose` - Mark as lost
   - Automatically tracks lifetime totals per player

3. **Exporting Data**: Press `Right Shift` or export from config
   - Saves to `.minecraft/config/isaiahutils/exports/`
   - CSV format with all bet details

## 🌐 Website API

### Endpoints

#### Get Statistics
```http
GET /api/stats
```
Returns global statistics (total bets, wagered, house profit, etc.)

#### Get Leaderboards
```http
GET /api/leaderboard/{category}
```
Categories: `wagered`, `won`, `lost`

#### Get Player Stats
```http
GET /api/player/{username}
```
Returns detailed player statistics and bet history

#### Record Bet (for mod sync)
```http
POST /api/bet
Content-Type: application/json

{
    "username": "PlayerName",
    "amount": 100000000,
    "multiplier": 2.0,
    "result": "win"
}
```

## 🏗️ Project Structure

```
isaiahstats/
├── website/                    # Flask web application
│   ├── app.py                 # Main server file
│   ├── templates/             # HTML templates
│   │   └── index.html         # Main page
│   ├── static/                # Static assets
│   │   ├── css/
│   │   │   └── styles.css     # Custom styles
│   │   ├── js/
│   │   │   └── app.js         # Frontend logic
│   │   └── downloads/         # Mod downloads
│   └── database/              # SQLite database
│
├── mod/                        # Minecraft Fabric mod
│   ├── src/main/java/com/isaiahutils/
│   │   ├── IsaiahUtils.java   # Main mod class
│   │   ├── config/
│   │   │   └── Config.java    # Configuration
│   │   ├── gui/
│   │   │   ├── BetScreen.java # Config screen
│   │   │   └── BetHud.java    # In-game overlay
│   │   ├── manager/
│   │   │   ├── BetManager.java        # Bet tracking
│   │   │   ├── StatsManager.java      # Statistics
│   │   │   └── SoundManager.java      # Audio
│   │   ├── model/
│   │   │   └── Bet.java       # Bet data model
│   │   └── util/
│   │       └── WebSync.java   # Web synchronization
│   ├── build.gradle           # Gradle build file
│   └── gradle.properties      # Mod properties
│
├── scripts/                    # Build automation
│   ├── build-all.bat          # Build everything
│   ├── build-mod-only.bat     # Build mod only
│   ├── setup-website.bat      # Install website deps
│   └── start-website.bat      # Start web server
│
├── build/                      # Compiled output
│   ├── mod/                   # Mod JAR file
│   └── website/               # Website files
│
└── README.md                   # This file
```

## ⚙️ Configuration Files

### Mod Config
Location: `.minecraft/config/isaiahutils/config.json`

```json
{
  "username": "Isaiah",
  "minBet": "100K",
  "maxBet": "25M",
  "defaultMultiplier": 2.0,
  "guiX": 10,
  "guiY": 10,
  "guiScale": 1.0,
  "soundEnabled": true,
  "syncEnabled": false,
  "serverUrl": "http://localhost:5000"
}
```

### Website Config
Edit in `website/app.py`:
- Database path
- Server port
- Socket.IO settings

## 🔧 Development

### Building the Mod
```batch
cd mod
gradlew.bat build
```

### Running the Website
```batch
cd website
python app.py
```

### Testing
```batch
# Test bet endpoint
curl -X POST http://localhost:5000/api/bet ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"TestPlayer\",\"amount\":100000000,\"multiplier\":2.0,\"result\":\"win\"}"
```

## 📊 Database Schema

### Players Table
- `id` - Unique player ID
- `username` - Player name
- `total_bets` - Total number of bets
- `total_wagered` - Total amount wagered
- `total_won` - Total amount won
- `total_lost` - Total amount lost
- `net_profit` - Net profit/loss
- `win_count` - Number of wins
- `loss_count` - Number of losses

### Bets Table
- `id` - Unique bet ID
- `player_id` - Reference to player
- `username` - Player name
- `amount` - Bet amount
- `multiplier` - Win multiplier
- `payout` - Payout amount
- `profit` - Profit/loss
- `result` - 'win' or 'loss'
- `timestamp` - When bet occurred

## 🎨 Customization

### Mod Colors
Edit in config screen or `config.json`:
- `titleColor` - HUD title color (hex)
- `titleBarColor` - HUD border color (hex)
- `usernameColor` - Username text color (hex)

### Website Theme
Edit `website/static/css/styles.css`:
```css
:root {
    --neon-green: #10b981;
    --neon-purple: #a855f7;
    --dark-bg: #0a0a0f;
    /* etc. */
}
```

## 🐛 Troubleshooting

### Mod Not Working
1. Check Minecraft version (must be 1.21.3)
2. Verify Fabric Loader is installed
3. Check logs: `.minecraft/logs/latest.log`
4. Ensure chat messages match expected format

### Website Not Starting
1. Check Python version: `python --version` (need 3.8+)
2. Install dependencies: Run `setup-website.bat`
3. Check port 5000 is not in use
4. Check console for error messages

### Mod Not Detecting Bets
1. Verify min/max bet settings
2. Check chat message format
3. Enable mod with `Left Ctrl`
4. Check if payment messages contain amount with K/M/B suffix

## 📝 License

This project is released under the MIT License.

## 👥 Credits

- **Original LakStats** - Inspiration for the website design
- **Isaiah Casino Team** - Development and enhancement
- **Fabric** - Minecraft modding framework

## 🚀 Future Features

- [ ] Multi-session support
- [ ] Advanced analytics and graphs
- [ ] Discord webhook integration
- [ ] Mobile app
- [ ] Profit/loss calculator
- [ ] Bet history filtering
- [ ] Player comparison tool
- [ ] Auto-backup system

## 📞 Support

For issues or questions:
1. Check this README
2. Review the troubleshooting section
3. Check the logs
4. Create an issue on GitHub

---

**Made with ❤️ for the Isaiah gambling community**
