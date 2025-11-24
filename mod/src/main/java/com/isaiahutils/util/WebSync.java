package com.isaiahutils.util;

import com.google.gson.Gson;
import com.isaiahutils.IsaiahUtils;
import com.isaiahutils.model.Bet;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * Handles syncing bet data with the IsaiahStats web server
 */
public class WebSync {
    private static final Gson GSON = new Gson();
    private final HttpClient client;
    private final String serverUrl;
    private boolean enabled;

    public WebSync(String serverUrl, boolean enabled) {
        this.serverUrl = serverUrl;
        this.enabled = enabled;
        this.client = HttpClient.newHttpClient();
        IsaiahUtils.LOGGER.info("WebSync initialized: url={}, enabled={}", serverUrl, enabled);
    }

    /**
     * Send bet to server asynchronously
     */
    public void sendBet(Bet bet) {
        if (!enabled || bet == null) return;

        CompletableFuture.runAsync(() -> {
            try {
                Map<String, Object> data = new HashMap<>();
                data.put("username", bet.getPlayerName());
                data.put("amount", bet.getAmount());
                data.put("multiplier", bet.getMultiplier());
                data.put("result", bet.isWon() ? "win" : "loss");

                String json = GSON.toJson(data);

                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create(serverUrl + "/api/bet"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build();

                HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

                if (response.statusCode() == 200) {
                    IsaiahUtils.LOGGER.debug("Bet synced: {}", bet);
                } else {
                    IsaiahUtils.LOGGER.warn("Sync failed: HTTP {}", response.statusCode());
                }
            } catch (Exception e) {
                IsaiahUtils.LOGGER.error("Failed to sync bet", e);
            }
        });
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public boolean isEnabled() {
        return enabled;
    }
}
