package com.isaiahutils.manager;

import com.isaiahutils.IsaiahUtils;
import com.isaiahutils.model.Bet;

import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

/**
 * Manages statistics tracking and export functionality
 */
public class StatsManager {
    private static final DateTimeFormatter FILE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm-ss");

    private final List<Bet> allBets = new ArrayList<>();
    private long sessionStart;
    private long sessionWagered = 0;
    private long sessionWon = 0;
    private long sessionLost = 0;

    public StatsManager() {
        this.sessionStart = System.currentTimeMillis();
        IsaiahUtils.LOGGER.info("StatsManager initialized");
    }

    /**
     * Record a completed bet
     */
    public void recordBet(Bet bet) {
        allBets.add(bet);

        if (bet.isWon()) {
            sessionWon += bet.getPayout();
        } else {
            sessionLost += bet.getAmount();
        }

        sessionWagered += bet.getAmount();
    }

    /**
     * Export all bets to CSV file
     */
    public String exportToCSV() throws IOException {
        String filename = "bets_" + LocalDateTime.now().format(FILE_FORMATTER) + ".csv";
        String filepath = IsaiahUtils.EXPORTS_DIR.getAbsolutePath() + "/" + filename;

        try (FileWriter writer = new FileWriter(filepath)) {
            // Write header
            writer.write("Time,Player,Amount,Status,Result,Multiplier,Payout,Profit\n");

            // Write all bets
            for (Bet bet : allBets) {
                writer.write(bet.toCSV() + "\n");
            }

            // Write summary
            writer.write("\n");
            writer.write("=== SUMMARY ===\n");
            writer.write(String.format("Total Bets,%d\n", allBets.size()));
            writer.write(String.format("Total Wagered,%d\n", sessionWagered));
            writer.write(String.format("Total Won,%d\n", sessionWon));
            writer.write(String.format("Total Lost,%d\n", sessionLost));
            writer.write(String.format("Net Profit,%d\n", sessionWon - sessionLost));
        }

        IsaiahUtils.LOGGER.info("Exported {} bets to {}", allBets.size(), filename);
        return filename;
    }

    /**
     * Get session statistics
     */
    public SessionStats getSessionStats() {
        long sessionDuration = System.currentTimeMillis() - sessionStart;
        return new SessionStats(
                allBets.size(),
                sessionWagered,
                sessionWon,
                sessionLost,
                sessionWon - sessionLost,
                sessionDuration
        );
    }

    /**
     * Reset session statistics
     */
    public void resetSession() {
        allBets.clear();
        sessionStart = System.currentTimeMillis();
        sessionWagered = 0;
        sessionWon = 0;
        sessionLost = 0;
        IsaiahUtils.LOGGER.info("Session statistics reset");
    }

    /**
     * Session statistics data class
     */
    public static class SessionStats {
        public final int totalBets;
        public final long totalWagered;
        public final long totalWon;
        public final long totalLost;
        public final long netProfit;
        public final long duration;

        public SessionStats(int totalBets, long totalWagered, long totalWon, long totalLost, long netProfit, long duration) {
            this.totalBets = totalBets;
            this.totalWagered = totalWagered;
            this.totalWon = totalWon;
            this.totalLost = totalLost;
            this.netProfit = netProfit;
            this.duration = duration;
        }

        public String getFormattedDuration() {
            long seconds = duration / 1000;
            long minutes = seconds / 60;
            long hours = minutes / 60;

            if (hours > 0) {
                return String.format("%dh %dm", hours, minutes % 60);
            } else if (minutes > 0) {
                return String.format("%dm %ds", minutes, seconds % 60);
            } else {
                return String.format("%ds", seconds);
            }
        }
    }
}
