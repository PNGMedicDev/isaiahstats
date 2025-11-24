package com.isaiahutils.gui;

import com.isaiahutils.IsaiahUtils;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.screen.Screen;
import net.minecraft.client.gui.widget.ButtonWidget;
import net.minecraft.client.gui.widget.TextFieldWidget;
import net.minecraft.text.Text;

/**
 * Configuration screen for IsaiahUtils
 */
public class BetScreen extends Screen {
    private TextFieldWidget usernameField;
    private TextFieldWidget minBetField;
    private TextFieldWidget maxBetField;
    private TextFieldWidget multiplierField;
    private TextFieldWidget serverUrlField;

    public BetScreen() {
        super(Text.literal("IsaiahUtils Configuration"));
    }

    @Override
    protected void init() {
        int centerX = this.width / 2;
        int startY = 50;
        int fieldSpacing = 30;

        // Username field
        this.usernameField = new TextFieldWidget(this.textRenderer, centerX - 100, startY, 200, 20, Text.literal("Username"));
        this.usernameField.setMaxLength(16);
        this.usernameField.setText(IsaiahUtils.config.username);
        this.addSelectableChild(this.usernameField);

        // Min Bet field
        int currentY = startY + fieldSpacing;
        this.minBetField = new TextFieldWidget(this.textRenderer, centerX - 100, currentY, 200, 20, Text.literal("Min Bet"));
        this.minBetField.setMaxLength(10);
        this.minBetField.setText(IsaiahUtils.config.minBet);
        this.addSelectableChild(this.minBetField);

        // Max Bet field
        currentY += fieldSpacing;
        this.maxBetField = new TextFieldWidget(this.textRenderer, centerX - 100, currentY, 200, 20, Text.literal("Max Bet"));
        this.maxBetField.setMaxLength(10);
        this.maxBetField.setText(IsaiahUtils.config.maxBet);
        this.addSelectableChild(this.maxBetField);

        // Multiplier field
        currentY += fieldSpacing;
        this.multiplierField = new TextFieldWidget(this.textRenderer, centerX - 100, currentY, 200, 20, Text.literal("Default Multiplier"));
        this.multiplierField.setMaxLength(5);
        this.multiplierField.setText(String.valueOf(IsaiahUtils.config.defaultMultiplier));
        this.addSelectableChild(this.multiplierField);

        // Server URL field
        currentY += fieldSpacing;
        this.serverUrlField = new TextFieldWidget(this.textRenderer, centerX - 100, currentY, 200, 20, Text.literal("Server URL"));
        this.serverUrlField.setMaxLength(100);
        this.serverUrlField.setText(IsaiahUtils.config.serverUrl);
        this.addSelectableChild(this.serverUrlField);

        // Sound toggle button
        currentY += fieldSpacing + 10;
        this.addDrawableChild(ButtonWidget.builder(
                Text.literal("Sounds: " + (IsaiahUtils.config.soundEnabled ? "ON" : "OFF")),
                button -> {
                    IsaiahUtils.config.soundEnabled = !IsaiahUtils.config.soundEnabled;
                    button.setMessage(Text.literal("Sounds: " + (IsaiahUtils.config.soundEnabled ? "ON" : "OFF")));
                }
        ).dimensions(centerX - 100, currentY, 200, 20).build());

        // Auto-sync info label (web sync is always enabled)
        currentY += 25;

        // Save and Cancel buttons
        currentY += 25;
        this.addDrawableChild(ButtonWidget.builder(
                Text.literal("Save"),
                button -> {
                    saveConfig();
                    this.close();
                }
        ).dimensions(centerX - 100, currentY, 95, 20).build());

        this.addDrawableChild(ButtonWidget.builder(
                Text.literal("Cancel"),
                button -> this.close()
        ).dimensions(centerX + 5, currentY, 95, 20).build());
    }

    private void saveConfig() {
        IsaiahUtils.config.username = this.usernameField.getText();
        IsaiahUtils.config.minBet = this.minBetField.getText();
        IsaiahUtils.config.maxBet = this.maxBetField.getText();
        IsaiahUtils.config.serverUrl = this.serverUrlField.getText();

        try {
            IsaiahUtils.config.defaultMultiplier = Double.parseDouble(this.multiplierField.getText());
        } catch (NumberFormatException e) {
            IsaiahUtils.config.defaultMultiplier = 2.0;
        }

        IsaiahUtils.saveConfig();
        IsaiahUtils.sendMessage("§a§lConfiguration saved!");
    }

    @Override
    public void render(DrawContext context, int mouseX, int mouseY, float delta) {
        super.render(context, mouseX, mouseY, delta);

        int centerX = this.width / 2;
        int startY = 50;
        int fieldSpacing = 30;

        // Title
        context.drawCenteredTextWithShadow(this.textRenderer, "IsaiahUtils Configuration", centerX, 20, 0xFFFFFF);

        // Field labels
        context.drawTextWithShadow(this.textRenderer, "Username:", centerX - 100, startY - 10, 0xAAAAAAA);
        this.usernameField.render(context, mouseX, mouseY, delta);

        int currentY = startY + fieldSpacing;
        context.drawTextWithShadow(this.textRenderer, "Min Bet:", centerX - 100, currentY - 10, 0xAAAAAAA);
        this.minBetField.render(context, mouseX, mouseY, delta);

        currentY += fieldSpacing;
        context.drawTextWithShadow(this.textRenderer, "Max Bet:", centerX - 100, currentY - 10, 0xAAAAAAA);
        this.maxBetField.render(context, mouseX, mouseY, delta);

        currentY += fieldSpacing;
        context.drawTextWithShadow(this.textRenderer, "Default Multiplier:", centerX - 100, currentY - 10, 0xAAAAAAA);
        this.multiplierField.render(context, mouseX, mouseY, delta);

        currentY += fieldSpacing;
        context.drawTextWithShadow(this.textRenderer, "Server URL:", centerX - 100, currentY - 10, 0xAAAAAAA);
        this.serverUrlField.render(context, mouseX, mouseY, delta);

        // Auto-sync info
        currentY += fieldSpacing + 10;
        currentY += 25;
        context.drawCenteredTextWithShadow(this.textRenderer, "§a§lWeb Sync: Always Enabled", centerX, currentY + 5, 0x00FF00);
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        this.usernameField.mouseClicked(mouseX, mouseY, button);
        this.minBetField.mouseClicked(mouseX, mouseY, button);
        this.maxBetField.mouseClicked(mouseX, mouseY, button);
        this.multiplierField.mouseClicked(mouseX, mouseY, button);
        this.serverUrlField.mouseClicked(mouseX, mouseY, button);
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (this.usernameField.keyPressed(keyCode, scanCode, modifiers)) return true;
        if (this.minBetField.keyPressed(keyCode, scanCode, modifiers)) return true;
        if (this.maxBetField.keyPressed(keyCode, scanCode, modifiers)) return true;
        if (this.multiplierField.keyPressed(keyCode, scanCode, modifiers)) return true;
        if (this.serverUrlField.keyPressed(keyCode, scanCode, modifiers)) return true;
        return super.keyPressed(keyCode, scanCode, modifiers);
    }

    @Override
    public boolean charTyped(char chr, int modifiers) {
        if (this.usernameField.charTyped(chr, modifiers)) return true;
        if (this.minBetField.charTyped(chr, modifiers)) return true;
        if (this.maxBetField.charTyped(chr, modifiers)) return true;
        if (this.multiplierField.charTyped(chr, modifiers)) return true;
        if (this.serverUrlField.charTyped(chr, modifiers)) return true;
        return super.charTyped(chr, modifiers);
    }
}
