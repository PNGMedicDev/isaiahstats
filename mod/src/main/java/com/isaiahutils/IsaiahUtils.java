package com.isaiahutils;

import com.isaiahutils.config.Config;
import com.isaiahutils.gui.BetScreen;
import com.isaiahutils.manager.BetManager;
import com.isaiahutils.manager.StatsManager;
import com.isaiahutils.manager.SoundManager;
import com.isaiahutils.util.WebSync;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.fabricmc.fabric.api.client.message.v1.ClientReceiveMessageEvents;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.option.KeyBinding;
import net.minecraft.client.util.InputUtil;
import org.lwjgl.glfw.GLFW;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;

/**
 * IsaiahUtils - Enhanced Casino Betting Mod for Minecraft 1.21.3
 * An improved version with advanced features and better UX
 *
 * @author Isaiah Casino Team
 * @version 2.0.0
 */
public class IsaiahUtils implements ClientModInitializer {

    public static final String MOD_ID = "isaiahutils";
    public static final String MOD_NAME = "IsaiahUtils";
    public static final String VERSION = "2.0.0";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    public static MinecraftClient mc;
    public static final File CONFIG_DIR = new File("config/isaiahutils");
    public static final File EXPORTS_DIR = new File("config/isaiahutils/exports");

    private static KeyBinding openGuiKey;
    private static KeyBinding moveGuiKey;
    private static KeyBinding configKey;
    private static KeyBinding exportKey;

    public static BetManager betManager;
    public static StatsManager statsManager;
    public static SoundManager soundManager;
    public static Config config;
    public static WebSync webSync;

    @Override
    public void onInitializeClient() {
        LOGGER.info("Initializing {} v{}", MOD_NAME, VERSION);

        mc = MinecraftClient.getInstance();

        // Create directories
        if (!CONFIG_DIR.exists()) {
            CONFIG_DIR.mkdirs();
        }
        if (!EXPORTS_DIR.exists()) {
            EXPORTS_DIR.mkdirs();
        }

        // Initialize components
        config = new Config();
        config.load();

        betManager = new BetManager();
        statsManager = new StatsManager();
        soundManager = new SoundManager();
        webSync = new WebSync(config.serverUrl, config.syncEnabled);

        // Register keybindings
        registerKeybindings();

        // Register event handlers
        registerEvents();

        LOGGER.info("{} initialized successfully", MOD_NAME);
    }

    private void registerKeybindings() {
        openGuiKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "key.isaiahutils.toggle",
                InputUtil.Type.KEYSYM,
                GLFW.GLFW_KEY_LEFT_CONTROL,
                "category.isaiahutils"
        ));

        moveGuiKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "key.isaiahutils.move",
                InputUtil.Type.KEYSYM,
                GLFW.GLFW_KEY_LEFT_ALT,
                "category.isaiahutils"
        ));

        configKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "key.isaiahutils.config",
                InputUtil.Type.KEYSYM,
                GLFW.GLFW_KEY_RIGHT_CONTROL,
                "category.isaiahutils"
        ));

        exportKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "key.isaiahutils.export",
                InputUtil.Type.KEYSYM,
                GLFW.GLFW_KEY_RIGHT_SHIFT,
                "category.isaiahutils"
        ));
    }

    private void registerEvents() {
        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            // Toggle betting tracker
            if (openGuiKey.wasPressed()) {
                betManager.toggleEnabled();
                if (betManager.isEnabled()) {
                    sendMessage("§a§lBet Tracker Enabled");
                } else {
                    sendMessage("§c§lBet Tracker Disabled");
                }
            }

            // Toggle move mode
            if (moveGuiKey.wasPressed()) {
                betManager.toggleMoveMode();
                if (betManager.isMoveMode()) {
                    sendMessage("§e§lMove Mode: §aON §7- Use arrow keys to move, +/- to scale");
                } else {
                    sendMessage("§e§lMove Mode: §cOFF");
                    saveConfig();
                }
            }

            // Open config screen
            if (configKey.wasPressed() && client.currentScreen == null) {
                client.setScreen(new BetScreen());
            }

            // Export data
            if (exportKey.wasPressed()) {
                exportData();
            }

            // Handle move mode controls
            if (betManager.isMoveMode() && client.currentScreen == null) {
                handleMoveMode();
            }
        });

        // Chat message handler for bet detection
        ClientReceiveMessageEvents.GAME.register((message, overlay) -> {
            if (!overlay && betManager.isEnabled()) {
                String text = message.getString();
                betManager.onChatMessage(text);
            }
        });
    }

    private void handleMoveMode() {
        long windowHandle = mc.getWindow().getHandle();
        boolean shiftPressed = GLFW.glfwGetKey(windowHandle, GLFW.GLFW_KEY_LEFT_SHIFT) == GLFW.GLFW_PRESS ||
                               GLFW.glfwGetKey(windowHandle, GLFW.GLFW_KEY_RIGHT_SHIFT) == GLFW.GLFW_PRESS;

        if (shiftPressed) {
            // Scale adjustment
            if (GLFW.glfwGetKey(windowHandle, GLFW.GLFW_KEY_EQUAL) == GLFW.GLFW_PRESS ||
                GLFW.glfwGetKey(windowHandle, GLFW.GLFW_KEY_KP_ADD) == GLFW.GLFW_PRESS) {
                config.guiScale = Math.min(config.guiScale + 0.05f, 3.0f);
                sleep(50);
            }

            if (GLFW.glfwGetKey(windowHandle, GLFW.GLFW_KEY_MINUS) == GLFW.GLFW_PRESS ||
                GLFW.glfwGetKey(windowHandle, GLFW.GLFW_KEY_KP_SUBTRACT) == GLFW.GLFW_PRESS) {
                config.guiScale = Math.max(config.guiScale - 0.05f, 0.5f);
                sleep(50);
            }
        } else {
            // Position adjustment
            int moveSpeed = 5;

            if (GLFW.glfwGetKey(windowHandle, GLFW.GLFW_KEY_LEFT) == GLFW.GLFW_PRESS) {
                config.guiX -= moveSpeed;
            }
            if (GLFW.glfwGetKey(windowHandle, GLFW.GLFW_KEY_RIGHT) == GLFW.GLFW_PRESS) {
                config.guiX += moveSpeed;
            }
            if (GLFW.glfwGetKey(windowHandle, GLFW.GLFW_KEY_UP) == GLFW.GLFW_PRESS) {
                config.guiY -= moveSpeed;
            }
            if (GLFW.glfwGetKey(windowHandle, GLFW.GLFW_KEY_DOWN) == GLFW.GLFW_PRESS) {
                config.guiY += moveSpeed;
            }
        }
    }

    private void exportData() {
        try {
            String filename = statsManager.exportToCSV();
            sendMessage("§a§lData Exported: §f" + filename);
            soundManager.playSuccessSound();
        } catch (Exception e) {
            sendMessage("§c§lExport Failed: " + e.getMessage());
            soundManager.playErrorSound();
            LOGGER.error("Failed to export data", e);
        }
    }

    public static void saveConfig() {
        config.save();
        LOGGER.info("Configuration saved");
    }

    public static void sendMessage(String message) {
        if (mc.player != null) {
            mc.player.sendMessage(net.minecraft.text.Text.literal(message), false);
        }
    }

    private void sleep(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
