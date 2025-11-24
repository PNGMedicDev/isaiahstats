# IsaiahUtils Mod - Build Instructions

## Build Issue in Current Environment

The mod cannot be built in the current environment due to DNS resolution failures when accessing Maven repositories:
- maven.fabricmc.net
- repo.maven.apache.org
- plugins.gradle.org

This is a network infrastructure issue, not a code issue.

## How to Build on Your Local Machine

### Prerequisites

1. **Java 21** - Download from [Adoptium](https://adoptium.net/)
2. **Git** - To clone the repository
3. **Internet Connection** - Required to download dependencies

### Build Steps

1. **Navigate to the mod directory:**
   ```bash
   cd mod
   ```

2. **Build the mod using Gradle:**

   On Windows:
   ```bash
   gradlew.bat build
   ```

   On Linux/Mac:
   ```bash
   ./gradlew build
   ```

3. **Find the compiled JAR:**

   After a successful build, the mod JAR will be located at:
   ```
   mod/build/libs/isaiahutils-2.0.0.jar
   ```

### Installing the Mod

1. Make sure you have **Minecraft 1.21.3** installed
2. Install **Fabric Loader** from [fabricmc.net](https://fabricmc.net/use/installer/)
3. Install **Fabric API** from [Modrinth](https://modrinth.com/mod/fabric-api) or [CurseForge](https://www.curseforge.com/minecraft/mc-mods/fabric-api)
4. Copy `isaiahutils-2.0.0.jar` to your Minecraft `mods` folder:
   - Windows: `%APPDATA%\.minecraft\mods\`
   - Linux: `~/.minecraft/mods/`
   - Mac: `~/Library/Application Support/minecraft/mods/`

## Mod Features

✅ **Automatic Web Sync** - Always enabled, syncs bets to IsaiahStats website
✅ **Dual Payment Detection** - Recognizes multiple payment message formats
✅ **Sound Notifications** - Audio feedback for bets and results
✅ **CSV Export** - Export bet history with `Left Alt`
✅ **Session Stats** - View statistics in config screen
✅ **Lifetime Tracking** - Persistent bet tracking per player

## Keybinds

- **Left Ctrl** - Toggle in-game HUD overlay
- **Left Alt** - Export bets to CSV
- **Right Ctrl** - Reset current session stats
- **Right Shift** - Open configuration screen

## Troubleshooting

### Build Fails with Network Errors

Make sure you have a stable internet connection. Gradle needs to download:
- Minecraft 1.21.3
- Fabric Loader 0.16.0
- Fabric API 0.105.0+1.21.3
- Fabric Loom 1.6.7
- Various dependencies

### "Could not find fabric-loom"

The buildscript uses Fabric Loom 1.6.7. If this version is unavailable:

1. Check for newer versions at [fabricmc.net](https://fabricmc.net/develop)
2. Update `build.gradle` line 10:
   ```gradle
   classpath 'net.fabricmc:fabric-loom:1.7.0'  // Use newer version
   ```

### Build Succeeds But JAR is Only 1-2KB

This usually means the build failed silently. Check the build output for errors.
Try cleaning first:
```bash
gradlew clean
gradlew build --refresh-dependencies
```

## Alternative: Pre-built JAR

If you cannot build the mod yourself:

1. Ask someone with a working Java/Gradle setup to build it
2. They can send you the compiled JAR from `build/libs/`
3. Install it following the "Installing the Mod" instructions above

## Support

For issues related to:
- **Mod functionality** - Check the main README.md
- **Building from source** - See this document
- **Website integration** - Check website/README.md
