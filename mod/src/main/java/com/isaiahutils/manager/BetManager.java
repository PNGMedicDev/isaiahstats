package com.isaiahutils.manager;

import com.isaiahutils.IsaiahUtils;
import com.isaiahutils.model.Bet;
import com.isaiahutils.util.WebSync;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Enhanced Bet Manager with better tracking and features
 */
public class BetManager {
    // Regex patterns for bet detection
    private static final Pattern PAYMENT_PATTERN = Pattern.compile("^(.+?) paid you \\$?([0-9,.]+)([KMB]?)?\\.?$");
    private static final Pattern PAYMENT_PATTERN_ALT = Pattern.compile("^You received \\$?([0-9,.]+)([KMB]?)? from (.+?)$");

    private final List<Bet> activeBets = new ArrayList<>();
    private final Map<String, Long> lifetimeTotals = new HashMap<>();
    private final List<Bet> completedBets = new ArrayList<>();

    private boolean enabled = false;
    private boolean moveMode = false;

    private String highestRoller = "";
    private long highestRollerAmount = 0L;

    private long totalBetsProcessed = 0;
    private long totalWagered = 0;
    private long totalWon = 0;
    private long totalLost = 0;

    public BetManager() {
        IsaiahUtils.LOGGER.info("BetManager initialized");
    }

    /**
     * Process incoming chat messages for bet detection
     */
    public void onChatMessage(String message) {
        if (!enabled) return;

        // Try main payment pattern
        Matcher matcher = PAYMENT_PATTERN.matcher(message);
        if (!matcher.matches()) {
            // Try alternative pattern
            matcher = PAYMENT_PATTERN_ALT.matcher(message);
            if (!matcher.matches()) {
                return;
            }
        }

        processBetPayment(matcher);
    }

    private void processBetPayment(Matcher matcher) {
        String playerName;
        String amountStr;
        String suffix;

        // Determine which pattern matched
        if (matcher.groupCount() == 3) {
            // Main pattern: "PlayerName paid you $100M"
            playerName = matcher.group(1);
            amountStr = matcher.group(2).replace(",", "");
            suffix = matcher.group(3) != null ? matcher.group(3) : "";
        } else {
            // Alt pattern: "You received $100M from PlayerName"
            amountStr = matcher.group(1).replace(",", "");
            suffix = matcher.group(2) != null ? matcher.group(2) : "";
            playerName = matcher.group(3);
        }

        try {
            long amount = parseAmount(amountStr, suffix);

            // Check min/max bet limits
            long minBet = Bet.parseAmount(IsaiahUtils.config.minBet);
            long maxBet = Bet.parseAmount(IsaiahUtils.config.maxBet);

            if (amount < minBet || (maxBet > 0 && amount > maxBet)) {
                IsaiahUtils.LOGGER.debug("Bet amount {} outside range [{}, {}]", amount, minBet, maxBet);
                return;
            }

            // Update lifetime totals
            lifetimeTotals.put(playerName, lifetimeTotals.getOrDefault(playerName, 0L) + amount);
            long playerTotal = lifetimeTotals.get(playerName);

            // Update highest roller
            if (playerTotal > highestRollerAmount) {
                highestRoller = playerName;
                highestRollerAmount = playerTotal;
            }

            // Find or create bet
            Bet bet = findActiveBet(playerName);
            if (bet != null) {
                bet.addAmount(amount);
                IsaiahUtils.LOGGER.info("Added {} to existing bet for {}", amount, playerName);
            } else {
                bet = new Bet(playerName, amount);
                activeBets.add(bet);
                IsaiahUtils.LOGGER.info("New bet created: {}", bet);
            }

            totalWagered += amount;
            totalBetsProcessed++;

            // Play sound notification
            IsaiahUtils.soundManager.playBetReceivedSound();

        } catch (NumberFormatException e) {
            IsaiahUtils.LOGGER.error("Failed to parse bet amount: {}{}", amountStr, suffix, e);
        }
    }

    private Bet findActiveBet(String playerName) {
        return activeBets.stream()
                .filter(bet -> bet.getPlayerName().equalsIgnoreCase(playerName) && bet.isPending())
                .findFirst()
                .orElse(null);
    }

    private long parseAmount(String value, String suffix) {
        double amount = Double.parseDouble(value);

        return switch (suffix.toUpperCase()) {
            case "K" -> (long) (amount * 1_000);
            case "M" -> (long) (amount * 1_000_000);
            case "B" -> (long) (amount * 1_000_000_000);
            default -> (long) amount;
        };
    }

    /**
     * Mark a bet as won
     */
    public void markWon(Bet bet, double multiplier) {
        if (bet == null) return;

        bet.markWon(multiplier);
        completedBets.add(bet);
        activeBets.remove(bet);

        totalWon += bet.getPayout();

        // Sync to web if enabled
        if (IsaiahUtils.config.syncEnabled && IsaiahUtils.webSync != null) {
            IsaiahUtils.webSync.sendBet(bet);
        }

        // Update stats
        IsaiahUtils.statsManager.recordBet(bet);

        // Play success sound
        IsaiahUtils.soundManager.playWinSound();

        IsaiahUtils.LOGGER.info("Bet marked as won: {}", bet);
    }

    /**
     * Mark a bet as lost
     */
    public void markLost(Bet bet) {
        if (bet == null) return;

        bet.markLost();
        completedBets.add(bet);
        activeBets.remove(bet);

        totalLost += bet.getAmount();

        // Sync to web if enabled
        if (IsaiahUtils.config.syncEnabled && IsaiahUtils.webSync != null) {
            IsaiahUtils.webSync.sendBet(bet);
        }

        // Update stats
        IsaiahUtils.statsManager.recordBet(bet);

        // Play loss sound
        IsaiahUtils.soundManager.playLossSound();

        IsaiahUtils.LOGGER.info("Bet marked as lost: {}", bet);
    }

    /**
     * Remove/cancel a bet
     */
    public void removeBet(Bet bet) {
        activeBets.remove(bet);
        IsaiahUtils.LOGGER.info("Bet removed: {}", bet);
    }

    /**
     * Clear all active bets
     */
    public void clearAllBets() {
        int count = activeBets.size();
        activeBets.clear();
        IsaiahUtils.LOGGER.info("Cleared {} active bets", count);
        IsaiahUtils.sendMessage("§e§lCleared " + count + " active bets");
    }

    // Getters
    public List<Bet> getActiveBets() {
        return new ArrayList<>(activeBets);
    }

    public List<Bet> getCompletedBets() {
        return new ArrayList<>(completedBets);
    }

    public long getLifetimeTotal(String playerName) {
        return lifetimeTotals.getOrDefault(playerName, 0L);
    }

    public boolean isEnabled() {
        return enabled;
    }

    public boolean isMoveMode() {
        return moveMode;
    }

    public String getHighestRoller() {
        return highestRoller;
    }

    public long getHighestRollerAmount() {
        return highestRollerAmount;
    }

    public long getTotalBetsProcessed() {
        return totalBetsProcessed;
    }

    public long getTotalWagered() {
        return totalWagered;
    }

    public long getTotalWon() {
        return totalWon;
    }

    public long getTotalLost() {
        return totalLost;
    }

    public long getNetProfit() {
        return totalWon - totalLost;
    }

    // Setters/Toggles
    public void toggleEnabled() {
        enabled = !enabled;
        IsaiahUtils.LOGGER.info("Bet tracking {}", enabled ? "enabled" : "disabled");
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public void toggleMoveMode() {
        moveMode = !moveMode;
        IsaiahUtils.LOGGER.info("Move mode {}", moveMode ? "enabled" : "disabled");
    }

    public void setMoveMode(boolean moveMode) {
        this.moveMode = moveMode;
    }

    /**
     * Get statistics summary
     */
    public Map<String, Object> getStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("activeBets", activeBets.size());
        stats.put("completedBets", completedBets.size());
        stats.put("totalProcessed", totalBetsProcessed);
        stats.put("totalWagered", totalWagered);
        stats.put("totalWon", totalWon);
        stats.put("totalLost", totalLost);
        stats.put("netProfit", getNetProfit());
        stats.put("highestRoller", highestRoller);
        stats.put("highestRollerAmount", highestRollerAmount);
        return stats;
    }
}
