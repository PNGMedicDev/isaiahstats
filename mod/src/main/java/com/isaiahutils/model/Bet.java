package com.isaiahutils.model;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Represents a single bet with enhanced tracking capabilities
 */
public class Bet {
    private static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("HH:mm:ss");

    private final String playerName;
    private long amount;
    private long totalPaid;
    private final LocalDateTime timestamp;
    private String status; // "pending", "won", "lost"
    private double multiplier;
    private long payout;
    private long profit;

    public Bet(String playerName, long amount) {
        this.playerName = playerName;
        this.amount = amount;
        this.totalPaid = amount;
        this.timestamp = LocalDateTime.now();
        this.status = "pending";
        this.multiplier = 0;
        this.payout = 0;
        this.profit = -amount; // Initially negative
    }

    /**
     * Add additional payment from the same player
     */
    public void addAmount(long additional) {
        this.amount += additional;
        this.totalPaid += additional;
        this.profit -= additional; // More loss initially
    }

    /**
     * Mark bet as won with multiplier
     */
    public void markWon(double multiplier) {
        this.status = "won";
        this.multiplier = multiplier;
        this.payout = (long) (amount * multiplier);
        this.profit = payout - amount;
    }

    /**
     * Mark bet as lost
     */
    public void markLost() {
        this.status = "lost";
        this.multiplier = 0;
        this.payout = 0;
        this.profit = -amount;
    }

    // Getters
    public String getPlayerName() {
        return playerName;
    }

    public long getAmount() {
        return amount;
    }

    public long getTotalPaid() {
        return totalPaid;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public String getStatus() {
        return status;
    }

    public double getMultiplier() {
        return multiplier;
    }

    public long getPayout() {
        return payout;
    }

    public long getProfit() {
        return profit;
    }

    public String getFormattedTime() {
        return timestamp.format(TIME_FORMATTER);
    }

    public String getFormattedAmount() {
        return formatMoney(amount);
    }

    public String getFormattedTotalPaid() {
        return formatMoney(totalPaid);
    }

    public String getFormattedPayout() {
        return formatMoney(payout);
    }

    public String getFormattedProfit() {
        return formatMoney(Math.abs(profit));
    }

    public boolean isWon() {
        return "won".equals(status);
    }

    public boolean isLost() {
        return "lost".equals(status);
    }

    public boolean isPending() {
        return "pending".equals(status);
    }

    /**
     * Format money with K/M/B suffixes
     */
    public static String formatMoney(long amount) {
        if (amount >= 1_000_000_000L) {
            return String.format("$%.2fB", amount / 1_000_000_000.0);
        } else if (amount >= 1_000_000L) {
            return String.format("$%.2fM", amount / 1_000_000.0);
        } else if (amount >= 1_000L) {
            return String.format("$%.2fK", amount / 1_000.0);
        } else {
            return "$" + amount;
        }
    }

    /**
     * Parse amount string with K/M/B suffixes
     */
    public static long parseAmount(String str) {
        if (str == null || str.isEmpty()) {
            return 0L;
        }

        str = str.toUpperCase().trim().replace("$", "").replace(",", "");

        try {
            char lastChar = str.charAt(str.length() - 1);

            if (Character.isDigit(lastChar)) {
                return Long.parseLong(str);
            }

            double value = Double.parseDouble(str.substring(0, str.length() - 1));

            return switch (lastChar) {
                case 'K' -> (long) (value * 1_000);
                case 'M' -> (long) (value * 1_000_000);
                case 'B' -> (long) (value * 1_000_000_000);
                default -> (long) value;
            };
        } catch (NumberFormatException e) {
            return 0L;
        }
    }

    /**
     * Convert to CSV format
     */
    public String toCSV() {
        return String.format("%s,%s,%d,%s,%s,%.2f,%d,%d",
                getFormattedTime(),
                playerName,
                amount,
                status,
                isWon() ? "WIN" : "LOSS",
                multiplier,
                payout,
                profit
        );
    }

    @Override
    public String toString() {
        return String.format("Bet{player=%s, amount=%s, status=%s, profit=%s}",
                playerName, getFormattedAmount(), status, getFormattedProfit());
    }
}
