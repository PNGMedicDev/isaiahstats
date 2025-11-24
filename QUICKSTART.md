# IsaiahStats - Quick Start Guide

Get up and running in 5 minutes!

## 🚀 Prerequisites

- **Windows OS**
- **Python 3.8+** (for website)
- **Java 21+** (for mod compilation)
- **Minecraft 1.21.3** with **Fabric Loader**

## 📦 Installation Steps

### Option 1: Build Everything (Recommended)

```batch
# Navigate to project directory
cd isaiahstats

# Run the build script
cd scripts
build-all.bat
```

This creates a `build/` folder with:
- `build/mod/` - Compiled mod JAR
- `build/website/` - Ready-to-run website

### Option 2: Quick Setup (Individual Components)

#### Website Only
```batch
cd scripts
setup-website.bat
start-website.bat
```

#### Mod Only
```batch
cd scripts
build-mod-only.bat
```

## 🎮 Using the Mod

1. **Install**
   - Copy `isaiahutils-2.0.0.jar` to `.minecraft/mods/`
   - Start Minecraft 1.21.3 with Fabric

2. **Configure**
   - Press `Right Ctrl` in-game
   - Set username and bet limits
   - Save and close

3. **Start Tracking**
   - Press `Left Ctrl` to enable
   - Bets are auto-detected from chat
   - Use Win/Lose buttons to mark outcomes

## 🌐 Using the Website

1. **Start Server**
   ```batch
   cd website
   python app.py
   ```

2. **Open Browser**
   - Visit `http://localhost:5000`
   - View live stats and leaderboards

3. **Enable Mod Sync** (Optional)
   - In mod config, enable "Web Sync"
   - Set server URL to `http://localhost:5000`
   - Bets automatically sync to website

## ⌨️ Mod Keybinds

| Key | Action |
|-----|--------|
| `Left Ctrl` | Toggle bet tracker |
| `Left Alt` | Move GUI mode |
| `Right Ctrl` | Open config |
| `Right Shift` | Export to CSV |

## 🎯 First Bet Example

1. Enable tracker: Press `Left Ctrl`
2. Someone pays you: `PlayerName paid you $100M`
3. Click `Win` or `Lose` button
4. If win, enter multiplier (e.g., 2.0)
5. Bet is recorded!

## 📊 Viewing Stats

### In-Game
- Active bets shown in HUD
- Lifetime totals per player
- Session statistics

### Website
- Real-time leaderboards
- Player search
- Live bet feed
- Detailed player stats

## 💡 Tips

- Use move mode (`Left Alt`) to position the HUD
- Export data regularly (`Right Shift`)
- Enable sounds for better feedback
- Sync to website for permanent records

## ❓ Common Issues

**Mod not detecting bets?**
- Check chat message format
- Verify bet is within min/max range
- Make sure tracker is enabled

**Website won't start?**
- Run `setup-website.bat` first
- Check Python is installed: `python --version`
- Ensure port 5000 is free

**Build failed?**
- Make sure Java 21+ is installed
- Run `gradle wrapper` in mod directory
- Check internet connection (downloads dependencies)

## 📚 Next Steps

- Read full [README.md](README.md)
- Customize colors and settings
- Set up web sync for cloud statistics
- Export data for analysis

---

**That's it! You're ready to track Isaiah's gambling stats! 🎰**
