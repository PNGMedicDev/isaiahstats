#!/usr/bin/env python3
"""
Discord Bot for Voice Channel Tracking
Monitors voice channel activity and updates IsaiahStats website
"""

import discord
from discord.ext import commands
import requests
import os
import json
from datetime import datetime

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN', 'YOUR_DISCORD_BOT_TOKEN_HERE')
WEBSITE_URL = os.getenv('WEBSITE_URL', 'http://localhost:5000')

# Bot setup with necessary intents
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# In-memory storage for minecraft username mappings
# Format: {discord_id: minecraft_username}
minecraft_mappings = {}

def load_mappings():
    """Load Minecraft username mappings from file"""
    global minecraft_mappings
    try:
        if os.path.exists('minecraft_mappings.json'):
            with open('minecraft_mappings.json', 'r') as f:
                minecraft_mappings = json.load(f)
    except Exception as e:
        print(f"Error loading mappings: {e}")
        minecraft_mappings = {}

def save_mappings():
    """Save Minecraft username mappings to file"""
    try:
        with open('minecraft_mappings.json', 'w') as f:
            json.dump(minecraft_mappings, f, indent=2)
    except Exception as e:
        print(f"Error saving mappings: {e}")

def update_website(discord_user, guild, channel, is_connected):
    """Send voice channel status update to website"""
    try:
        minecraft_username = minecraft_mappings.get(str(discord_user.id))

        data = {
            'discord_id': str(discord_user.id),
            'discord_username': str(discord_user),
            'minecraft_username': minecraft_username,
            'guild_name': guild.name if guild else None,
            'guild_id': str(guild.id) if guild else None,
            'channel_name': channel.name if channel else None,
            'channel_id': str(channel.id) if channel else None,
            'is_connected': is_connected
        }

        response = requests.post(
            f'{WEBSITE_URL}/api/discord/update',
            json=data,
            timeout=5
        )

        if response.status_code == 200:
            print(f"✅ Updated {discord_user} - {'Joined' if is_connected else 'Left'} {channel.name if channel else 'VC'}")
        else:
            print(f"❌ Failed to update website: {response.status_code}")

    except Exception as e:
        print(f"Error updating website: {e}")

@bot.event
async def on_ready():
    """Bot is ready"""
    print(f'🤖 Logged in as {bot.user}')
    print(f'📊 Monitoring {len(bot.guilds)} guild(s)')

    # Load mappings
    load_mappings()

    # Check all currently connected users in voice channels
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            for member in channel.members:
                if not member.bot:
                    update_website(member, guild, channel, True)

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice channel state changes"""
    # Ignore bots
    if member.bot:
        return

    # User joined a voice channel
    if before.channel is None and after.channel is not None:
        update_website(member, after.channel.guild, after.channel, True)

    # User left a voice channel
    elif before.channel is not None and after.channel is None:
        update_website(member, before.channel.guild, before.channel, False)

    # User switched voice channels
    elif before.channel != after.channel and after.channel is not None:
        # Update as disconnected from old channel
        update_website(member, before.channel.guild, before.channel, False)
        # Update as connected to new channel
        update_website(member, after.channel.guild, after.channel, True)

@bot.command(name='link')
async def link_minecraft(ctx, minecraft_username: str):
    """Link your Discord account to your Minecraft username"""
    minecraft_mappings[str(ctx.author.id)] = minecraft_username
    save_mappings()

    # Update current VC status with new minecraft username
    if ctx.author.voice and ctx.author.voice.channel:
        update_website(ctx.author, ctx.guild, ctx.author.voice.channel, True)

    await ctx.send(f'✅ Linked {ctx.author.mention} to Minecraft username: **{minecraft_username}**')

@bot.command(name='unlink')
async def unlink_minecraft(ctx):
    """Unlink your Minecraft username"""
    if str(ctx.author.id) in minecraft_mappings:
        del minecraft_mappings[str(ctx.author.id)]
        save_mappings()
        await ctx.send(f'✅ Unlinked {ctx.author.mention} from Minecraft username')
    else:
        await ctx.send(f'❌ No Minecraft username linked for {ctx.author.mention}')

@bot.command(name='whoami')
async def whoami(ctx):
    """Check your linked Minecraft username"""
    minecraft_username = minecraft_mappings.get(str(ctx.author.id))
    if minecraft_username:
        await ctx.send(f'🎮 {ctx.author.mention} is linked to: **{minecraft_username}**')
    else:
        await ctx.send(f'❌ {ctx.author.mention} has no linked Minecraft username. Use `!link <username>` to link.')

@bot.command(name='vcstatus')
async def vc_status(ctx):
    """Show current voice channel status"""
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send('❌ You are not in a voice channel')
        return

    channel = ctx.author.voice.channel
    members_list = [f"• {member.name}" for member in channel.members if not member.bot]

    embed = discord.Embed(
        title=f"🔊 {channel.name}",
        description=f"**{len(members_list)}** member(s) connected",
        color=discord.Color.green()
    )

    if members_list:
        embed.add_field(name="Members", value="\n".join(members_list), inline=False)

    await ctx.send(embed=embed)

if __name__ == '__main__':
    if DISCORD_TOKEN == 'YOUR_DISCORD_BOT_TOKEN_HERE':
        print("⚠️  ERROR: Please set DISCORD_BOT_TOKEN environment variable")
        print("   Example: export DISCORD_BOT_TOKEN='your_token_here'")
        exit(1)

    print("🚀 Starting Discord bot...")
    bot.run(DISCORD_TOKEN)
