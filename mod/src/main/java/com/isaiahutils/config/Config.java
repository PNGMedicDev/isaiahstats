package com.isaiahutils.config;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.isaiahutils.IsaiahUtils;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;

public class Config {
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final File CONFIG_FILE = new File(IsaiahUtils.CONFIG_DIR, "config.json");

    // General settings
    public String username = "Isaiah";
    public String minBet = "100K";
    public String maxBet = "25M";
    public double defaultMultiplier = 2.0;

    // GUI settings
    public int guiX = 10;
    public int guiY = 10;
    public float guiScale = 1.0f;

    // Colors
    public int titleColor = 0x00FF00; // Green
    public int titleBarColor = 0xFF00FF00; // Solid green
    public int usernameColor = 0xAAAAAAA; // Light gray
    public int minMaxColor = 0xAAAAAAA;

    // Features
    public boolean soundEnabled = true;
    public boolean syncEnabled = false;
    public String serverUrl = "http://localhost:5000";

    // Advanced
    public boolean showLifetimeTotals = true;
    public boolean showSessionStats = true;
    public boolean confirmBeforeExport = false;

    public void load() {
        if (!CONFIG_FILE.exists()) {
            save();
            return;
        }

        try (FileReader reader = new FileReader(CONFIG_FILE)) {
            Config loaded = GSON.fromJson(reader, Config.class);
            if (loaded != null) {
                copyFrom(loaded);
            }
        } catch (Exception e) {
            IsaiahUtils.LOGGER.error("Failed to load config", e);
        }
    }

    public void save() {
        try (FileWriter writer = new FileWriter(CONFIG_FILE)) {
            GSON.toJson(this, writer);
        } catch (Exception e) {
            IsaiahUtils.LOGGER.error("Failed to save config", e);
        }
    }

    private void copyFrom(Config other) {
        this.username = other.username;
        this.minBet = other.minBet;
        this.maxBet = other.maxBet;
        this.defaultMultiplier = other.defaultMultiplier;
        this.guiX = other.guiX;
        this.guiY = other.guiY;
        this.guiScale = other.guiScale;
        this.titleColor = other.titleColor;
        this.titleBarColor = other.titleBarColor;
        this.usernameColor = other.usernameColor;
        this.minMaxColor = other.minMaxColor;
        this.soundEnabled = other.soundEnabled;
        this.syncEnabled = other.syncEnabled;
        this.serverUrl = other.serverUrl;
        this.showLifetimeTotals = other.showLifetimeTotals;
        this.showSessionStats = other.showSessionStats;
        this.confirmBeforeExport = other.confirmBeforeExport;
    }
}
