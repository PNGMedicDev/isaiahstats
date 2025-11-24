# IsaiahStats - Project Summary

## 🎉 Project Complete!

This is a complete, production-ready gambling statistics system for Isaiah, featuring a real-time website and an enhanced Minecraft mod with advanced features.

## 📦 What's Included

### 🌐 Website (IsaiahStats Dashboard)
A Flask-based web application with Socket.IO for real-time updates:

**Features:**
- ✅ Real-time bet tracking and live feed
- ✅ Interactive leaderboards (Wagered, Winners, Losers)
- ✅ Player search with detailed statistics
- ✅ Beautiful dark theme with neon accents
- ✅ Fully responsive design (mobile-friendly)
- ✅ SQLite database for data persistence
- ✅ RESTful API for mod integration
- ✅ Socket.IO for real-time updates

**Tech Stack:**
- Python 3.8+ with Flask
- Socket.IO for WebSockets
- SQLite database
- TailwindCSS for styling
- Chart.js for visualizations

### 🎮 Minecraft Mod (IsaiahUtils v2.0)
An enhanced Fabric mod for Minecraft 1.21.3:

**New Features (Improvements over LakUtils):**
- ✅ **Sound Notifications** - Audio feedback for wins, losses, and bets
- ✅ **CSV Export** - Export all bet data for offline analysis
- ✅ **Web Sync** - Real-time synchronization with website
- ✅ **Enhanced Statistics** - Session stats, lifetime totals
- ✅ **Better UI** - Improved HUD with smooth animations
- ✅ **More Keybinds** - Quick export, better controls
- ✅ **Advanced Config** - More customization options
- ✅ **Error Handling** - Better error messages and recovery

**Core Features:**
- ✅ Auto-detection of bets from chat messages
- ✅ Win/Loss tracking with multipliers
- ✅ Movable and scalable GUI
- ✅ Min/Max bet filtering
- ✅ Lifetime totals per player
- ✅ Customizable colors
- ✅ Multiple payment format support

## 📂 Project Structure

```
isaiahstats/
├── website/              # Flask web application
│   ├── app.py           # Main server (Flask + Socket.IO)
│   ├── database/        # SQLite database
│   ├── static/
│   │   ├── css/styles.css
│   │   ├── js/app.js    # Frontend JavaScript
│   │   └── downloads/   # Mod download location
│   ├── templates/
│   │   └── index.html   # Main dashboard page
│   └── requirements.txt
│
├── mod/                  # Minecraft Fabric mod
│   ├── src/main/java/com/isaiahutils/
│   │   ├── IsaiahUtils.java       # Main mod class
│   │   ├── config/Config.java     # Configuration
│   │   ├── manager/
│   │   │   ├── BetManager.java    # Bet tracking logic
│   │   │   ├── StatsManager.java  # Statistics and export
│   │   │   └── SoundManager.java  # Audio notifications
│   │   ├── model/Bet.java         # Bet data model
│   │   ├── gui/BetScreen.java     # Config screen
│   │   └── util/WebSync.java      # Website sync
│   ├── build.gradle
│   └── gradle.properties
│
├── scripts/              # Build automation
│   ├── build-all.bat           # Build everything
│   ├── build-mod-only.bat      # Compile mod only
│   ├── setup-website.bat       # Install dependencies
│   └── start-website.bat       # Run web server
│
├── README.md            # Full documentation
├── QUICKSTART.md        # Quick setup guide
└── .gitignore          # Git ignore rules
```

## 🚀 Quick Start

### Build Everything
```batch
cd scripts
build-all.bat
```

### Start Website
```batch
cd scripts
setup-website.bat
start-website.bat
```

### Install Mod
1. Copy `build/mod/isaiahutils-2.0.0.jar` to `.minecraft/mods/`
2. Launch Minecraft 1.21.3 with Fabric

## 🔑 Key Improvements Over Original

### Compared to LakStats:
- ✅ Customized for Isaiah (not Lak)
- ✅ Cleaner codebase
- ✅ Better error handling
- ✅ More features

### Compared to LakUtils Mod:
| Feature | LakUtils | IsaiahUtils |
|---------|----------|-------------|
| Sound Notifications | ❌ | ✅ |
| CSV Export | ❌ | ✅ |
| Web Sync | ❌ | ✅ |
| Session Statistics | ❌ | ✅ |
| Advanced Config | ⚠️ Basic | ✅ Full |
| Export Keybind | ❌ | ✅ |
| Error Messages | ⚠️ Basic | ✅ Detailed |
| Code Quality | ⚠️ | ✅ Improved |

## 📊 Features Comparison

### Website Features
- [x] Real-time updates
- [x] Leaderboards (3 categories)
- [x] Player search
- [x] Live bet feed
- [x] Player statistics
- [x] Bet history
- [x] Mobile responsive
- [x] Socket.IO integration
- [x] RESTful API
- [x] SQLite database
- [x] Dark theme
- [x] Customizable colors

### Mod Features
- [x] Bet detection (multiple formats)
- [x] Win/Loss tracking
- [x] Multiplier support
- [x] GUI HUD overlay
- [x] Move mode
- [x] Configuration screen
- [x] Min/Max bet filtering
- [x] Lifetime totals
- [x] Sound effects
- [x] CSV export
- [x] Web synchronization
- [x] Session statistics
- [x] Custom colors
- [x] Scalable GUI

## 🔧 Technical Details

### Website
- **Backend**: Flask 3.0.0
- **Real-time**: Flask-SocketIO 5.3.5
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: TailwindCSS
- **Charts**: Chart.js

### Mod
- **Minecraft Version**: 1.21.3
- **Mod Loader**: Fabric
- **Java Version**: 21
- **Build System**: Gradle
- **Dependencies**: Fabric API, Gson

## 📝 API Endpoints

```
GET  /api/stats              - Global statistics
GET  /api/leaderboard/{cat}  - Leaderboards
GET  /api/player/{username}  - Player stats
GET  /api/recent             - Recent bets
GET  /api/search?q={query}   - Search players
POST /api/bet                - Record bet
```

## 🎯 Use Cases

1. **Live Streaming** - Display real-time stats on stream
2. **Discord Integration** - Share stats with community
3. **Personal Tracking** - Keep records of all gambling
4. **Analytics** - Export data for detailed analysis
5. **Leaderboards** - Competitive rankings
6. **Transparency** - Public statistics for trust

## 🛠️ Customization

### Colors (Mod)
Edit config.json or use in-game config screen:
- Title color
- Border color
- Username color
- Min/Max color

### Colors (Website)
Edit `website/static/css/styles.css`:
- Neon green, purple, blue
- Dark background
- Card backgrounds

### Bet Detection
Modify patterns in `BetManager.java`:
```java
Pattern.compile("^(.+?) paid you \\$?([0-9,.]+)([KMB]?)?\\.?$")
```

## 📊 Database Schema

**players** table:
- id, username, total_bets, total_wagered
- total_won, total_lost, net_profit
- win_count, loss_count
- created_at, updated_at

**bets** table:
- id, player_id, username
- amount, multiplier, payout, profit
- result, timestamp

**daily_stats** table:
- id, date, total_bets
- total_wagered, house_profit
- unique_players

## 🔒 Security Notes

- Website runs on localhost by default (safe)
- No authentication (add if deploying publicly)
- Database is local SQLite (file-based)
- Mod only monitors chat (no server modification)
- Web sync is optional and disabled by default

## 🚀 Future Enhancements

Possible additions:
- [ ] Discord bot integration
- [ ] Advanced analytics dashboard
- [ ] Mobile app
- [ ] Multi-user support
- [ ] Authentication system
- [ ] Cloud database option
- [ ] Automated backups
- [ ] Profit/loss calculator
- [ ] Bet predictions (AI/ML)
- [ ] Tournament mode

## 📦 Deliverables

✅ Complete source code
✅ Build scripts (.bat files)
✅ Comprehensive documentation
✅ Quick start guide
✅ Working website
✅ Enhanced Minecraft mod
✅ Database schema
✅ API documentation
✅ Examples and usage guides

## 🎓 Learning Resources

- **Flask**: https://flask.palletsprojects.com/
- **Socket.IO**: https://socket.io/
- **Fabric Modding**: https://fabricmc.net/wiki/
- **Gradle**: https://docs.gradle.org/

## 📞 Support

For issues:
1. Check README.md
2. Review QUICKSTART.md
3. Check logs (mod: .minecraft/logs/, website: console)
4. Verify requirements are met

## 🎉 Credits

- **Design Inspiration**: LakStats.cc
- **Base Mod Concept**: LakUtils
- **Enhanced by**: Isaiah Casino Team
- **Built with**: Love for the gambling community ❤️

---

**Status**: ✅ COMPLETE AND READY TO USE

**Version**: 2.0.0

**Last Updated**: 2024

**Made for**: Isaiah Gambling Statistics

**License**: MIT
