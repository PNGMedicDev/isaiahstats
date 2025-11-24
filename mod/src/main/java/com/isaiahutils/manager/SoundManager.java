package com.isaiahutils.manager;

import com.isaiahutils.IsaiahUtils;
import net.minecraft.client.sound.PositionedSoundInstance;
import net.minecraft.sound.SoundEvents;

/**
 * Manages sound notifications for bet events
 */
public class SoundManager {

    public SoundManager() {
        IsaiahUtils.LOGGER.info("SoundManager initialized");
    }

    /**
     * Play sound when bet is received
     */
    public void playBetReceivedSound() {
        if (!IsaiahUtils.config.soundEnabled) return;

        playSound(SoundEvents.ENTITY_EXPERIENCE_ORB_PICKUP, 1.0f, 1.0f);
    }

    /**
     * Play sound when bet wins
     */
    public void playWinSound() {
        if (!IsaiahUtils.config.soundEnabled) return;

        playSound(SoundEvents.ENTITY_PLAYER_LEVELUP, 1.0f, 1.2f);
    }

    /**
     * Play sound when bet loses
     */
    public void playLossSound() {
        if (!IsaiahUtils.config.soundEnabled) return;

        playSound(SoundEvents.ENTITY_VILLAGER_NO, 0.5f, 0.8f);
    }

    /**
     * Play success sound (e.g., for export)
     */
    public void playSuccessSound() {
        if (!IsaiahUtils.config.soundEnabled) return;

        playSound(SoundEvents.ENTITY_PLAYER_LEVELUP, 1.0f, 1.5f);
    }

    /**
     * Play error sound
     */
    public void playErrorSound() {
        if (!IsaiahUtils.config.soundEnabled) return;

        playSound(SoundEvents.BLOCK_ANVIL_LAND, 0.3f, 0.5f);
    }

    /**
     * Helper method to play a sound
     */
    private void playSound(net.minecraft.sound.SoundEvent sound, float volume, float pitch) {
        if (IsaiahUtils.mc != null && IsaiahUtils.mc.getSoundManager() != null) {
            IsaiahUtils.mc.getSoundManager().play(
                    PositionedSoundInstance.master(sound, pitch, volume)
            );
        }
    }
}
